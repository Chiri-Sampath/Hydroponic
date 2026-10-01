# AgriSmart AI — Project Master Plan
> **Version:** 1.0 | **Date:** 2026-09-26 | **Phase:** 0 — Requirements & Architecture

---

## 1. Project Vision

**AgriSmart AI** is a complete AI-based decision-support web platform that helps individuals and small businesses determine the best food-production opportunity by analysing their location, available resources, objectives, and market conditions across three alternative cultivation ecosystems:

1. **Hydroponics** — soil-free water-based plant cultivation
2. **Algaculture / Microalgae** — photobioreactor or open-raceway cultivation
3. **Fungi / Mushroom** — substrate-based indoor cultivation

The platform guides users through a continuous, connected workflow:

```
Location → Weather → Resources → Objective → AI Recommendation
→ Cultivation Plan → Economics → Risk → Quality Testing
→ Laboratory Discovery → Lab Report Analysis → Quality Passport
→ Market Intelligence → Buyer Matching → Packaging → Logistics
→ Net Realizable Price → Break-Even → Cultivate-to-Market Score
```

**Tagline:** *"From Location to Cultivation to Market — AI-powered decision support for smarter food production."*

> **IMPORTANT:** This platform provides **estimates and decision support only**. It does not guarantee yield, profit, ROI, or market price. It does not certify regulatory compliance. All AI outputs must display assumptions, sources, and dates.

---

## 2. Complete Feature Inventory

### 2.1 Public Features
| # | Feature | Description |
|---|---------|-------------|
| F01 | Landing Page | Platform introduction, feature overview |
| F02 | Registration | General User and Buyer self-registration |
| F03 | Login | Multi-role authentication |
| F04 | Explore | Public info on Hydroponics, Algaculture, Fungi |
| F05 | Compare | Public cultivation comparison |

### 2.2 General User Features
| # | Feature | Description |
|---|---------|-------------|
| F10 | Dashboard | Summary of projects, alerts, quick actions |
| F11 | Project Management | Create, view, edit, archive projects |
| F12 | Location Input | Address/place input, auto-geocoding |
| F13 | Automatic Weather | Open-Meteo current + forecast + historical |
| F14 | Resource Profile | Area, capital, water, manpower, infrastructure |
| F15 | Objective Selection | 10 objective types + dynamic weight adjustment |
| F16 | AI Feasibility Filter | Rule-based go/no-go per cultivation type |
| F17 | AI Suitability Scoring | Weighted multi-factor score (objective-adjusted) |
| F18 | Yield Prediction | Regression model per product |
| F19 | Recommendation Output | Top options with scores, explanation |
| F20 | Why This / Not That | SHAP-based feature contributions |
| F21 | Cultivation Comparison | Side-by-side Hydroponics vs Algae vs Fungi |
| F22 | What-If Simulator | Parameter changes -> immediate recalculation |
| F23 | Portfolio Optimizer | Multi-crop allocation optimization |
| F24 | Cultivation Plan | Step-by-step growing plan per product |
| F25 | CAPEX / OPEX Economics | Infrastructure + operational cost breakdown |
| F26 | Yield & Revenue | Estimated production, revenue, profit |
| F27 | ROI Calculation | Return on investment with assumptions |
| F28 | Break-Even Analysis | Break-even point and timeline |
| F29 | Risk Analysis | Factor-based risk scoring and mitigation |
| F30 | Sustainability Score | Water, land, energy, waste efficiency |
| F31 | Resource Efficiency | Production per m2, per litre, per INR, per hour |
| F32 | Quality Test Planner | Product-specific legal + buyer + recommended tests |
| F33 | Laboratory Finder | Test-specific lab search by location and capability |
| F34 | Lab Comparison | Multi-lab comparison: capability, distance, cost |
| F35 | One-Lab Optimization | Find single lab covering all required tests |
| F36 | Lab Report Upload | PDF / image upload |
| F37 | OCR Report Analysis | Extract fields, flag low-confidence values |
| F38 | Quality Passport | Batch-linked digital quality record with QR |
| F39 | Market Intelligence | Industries, end users, sales channels |
| F40 | Market Prices | Source-labelled, date-stamped price observations |
| F41 | Buyer Matching | Compatibility score with registered buyers |
| F42 | Packaging Recommendations | Product/channel/buyer-specific packaging |
| F43 | Logistics Planner | Distance, cost, spoilage, cold-chain |
| F44 | Net Realizable Price | Price minus transport, packaging, commission, spoilage |
| F45 | Market Scenarios | Price range simulation |
| F46 | Cultivate-to-Market Score | Composite end-to-end viability score |
| F47 | Digital Twin | Simulation environment with parameter sliders |
| F48 | Failure Prediction | Data-dependent; rule baseline if insufficient data |
| F49 | Early Warning | Threshold-based alerts |
| F50 | Rotation Planner | 12-month production/rotation plan |
| F51 | Production-to-Order | Order-driven cultivation planning |
| F52 | Infrastructure Reuse | Reuse optimizer across products |
| F53 | Waste-to-Value | By-product and waste recommendations |
| F54 | AI Cultivation Assistant | Context-aware Q&A using project data |

