import requests
from flask import Blueprint, request, jsonify, current_app

geocoding_bp = Blueprint("geocoding", __name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

@geocoding_bp.route("/search", methods=["GET"])
def search_location():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "success": False,
            "error": "Location is required"
        }), 400

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 5
            },
            headers={
                "User-Agent": "AgriSmartAI/1.0 (contact: sampath.grc4558@gmail.com)"
            },
            timeout=10
        )
        if response.status_code != 200:
            current_app.logger.error(
                "Nominatim status: %s | Response: %s",
                response.status_code,
                response.text[:500]
        )

        if response.status_code != 200:
            current_app.logger.error(
                "Nominatim returned %s: %s",
                response.status_code,
                response.text[:500]
            )

        response.raise_for_status()

        return jsonify({
            "success": True,
            "results": response.json()
        }), 200

    except requests.RequestException as e:
        current_app.logger.exception("Geocoding request failed")

        return jsonify({
            "success": False,
            "error": "Geocoding service is temporarily unavailable"
        }), 502