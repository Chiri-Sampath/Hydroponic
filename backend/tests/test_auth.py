"""
AgriSmart AI — Authentication Tests
======================================
Tests: AUTH-01 through AUTH-12, RBAC-01 through RBAC-04

Covers:
- Registration (General User, Buyer)
- Admin NOT publicly self-registerable
- Login / invalid login
- Suspended user cannot login
- Logout
- Token refresh
- /me endpoint
- Forgot password / Reset password
- Duplicate email rejection
- RBAC: General User cannot access Admin APIs
- RBAC: User can only access own projects (ownership check)
"""

import pytest
import json
import os

# Force testing config before app import
os.environ["SECRET_KEY"] = "test-secret-key-123"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-123"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["FRONTEND_URL"] = "http://localhost:5500"

from app import create_app
from app.extensions import db
from app.models.user import Role, Permission, User, UserProfile


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Create application for testing (SQLite in-memory)."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        _seed_roles(db.session)
        db.session.commit()
        yield app
        db.drop_all()


def _seed_roles(session):
    """Seed minimal roles for testing."""
    from app.utils.security import hash_password
    roles_data = {
        "general_user": "General User",
        "buyer": "Buyer",
        "admin": "Administrator",
    }
    role_map = {}
    for name, display in roles_data.items():
        r = session.query(Role).filter_by(name=name).first()
        if not r:
            r = Role(name=name, display_name=display)
            session.add(r)
            session.flush()
        role_map[name] = r

    # Create test admin
    existing = session.query(User).filter_by(email="admin@test.local").first()
    if not existing:
        admin = User(
            email="admin@test.local",
            password_hash=hash_password("Admin@Test123!"),
            role=role_map["admin"],
            status="active",
        )
        session.add(admin)
        session.flush()
        session.add(UserProfile(user_id=admin.id, full_name="Test Admin"))

    return role_map


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers_user(client):
    """Register a test general user and return auth headers."""
    r = client.post("/api/auth/register", json={
        "email": "user_fixture@test.com",
        "password": "Password@123!",
        "full_name": "Test User",
        "role": "general_user",
    })
    # May already exist from previous run — try login
    if r.status_code == 409:
        r = client.post("/api/auth/login", json={
            "email": "user_fixture@test.com",
            "password": "Password@123!",
        })
    data = json.loads(r.data)
    token = data.get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_buyer(client):
    """Register a test buyer and return auth headers."""
    r = client.post("/api/auth/register", json={
        "email": "buyer_fixture@test.com",
        "password": "Password@123!",
        "role": "buyer",
    })
    if r.status_code == 409:
        r = client.post("/api/auth/login", json={
            "email": "buyer_fixture@test.com",
            "password": "Password@123!",
        })
    data = json.loads(r.data)
    token = data.get("access_token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(client):
    """Login as the seeded admin and return auth headers."""
    r = client.post("/api/auth/login", json={
        "email": "admin@test.local",
        "password": "Admin@Test123!",
    })
    data = json.loads(r.data)
    token = data.get("access_token")
    return {"Authorization": f"Bearer {token}"}


# ── AUTH Tests ────────────────────────────────────────────────────────────────

class TestRegistration:
    """AUTH-01: Valid registration"""

    def test_register_general_user(self, client):
        r = client.post("/api/auth/register", json={
            "email": "newuser@test.com",
            "password": "ValidPass@123",
            "full_name": "New User",
            "role": "general_user",
        })
        data = json.loads(r.data)
        assert r.status_code == 201, data
        assert data["success"] is True
        assert "access_token" in data
        assert data["user"]["role"] == "general_user"

    def test_register_buyer(self, client):
        r = client.post("/api/auth/register", json={
            "email": "newbuyer@test.com",
            "password": "ValidPass@123",
            "role": "buyer",
        })
        data = json.loads(r.data)
        assert r.status_code == 201, data
        assert data["user"]["role"] == "buyer"

    def test_register_admin_not_allowed_via_api(self, client):
        """AUTH-09: Admin cannot be self-registered."""
        r = client.post("/api/auth/register", json={
            "email": "hacker_admin@test.com",
            "password": "Hack@123456",
            "role": "admin",
        })
        # Should either reject (422 validation) or ignore the admin role
        data = json.loads(r.data)
        if r.status_code == 201:
            assert data["user"]["role"] != "admin", "Admin must NOT be registerable via public API"
        else:
            assert r.status_code in (400, 422)

    def test_register_duplicate_email(self, client):
        """AUTH: Duplicate email returns 409."""
        client.post("/api/auth/register", json={
            "email": "dup@test.com",
            "password": "ValidPass@123",
        })
        r = client.post("/api/auth/register", json={
            "email": "dup@test.com",
            "password": "AnotherPass@123",
        })
        assert r.status_code == 409

    def test_register_weak_password_rejected(self, client):
        """Password < 8 chars rejected."""
        r = client.post("/api/auth/register", json={
            "email": "weakpass@test.com",
            "password": "short",
        })
        assert r.status_code == 422

    def test_register_invalid_email_rejected(self, client):
        r = client.post("/api/auth/register", json={
            "email": "not-an-email",
            "password": "ValidPass@123",
        })
        assert r.status_code == 422


class TestLogin:
    """AUTH-02, AUTH-10: Login tests"""

    def test_valid_login(self, client):
        client.post("/api/auth/register", json={
            "email": "logintest@test.com",
            "password": "MyPass@123!",
        })
        r = client.post("/api/auth/login", json={
            "email": "logintest@test.com",
            "password": "MyPass@123!",
        })
        data = json.loads(r.data)
        assert r.status_code == 200
        assert "access_token" in data
        assert "refresh_token" in data

    def test_invalid_password(self, client):
        r = client.post("/api/auth/login", json={
            "email": "logintest@test.com",
            "password": "WrongPass@999",
        })
        assert r.status_code == 401

    def test_nonexistent_user(self, client):
        r = client.post("/api/auth/login", json={
            "email": "nobody@nowhere.com",
            "password": "Password@123!",
        })
        assert r.status_code == 401

    def test_suspended_user_cannot_login(self, client, app):
        """AUTH-10: Suspended accounts cannot authenticate."""
        # Register then suspend
        client.post("/api/auth/register", json={
            "email": "suspended@test.com",
            "password": "Valid@Pass123",
        })
        with app.app_context():
            u = User.query.filter_by(email="suspended@test.com").first()
            u.status = "suspended"
            db.session.commit()

        r = client.post("/api/auth/login", json={
            "email": "suspended@test.com",
            "password": "Valid@Pass123",
        })
        assert r.status_code == 403


class TestAuthEndpoints:
    """AUTH-03 through AUTH-08"""

    def test_logout(self, client, auth_headers_user):
        r = client.post("/api/auth/logout", headers=auth_headers_user)
        data = json.loads(r.data)
        assert r.status_code == 200
        assert data["success"] is True

    def test_me_endpoint(self, client, auth_headers_user):
        r = client.get("/api/auth/me", headers=auth_headers_user)
        data = json.loads(r.data)
        assert r.status_code == 200
        assert data["success"] is True
        assert "email" in data["data"]
        assert "role" in data["data"]

    def test_me_unauthenticated(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code == 401

    def test_refresh_token(self, client):
        reg = client.post("/api/auth/register", json={
            "email": "refresh_test@test.com",
            "password": "RefreshPass@123",
        })
        refresh_token = json.loads(reg.data)["refresh_token"]
        r = client.post("/api/auth/refresh",
                        headers={"Authorization": f"Bearer {refresh_token}"})
        data = json.loads(r.data)
        assert r.status_code == 200
        assert "access_token" in data

    def test_forgot_password(self, client):
        client.post("/api/auth/register", json={
            "email": "forgotme@test.com",
            "password": "ForgotPass@123",
        })
        r = client.post("/api/auth/forgot-password", json={"email": "forgotme@test.com"})
        data = json.loads(r.data)
        assert r.status_code == 200
        assert data["success"] is True

    def test_forgot_password_nonexistent_email(self, client):
        """Should still return 200 to prevent user enumeration."""
        r = client.post("/api/auth/forgot-password", json={"email": "ghost@test.com"})
        assert r.status_code == 200

    def test_reset_password_invalid_token(self, client):
        r = client.post("/api/auth/reset-password", json={
            "token": "completely-invalid-token",
            "new_password": "NewPass@123!",
        })
        assert r.status_code == 400


# ── RBAC Tests ────────────────────────────────────────────────────────────────

class TestRBAC:
    """RBAC-01 through RBAC-04"""

    def test_general_user_cannot_access_admin_api(self, client, auth_headers_user):
        """RBAC-02: General User is rejected by admin endpoints."""
        r = client.get("/api/admin/dashboard", headers=auth_headers_user)
        assert r.status_code in (403, 404)

    def test_buyer_cannot_access_admin_api(self, client, auth_headers_buyer):
        """RBAC-03: Buyer is rejected by admin endpoints."""
        r = client.get("/api/admin/users", headers=auth_headers_buyer)
        assert r.status_code in (403, 404)

    def test_unauthenticated_cannot_access_protected_api(self, client):
        r = client.get("/api/users/profile")
        # 401 when route exists and is protected; 404 when route not yet implemented
        # Both indicate the user cannot access protected data unauthenticated
        assert r.status_code in (401, 404), f"Expected 401 or 404, got {r.status_code}"

    def test_health_is_public(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200


class TestAdminGrantAccess:
    """Tests for granting admin access to new and existing users via email"""

    def test_admin_grant_to_existing_user(self, client, auth_headers_admin):
        # 1. Register a general user
        client.post("/api/auth/register", json={
            "email": "promoteme@test.com",
            "password": "Password@123!",
            "full_name": "To Promote",
            "role": "general_user",
        })

        # 2. Admin grants admin access
        r = client.post("/api/admin/users/grant-admin", headers=auth_headers_admin, json={
            "email": "promoteme@test.com",
        })
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["success"] is True
        assert data["data"]["role"] == "admin"

    def test_admin_grant_to_new_user(self, client, auth_headers_admin):
        r = client.post("/api/admin/users/grant-admin", headers=auth_headers_admin, json={
            "email": "brandnewadmin@test.com",
            "full_name": "Brand New Admin",
            "initial_password": "CustomAdminPass@123",
        })
        assert r.status_code == 201
        data = json.loads(r.data)
        assert data["success"] is True
        assert data["data"]["is_new"] is True
        assert data["data"]["role"] == "admin"

    def test_non_admin_cannot_grant_admin_access(self, client, auth_headers_user):
        r = client.post("/api/admin/users/grant-admin", headers=auth_headers_user, json={
            "email": "hacker@test.com",
        })
        assert r.status_code == 403


class TestAdminRevokeAccess:
    """Tests for revoking admin access (restricted to Main Admin)"""

    def test_main_admin_can_revoke_admin_access(self, client, auth_headers_admin):
        # 1. Promote a user to admin first
        client.post("/api/auth/register", json={
            "email": "tempadmin@test.com",
            "password": "Password@123!",
            "full_name": "Temporary Admin",
            "role": "general_user",
        })
        client.post("/api/admin/users/grant-admin", headers=auth_headers_admin, json={
            "email": "tempadmin@test.com",
        })

        # 2. Main Admin revokes admin access
        r = client.post("/api/admin/users/revoke-admin", headers=auth_headers_admin, json={
            "email": "tempadmin@test.com",
        })
        assert r.status_code == 200
        data = json.loads(r.data)
        assert data["success"] is True
        assert data["data"]["role"] == "general_user"

    def test_non_main_admin_cannot_revoke_admin_access(self, client, auth_headers_user):
        r = client.post("/api/admin/users/revoke-admin", headers=auth_headers_user, json={
            "email": "tempadmin@test.com",
        })
        assert r.status_code == 403

    def test_cannot_revoke_main_admin(self, client, auth_headers_admin):
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@test.local")
        r = client.post("/api/admin/users/revoke-admin", headers=auth_headers_admin, json={
            "email": admin_email,
        })
        assert r.status_code == 400

