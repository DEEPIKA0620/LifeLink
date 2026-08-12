# LifeLink — Emergency Blood & Medicine Locator System

> **"Find Blood. Find Medicine. Save Lives."**

LifeLink is a web-based emergency healthcare coordination platform that connects **Patients**, **Blood Donors**, **Hospitals**, **Pharmacies**, and **Administrators** to help users quickly locate suitable blood donors, nearby hospitals, available blood stock, nearby pharmacies, and required medicines.

---

## Problem Statement

In emergency situations, finding compatible blood donors or specific medicines quickly can be extremely difficult. Patients and hospitals often resort to manually calling multiple contacts, visiting blood banks, or searching pharmacies — wasting precious time when every second counts.

## Solution

LifeLink provides a centralized digital platform with:

- **Smart Emergency Donor Matching System** — A transparent 100-point scoring algorithm that ranks donors based on blood compatibility, distance, availability, response rate, and eligibility
- **Real-time Location Search** — Find nearby donors, hospitals, and pharmacies using GPS and Haversine distance calculations
- **Medicine Locator** — Search for medicines across nearby pharmacies with availability status
- **Emergency Request Workflow** — Create urgent blood requests that automatically match and notify suitable donors
- **Role-based Dashboards** — Specialized interfaces for patients, donors, hospitals, pharmacies, and administrators

---

## Features

### Core Features
- 🚨 **Emergency Blood Requests** with priority levels (Critical/Urgent/Normal)
- 🧠 **Smart Donor Matching Engine** — Transparent 0-100 scoring with human-readable explanations
- 🗺️ **Interactive Map** (Leaflet + OpenStreetMap) showing nearby donors, hospitals, pharmacies
- 💊 **Medicine Locator** with pharmacy proximity search
- 🔔 **Real-time Notifications** for emergency alerts and status updates
- 📊 **Admin Dashboard** with statistics and charts
- 🔐 **JWT Authentication** with bcrypt password hashing
- 🛡️ **Role-Based Access Control** (RBAC) enforced on backend

### Smart Matching Algorithm (100 Points)
| Factor | Points | Description |
|--------|--------|-------------|
| Blood Compatibility | 30 | ABO/Rh compatibility check |
| Availability | 20 | Current donor availability status |
| Distance | 20 | Haversine distance from request location |
| Travel Time | 10 | Estimated travel time |
| Response Rate | 10 | Historical response rate |
| Eligibility | 10 | Donation eligibility based on last donation |

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, CSS3, Tailwind CSS (CDN), Vanilla JavaScript |
| **Backend** | Python, FastAPI |
| **Database** | MySQL (SQLite fallback for development) |
| **Authentication** | JWT (python-jose), bcrypt (passlib) |
| **Maps** | Leaflet.js + OpenStreetMap |
| **Location** | Haversine formula, Browser Geolocation API |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic v2 |

---

## Architecture

```
                    LIFELINK
                       |
          +------------+------------+
          |                         |
      FRONTEND                   BACKEND
    (HTML/CSS/JS)              (FastAPI)
          |                         |
     Tailwind CSS              REST API
     Leaflet Maps                  |
          |                    SQLAlchemy
          +------------+------------+
                       |
                   MySQL/SQLite
                       |
       +-------+-------+-------+-------+
       |       |       |       |       |
     Users  Donors  Hospitals  Pharma  Admin
```

---

## Project Structure

