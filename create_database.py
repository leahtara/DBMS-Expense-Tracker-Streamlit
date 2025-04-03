import sqlite3

def create_database():
    conn = sqlite3.connect("expense_tracker.db")
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT,
            user_id TEXT,
            type TEXT CHECK(type IN ('Income', 'Expense')),
            deleted INTEGER DEFAULT 0,
            PRIMARY KEY (name, user_id),
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            category_name TEXT,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
            FOREIGN KEY (category_name, user_id) REFERENCES categories(name, user_id) ON DELETE CASCADE
        )
    ''')
    
    # Budgets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            category_name TEXT,
            amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
            FOREIGN KEY (category_name, user_id) REFERENCES categories(name, user_id) ON DELETE CASCADE
        )
    ''')
    
    # Recurring Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            category_name TEXT,
            amount REAL NOT NULL,
            interval TEXT CHECK(interval IN ('Daily', 'Weekly', 'Monthly', 'Yearly')) NOT NULL,
            next_due_date TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
            FOREIGN KEY (category_name, user_id) REFERENCES categories(name, user_id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database and tables created successfully.")
