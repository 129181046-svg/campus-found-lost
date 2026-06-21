# 🔍 Campus Lost & Found Network

A full-stack web application that helps students at SASTRA Deemed University report, discover, and recover lost or found items on campus — powered by an intelligent matching engine, real-time notifications, and an admin moderation panel.

**🔗 Live Demo:** [campus-lost-found.onrender.com](https://campus-lost-found.onrender.com) *(hosted on Render free tier — may take ~30s to wake up on first load)*

---

## ✨ Features

- 🔐 **Secure Authentication** — Registration restricted to campus email domain, bcrypt password hashing, session-based login
- 📝 **Item Reporting** — Report lost or found items with photo upload (Cloudinary), category, campus location, floor/room number, and tags
- 🧠 **Smart Matching Engine** — Automatically scores potential matches between lost and found reports using fuzzy string matching (RapidFuzz) across item name, location, category, and date
- 📬 **Email Notifications** — Automated emails for high-confidence matches (≥80%), claim submissions, approvals, and rejections via Gmail SMTP
- 🔔 **In-App Notifications** — Real-time notification bell with unread count for matches and claim updates
- 🧭 **Explore Feed** — Discover items reported by other students, browsable immediately after submitting your own report
- 🔍 **Search & Filters** — Full-text search with category, location, and status filters using MongoDB text indexes
- ✅ **Claims Workflow** — Submit ownership claims with verification details (color, brand, unique marks); finders approve or reject
- 🛡️ **Admin Panel** — Role-based moderation dashboard with user management, item moderation, and platform-wide analytics
- 📊 **Analytics Dashboard** — Live charts (Chart.js) showing recovery rate, lost-vs-found ratio, category breakdown, and reporting trends
- 📱 **Responsive Sidebar UI** — Mobile-friendly collapsible sidebar navigation with active-page highlighting

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask (Blueprint architecture) |
| Database | MongoDB Atlas (PyMongo) |
| Frontend | Jinja2, Bootstrap 5, Bootstrap Icons |
| Image Storage | Cloudinary |
| Email | Flask-Mail (Gmail SMTP) |
| Matching | RapidFuzz (fuzzy string matching) |
| Charts | Chart.js 4.4 |
| Auth | Flask-Bcrypt, Flask-WTF (CSRF protection) |
| Deployment | Render (Gunicorn WSGI server) |

---

## 🏗️ Architecture

```
campus-lost-found/
├── app/
│   ├── __init__.py          # App factory, blueprint registration, context processors
│   ├── config.py            # Environment-based configuration
│   ├── extensions.py        # Flask extensions (bcrypt, mail)
│   ├── auth/                # Registration, login, session management
│   ├── items/                # Report, edit, delete, explore, item detail
│   ├── matching/             # Fuzzy-match engine + match dashboard
│   ├── claims/                # Claim submission, approval, rejection
│   ├── search/                # Full-text search with filters
│   ├── admin/                 # Role-based admin panel + analytics
│   ├── notifications/         # In-app notification system
│   ├── static/css/            # Custom styling
│   └── templates/             # Jinja2 templates (sidebar layout, per-feature views)
├── run.py                     # Application entry point
├── Procfile                   # Render/Gunicorn start command
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- MongoDB Atlas account (free tier works)
- Cloudinary account (free tier works)
- Gmail account with an [App Password](https://support.google.com/accounts/answer/185833) for SMTP

### Local Setup

```bash
# Clone the repository
git clone https://github.com/<your-username>/campus-lost-found.git
cd campus-lost-found

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```dotenv
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

MONGO_URI=your-mongodb-atlas-connection-string

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-16-char-app-password
```

### Run Locally

```bash
python run.py
```

Visit `http://127.0.0.1:5000`

---

## 🚀 Deployment (Render)

1. Push the repository to GitHub
2. Create a new **Web Service** on [Render](https://render.com), connected to the GitHub repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn "app:create_app()"`
5. Add all environment variables from `.env` in the Render dashboard
6. In MongoDB Atlas → Network Access, allow `0.0.0.0/0` so Render can connect
7. Every `git push` to `main` automatically triggers a redeploy

---

## 🧠 How the Matching Engine Works

When an item is reported, the matching engine compares it against all open items of the opposite type (lost ↔ found) using a weighted similarity score:

| Factor | Weight |
|---|---|
| Item name similarity (fuzzy match) | 60% |
| Location match | 20% |
| Category match | 10% |
| Date proximity | 10% |

Matches scoring **55+** are recorded and visible on the My Matches page. Matches scoring **80+** additionally trigger automatic email and in-app notifications to both reporters.

---

## 📋 Known Limitations

- Duplicate match-found emails may occasionally be sent for the same match pair, since the matching engine runs once per report submission (a documented fix would add a `notified` flag to match records)
- Free-tier hosting means the live demo may take ~30 seconds to wake up after periods of inactivity
- Emails to institutional (`@sastra.ac.in`) addresses may occasionally be filtered; Gmail-to-Gmail delivery is reliable

---

## 👤 Author

**Sathiyanarayanan G**
B.tech CSE Sophomore student
SASTRA Deemed University

---

## 📄 License

This project was built as an academic project. Feel free to fork and adapt for your own institution.