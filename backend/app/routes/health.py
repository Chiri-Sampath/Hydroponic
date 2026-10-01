"""
AgriSmart AI — Health Check Route
===================================
Returns API health status. Public endpoint — no authentication required.
"""

from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/health
    ---------------
    Returns service health and version.
    Used by deployment pipeline and load balancer probes.
    """
    return jsonify(
        {
            "status": "ok",
            "service": current_app.config["APP_NAME"],
            "version": current_app.config["APP_VERSION"],
        }
    ), 200
