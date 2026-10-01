"""
AgriSmart AI — Health Check Route
===================================
Returns API health status, database connectivity, and email diagnostics.
Public endpoints — no authentication required.
"""

from flask import Blueprint, jsonify, current_app, request

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/health
    ---------------
    Returns service health, database status, and version.
    """
    db_status = "connected"
    products_count = 0
    try:
        from ..models.cultivation import Product
        products_count = Product.query.count()
    except Exception as e:
        db_status = f"error: {e}"

    return jsonify(
        {
            "status": "ok",
            "service": current_app.config.get("APP_NAME", "AgriSmart AI"),
            "version": current_app.config.get("APP_VERSION", "1.0.0"),
            "build": "2026.10.02-v6-verified",
            "database": db_status,
            "products_count": products_count,
        }
    ), 200


@health_bp.route("/init", methods=["GET", "POST"])
def init_database():
    """
    GET/POST /api/init
    ------------------
    Initialize all tables and seed master data on demand.
    """
    try:
        from ..extensions import db
        from .. import models
        db.create_all()
        from ..services.seeder import seed_all_master_data
        seed_all_master_data(db.session)
        from ..models.cultivation import Product
        count = Product.query.count()
        return jsonify({
            "success": True,
            "build": "2026.10.02-v6-verified",
            "message": "Database initialized and master data seeded successfully",
            "products_count": count
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "build": "2026.10.02-v6-verified",
            "error": str(e)
        }), 500


@health_bp.route("/email-status", methods=["GET"])
def email_status():
    """
    GET /api/email-status
    ---------------------
    Diagnostics: shows which HTTP email provider is active and last send attempt.
    """
    try:
        from ..services.email_service import test_smtp_connection, LAST_EMAIL_STATUS
        provider_report = test_smtp_connection()
        return jsonify({
            "provider_test": provider_report,
            "last_email_attempt": LAST_EMAIL_STATUS
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@health_bp.route("/email-test", methods=["GET", "POST"])
def email_test():
    """
    GET/POST /api/email-test?to=user@example.com
    ---------------------------------------------
    Sends a real password reset email directly to the given address.
    """
    import os
    from datetime import datetime, timezone, timedelta
    from ..extensions import db
    from ..models.user import User
    from ..routes.auth import generate_reset_token
    from ..services.email_service import send_password_reset_email, LAST_EMAIL_STATUS

    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        email = (data.get("email") or data.get("to") or "").strip().lower()
    else:
        email = (request.args.get("to") or request.args.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Provide ?to=your@email.com in query parameters or { \"email\": \"...\" } in JSON"}), 400

    user = db.session.query(User).filter_by(email=email).first()
    token = generate_reset_token()
    if user:
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db.session.commit()
        display_name = user.full_name or email
    else:
        display_name = email

    frontend_base = current_app.config.get(
        "FRONTEND_URL", "https://hydroponic-frontend-seven.vercel.app"
    ).rstrip("/")
    reset_url = f"{frontend_base}/pages/user/reset-password.html?token={token}"

    ok = send_password_reset_email(email, display_name, reset_url)

    return jsonify({
        "success": ok,
        "sent_to": email,
        "sent_from": os.environ.get("MAIL_FROM_EMAIL", "hydroponiccrop@gmail.com"),
        "reset_link": reset_url,
        "token_expires_in": "1 hour",
        "last_status": LAST_EMAIL_STATUS,
    }), 200 if ok else 500
