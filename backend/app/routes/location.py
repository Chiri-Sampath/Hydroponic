"""
AgriSmart AI — Location Routes
================================
Provides geocoding query endpoint and handles binding locations to projects.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db
from ..models.project import Project, Location
from ..services.geocoding_service import geocode_location
from ..services.weather_service import fetch_weather
from ..utils.auth_decorators import require_active_user, require_ownership

location_bp = Blueprint("location", __name__)


class GeocodeQuerySchema(Schema):
    q = fields.Str(required=True, validate=validate.Length(min=2, max=300))


class SetLocationSchema(Schema):
    raw_input = fields.Str(required=True, validate=validate.Length(min=2, max=500))
    latitude = fields.Float(load_default=None)
    longitude = fields.Float(load_default=None)
    display_name = fields.Str(load_default=None)
    country = fields.Str(load_default=None)
    state = fields.Str(load_default=None)
    city = fields.Str(load_default=None)
    auto_fetch_weather = fields.Boolean(load_default=True)


@location_bp.route("/geocode", methods=["GET"])
def geocode():
    """
    GET /api/location/geocode?q=Bengaluru
    ------------------------------------
    Lookup coordinates and address breakdown for a location string.
    Rate limited to 1 request per second.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"success": False, "error": "Query parameter 'q' is required"}), 400

    try:
        result = geocode_location(query)
        return jsonify({
            "success": True,
            "data": result,
            "meta": {
                "source": result.get("source"),
                "attribution": result.get("attribution"),
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@location_bp.route("/project/<int:project_id>", methods=["POST"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def set_project_location(project_id: int):
    """
    POST /api/location/project/<id>
    -------------------------------
    Resolve and bind a location to a project.
    Automatically fetches and caches weather for the project coordinates.
    """
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    schema = SetLocationSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    raw_input = data["raw_input"].strip()
    lat = data.get("latitude")
    lon = data.get("longitude")
    display_name = data.get("display_name")
    country = data.get("country")
    state = data.get("state")
    city = data.get("city")

    # If lat/lon not supplied directly, geocode the raw_input
    if lat is None or lon is None:
        geo = geocode_location(raw_input)
        if not geo.get("found"):
            return jsonify({
                "success": False,
                "error": f"Could not find coordinates for '{raw_input}'. Please enter a more specific location."
            }), 400
        lat = geo["latitude"]
        lon = geo["longitude"]
        display_name = geo["display_name"]
        country = geo["country"]
        state = geo["state"]
        city = geo["city"]

    # Update or create location record
    loc = project.location
    if not loc:
        loc = Location(project_id=project.id)
        db.session.add(loc)

    loc.raw_input = raw_input
    loc.display_name = display_name
    loc.latitude = lat
    loc.longitude = lon
    loc.country = country
    loc.state = state
    loc.city = city
    loc.geocoding_source = "OSM Nominatim"
    loc.geocoded_at = datetime.now(timezone.utc)

    # Auto-fetch weather
    if data.get("auto_fetch_weather", True) and lat is not None and lon is not None:
        weather_data = fetch_weather(lat, lon)
        loc.current_weather = weather_data.get("current")
        loc.forecast = weather_data.get("forecast_7day")
        loc.historical_climate = weather_data.get("climate_profile")
        loc.weather_source = weather_data.get("source", "Open-Meteo")
        loc.weather_retrieved_at = datetime.now(timezone.utc)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Project location and weather updated",
        "data": {
            "project_id": project.id,
            "raw_input": loc.raw_input,
            "display_name": loc.display_name,
            "latitude": float(loc.latitude),
            "longitude": float(loc.longitude),
            "country": loc.country,
            "state": loc.state,
            "city": loc.city,
            "weather": {
                "current": loc.current_weather,
                "forecast": loc.forecast,
                "climate_profile": loc.historical_climate,
                "source": loc.weather_source,
                "retrieved_at": loc.weather_retrieved_at.isoformat() if loc.weather_retrieved_at else None,
            }
        },
        "meta": {
            "geocoding_attribution": "© OpenStreetMap contributors (ODbL)",
            "weather_attribution": "Weather data by Open-Meteo.com (CC BY 4.0)",
        }
    }), 200
