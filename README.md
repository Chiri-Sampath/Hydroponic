# AgriSmart AI

**AI-Based Smart Food Production & Market Intelligence Platform**

> *"From Location to Cultivation to Market — AI-powered decision support for smarter food production."*

---

## Overview

AgriSmart AI helps users determine the best food-production opportunity by analysing their location, available resources, objectives, and market conditions across three cultivation ecosystems:

- **Hydroponics** — soil-free, water-based plant cultivation
- **Algaculture / Microalgae** — photobioreactor or open-raceway cultivation  
- **Fungi / Mushrooms** — substrate-based indoor cultivation

The platform guides users through a complete decision workflow: location → weather → resources → AI recommendation → cultivation plan → economics → quality testing → laboratory discovery → market intelligence → buyer matching → logistics → net realizable price → Cultivate-to-Market Score.

## Three User Roles

| Role | Purpose |
|------|---------|
| General User | Plans and operates alternative food production |
| Buyer | Business buyer seeking compatible producers |
| Administrator | Platform and data administrator |

> **Admin accounts are NOT publicly registerable.** They are provisioned by the seed script.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5 + CSS3 + JavaScript + Glassmorphism + Bootstrap 5 |
| Backend | Python + Flask + Flask-JWT-Extended + Flask-SQLAlchemy |
| Database | MySQL (Aiven Free for cloud; local MySQL for dev) |
| ML | Scikit-learn + XGBoost + SHAP |
| OCR | Tesseract + pytesseract + OpenCV + PyMuPDF |
| Weather | Open-Meteo (free, non-commercial) |
| Geocoding | OSM Nominatim (policy-compliant) |
| Charts | Chart.js |
| Maps | Leaflet |

## Quick Start (Development)

### Prerequisites
- Python 3.11+
- MySQL 8.0+ (local) or Aiven Free MySQL (cloud)
- Tesseract OCR (for lab report analysis)
- Git

### 1. Clone the repository
```bash
git clone https://github.com/your-org/agrismart-ai.git
cd agrismart-ai
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your database credentials and secret keys
```

### 4. Create MySQL database
```sql
CREATE DATABASE agri_smart_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'agrismart'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON agri_smart_ai.* TO 'agrismart'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Initialize database and seed data
```bash
python -m flask --app "app:create_app()" db upgrade
python seed.py
```

### 6. Run the development server
```bash
python run.py
```

Backend runs at: `http://localhost:5000`  
Health check: `http://localhost:5000/api/health`

### 7. Open the frontend
Open `frontend/index.html` in your browser or serve with:
```bash
# Using Python's built-in server from the frontend directory
python -m http.server 5500
```

## Production Deployment

| Component | Platform |
|-----------|---------|
| Backend | Render Free Web Service |
| Database | Aiven Free MySQL |
| Frontend | Cloudflare Pages or Render Static Site |
| CI/CD | GitHub Actions |

Production start command:
```bash
gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app()"
```

See [docs/deployment.md](docs/deployment.md) for full deployment instructions.

## Project Structure

```
agrismart-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py            # Environment configuration
│   │   ├── extensions.py        # Flask extensions (db, jwt, etc.)
│   │   ├── routes/              # API blueprints
│   │   ├── models/              # SQLAlchemy models
│   │   ├── services/            # Business logic services
│   │   ├── ml/                  # ML pipeline
│   │   └── utils/               # Security, validators, logging
│   ├── tests/                   # Test suite
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
│
├── frontend/
│   ├── css/                     # Glassmorphism design system
│   ├── js/                      # JavaScript modules
│   ├── pages/                   # HTML pages
│   └── assets/
│
├── docs/                        # Documentation
│   ├── PROJECT_MASTER_PLAN.md
│   ├── REQUIREMENT_TRACEABILITY.md
│   ├── DEVELOPMENT_PROGRESS.md
│   └── ...
│
└── .github/workflows/           # CI/CD
```

## API Documentation

Base URL: `https://your-backend.onrender.com`

All protected endpoints require: `Authorization: Bearer <access_token>`

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | /api/health | Health check (public) |
| POST | /api/auth/register | Register user/buyer |
| POST | /api/auth/login | Login |
| GET | /api/auth/me | Current user info |
| POST | /api/recommendations | Run AI recommendation |
| GET | /api/weather | Get weather for location |

See [docs/api.md](docs/api.md) for complete API documentation.

## Important Disclaimers

- All yield, profit, ROI, and market price values are **estimates** for decision support only
- The platform does **not** certify regulatory compliance
- Weather data is retrieved from Open-Meteo (attribution required)
- Market prices are **observations** sourced from admin-verified data, not live market feeds
- Laboratory information reflects admin-maintained records; availability and capability should be verified directly

## Development Phases

| Phase | Status | Description |
|-------|--------|-------------|
| 0 | ✅ Complete | Requirements & Architecture |
| 1 | 🔄 In Progress | Project Setup |
| 2 | ⏳ Pending | Database & RBAC |
| 3 | ⏳ Pending | Authentication |
| 4–14 | ⏳ Pending | See DEVELOPMENT_PROGRESS.md |

## License

Academic capstone project. See licence file for details.

---

*Primary requirements source: AgriSmart_AI_CRS_SRS_v3_Free_Resources_Implementation_Guide.docx v3.0*
