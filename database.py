import sqlite3

DB_NAME = "support_crm.db"


def get_db_connection():
    """Opens a connection to the SQLite database.
    row_factory lets us access columns by name (like a dict) instead of index."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the tickets and notes tables if they don't already exist.
    Called once when the app starts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            priority TEXT NOT NULL DEFAULT 'Medium',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            note_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
        )
    """)

    conn.commit()
    conn.close()


def generate_ticket_id(conn):
    """Looks at how many tickets exist and generates the next ID: TKT-001, TKT-002, ..."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM tickets")
    count = cursor.fetchone()["count"]
    next_number = count + 1
    return f"TKT-{next_number:03d}"   # :03d pads with zeros -> 001, 002, ... 010, 011