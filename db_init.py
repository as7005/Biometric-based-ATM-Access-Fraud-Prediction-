# db_init.py
import sqlite3

DB = "biometric_atm.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # Users: id, name, encoding (blob), created_at
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        encoding BLOB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # Logs: id, timestamp, event_type, details
    c.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT,
        details TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("Database initialized:", DB)

if __name__ == "__main__":
    init_db()
