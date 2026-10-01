"""
AgriSmart AI — Health Check Route
===================================
Returns API health status and database connectivity.
Public endpoint — no authentication required.
"""

from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/health
    ---------------
    Returns service health, database status, and version.
    Used by deployment pipeline, uptime monitors, and load balancer probes.
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
            "build": "2026.10.02-v4-ssl465",
            "database": db_status,
            "products_count": products_count,
        }
    ), 200


@health_bp.route("/init", methods=["GET", "POST"])
def init_database():
    """
    GET/POST /api/init
    ------------------
    Explicit endpoint to initialize all tables and seed master data on demand.
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
            "build": "2026.10.02-v4-ssl465",
            "message": "Database initialized and master data seeded successfully",
            "products_count": count
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "build": "2026.10.02-v4-ssl465",
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

