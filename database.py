import sqlite3

def get_db():
    conn = sqlite3.connect("budget.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT NOT NULL,
            name TEXT NOT NULL,
            default_amount REAL DEFAULT 0,
            frequency TEXT DEFAULT 'biweekly'
        );

        CREATE TABLE IF NOT EXISTS paychecks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paycheck_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (paycheck_id) REFERENCES paychecks(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target REAL NOT NULL,
            saved REAL DEFAULT 0,
            deadline TEXT,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    """)

    cursor.executescript("""
        INSERT OR IGNORE INTO categories (id, group_name, name, default_amount, frequency) VALUES
        (1,  'Investing', 'Roth IRA',        556,  'biweekly'),
        (2,  'Investing', 'Brokerage',        200,  'biweekly'),
        (3,  'Savings',   'House Fund',       375,  'biweekly'),
        (4,  'Savings',   'Emergency Fund',   250,  'biweekly'),
        (5,  'Housing',   'Rent',             600,  'monthly'),
        (6,  'Transport', 'Car',              200,  'monthly'),
        (7,  'Food',      'Groceries',        200,  'biweekly'),
        (8,  'Food',      'Dining',           150,  'biweekly'),
        (9,  'Other',     'Subscriptions',     75,  'monthly'),
        (10, 'Other',     'Misc',             100,  'biweekly');
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database created successfully.")