# 🎫 Support Ticketing CRM

A simple, clean full-stack support ticket management system — create tickets, search in real-time, filter by status, and track updates with notes and priority levels.

Built as part of the **Datastraw Technologies** hiring assessment.

---

## ✨ Features

- 📝 **Create Tickets** — capture customer name, email, issue title, and description
- 🆔 **Auto-generated Ticket IDs** — `TKT-001`, `TKT-002`, ...
- 📋 **List All Tickets** — clean table view with ID, customer, subject, priority, status, and date
- 🔍 **Real-time Search** — filter across name, email, ticket ID, and description as you type
- 🚦 **Filter by Status** — Open / In Progress / Closed
- 🔥 **Priority Levels** — High / Medium / Low, with urgent tickets surfaced first *(bonus feature)*
- 🗒️ **Ticket Detail & Notes** — view full ticket, update status/priority, and log notes over time

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| 🐍 Backend | Python + Flask |
| 🗄️ Database | SQLite |
| 🎨 Frontend | HTML + Tailwind CSS (CDN) |
| ⚡ Logic | Vanilla JavaScript (fetch API) |
| 🚀 Deployment | Render.com (via gunicorn) |

---

## 🚀 Quick Start (Local Setup)

**1. Clone the repo**
```bash
git clone <your-repo-url>
cd support-crm
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**
```bash
cp .env.example .env
```

**5. Run the app**
```bash
python app.py
```

**6. Open in browser** 👉 `http://127.0.0.1:5000`

> 💡 The SQLite database (`support_crm.db`) is created automatically on first run — no manual setup needed.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/tickets` | ➕ Create a new ticket |
| `GET` | `/api/tickets?status=&search=` | 📋 List tickets (with optional filters) |
| `GET` | `/api/tickets/<ticket_id>` | 🔎 Get a single ticket with its notes |
| `PUT` | `/api/tickets/<ticket_id>` | ✏️ Update status, priority, and/or add a note |

---

## 📁 Project Structure

```
support-crm/
├── app.py              # 🧠 Flask routes — pages + API
├── database.py           # 🗄️ SQLite connection & table setup
├── templates/             # 🖼️ HTML pages
│   ├── index.html
│   ├── create.html
│   └── detail.html
├── static/
│   └── script.js           # ⚡ Frontend logic — search, filter, API calls
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 💡 Bonus Feature: Priority Levels

Added a **priority field** (High / Medium / Low) to tickets so urgent issues surface at the top of the list.

**Why:** A real support team handling hundreds of tickets a day can't triage everything equally — urgency needs to be visible at a glance.

**Trade-off:** Priority is set manually (by whoever creates/updates the ticket) rather than auto-detected from keywords or SLAs — kept simple given the project timeline, with room to automate later.

---

## 🌐 Deployment

Deployed on **Render.com** using `gunicorn` as the production server.

**Start command:** `gunicorn app:app`

🔗 **Live app:** _add your deployed URL here_

---

## 🎥 Demo Video

📹 _add your demo video link here_

---