### 2.3 Buyer Features
| # | Feature | Description |
|---|---------|-------------|
| F60 | Buyer Dashboard | Summary, matches, inquiries |
| F61 | Buyer Profile | Business info, location, categories |
| F62 | Buyer Requirements | Product, qty, grade, tests, price, logistics |
| F63 | Product Discovery | Search compatible producers/products |
| F64 | Supplier Discovery | Browse compatible producers |
| F65 | Buyer Matches | Ranked compatible producers with score |
| F66 | Quality Document Review | View shared quality passports / lab reports |
| F67 | Inquiry System | Send/track inquiries (New->Closed workflow) |
| F68 | Packaging Requirements | Specify packaging expectations |
| F69 | Logistics Requirements | Delivery, cold-chain, lead time |

### 2.4 Admin Features
| # | Feature | Description |
|---|---------|-------------|
| F80 | Admin Dashboard | Platform-wide metrics and health |
| F81 | User Management | List, verify, activate, suspend, deactivate |
| F82 | Buyer Management | Buyer accounts and verification |
| F83 | Cultivation Master Data | Products, methods, requirements |
| F84 | Nutrition Database | Human nutritional values per product |
| F85 | Economic Assumptions | Cost, yield, price assumptions per product |
| F86 | Quality Test Library | Test definitions, standards, jurisdictions |
| F87 | Laboratory Registry | Lab capability, accreditation, location |
| F88 | Market Observations | Industry mappings, price observations |
| F89 | Buyer Category Config | Category definitions and mapping |
| F90 | Packaging/Logistics Data | Master packaging and logistics options |
| F91 | Recommendation Weights | Objective-weight configuration |
| F92 | ML Model Registry | Model versions, metrics, metadata |
| F93 | Business Rules Config | System-wide business rules |
| F94 | Audit Logs | Full audit trail viewer |
| F95 | System Configuration | Global settings, feature flags |

---

## 3. User Roles

### Role 1 — General User
- Self-registers via /register
- Creates and manages projects
- Full cultivation -> market workflow access
- Can only access own projects (ownership enforced server-side)

### Role 2 — Buyer
- Self-registers via /register (role selection)
- Manages business profile and requirements
- Discovers compatible products/producers
- Sends and tracks inquiries

### Role 3 — Administrator
- **NOT publicly registerable**
- Provisioned via CLI seed or secure admin panel
- Full platform data management
- Cannot be created by General User or Buyer

> **CAUTION:** Admin accounts must be created only through the seeded provisioning script or a protected admin-creation endpoint that requires an existing admin session.

---

## 4. System Architecture

```
+-----------------------------------------------------+
|                    BROWSER CLIENT                    |
|   HTML5 + CSS3 + JavaScript + Glassmorphism UI       |
|   Bootstrap 5 . Chart.js . Leaflet . Lucide Icons    |
+----------------------+------------------------------+
                       |
                  HTTPS / JSON REST
                       |
                       v
+-----------------------------------------------------+
|                  FLASK REST API                      |
|   Flask + Flask-JWT-Extended + Flask-SQLAlchemy      |
|   Auth . RBAC . Validation . Business Services       |
|   +----------------------------------------------+  |
|   |              AI / ML LAYER                   |  |
|   |  Scikit-learn . XGBoost . SHAP               |  |
|   |  Feasibility . Suitability . Yield . Risk    |  |
|   +----------------------------------------------+  |
+------------------+----------------------------------+
                   |
             SQLAlchemy ORM
                   |
                   v
+-----------------------------------------------------+
|                 MYSQL DATABASE                       |
|  Users . Projects . Cultivation . Quality            |
|  Labs . Market . Buyers . Planning . Audit           |
+-----------------------------------------------------+

EXTERNAL SERVICES:
  User Location -> Nominatim Geocoder -> Coordinates
  Coordinates -> Open-Meteo -> Weather / Historical Climate
  Product -> Quality Engine -> Lab Finder (internal DB)
  Product -> Market Intelligence -> Buyer Matching
```

### 4.1 Request Flow
1. Frontend sends HTTPS request with JWT Bearer token
2. Flask validates JWT and extracts identity + role
3. Role authorization middleware checks permission
4. Ownership check (user can only access own resources)
5. Input validation (schema + business rules)
6. Service layer executes business logic
7. ML inference called if required
8. Database read/write via SQLAlchemy ORM
9. Audit log written for sensitive operations
10. JSON response with data, assumptions, source, retrieved_at

