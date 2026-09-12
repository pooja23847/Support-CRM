from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db, generate_ticket_id

app = Flask(__name__)

# Needed for Flask sessions (login cookies) to work — in a real app, keep this
# secret and load it from an environment variable, not hardcoded.
app.secret_key = "dev-secret-key-change-this-in-production"

# Create the tables (if they don't exist yet) when the app starts
init_db()


# ---------- AUTH HELPER ----------

def login_required(f):
    """Decorator: wrap any route with this to require the user to be logged in.
    If not logged in, page routes redirect to /login, API routes return 401."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "company_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Not logged in"}), 401
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


# ---------- AUTH PAGE ROUTES ----------

@app.route("/signup")
def signup_page():
    if "company_id" in session:
        return redirect(url_for("home"))
    return render_template("signup.html")


@app.route("/login")
def login_page():
    if "company_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ---------- AUTH API ROUTES ----------

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json()

    required_fields = ["company_name", "username", "password"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    conn = get_db_connection()

    existing = conn.execute(
        "SELECT id FROM companies WHERE username = ?", (data["username"],)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "Username already taken"}), 400

    password_hash = generate_password_hash(data["password"])
    now = datetime.now().isoformat()

    cursor = conn.execute(
        "INSERT INTO companies (company_name, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (data["company_name"], data["username"], password_hash, now)
    )
    conn.commit()
    company_id = cursor.lastrowid
    conn.close()

    # log the new company in immediately after signup
    session["company_id"] = company_id
    session["company_name"] = data["company_name"]

    return jsonify({"success": True}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    company = conn.execute(
        "SELECT * FROM companies WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if company is None or not check_password_hash(company["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["company_id"] = company["id"]
    session["company_name"] = company["company_name"]

    return jsonify({"success": True})


# ---------- PAGE ROUTES (serve HTML) ----------

@app.route("/")
@login_required
def home():
    return render_template("index.html", company_name=session.get("company_name"))


@app.route("/create")
@login_required
def create_page():
    return render_template("create.html")


@app.route("/tickets/<ticket_id>")
@login_required
def ticket_detail_page(ticket_id):
    return render_template("detail.html", ticket_id=ticket_id)


# ---------- API ROUTES (return JSON) ----------

@app.route("/api/tickets", methods=["POST"])
@login_required
def create_ticket():
    data = request.get_json()
    company_id = session["company_id"]

    required_fields = ["customer_name", "customer_email", "subject", "description"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    priority = data.get("priority", "Medium")

    conn = get_db_connection()
    ticket_id = generate_ticket_id(conn, company_id)
    now = datetime.now().isoformat()

    conn.execute("""
        INSERT INTO tickets (ticket_id, company_id, customer_name, customer_email, subject, description, status, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'Open', ?, ?, ?)
    """, (ticket_id, company_id, data["customer_name"], data["customer_email"], data["subject"], data["description"], priority, now, now))

    conn.commit()
    conn.close()

    return jsonify({"ticket_id": ticket_id, "created_at": now}), 201


@app.route("/api/tickets", methods=["GET"])
@login_required
def get_tickets():
    company_id = session["company_id"]
    status_filter = request.args.get("status")
    search_query = request.args.get("search")

    conn = get_db_connection()
    query = "SELECT ticket_id, customer_name, subject, status, priority, created_at FROM tickets WHERE company_id = ?"
    params = [company_id]

    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    if search_query:
        query += """ AND (
            customer_name LIKE ? OR
            customer_email LIKE ? OR
            ticket_id LIKE ? OR
            description LIKE ?
        )"""
        like_term = f"%{search_query}%"
        params.extend([like_term, like_term, like_term, like_term])

    query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, created_at DESC"

    tickets = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(t) for t in tickets])


@app.route("/api/tickets/<ticket_id>", methods=["GET"])
@login_required
def get_ticket(ticket_id):
    company_id = session["company_id"]
    conn = get_db_connection()

    # the company_id check here means someone can't view another company's
    # ticket even if they guess/type its ticket_id
    ticket = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ? AND company_id = ?", (ticket_id, company_id)
    ).fetchone()
    if ticket is None:
        conn.close()
        return jsonify({"error": "Ticket not found"}), 404

    notes = conn.execute(
        "SELECT * FROM notes WHERE ticket_id = ? ORDER BY created_at ASC", (ticket_id,)
    ).fetchall()
    conn.close()

    result = dict(ticket)
    result["notes"] = [dict(n) for n in notes]
    return jsonify(result)


@app.route("/api/tickets/<ticket_id>", methods=["PUT"])
@login_required
def update_ticket(ticket_id):
    company_id = session["company_id"]
    data = request.get_json()
    conn = get_db_connection()

    ticket = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ? AND company_id = ?", (ticket_id, company_id)
    ).fetchone()
    if ticket is None:
        conn.close()
        return jsonify({"error": "Ticket not found"}), 404

    now = datetime.now().isoformat()

    if data.get("status"):
        conn.execute(
            "UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_id = ?",
            (data["status"], now, ticket_id)
        )

    if data.get("priority"):
        conn.execute(
            "UPDATE tickets SET priority = ?, updated_at = ? WHERE ticket_id = ?",
            (data["priority"], now, ticket_id)
        )

    if data.get("notes"):
        conn.execute(
            "INSERT INTO notes (ticket_id, note_text, created_at) VALUES (?, ?, ?)",
            (ticket_id, data["notes"], now)
        )
        conn.execute("UPDATE tickets SET updated_at = ? WHERE ticket_id = ?", (now, ticket_id))

    conn.commit()
    conn.close()

    return jsonify({"success": True, "updated_at": now})


if __name__ == "__main__":
    app.run(debug=True)