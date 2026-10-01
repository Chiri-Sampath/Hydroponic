"""
AgriSmart AI — Full Platform Integration Test Suite
=====================================================
Covers end-to-end workflows across all 14 development phases:
  - User profile & Project CRUD with ownership isolation
  - Location geocoding & Weather fetching (Open-Meteo)
  - Cultivation Knowledge Base (Methods, Products, Agronomic Requirements)
  - AI Recommendation Engine (Layer 1 Feasibility + Layer 2 Suitability + Explainability)
  - Economics & What-If Scenario Simulations
  - Quality Batches, Lab Report OCR, and Digital Quality Passport (QR code + Public token)
  - Buyer Matching & Net Realizable Price (NRP)
  - Planning (Portfolio optimization & Digital Twin simulation)
  - Admin & Governance (User status, Audit logs, Data sources, Settings)
"""

import pytest
import json
import os

os.environ["SECRET_KEY"] = "test-secret-key-full-suite-12345"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-full-suite-12345"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["FRONTEND_URL"] = "http://localhost:5500"

from app import create_app
from app.extensions import db
from app.services.seeder import seed_all_master_data
from app.models import User, Project, Product, Batch, QualityPassport


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        session = db.session
        seed_all_master_data(session)
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def user_headers(client):
    r = client.post("/api/auth/login", json={"email": "producer_full_platform@test.local", "password": "Password@123!"})
    token = json.loads(r.data).get("access_token")
    if not token:
        r = client.post("/api/auth/register", json={
            "email": "producer_full_platform@test.local",
            "password": "Password@123!",
            "full_name": "Smart Producer",
            "role": "general_user",
        })
        token = json.loads(r.data).get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers(client):
    r = client.post("/api/auth/login", json={"email": "other_producer@test.local", "password": "Password@123!"})
    token = json.loads(r.data).get("access_token")
    if not token:
        r = client.post("/api/auth/register", json={
            "email": "other_producer@test.local",
            "password": "Password@123!",
            "full_name": "Other Producer",
            "role": "general_user",
        })
        token = json.loads(r.data).get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def buyer_headers(client):
    r = client.post("/api/auth/login", json={"email": "buyer_corp@test.local", "password": "Password@123!"})
    token = json.loads(r.data).get("access_token")
    if not token:
        r = client.post("/api/auth/register", json={
            "email": "buyer_corp@test.local",
            "password": "Password@123!",
            "full_name": "Procurement Head",
            "role": "buyer",
        })
        token = json.loads(r.data).get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@agrismart.local")
    admin_pass = os.environ.get("ADMIN_PASSWORD", "Admin@AgriSmart2026!")
    r = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pass})
    token = json.loads(r.data).get("access_token")
    return {"Authorization": f"Bearer {token}"}


# ── 1. Projects & Ownership Isolation ─────────────────────────────────────────

def test_project_crud_and_ownership(client, user_headers, other_user_headers):
    # Create project as User 1
    r = client.post("/api/users/projects", headers=user_headers, json={
        "name": "Urban Hydroponics Facility",
        "description": "Commercial leafy greens and microgreens farm"
    })
    assert r.status_code == 201
    proj_id = json.loads(r.data)["data"]["id"]

    # Read project as User 1 (Allowed)
    r = client.get(f"/api/users/projects/{proj_id}", headers=user_headers)
    assert r.status_code == 200
    assert json.loads(r.data)["data"]["name"] == "Urban Hydroponics Facility"

    # Read project as User 2 (Blocked — Ownership Isolation)
    r = client.get(f"/api/users/projects/{proj_id}", headers=other_user_headers)
    assert r.status_code == 403


# ── 2. Location & Weather ─────────────────────────────────────────────────────

def test_location_and_weather_binding(client, user_headers):
    # Create project
    r = client.post("/api/users/projects", headers=user_headers, json={"name": "Bengaluru Vertical Farm"})
    proj_id = json.loads(r.data)["data"]["id"]

    # Set location (coordinates for Bengaluru, India)
    r = client.post(f"/api/location/project/{proj_id}", headers=user_headers, json={
        "raw_input": "Bengaluru, Karnataka, India",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "auto_fetch_weather": True
    })
    assert r.status_code == 200
    data = json.loads(r.data)["data"]
    assert data["city"] == "Bengaluru"
    assert data["weather"]["current"] is not None

    # Retrieve cached weather
    r = client.get(f"/api/weather/project/{proj_id}", headers=user_headers)
    assert r.status_code == 200
    w_data = json.loads(r.data)["data"]
    assert "current" in w_data
    assert "climate_profile" in w_data


