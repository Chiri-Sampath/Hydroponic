"""
AgriSmart AI — Weather Routes
===============================
Retrieves current conditions, forecasts, and climate profiles for projects or raw coordinates.
Always returns source attribution.
"""

from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models.project import Project, Location
from ..services.weather_service import fetch_weather
from ..utils.auth_decorators import require_active_user, require_ownership

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/project/<int:project_id>", methods=["GET"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def get_project_weather(project_id: int):
    """
    GET /api/weather/project/<id>
    -----------------------------
    Get weather data for a project. Returns cached weather if within TTL,
    otherwise refreshes from Open-Meteo automatically.
    """
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    loc = project.location
    if not loc or loc.latitude is None or loc.longitude is None:
        return jsonify({
            "success": False,
            "error": "Location has not been configured for this project yet"
        }), 400

    ttl_seconds = current_app.config.get("WEATHER_CACHE_TTL_SECONDS", 3600)
    now = datetime.now(timezone.utc)

    # Check if cache is fresh
    needs_refresh = (
        loc.current_weather is None
        or loc.weather_retrieved_at is None
        or (now - loc.weather_retrieved_at.replace(tzinfo=timezone.utc)).total_seconds() > ttl_seconds
    )

    if needs_refresh:
        weather_data = fetch_weather(float(loc.latitude), float(loc.longitude))
        loc.current_weather = weather_data.get("current")
        loc.forecast = weather_data.get("forecast_7day")
        loc.historical_climate = weather_data.get("climate_profile")
        loc.weather_source = weather_data.get("source", "Open-Meteo")
        loc.weather_retrieved_at = now
        db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "project_id": project.id,
            "location_name": loc.display_name or loc.raw_input,
            "latitude": float(loc.latitude),
            "longitude": float(loc.longitude),
            "current": loc.current_weather,
            "forecast": loc.forecast,
            "climate_profile": loc.historical_climate,
        },
        "meta": {
            "source": loc.weather_source,
            "retrieved_at": loc.weather_retrieved_at.isoformat() if loc.weather_retrieved_at else None,
            "attribution": "Weather data by Open-Meteo.com (CC BY 4.0)",
            "cache_ttl_seconds": ttl_seconds,
        }
    }), 200


@weather_bp.route("/coordinates", methods=["GET"])
def get_coordinates_weather():
    """
    GET /api/weather/coordinates?lat=12.9716&lon=77.5946
    ----------------------------------------------------
    Lookup live weather for ad-hoc latitude and longitude.
    """
    try:
        lat = float(request.args.get("lat", ""))
        lon = float(request.args.get("lon", ""))
    except ValueError:
        return jsonify({"success": False, "error": "Invalid 'lat' and 'lon' query parameters"}), 400

    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return jsonify({"success": False, "error": "Coordinates out of bounds"}), 400

    weather_data = fetch_weather(lat, lon)
    return jsonify({
        "success": True,
        "data": weather_data,
        "meta": {
            "source": weather_data.get("source"),
            "attribution": weather_data.get("attribution"),
        }
    }), 200
