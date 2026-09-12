from flask import Flask, request, jsonify, render_template
from datetime import datetime
from database import get_db_connection, init_db, generate_ticket_id

app = Flask(__name__)

# Create the tables (if they don't exist yet) when the app starts
init_db()


# ---------- PAGE ROUTES (serve HTML) ----------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create")
def create_page():
    return render_template("create.html")


@app.route("/tickets/<ticket_id>")
def ticket_detail_page(ticket_id):
    return render_template("detail.html", ticket_id=ticket_id)


# ---------- API ROUTES (return JSON) ----------

@app.route("/api/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json()

    # basic validation — required fields must be present
    required_fields = ["customer_name", "customer_email", "subject", "description"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    priority = data.get("priority", "Medium")

    conn = get_db_connection()
    ticket_id = generate_ticket_id(conn)
    now = datetime.now().isoformat()

    conn.execute("""
        INSERT INTO tickets (ticket_id, customer_name, customer_email, subject, description, status, priority, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'Open', ?, ?, ?)
    """, (ticket_id, data["customer_name"], data["customer_email"], data["subject"], data["description"], priority, now, now))

    conn.commit()
    conn.close()

    return jsonify({"ticket_id": ticket_id, "created_at": now}), 201


@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    status_filter = request.args.get("status")
    search_query = request.args.get("search")

    conn = get_db_connection()
    query = "SELECT ticket_id, customer_name, subject, status, priority, created_at FROM tickets WHERE 1=1"
    params = []

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

    # High priority tickets first, then Medium, then Low; newest first within each
    query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, created_at DESC"

    tickets = conn.execute(query, params).fetchall()
    conn.close()

    # convert sqlite3.Row objects into plain dicts so jsonify can serialize them
    return jsonify([dict(t) for t in tickets])


@app.route("/api/tickets/<ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    conn = get_db_connection()

    ticket = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
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
def update_ticket(ticket_id):
    data = request.get_json()
    conn = get_db_connection()

    ticket = conn.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
    if ticket is None:
        conn.close()
        return jsonify({"error": "Ticket not found"}), 404

    now = datetime.now().isoformat()

    # update status only if it was provided
    if data.get("status"):
        conn.execute(
            "UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_id = ?",
            (data["status"], now, ticket_id)
        )

    # update priority only if it was provided
    if data.get("priority"):
        conn.execute(
            "UPDATE tickets SET priority = ?, updated_at = ? WHERE ticket_id = ?",
            (data["priority"], now, ticket_id)
        )

    # add a note only if note text was provided
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