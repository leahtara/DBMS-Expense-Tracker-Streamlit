# Expense Tracker

## Schema 

### **Tables**
#### **Users**
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL
);
```

#### **Categories**
```sql
CREATE TABLE categories (
    name TEXT,
    user_id TEXT,
    type TEXT CHECK(type IN ('Income', 'Expense')),
    PRIMARY KEY (name, user_id),
    FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE
);
```

#### **Transactions**
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    category_name TEXT,
    amount REAL NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY (category_name, user_id) REFERENCES categories(name, user_id) ON DELETE CASCADE
);
```

#### **Budgets**
```sql
CREATE TABLE budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    category_name TEXT,
    amount REAL NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY (category_name, user_id) REFERENCES categories(name, user_id) ON DELETE CASCADE
);
```

#### **Recurring Transactions**
```sql
CREATE TABLE recurring_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    category_name TEXT,
    amount REAL NOT NULL,
    interval TEXT CHECK(interval IN ('Daily', 'Weekly', 'Monthly', 'Yearly')) NOT NULL,
    next_due_date TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(username) ON DELETE CASCADE,
    FOREIGN KEY (category_name, user_id) REFERENCES categories(name, user_id) ON DELETE CASCADE
);
```

##