"""
AgriSmart AI — Auth Routes
============================
Implements: register, login, logout, me, refresh, forgot-password, reset-password.

Security:
- Bcrypt password hashing
- JWT access + refresh tokens
- Suspended/deactivated accounts cannot create sessions
- Admin is NOT publicly registerable
- Rate limiting on login endpoint
- Audit logging on login, logout, registration
"""

from datetime import datetime, timezone, timedelta
import flask
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db, limiter
from ..models.user import User, Role, UserProfile, AuditLog
from ..utils.security import hash_password, check_password, generate_reset_token, is_valid_email

auth_bp = Blueprint("auth", __name__)


# ── Schemas ──────────────────────────────────────────────────────────────────

class RegisterSchema(Schema):
    email = fields.Email(required=True, validate=validate.Length(max=254))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))
    full_name = fields.Str(load_default=None, validate=validate.Length(max=200))
    role = fields.Str(
        load_default="general_user",
        validate=validate.OneOf(["general_user", "buyer"]),
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)


class ForgotPasswordSchema(Schema):
    email = fields.Email(required=True)


class ResetPasswordSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=128))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_audit(action: str, user_id=None, target_type=None, target_id=None, details=None):
    """Write an audit log entry."""
    try:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:500],
        )
        db.session.add(entry)
        db.session.commit()
    except Exception:
        # Audit log failure must NEVER break the main request
        db.session.rollback()


def _user_to_dict(user: User) -> dict:
    """Serialize a user for the /me response."""
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.name,
        "role_display": user.role.display_name,
        "status": user.status,
        "full_name": user.profile.full_name if user.profile else None,
        "email_verified": user.email_verified,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    """
    POST /api/auth/register
    -----------------------
    Register a new General User or Buyer.
    Admin registration is NOT permitted through this endpoint.
    """
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    email = data["email"].lower().strip()

    # Check email uniqueness
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "Email already registered"}), 409

    # Get role — admin cannot be created via public API
    role_name = data["role"]
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({"success": False, "error": "Invalid role"}), 400

    try:
        user = User(
            email=email,
            password_hash=hash_password(data["password"]),
            role=role,
            status="active",
        )
        db.session.add(user)
        db.session.flush()

        profile = UserProfile(user_id=user.id, full_name=data.get("full_name"))
        db.session.add(profile)
        db.session.commit()

        _write_audit("user.register", user_id=user.id, target_type="User", target_id=user.id,
                     details={"role": role_name, "email": email})

        # Create tokens
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": role.name, "email": email},
        )
        refresh_token = create_refresh_token(identity=str(user.id))

        return jsonify({
            "success": True,
            "message": "Registration successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": _user_to_dict(user),
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {e}")
        return jsonify({"success": False, "error": "Registration failed. Please try again."}), 500


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    """
    POST /api/auth/login
    --------------------
    Authenticate a user. Returns JWT access and refresh tokens.
    Suspended/deactivated accounts are rejected.
    """
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    email = data["email"].lower().strip()
    user = User.query.filter_by(email=email).first()

    # Deliberate generic message to avoid user enumeration
    invalid_msg = "Invalid email or password"

    if not user or not check_password(data["password"], user.password_hash):
        _write_audit("user.login.failed", details={"email": email, "reason": "invalid_credentials"})
        return jsonify({"success": False, "error": invalid_msg}), 401

    if user.status in ("suspended", "deactivated"):
        _write_audit("user.login.blocked", user_id=user.id,
                     details={"reason": user.status})
        return jsonify({
            "success": False,
            "error": f"Account is {user.status}. Contact support.",
        }), 403

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()

    _write_audit("user.login", user_id=user.id,
                 details={"email": email, "role": user.role.name})

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.name, "email": email},
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": _user_to_dict(user),
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    POST /api/auth/logout
    ----------------------
    Logs out the current user (audit logged).
    In this implementation, token expiry is the primary invalidation mechanism.
    For a blocklist, use Flask-JWT-Extended's token blocklist.
    """
    user_id = get_jwt_identity()
    _write_audit("user.logout", user_id=int(user_id))
    return jsonify({"success": True, "message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    GET /api/auth/me
    -----------------
    Returns current authenticated user's profile.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    if user.status in ("suspended", "deactivated"):
        return jsonify({"success": False, "error": "Account is not active"}), 403

    return jsonify({"success": True, "data": _user_to_dict(user)}), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    POST /api/auth/refresh
    -----------------------
    Issue a new access token using a valid refresh token.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user or user.status in ("suspended", "deactivated"):
        return jsonify({"success": False, "error": "Cannot refresh — account inactive"}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.name, "email": user.email},
    )
    return jsonify({"success": True, "access_token": access_token}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per minute")
def forgot_password():
    """
    POST /api/auth/forgot-password
    --------------------------------
    Generate a password reset token and (in production) send via email.
    For academic prototype: returns the token in the response.
    In production: send via email only — remove token from response.
    """
    schema = ForgotPasswordSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    email = data["email"].lower().strip()
    user = User.query.filter_by(email=email).first()

    # Always return success to prevent user enumeration
    if not user or user.status == "deactivated":
        return jsonify({
            "success": True,
            "message": "If the email is registered, a reset link will be sent.",
        }), 200

    token = generate_reset_token()
    user.password_reset_token = token
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.session.commit()

    _write_audit("user.forgot_password", user_id=user.id)

    response_data = {
        "success": True,
        "message": "If the email is registered, a reset link will be sent.",
    }

    # DEMO MODE: expose token in response for academic prototype only
    if current_app.config.get("FLASK_ENV") == "development":
        response_data["_demo_reset_token"] = token
        response_data["_demo_note"] = "Token shown for development only. Remove in production."

    return jsonify(response_data), 200


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("5 per minute")
def reset_password():
    """
    POST /api/auth/reset-password
    --------------------------------
    Reset password using a valid token (from forgot-password).
    Token expires in 1 hour.
    """
    schema = ResetPasswordSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    user = User.query.filter_by(password_reset_token=data["token"]).first()
    if not user:
        return jsonify({"success": False, "error": "Invalid or expired reset token"}), 400

    if not user.password_reset_expires or \
       user.password_reset_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return jsonify({"success": False, "error": "Reset token has expired"}), 400

    user.password_hash = hash_password(data["new_password"])
    user.password_reset_token = None
    user.password_reset_expires = None
    db.session.commit()

    _write_audit("user.reset_password", user_id=user.id)

    return jsonify({"success": True, "message": "Password reset successfully"}), 200
