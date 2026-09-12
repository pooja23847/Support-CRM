# 🎫 Support Ticketing CRM

A simple, clean full-stack support ticket management system — create tickets, search in real-time, filter by status, and track updates with notes and priority levels. Supports multiple companies with fully isolated data.

Built as part of the **Datastraw Technologies** hiring assessment.

🔗 **Live app:** https://support-crm-b1ap.onrender.com
📹 **Demo video:** _add your demo video link here_

> ⚠️ Free-tier hosting: the app may take 30-50 seconds to wake up on first load if it's been idle.

---

## ✨ Features

- 🔐 **Company Signup & Login** — each company gets its own isolated workspace *(bonus feature)*
- 📝 **Create Tickets** — capture customer name, email, issue title, and description
- 🆔 **Auto-generated Ticket IDs** — `TKT-001`, `TKT-002`, ... (scoped per company)
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
| 🔑 Auth | Flask sessions + Werkzeug password hashing |
| 🎨 Frontend | HTML + Tailwind CSS (CDN) |
| ⚡ Logic | Vanilla JavaScript (fetch API) |
| 🚀 Deployment | Render.com (via gunicorn) |

---

## 🚀 Quick Start (Local Setup)

**1. Clone the repo**
```bash
git clone https://github.com/pooja23847/Support-CRM.git
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

**6. Open in browser** 👉 `http://127.0.0.1:5000` — you'll land on the signup page first.

> 💡 The SQLite database (`support_crm.db`) is created automatically on first run — no manual setup needed.

---

## 🔌 API Endpoints

All ticket endpoints require an active login session.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/signup` | 🏢 Register a new company account |
| `POST` | `/api/login` | 🔑 Log in to a company account |
| `GET` | `/logout` | 🚪 End the session |
| `POST` | `/api/tickets` | ➕ Create a new ticket |
| `GET` | `/api/tickets?status=&search=` | 📋 List tickets (with optional filters) |
| `GET` | `/api/tickets/<ticket_id>` | 🔎 Get a single ticket with its notes |
| `PUT` | `/api/tickets/<ticket_id>` | ✏️ Update status, priority, and/or add a note |

---

## 📁 Project Structure

```
support-crm/
├── app.py              # 🧠 Flask routes — auth, pages, API
├── database.py           # 🗄️ SQLite connection & table setup
├── templates/             # 🖼️ HTML pages
│   ├── login.html
│   ├── signup.html
│   ├── index.html
│   ├── create.html
│   └── detail.html
├── static/
│   └── script.js           # ⚡ Frontend logic — auth, search, filter, API calls
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 💡 Bonus Features

**1. Priority Levels**
Added a priority field (High / Medium / Low) so urgent issues surface at the top of the list.
*Why:* A real support team handling hundreds of tickets a day can't triage everything equally.
*Trade-off:* Priority is set manually rather than auto-detected from keywords — kept simple given the timeline.

**2. Multi-Tenancy (Company Signup/Login)**
Each company that signs up gets a fully isolated ticket workspace — one company can never see or access another's tickets, even by guessing a ticket ID.
*Why:* Datastraw (or any company) would realistically sell this CRM to multiple client teams, not just one — data isolation is a hard requirement in that scenario.
*Trade-off:* One shared login per company (not per individual employee) and passwords are hashed but sessions aren't hardened for production (e.g. no rate limiting, no password reset flow) — reasonable for this assignment's scope, but would need hardening for real production use.

---

## 🌐 Deployment

Deployed on **Render.com** using `gunicorn` as the production server.

**Start command:** `gunicorn app:app`

---

Made with ☕ and a lot of debugging by Pooja 🙂