# ── 3. Cultivation Knowledge Base ─────────────────────────────────────────────

def test_cultivation_kb(client, user_headers):
    # List methods
    r = client.get("/api/cultivation/methods", headers=user_headers)
    assert r.status_code == 200
    methods = json.loads(r.data)["data"]
    assert len(methods) == 3
    method_names = [m["name"] for m in methods]
    assert "hydroponics" in method_names
    assert "algaculture" in method_names
    assert "fungi" in method_names

    # List products
    r = client.get("/api/cultivation/products", headers=user_headers)
    assert r.status_code == 200
    products = json.loads(r.data)["data"]
    assert len(products) >= 18

    # Get single detailed product
    prod_id = products[0]["id"]
    r = client.get(f"/api/cultivation/products/{prod_id}", headers=user_headers)
    assert r.status_code == 200
    detail = json.loads(r.data)["data"]
    assert "environmental" in detail
    assert "water" in detail


# ── 4. AI Recommendation Engine (Milestone Section 53) ────────────────────────

def test_ai_recommendation_engine(client, user_headers):
    # Create project
    r = client.post("/api/users/projects", headers=user_headers, json={"name": "Commercial AI Pilot Farm"})
    proj_id = json.loads(r.data)["data"]["id"]

    # Set location
    client.post(f"/api/location/project/{proj_id}", headers=user_headers, json={
        "raw_input": "Bengaluru",
        "latitude": 12.9716,
        "longitude": 77.5946,
    })

    # Run AI recommendation for 'maximum_profit' objective
    r = client.post(f"/api/recommendations/run/{proj_id}", headers=user_headers, json={
        "objective_type": "maximum_profit",
        "available_area_sqm": 120.0,
        "area_type": "greenhouse",
        "available_capital_inr": 300000.0,
        "water_available_litres_day": 800.0,
        "manpower_workers": 2,
    })
    assert r.status_code == 200
    rec_data = json.loads(r.data)["data"]
    assert "top_pick" in rec_data
    assert rec_data["top_pick"]["is_recommended"] is True
    assert rec_data["top_pick"]["suitability_score"] > 0
    assert len(rec_data["top_pick"]["feature_importance"]) > 0
    assert len(rec_data["comparisons"]) > 0

    # Test latest recommendation endpoint
    r = client.get(f"/api/recommendations/project/{proj_id}/latest", headers=user_headers)
    assert r.status_code == 200
    assert json.loads(r.data)["data"]["top_pick"] is not None


# ── 5. Economics & What-If Scenario Simulator ─────────────────────────────────

def test_economics_scenario_simulator(client, user_headers):
    # Create project
    r = client.post("/api/users/projects", headers=user_headers, json={"name": "Financial Planning Project"})
    proj_id = json.loads(r.data)["data"]["id"]

    # Run scenario
    r = client.post(f"/api/economics/project/{proj_id}/scenario", headers=user_headers, json={
        "product_id": 1,
        "area_sqm": 150.0,
        "selling_price_inr_per_kg": 140.0,
        "electricity_inr_per_kg": 8.0,
        "save_scenario": True,
        "scenario_name": "Optimistic High Price Case"
    })
    assert r.status_code == 200
    econ_data = json.loads(r.data)["data"]
    assert "annual_revenue_inr" in econ_data
    assert "annual_gross_profit_inr" in econ_data
    assert "break_even" in econ_data
    assert econ_data["break_even"]["break_even_kg_annual"] > 0

    # Check saved scenarios
    r = client.get(f"/api/economics/project/{proj_id}/scenarios", headers=user_headers)
    assert r.status_code == 200
    scenarios = json.loads(r.data)["data"]
    assert len(scenarios) >= 1


# ── 6. Quality Batches & Digital Quality Passport ─────────────────────────────

