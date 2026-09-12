import sqlite3

DB_NAME = "support_crm.db"


def get_db_connection():
    """Opens a connection to the SQLite database.
    row_factory lets us access columns by name (like a dict) instead of index."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the companies, tickets, and notes tables if they don't already exist.
    Called once when the app starts."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Each company = one tenant. Their employees share this one login.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            company_id INTEGER NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            priority TEXT NOT NULL DEFAULT 'Medium',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies (id),
            UNIQUE (company_id, ticket_id)
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


def generate_ticket_id(conn, company_id):
    """Generates the next ticket ID *within this company* — each company gets
    its own TKT-001, TKT-002, ... sequence. Safe now because the UNIQUE
    constraint is on (company_id, ticket_id) together, not ticket_id alone."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM tickets WHERE company_id = ?", (company_id,))
    count = cursor.fetchone()["count"]
    next_number = count + 1
    return f"TKT-{next_number:03d}"