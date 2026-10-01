"""
AgriSmart AI — RBAC & Authorization Decorators
================================================
Server-side role and ownership enforcement.
Never trust frontend role claims alone.
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt

from ..extensions import db
from ..models.user import User


def roles_required(*allowed_roles):
    """
    Decorator: enforce that the JWT-authenticated user has one of the allowed roles.
    Usage:
        @roles_required("admin")
        @roles_required("general_user", "admin")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role", "")
            if user_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "error": "Forbidden",
                    "message": f"Required role(s): {', '.join(allowed_roles)}",
                }), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user() -> User:
    """Return the current authenticated user from JWT identity."""
    user_id = int(get_jwt_identity())
    return db.session.get(User, user_id)


def require_active_user(fn):
    """
    Decorator: verify JWT and ensure the user account is active.
    Suspend/deactivated users are blocked even with valid JWT.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_current_user()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        if user.status in ("suspended", "deactivated"):
            return jsonify({"success": False, "error": f"Account is {user.status}"}), 403
        return fn(*args, **kwargs)
    return wrapper


def require_ownership(model_class, id_param: str = "project_id", owner_field: str = "user_id"):
    """
    Decorator factory: verify the authenticated user owns the requested resource.
    Example:
        @require_ownership(Project, id_param="project_id")
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_id = int(get_jwt_identity())
            user_role = claims.get("role", "")

            # Admins can access any resource
            if user_role == "admin":
                return fn(*args, **kwargs)

            resource_id = kwargs.get(id_param) or request.view_args.get(id_param)
            if resource_id is None:
                return jsonify({"success": False, "error": "Resource ID not provided"}), 400

            resource = db.session.get(model_class, resource_id)
            if not resource:
                return jsonify({"success": False, "error": "Resource not found"}), 404

            if getattr(resource, owner_field) != user_id:
                return jsonify({"success": False, "error": "Access denied — you do not own this resource"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
