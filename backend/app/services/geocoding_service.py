"""
AgriSmart AI — Geocoding Service (OSM Nominatim)
=================================================
Resolves location strings to latitude/longitude and address components.
"""

import time
import requests
from flask import current_app

_last_request_time = 0.0


def geocode_location(query: str) -> dict:
    global _last_request_time

    if not query or not query.strip():
        raise ValueError("Location query cannot be empty")

    query = query.strip()

    # Enforce a minimum one-second interval between requests
    now = time.time()
    elapsed = now - _last_request_time

    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)

    base_url = current_app.config.get(
        "GEOCODING_API_BASE_URL",
        "https://nominatim.openstreetmap.org"
    )

    user_agent = current_app.config.get(
        "GEOCODING_USER_AGENT",
        "AgriSmartAI/1.0 (contact: sampath.grc4558@gmail.com)"
    )

    headers = {
    "User-Agent": current_app.config["GEOCODING_USER_AGENT"],
    "Accept": "application/json",
    }

    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": 5,
    }

    try:
        _last_request_time = time.time()
        current_app.logger.info(
     "Geocoding request User-Agent: %s",
        headers.get("User-Agent")
        )

        response = requests.get(
            f"{base_url.rstrip('/')}/search",
            params=params,
            headers=headers,
            timeout=10
        )

        current_app.logger.info(
            "Nominatim response status: %s",
            response.status_code
        )

        if response.status_code != 200:
            current_app.logger.error(
                "Nominatim response body: %s",
                response.text[:500]
            )

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as e:
        current_app.logger.exception(
            "Nominatim geocoding failed for query: %s",
            query
        )
        raise RuntimeError(
            "Geocoding service unavailable"
        ) from e

    if not data:
        return {
            "found": False,
            "query": query,
            "message": (
                "Location not found. Please try a more specific "
                "city or region name."
            )
        }

    top_result = data[0]
    address = top_result.get("address", {})

    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or ""
    )

    state = address.get("state") or address.get("region") or ""
    country = address.get("country") or ""

    return {
        "found": True,
        "query": query,
        "display_name": top_result.get("display_name"),
        "latitude": float(top_result["lat"]),
        "longitude": float(top_result["lon"]),
        "country": country,
        "state": state,
        "city": city,
        "source": "OSM Nominatim",
        "attribution": "© OpenStreetMap contributors (ODbL license)",
    }