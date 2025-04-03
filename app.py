import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timedelta

# Database connection
def get_db_connection():
    conn = sqlite3.connect("expense_tracker.db")
    conn.row_factory = sqlite3.Row
    return conn

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User Authentication
def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

# Category Management
def add_category(user_id, name, category_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)", (user_id, name, category_type))
    conn.commit()
    conn.close()

def get_categories(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE user_id = ? AND deleted = 0", (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return categories

def delete_category(user_id, category_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE categories SET deleted = 1 WHERE user_id = ? AND name = ?", (user_id, category_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Transaction Entry
def add_transaction(user_id, category_name, amount, date, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (user_id, category_name, amount, date, description) VALUES (?, ?, ?, ?, ?)", (user_id, category_name, amount, date, description))
    conn.commit()
    conn.close()

def get_transactions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.* FROM transactions t
        JOIN categories c ON t.category_name = c.name AND t.user_id = c.user_id
        WHERE t.user_id = ? AND c.deleted = 0
        ORDER BY t.date DESC
    """, (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Streamlit UI
st.title("Expense Tracker")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.subheader("Login or Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = authenticate_user(username, password)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["user_id"] = user["username"]
            st.rerun()
        else:
            st.error("Invalid credentials")
    if st.button("Sign Up"):
        if create_user(username, password):
            st.success("Account created! Please log in.")
        else:
            st.error("Username already taken.")
else:
    st.subheader("Welcome to Your Dashboard")
    
    # Category Management
    st.subheader("Manage Categories")
    category_name = st.text_input("Category Name")
    category_type = st.radio("Category Type", ["Expense", "Income"])
    if st.button("Add Category"):
        add_category(st.session_state["user_id"], category_name, category_type)
        st.success("Category added!")
        st.rerun()
    
    categories = get_categories(st.session_state["user_id"])
    for category in categories:
        if st.button(f"Delete {category['name']}"):
            if delete_category(st.session_state["user_id"], category['name']):
                st.success("Category deleted!")
                st.rerun()
            else:
                st.error("Cannot delete category with existing transactions.")
    
    # Transaction Entry
    st.subheader("Add Transaction")
    category_options = {cat["name"]: cat["name"] for cat in categories}
    selected_category = st.selectbox("Select Category", options=list(category_options.keys()))
    amount = st.number_input("Amount", min_value=0.01, format="%.2f")
    date = st.date_input("Date", datetime.today())
    description = st.text_area("Description")
    if st.button("Add Transaction"):
        add_transaction(st.session_state["user_id"], selected_category, amount, date, description)
        st.success("Transaction added!")
        st.rerun()
    
    # View Transactions
    st.subheader("Transaction History")
    transactions = get_transactions(st.session_state["user_id"])
    for txn in transactions:
        sign = "+" if next(cat["type"] for cat in categories if cat["name"] == txn["category_name"] and cat["user_id"] == st.session_state["user_id"]) == "Income" else "-"
        st.write(f"{txn['date']} - {category_options[txn['category_name']]}: {sign}${abs(txn['amount'])} - {txn['description']}")

    # View spending and earning summary
    st.subheader("Transaction Summary")
    # Date range input
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=7))
    end_date = st.date_input("End Date", datetime.today())
    # Ensure valid date range
    if start_date > end_date:
        st.error("Start date must be before or the same as the end date.")
    else:
        # Fetch transactions within the date range
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.amount, c.type 
            FROM transactions t 
            JOIN categories c ON t.category_name = c.name AND t.user_id = c.user_id
            WHERE t.user_id = ? AND t.date BETWEEN ? AND ?
        """, (st.session_state["user_id"], start_date, end_date))
        transactions = cursor.fetchall()
        conn.close()
        # Calculate total expenses and earnings
        total_expense = sum(txn["amount"] for txn in transactions if txn["type"] == "Expense")
        total_income = sum(txn["amount"] for txn in transactions if txn["type"] == "Income")
        # Display results
        st.write(f"**Total Income:** ${total_income:.2f}")
        st.write(f"**Total Expenses:** ${total_expense:.2f}")
        st.write(f"**Net Balance:** ${total_income - total_expense:.2f}")
 