---

## 5. Database Architecture

### 5.1 Entity Groups

```
RBAC:               users, roles, permissions, role_permissions, audit_logs
USER/PROJECT:       user_profiles, projects, locations, resource_profiles, objectives
CULTIVATION:        cultivation_methods, products, environmental_requirements,
                    water_requirements, nutrient_requirements,
                    substrate_requirements, infrastructure
AI/ML:              recommendation_runs, recommendation_results,
                    model_versions, model_metrics, feature_importance
ECONOMICS:          cost_assumptions, yield_estimates, scenarios, break_even_runs
QUALITY:            batches, quality_tests, product_test_requirements,
                    test_results, lab_reports, quality_passports
LABORATORY:         laboratories, lab_capabilities, lab_test_mappings
MARKET:             market_observations, industries, end_users,
                    sales_channels, packaging_options, logistics_rates
BUYER:              buyer_profiles, buyer_requirements, buyer_matches, buyer_inquiries
PLANNING:           what_if_runs, portfolios, rotation_plans,
                    production_orders, digital_twin_runs
GOVERNANCE:         data_sources, data_refresh_logs, system_settings
```

### 5.2 Core Data Flow Chain
```
User -> Project -> Location -> Resources -> Objective
  -> Recommendation Run -> Recommendation Result
  -> Cultivation Plan -> Batch
  -> Quality Tests -> Lab Reports -> Quality Passport
  -> Market Intelligence -> Buyer Match -> Inquiry / Sales Plan
```

---

## 6. API Architecture

### 6.1 API Module Map