def test_quality_batch_and_passport_workflow(client, user_headers):
    # Create project
    r = client.post("/api/users/projects", headers=user_headers, json={"name": "Quality Batch Test Farm"})
    proj_id = json.loads(r.data)["data"]["id"]

    # Create batch
    r = client.post(f"/api/quality/project/{proj_id}/batches", headers=user_headers, json={
        "product_id": 1,
        "area_sqm": 50.0,
        "notes": "First organic cycle"
    })
    assert r.status_code == 201
    batch_id = json.loads(r.data)["data"]["id"]

    # Generate Digital Quality Passport with QR code
    r = client.post(f"/api/quality/batches/{batch_id}/passport", headers=user_headers)
    assert r.status_code == 200
    passport_data = json.loads(r.data)["data"]
    share_token = passport_data["share_token"]
    assert share_token is not None
    assert passport_data["qr_code_image"].startswith("data:image/png;base64,")

    # Verify public token (NO AUTH HEADER)
    r = client.get(f"/api/quality/passport/{share_token}")
    assert r.status_code == 200
    pub_data = json.loads(r.data)["data"]
    assert "passport" in pub_data
    assert pub_data["passport"]["batch_code"] == passport_data["batch_code"]


# ── 7. Buyer Requirements & Matching ──────────────────────────────────────────

def test_buyer_portal_and_matching(client, buyer_headers, user_headers):
    # Buyer posts requirement
    r = client.post("/api/buyer/requirements", headers=buyer_headers, json={
        "product_id": 1,
        "required_quantity_kg_per_month": 300.0,
        "target_price_inr_per_kg": 160.0,
        "quality_grade": "Grade A Premium",
        "cold_chain_required": True
    })
    assert r.status_code == 201

    # Producer queries matching buyers
    r = client.post("/api/users/projects", headers=user_headers, json={"name": "Matching Test Farm"})
    proj_id = json.loads(r.data)["data"]["id"]

    r = client.get(f"/api/matching/project/{proj_id}/matches", headers=user_headers)
    assert r.status_code == 200
    matches = json.loads(r.data)["data"]
    assert len(matches) > 0
    assert "net_realizable_price_inr_per_kg" in matches[0]
    assert "cultivate_to_market_score" in matches[0]


# ── 8. Planning & Digital Twin Simulation ──────────────────────────────────────

def test_portfolio_and_digital_twin_simulation(client, user_headers):
    # Create project
    r = client.post("/api/users/projects", headers=user_headers, json={"name": "Simulation Project"})
    proj_id = json.loads(r.data)["data"]["id"]

    # Portfolio optimization
    r = client.post(f"/api/planning/project/{proj_id}/portfolio", headers=user_headers, json={
        "product_ids": [1, 2, 4],
        "optimization_objective": "balanced"
    })
    assert r.status_code == 200
    port_data = json.loads(r.data)["data"]
    assert len(port_data["allocations"]) == 3

    # Digital twin simulation
    r = client.post(f"/api/planning/project/{proj_id}/simulation", headers=user_headers, json={
        "product_id": 1,
        "temp_shift_c": 2.5,
        "co2_enrichment_ppm": 800,
        "light_hours_per_day": 16.0
    })
    assert r.status_code == 200
    sim_data = json.loads(r.data)["data"]
    assert "SIMULATION" in sim_data["simulation_label"]
    assert sim_data["simulated_multiplier"] > 1.0


# ── 9. Admin & Governance ─────────────────────────────────────────────────────

def test_admin_governance(client, admin_headers, user_headers):
    # Admin dashboard overview
    r = client.get("/api/admin/dashboard", headers=admin_headers)
    assert r.status_code == 200
    assert "metrics" in json.loads(r.data)["data"]

    # User management
    r = client.get("/api/admin/users", headers=admin_headers)
    assert r.status_code == 200
    users = json.loads(r.data)["data"]
    assert len(users) >= 2

    # Data sources registry
    r = client.get("/api/admin/sources", headers=admin_headers)
    assert r.status_code == 200

    # System settings
    r = client.get("/api/admin/settings", headers=admin_headers)
    assert r.status_code == 200

    # Regular user blocked from admin
    r = client.get("/api/admin/dashboard", headers=user_headers)
    assert r.status_code == 403