```
LifeLink/
├── frontend/
│   ├── index.html                    # Landing page
│   ├── css/
│   │   ├── style.css                 # Global design system
│   │   ├── dashboard.css             # Dashboard layouts
│   │   └── responsive.css            # Mobile responsive rules
│   ├── js/
│   │   ├── api.js                    # Reusable API client
│   │   ├── auth.js                   # Authentication module
│   │   ├── navigation.js             # Dynamic navbar
│   │   ├── location.js               # Geolocation helper
│   │   ├── map.js                    # Leaflet map module
│   │   ├── matching.js               # Match card renderer
│   │   ├── notifications.js          # Notification badge
│   │   ├── validation.js             # Form validation
│   │   └── utils.js                  # Utility functions
│   └── pages/
│       ├── login.html, register.html, about.html
│       ├── find-blood.html, emergency-request.html
│       ├── medicine-locator.html, notifications.html
│       ├── request-details.html, request-history.html
│       ├── patient/dashboard.html
│       ├── donor/dashboard.html, profile.html, donation-history.html
│       ├── hospital/dashboard.html, blood-stock.html, requests.html
│       ├── pharmacy/dashboard.html, medicine-stock.html
│       └── admin/dashboard.html
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry
│   │   ├── config.py                 # Environment configuration
│   │   ├── database.py               # SQLAlchemy setup
│   │   ├── security.py               # JWT & password utilities
│   │   ├── dependencies.py           # Auth dependencies & RBAC
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic validation schemas
│   │   ├── routers/                  # API route handlers
│   │   ├── services/                 # Business logic services
│   │   └── utils/                    # Helper utilities
│   ├── requirements.txt
│   ├── .env                          # Environment variables
│   └── .env.example
├── database/
│   ├── schema.sql                    # MySQL table definitions
│   ├── seed.sql                      # Demo data
│   └── README.md
├── tests/                            # Pytest test suite
├── postman/                          # Postman API collection
├── README.md
├── .gitignore
└── LICENSE
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- MySQL 8.0+ (optional — SQLite used as fallback)
- Web browser with JavaScript enabled

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Run the server
uvicorn app.main:app --reload --port 8000
```

The backend auto-seeds demo data on first startup if the database is empty.

### Frontend Setup

```bash
cd frontend

# Option 1: Python HTTP server
python -m http.server 5500

# Option 2: VS Code Live Server extension
# Right-click index.html → Open with Live Server
```

### Access Points
- **Frontend**: http://localhost:5500
- **Backend API**: http://localhost:8000/api
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Demo Accounts

All demo accounts use password: `LifeLink@123`

| Role | Email | Description |
|------|-------|-------------|
| **Admin** | admin@lifelink.org | Platform administrator |
| **Patient** | patient1@example.com | Emergency requester |
| **Donor** | ravi.kumar@example.com | Blood donor (O+) |
| **Hospital** | manipal@lifelink.org | Hospital blood bank |
| **Pharmacy** | apollopharm1@lifelink.org | Pharmacy manager |

---

## Environment Variables

```env
# Database (SQLite fallback if unconfigured)
DATABASE_URL=sqlite:///./lifelink.db

# JWT Security
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional Integrations
EMAIL_API_KEY=
SMS_API_KEY=
MAP_API_KEY=

# CORS
CORS_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

---

## API Documentation

All APIs are documented via FastAPI's automatic Swagger UI at `/docs`.

### Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login & get JWT |
| GET | `/api/auth/me` | Get current user |
| GET | `/api/donors/nearby` | Find nearby donors |
| POST | `/api/blood-requests` | Create emergency request |
| GET | `/api/blood-requests/{id}/matches` | Get ranked donor matches |
| POST | `/api/matches/{id}/accept` | Donor accepts request |
| GET | `/api/medicines/search` | Search medicines |
| GET | `/api/medicines/nearby` | Nearby medicine search |
| GET | `/api/hospitals/nearby` | Find nearby hospitals |
| GET | `/api/admin/dashboard` | Admin statistics |

---

## Testing

### Backend Tests
```bash
cd backend
pytest ../tests/ -v
```

### Postman
Import `postman/LifeLink_API_Collection.json` into Postman for full API testing.

---

## Deployment

### Backend (Render/Railway)
1. Push to GitHub
2. Connect repository to Render/Railway
3. Set environment variables
4. Deploy with: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel/Netlify)
1. Deploy the `frontend/` directory
2. Update `API_BASE_URL` in `js/api.js` to point to deployed backend

---

## Medical Disclaimer

> **LifeLink is an emergency coordination and information platform.** It does not provide medical diagnosis or treatment. Blood compatibility, transfusion decisions, medicine suitability, and emergency treatment must always be confirmed by qualified healthcare professionals, authorized blood banks, or pharmacies. Matching scores are generated strictly for donor discovery and prioritization — they do NOT guarantee medical compatibility.

---

## Future Scope

- AI-based blood demand prediction
- Native mobile application (React Native / Flutter)
- Real-time push notifications
- Hospital/blood bank API integration
- Advanced analytics dashboard
- Multilingual support
- Voice-based emergency search
- Ambulance integration
- Blood bank inventory integration

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**Built with ❤️ for emergency healthcare coordination.**
