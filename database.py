import sqlite3

def get_db():
    conn = sqlite3.connect("budget.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS paychecks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paycheck_id INTEGER,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            FOREIGN KEY (paycheck_id) REFERENCES paychecks(id)
        );

        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target REAL NOT NULL,
            saved REAL DEFAULT 0,
            deadline TEXT
        );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database created successfully.")