| Prefix | Module | Auth | Roles |
|--------|---------|:----:|-------|
| /api/auth/* | Authentication | Varies | All |
| /api/users/* | User profile | Yes | General User |
| /api/projects/* | Project CRUD | Yes | General User |
| /api/location/* | Geocoding | Yes | General User |
| /api/weather/* | Weather data | Yes | General User |
| /api/cultivation/* | Product/method data | Yes | All |
| /api/recommendations/* | AI engine | Yes | General User |
| /api/economics/* | Economics calc | Yes | General User |
| /api/quality/* | Quality tests + passports | Yes | General User |
| /api/labs/* | Laboratory finder | Yes | General User |
| /api/market/* | Market intelligence | Yes | General User, Buyer |
| /api/buyer/* | Buyer features | Yes | Buyer |
| /api/matching/* | Matching engine | Yes | General User, Buyer |
| /api/planning/* | Advanced planning | Yes | General User |
| /api/digital-twin/* | Digital twin sim | Yes | General User |
| /api/admin/* | Admin management | Yes | Admin only |
| /api/health | Health check | No | Public |

### 6.2 Standard Response Envelope
```json
{
  "success": true,
  "data": {},
  "meta": {
    "source": "Open-Meteo v1",
    "retrieved_at": "2026-09-26T06:22:01Z",
    "assumptions": [],
    "warnings": []
  },
  "error": null
}
```

---

## 7. AI / ML Architecture

### 7.1 Two-Layer Recommendation Engine

**Layer 1 — Rule-Based Feasibility**
- Hard constraints: temperature range, water availability, minimum area, minimum capital
- Binary pass/fail per cultivation option
- Transparent, auditable rules stored in database

**Layer 2 — Weighted Suitability Scoring**
```
Base Score = Sum(weight_i x normalized_factor_i)

Base weights:
  Weather compatibility   : 0.20
  Water suitability       : 0.15
  Area efficiency         : 0.10
  Investment feasibility  : 0.15
  Labor suitability       : 0.10
  Yield potential         : 0.10
  Economic potential      : 0.10
  Nutritional value       : 0.05
  Risk                    : 0.05
```

**Objective-based weight adjustment:**
| Objective | Modified weights |
|-----------|-----------------|
| Minimum Water | Water 0.35 |
| Maximum Profit | Economics 0.30, Market 0.15 |
| Fastest Harvest | Production cycle 0.25 |
| Minimum Area | Area efficiency 0.30 |
| Sustainability | Water+Energy+Waste 0.40 |
| Let AI Decide | Base weights unchanged |

### 7.2 Explainability
- SHAP values for XGBoost models where applicable
- Feature contribution breakdown for rule-based scoring
- "Why This / Not That" section on every recommendation
- All explanation rendered in human-readable language

---

## 8. External Data Sources

| Source | Purpose | Constraints |
|--------|---------|------------|
| Open-Meteo | Weather, forecast, historical | Free non-commercial; attribution; rate limits |
| OSM Nominatim | Geocoding | Max 1 req/sec; no bulk; attribution |
| Admin-seeded cultivation data | Product, environment requirements | Internal, versioned |
| Admin-seeded market observations | Market prices, industry mappings | Source+date tagged |
| Admin-seeded laboratory data | Lab capability, location | Admin verified |

---

## 9. Free Resource Plan

| Layer | Tool | Cost | Limitation |
|-------|------|------|-----------|
| Backend | Python + Flask | Free | — |
| Database | MySQL + Aiven Free | Free | Single-node, limited |
| Hosting | Render Free | Free | Sleeps after inactivity |
| Frontend | Cloudflare Pages | Free | Build limits |
| Weather | Open-Meteo | Free | Non-commercial |
| Geocoding | Nominatim | Free | Strict rate limits |
| ML | Scikit-learn + XGBoost | Free | — |
| Explainability | SHAP | Free | — |
| OCR | Tesseract | Free | Local install required |
| CI/CD | GitHub Actions | Free | Monthly minutes |

---

## 10. Development Phases

| Phase | Name | Key Deliverables |
|-------|------|-----------------|
| 0 | Requirements & Architecture | Master plan, traceability, progress tracker |
| 1 | Project Setup | Repo, Flask skeleton, MySQL, .env |
| 2 | Database & RBAC | All tables, roles, permissions, seed data |
| 3 | Authentication | Register, login, JWT, dashboards |
| 4 | Glassmorphism Frontend | Design system, components, responsive |
| 5 | Location & Weather | Geocoding, Open-Meteo, caching |
| 6 | Cultivation Knowledge Base | Products, requirements, admin management |
| 7 | AI Recommendation | Feasibility, scoring, SHAP, Why This/Not That |
| 8 | Economics | CAPEX/OPEX, ROI, break-even, what-if |
| 9 | Quality & Labs | Test planner, lab finder, OCR, passports |
| 10 | Market & Buyer | Intelligence, matching, packaging, logistics |
| 11 | Advanced Modules | Digital twin, rotation, production-to-order |
| 12 | QA & Security | Full test suite, security audit |
| 13 | Deployment | Render/Cloudflare, CI/CD, HTTPS |
| 14 | Final Handover | All documentation, manuals, model cards |

---

## 11. Testing Strategy

| Layer | Test Type |
|-------|-----------|
| Models/services | Unit tests |
| API endpoints | Integration tests |
| RBAC | Security / boundary tests |
| Weather | External API mock |
| AI engine | ML unit tests |
| Economics | Calculation accuracy |
| Quality | Workflow tests |
| Buyer | Matching and inquiry |
| Security | Auth bypass, injection, file upload |
| Deployment | Smoke tests |

---

## 12. Deployment Strategy

```
GitHub -> GitHub Actions CI/CD
  -> Lint -> Unit tests -> API tests -> ML smoke -> Build
  -> Backend: Render Free Web Service
       gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app()"
  -> Database: Aiven Free MySQL
  -> Frontend: Cloudflare Pages / Render Static Site
```

---

## 13. Security Strategy

| Concern | Mitigation |
|---------|-----------|
| Passwords | Bcrypt hashing (never plain-text) |
| JWT | Signed secret; access + refresh tokens; expiry |
| RBAC | Server-side role check on every protected endpoint |
| Ownership | User can only read/write own projects |
| SQL injection | SQLAlchemy ORM parameterized queries |
| File uploads | Type whitelist, size limit, safe storage |
| Secrets | .env only; .gitignore enforced |
| Rate limiting | Flask-Limiter on auth and external API endpoints |
| HTTPS | Enforced at reverse-proxy level in production |
| Audit logs | Login, logout, admin actions, data changes |

---

## 14. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Open-Meteo rate limit | Low | Medium | Cache responses |
| Nominatim policy violation | Medium | High | Cache; strict rate limits |
| Aiven Free MySQL limits | Medium | Medium | Connection pooling |
| Render service sleeps | High | Low | Accept for academic prototype |
| OCR accuracy | High | Medium | Low-confidence flagging |
| Insufficient ML training data | High | Medium | Rule-based baseline |
| Scope creep (54+ features) | High | High | Phase-by-phase development |

---

## 15. Definition of Done

A phase is **Done** when:
1. Database + API + Frontend implemented for all phase features
2. Server-side authorization enforced on all protected endpoints
3. Tests written and passing
4. Error handling with fallbacks for external APIs
5. Source/timestamp metadata present where required
6. Documentation updated
7. Requirement traceability updated
8. Phase status report written

---

*Primary requirements source: AgriSmart_AI_CRS_SRS_v3_Free_Resources_Implementation_Guide.docx v3.0*
