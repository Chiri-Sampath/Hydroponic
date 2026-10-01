# AgriSmart AI — Requirement Traceability Matrix
> **Version:** 1.0 | **Date:** 2026-09-26 | **Phase:** 0

> **Definition of Complete:** A requirement is COMPLETE only when Database + API + Frontend + Validation + Authorization + Tests + Documentation are all done where applicable.

---

## Legend
- Status: `NOT_STARTED` | `IN_PROGRESS` | `COMPLETE` | `DATA_DEPENDENT`
- Phase: Phase number when this will be delivered

---

## MODULE 1: Authentication & RBAC

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| AUTH-01 | User self-registration (General/Buyer) | users, roles | POST /api/auth/register | /register | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-02 | User login with JWT | users, sessions | POST /api/auth/login | /login | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-03 | Logout + token revocation | sessions | POST /api/auth/logout | — | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-04 | Get current user info | users | GET /api/auth/me | — | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-05 | Token refresh | sessions | POST /api/auth/refresh | — | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-06 | Forgot password | users | POST /api/auth/forgot-password | /login | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-07 | Reset password | users | POST /api/auth/reset-password | /login | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-08 | Password hashing (bcrypt) | users | — | — | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-09 | Admin NOT publicly self-registerable | users, roles | POST /api/auth/register | — | auth_service | test_rbac.py | 3 | NOT_STARTED |
| AUTH-10 | Suspended users cannot login | users | POST /api/auth/login | — | auth_service | test_auth.py | 3 | NOT_STARTED |
| AUTH-11 | Rate limiting on auth endpoints | — | POST /api/auth/* | — | auth_service | test_security.py | 3 | NOT_STARTED |
| AUTH-12 | Audit log on login/logout | audit_logs | — | — | audit_service | test_auth.py | 3 | NOT_STARTED |
| RBAC-01 | Role-based dashboard redirect | users, roles | GET /api/auth/me | /dashboard | auth_service | test_rbac.py | 3 | NOT_STARTED |
| RBAC-02 | General User cannot access Admin API | role_permissions | /api/admin/* | — | middleware | test_rbac.py | 3 | NOT_STARTED |
| RBAC-03 | Buyer cannot edit cultivation master data | role_permissions | /api/admin/cultivation | — | middleware | test_rbac.py | 3 | NOT_STARTED |
| RBAC-04 | User can only access own projects | projects | /api/projects/:id | — | project_service | test_rbac.py | 3 | NOT_STARTED |

---

## MODULE 2: User Profile & Projects

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| USR-01 | Create project | projects | POST /api/projects | /projects/new | project_service | test_projects.py | 2 | NOT_STARTED |
| USR-02 | List own projects | projects | GET /api/projects | /projects | project_service | test_projects.py | 2 | NOT_STARTED |
| USR-03 | View project detail | projects | GET /api/projects/:id | /project/:id | project_service | test_projects.py | 2 | NOT_STARTED |
| USR-04 | Edit project | projects | PUT /api/projects/:id | /project/:id | project_service | test_projects.py | 2 | NOT_STARTED |
| USR-05 | Archive/delete project | projects | DELETE /api/projects/:id | /projects | project_service | test_projects.py | 2 | NOT_STARTED |
| USR-06 | User profile management | user_profiles | GET/PUT /api/users/profile | /dashboard | user_service | test_users.py | 3 | NOT_STARTED |

---

## MODULE 3: Location & Weather

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| LOC-01 | User enters location (address/place) | locations | POST /api/location/resolve | /project/:id/location | location_service | test_location.py | 5 | NOT_STARTED |
| LOC-02 | Auto-geocoding via Nominatim | locations | POST /api/location/resolve | — | location_service | test_location.py | 5 | NOT_STARTED |
| LOC-03 | Store lat/long, location name | locations | — | — | location_service | test_location.py | 5 | NOT_STARTED |
| LOC-04 | Geocoding result cached | locations | — | — | location_service | test_location.py | 5 | NOT_STARTED |
| WTH-01 | Auto-fetch current weather from coordinates | locations | GET /api/weather/:location_id | /project/:id/location | weather_service | test_weather.py | 5 | NOT_STARTED |
| WTH-02 | Fetch forecast data | locations | GET /api/weather/:location_id | — | weather_service | test_weather.py | 5 | NOT_STARTED |
| WTH-03 | Fetch historical/seasonal climate | locations | GET /api/weather/:location_id/historical | — | weather_service | test_weather.py | 5 | NOT_STARTED |
| WTH-04 | Cache weather responses (1hr TTL) | locations | — | — | weather_service | test_weather.py | 5 | NOT_STARTED |
| WTH-05 | Display retrieved_at timestamp | locations | — | /project/:id/location | weather_service | test_weather.py | 5 | NOT_STARTED |
| WTH-06 | Weather API failure fallback (show cached) | locations | — | — | weather_service | test_weather.py | 5 | NOT_STARTED |
| WTH-07 | Do NOT ask user for temperature/humidity/rain | — | — | /project/:id/resources | — | test_weather.py | 5 | NOT_STARTED |

---

## MODULE 4: Resource Profile & Objective

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| RES-01 | Enter available area (m2) | resource_profiles | POST /api/projects/:id/resources | /project/:id/resources | project_service | test_resources.py | 5 | NOT_STARTED |
| RES-02 | Select indoor/outdoor/greenhouse/rooftop | resource_profiles | — | — | project_service | test_resources.py | 5 | NOT_STARTED |
| RES-03 | Enter available capital (INR) | resource_profiles | — | — | project_service | test_resources.py | 5 | NOT_STARTED |
| RES-04 | Enter water availability (litres/day) | resource_profiles | — | — | project_service | test_resources.py | 5 | NOT_STARTED |
| RES-05 | Enter manpower (workers, hours/day) | resource_profiles | — | — | project_service | test_resources.py | 5 | NOT_STARTED |
| RES-06 | Enter existing infrastructure | resource_profiles | — | — | project_service | test_resources.py | 5 | NOT_STARTED |
| OBJ-01 | Select one of 10 objectives | objectives | POST /api/projects/:id/objective | /project/:id/objective | project_service | test_objective.py | 5 | NOT_STARTED |
| OBJ-02 | Objective adjusts recommendation weights | objectives | — | — | recommendation_service | test_recommendation.py | 7 | NOT_STARTED |

---

## MODULE 5: AI Recommendation Engine

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service/ML | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|------------|------|-------|--------|
| REC-01 | Rule-based feasibility filter | recommendation_runs | POST /api/recommendations | /project/:id/recommendation | recommendation_service | test_recommendation.py | 7 | NOT_STARTED |
| REC-02 | Weighted suitability score (all 3 methods) | recommendation_results | POST /api/recommendations | — | recommendation_service | test_recommendation.py | 7 | NOT_STARTED |
| REC-03 | Objective-based weight adjustment | recommendation_runs | — | — | recommendation_service | test_recommendation.py | 7 | NOT_STARTED |
| REC-04 | Yield prediction per product | recommendation_results | — | — | yield_service / ML | test_ml.py | 7 | NOT_STARTED |
| REC-05 | Top recommendation output with score | recommendation_results | GET /api/recommendations/:id | /project/:id/recommendation | recommendation_service | test_recommendation.py | 7 | NOT_STARTED |
| REC-06 | SHAP/feature contribution explanation | feature_importance | GET /api/recommendations/:id/explanation | /project/:id/why | explainability | test_ml.py | 7 | NOT_STARTED |
| REC-07 | Why This / Not That comparison | recommendation_results | GET /api/recommendations/:id/why | /project/:id/why | recommendation_service | test_recommendation.py | 7 | NOT_STARTED |
| REC-08 | All 3 cultivation types compared | recommendation_results | GET /api/recommendations/:id/compare | /project/:id/compare | recommendation_service | test_recommendation.py | 7 | NOT_STARTED |
| REC-09 | Recommendation shows assumptions + sources | recommendation_results | — | — | — | test_recommendation.py | 7 | NOT_STARTED |
| REC-10 | Model version recorded with run | recommendation_runs, model_versions | — | — | recommendation_service | test_ml.py | 7 | NOT_STARTED |

---

## MODULE 6: Economics

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| ECO-01 | CAPEX breakdown | cost_assumptions | GET /api/economics/:project_id | /project/:id/economics | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-02 | OPEX breakdown | cost_assumptions | — | — | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-03 | Yield estimate | yield_estimates | — | — | yield_service | test_economics.py | 8 | NOT_STARTED |
| ECO-04 | Revenue estimate | scenarios | — | — | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-05 | Profit estimate | scenarios | — | — | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-06 | ROI calculation | scenarios | GET /api/economics/:id/roi | /project/:id/economics | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-07 | Break-even analysis | break_even_runs | GET /api/economics/:id/break-even | /project/:id/break-even | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-08 | All estimates clearly labelled | — | — | — | — | test_economics.py | 8 | NOT_STARTED |
| ECO-09 | What-If simulator | what_if_runs | POST /api/planning/what-if | /project/:id/what-if | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-10 | Portfolio optimizer | portfolios | POST /api/planning/portfolio | /project/:id/portfolio | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-11 | Resource efficiency scorecards | scenarios | GET /api/economics/:id/efficiency | /project/:id/sustainability | economics_service | test_economics.py | 8 | NOT_STARTED |
| ECO-12 | Sustainability score | scenarios | GET /api/economics/:id/sustainability | /project/:id/sustainability | economics_service | test_economics.py | 8 | NOT_STARTED |

---

## MODULE 7: Quality & Laboratory

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| QLT-01 | Product-specific test plan generation | product_test_requirements, quality_tests | GET /api/quality/tests/:product_id | /quality/tests | lab_service | test_quality.py | 9 | NOT_STARTED |
| QLT-02 | Separate legal/voluntary/buyer/recommended tests | quality_tests | — | — | lab_service | test_quality.py | 9 | NOT_STARTED |
| QLT-03 | Test-specific laboratory search | laboratories, lab_test_mappings | GET /api/labs/search | /quality/labs | lab_service | test_labs.py | 9 | NOT_STARTED |
| QLT-04 | Lab search filtered by distance | laboratories | GET /api/labs/search?radius=25 | /quality/labs | lab_service | test_labs.py | 9 | NOT_STARTED |
| QLT-05 | Lab comparison (capability/cost/distance) | laboratories | GET /api/labs/compare | /quality/labs/compare | lab_service | test_labs.py | 9 | NOT_STARTED |
| QLT-06 | One-lab optimization | lab_capabilities | GET /api/labs/optimize | /quality/labs | lab_service | test_labs.py | 9 | NOT_STARTED |
| QLT-07 | Lab report upload (PDF/image) | lab_reports | POST /api/labs/reports | /quality/reports | report_service | test_quality.py | 9 | NOT_STARTED |
| QLT-08 | OCR text extraction | lab_reports | POST /api/labs/reports | — | report_service | test_quality.py | 9 | NOT_STARTED |
| QLT-09 | Low-confidence field flagging | lab_reports | — | /quality/reports | report_service | test_quality.py | 9 | NOT_STARTED |
| QLT-10 | Result vs specification comparison | test_results | GET /api/quality/results/:id | /quality/reports | lab_service | test_quality.py | 9 | NOT_STARTED |
| QLT-11 | Digital quality passport creation | quality_passports, batches | POST /api/quality/passport | /quality/passports | lab_service | test_quality.py | 9 | NOT_STARTED |
| QLT-12 | QR-compatible batch ID | batches | — | /quality/passports | lab_service | test_quality.py | 9 | NOT_STARTED |

---

## MODULE 8: Market & Buyer

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| MKT-01 | Industry mapping per product | industries | GET /api/market/industries/:product_id | /market/industries | market_service | test_market.py | 10 | NOT_STARTED |
| MKT-02 | End-user mapping per product | end_users | GET /api/market/end-users/:product_id | /market/end-users | market_service | test_market.py | 10 | NOT_STARTED |
| MKT-03 | Market price observations (source+date) | market_observations | GET /api/market/prices/:product_id | /market/prices | market_service | test_market.py | 10 | NOT_STARTED |
| MKT-04 | Sales channel comparison | sales_channels | GET /api/market/channels/:product_id | /market/sales | market_service | test_market.py | 10 | NOT_STARTED |
| MKT-05 | Net realizable price calculation | scenarios | POST /api/market/net-price | /market/sales | market_service | test_market.py | 10 | NOT_STARTED |
| MKT-06 | Market price scenarios | scenarios | POST /api/market/scenarios | /market/prices | market_service | test_market.py | 10 | NOT_STARTED |
| MKT-07 | Cultivate-to-Market Score | recommendation_results | GET /api/recommendations/:id/ctm-score | /project/:id/recommendation | market_service | test_market.py | 10 | NOT_STARTED |
| BUY-01 | Buyer registration | users, buyer_profiles | POST /api/auth/register | /register | auth_service | test_buyer.py | 3 | NOT_STARTED |
| BUY-02 | Buyer profile management | buyer_profiles | GET/PUT /api/buyer/profile | /buyer/profile | buyer_service | test_buyer.py | 10 | NOT_STARTED |
| BUY-03 | Buyer requirements entry | buyer_requirements | POST /api/buyer/requirements | /buyer/requirements | buyer_service | test_buyer.py | 10 | NOT_STARTED |
| BUY-04 | Buyer-producer matching | buyer_matches | POST /api/matching/buyers | /buyer/matches | matching_service | test_matching.py | 10 | NOT_STARTED |
| BUY-05 | Compatibility score with reasons | buyer_matches | GET /api/matching/buyers/:id | /buyer/matches | matching_service | test_matching.py | 10 | NOT_STARTED |
| BUY-06 | Inquiry send/receive | buyer_inquiries | POST /api/buyer/inquiries | /buyer/inquiries | buyer_service | test_buyer.py | 10 | NOT_STARTED |
| BUY-07 | Inquiry status tracking (6 statuses) | buyer_inquiries | GET /api/buyer/inquiries/:id | /buyer/inquiries | buyer_service | test_buyer.py | 10 | NOT_STARTED |
| BUY-08 | Quality passport review (if shared) | quality_passports | GET /api/quality/passport/:id | /buyer/quality | buyer_service | test_buyer.py | 10 | NOT_STARTED |
| PKG-01 | Packaging recommendations | packaging_options | GET /api/market/packaging/:product_id | /market/logistics | market_service | test_market.py | 10 | NOT_STARTED |
| LOG-01 | Logistics cost calculator | logistics_rates | POST /api/market/logistics | /market/logistics | market_service | test_market.py | 10 | NOT_STARTED |

---

## MODULE 9: Advanced Features

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| ADV-01 | Digital Twin simulation | digital_twin_runs | POST /api/digital-twin/simulate | /digital-twin | economics_service | test_advanced.py | 11 | NOT_STARTED |
| ADV-02 | Failure prediction (data-dependent) | digital_twin_runs | GET /api/planning/failure-risk | /digital-twin | ml_service | test_advanced.py | 11 | DATA_DEPENDENT |
| ADV-03 | Early warning alerts | digital_twin_runs | GET /api/planning/alerts | /digital-twin | ml_service | test_advanced.py | 11 | NOT_STARTED |
| ADV-04 | 12-month rotation planner | rotation_plans | POST /api/planning/rotation | /rotation | planning_service | test_advanced.py | 11 | NOT_STARTED |
| ADV-05 | Production-to-order planning | production_orders | POST /api/planning/production-orders | /production-orders | planning_service | test_advanced.py | 11 | NOT_STARTED |
| ADV-06 | Infrastructure reuse optimizer | resource_profiles | GET /api/planning/infrastructure-reuse | /planning | planning_service | test_advanced.py | 11 | NOT_STARTED |
| ADV-07 | Waste-to-value recommendations | products | GET /api/planning/waste-to-value | /planning | planning_service | test_advanced.py | 11 | NOT_STARTED |
| ADV-08 | Market saturation detection | market_observations | GET /api/market/saturation | /market | market_service | test_advanced.py | 11 | DATA_DEPENDENT |
| ADV-09 | AI Cultivation Assistant | projects (context) | POST /api/assistant/chat | /assistant | assistant_service | test_advanced.py | 11 | NOT_STARTED |

---

## MODULE 10: Admin

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| ADM-01 | Admin dashboard | all | GET /api/admin/dashboard | /admin/dashboard | admin_service | test_admin.py | 3 | NOT_STARTED |
| ADM-02 | User management (activate/suspend) | users | PATCH /api/admin/users/:id/status | /admin/users | admin_service | test_admin.py | 3 | NOT_STARTED |
| ADM-03 | Cultivation master data management | products, env_req, etc. | /api/admin/cultivation/* | /admin/cultivation | admin_service | test_admin.py | 6 | NOT_STARTED |
| ADM-04 | Quality test library management | quality_tests | /api/admin/quality/* | /admin/quality | admin_service | test_admin.py | 9 | NOT_STARTED |
| ADM-05 | Laboratory registry management | laboratories | /api/admin/laboratories/* | /admin/laboratories | admin_service | test_admin.py | 9 | NOT_STARTED |
| ADM-06 | Market observations management | market_observations | /api/admin/market/* | /admin/market | admin_service | test_admin.py | 10 | NOT_STARTED |
| ADM-07 | ML model version registry | model_versions | /api/admin/models/* | /admin/models | admin_service | test_admin.py | 7 | NOT_STARTED |
| ADM-08 | Recommendation weights config | system_settings | /api/admin/configuration | /admin/configuration | admin_service | test_admin.py | 7 | NOT_STARTED |
| ADM-09 | Audit log viewer | audit_logs | GET /api/admin/audit | /admin/audit | admin_service | test_admin.py | 3 | NOT_STARTED |
| ADM-10 | Admin audit log on all admin actions | audit_logs | — | — | audit_service | test_admin.py | 3 | NOT_STARTED |

---

## MODULE 11: Cultivation Knowledge Base

| Req ID | Requirement | DB Tables | API Endpoint | Frontend Page | Service | Test | Phase | Status |
|--------|-------------|-----------|--------------|---------------|---------|------|-------|--------|
| CUL-01 | Hydroponics product data (11 products) | products, cultivation_methods | GET /api/cultivation/products | /explore/hydroponics | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-02 | Algaculture product data (Spirulina, Chlorella) | products | GET /api/cultivation/products | /explore/algaculture | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-03 | Fungi product data (5 products) | products | GET /api/cultivation/products | /explore/fungi | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-04 | Environmental requirements per product | environmental_requirements | GET /api/cultivation/:id/environment | — | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-05 | Water requirements per product | water_requirements | GET /api/cultivation/:id/water | — | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-06 | Nutrient requirements per product | nutrient_requirements | GET /api/cultivation/:id/nutrients | — | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-07 | Substrate requirements (Fungi) | substrate_requirements | GET /api/cultivation/:id/substrate | — | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-08 | Infrastructure requirements per product | infrastructure | GET /api/cultivation/:id/infrastructure | — | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-09 | Human nutrition database | products | GET /api/cultivation/:id/nutrition | — | cultivation_service | test_cultivation.py | 6 | NOT_STARTED |
| CUL-10 | Admin can edit all cultivation master data | all cultivation tables | /api/admin/cultivation/* | /admin/cultivation | admin_service | test_admin.py | 6 | NOT_STARTED |

---

## Summary Progress Table

| Module | Total Requirements | Complete | In Progress | Not Started | Data Dependent |
|--------|--------------------|----------|-------------|-------------|----------------|
| Auth & RBAC | 16 | 0 | 0 | 16 | 0 |
| User & Projects | 6 | 0 | 0 | 6 | 0 |
| Location & Weather | 11 | 0 | 0 | 11 | 0 |
| Resources & Objective | 8 | 0 | 0 | 8 | 0 |
| AI Recommendation | 10 | 0 | 0 | 10 | 0 |
| Economics | 12 | 0 | 0 | 12 | 0 |
| Quality & Labs | 12 | 0 | 0 | 12 | 0 |
| Market & Buyer | 18 | 0 | 0 | 18 | 0 |
| Advanced Features | 9 | 0 | 0 | 7 | 2 |
| Admin | 10 | 0 | 0 | 10 | 0 |
| Cultivation KB | 10 | 0 | 0 | 10 | 0 |
| **TOTAL** | **122** | **0** | **0** | **120** | **2** |

---

*Last updated: 2026-09-26 | Phase 0 baseline created*
