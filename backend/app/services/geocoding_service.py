"""
AgriSmart AI — Resilient Multi-Provider Geocoding Service
=========================================================
Resolves location strings to latitude/longitude and address components.
Uses Open-Meteo Geocoding API (primary, cloud-safe, non-blocking) with
OpenStreetMap Nominatim as secondary and a built-in fallback catalog.
"""

import time
import requests
from flask import current_app

_last_request_time = 0.0

# Curated catalog of major hubs for instant offline/fallback resolution
CITY_CATALOG = {
    "bengaluru": {"name": "Bengaluru", "city": "Bengaluru", "state": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946},
    "bangalore": {"name": "Bengaluru", "city": "Bengaluru", "state": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946},
    "hyderabad": {"name": "Hyderabad", "city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.3850, "lon": 78.4867},
    "mumbai": {"name": "Mumbai", "city": "Mumbai", "state": "Maharashtra", "country": "India", "lat": 19.0760, "lon": 72.8777},
    "delhi": {"name": "New Delhi", "city": "New Delhi", "state": "Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090},
    "new delhi": {"name": "New Delhi", "city": "New Delhi", "state": "Delhi", "country": "India", "lat": 28.6139, "lon": 77.2090},
    "chennai": {"name": "Chennai", "city": "Chennai", "state": "Tamil Nadu", "country": "India", "lat": 13.0827, "lon": 80.2707},
    "pune": {"name": "Pune", "city": "Pune", "state": "Maharashtra", "country": "India", "lat": 18.5204, "lon": 73.8567},
    "kolkata": {"name": "Kolkata", "city": "Kolkata", "state": "West Bengal", "country": "India", "lat": 22.5726, "lon": 88.3639},
    "ahmedabad": {"name": "Ahmedabad", "city": "Ahmedabad", "state": "Gujarat", "country": "India", "lat": 23.0225, "lon": 72.5714},
    "jaipur": {"name": "Jaipur", "city": "Jaipur", "state": "Rajasthan", "country": "India", "lat": 26.9124, "lon": 75.7873},
    "london": {"name": "London", "city": "London", "state": "England", "country": "United Kingdom", "lat": 51.5074, "lon": -0.1278},
    "singapore": {"name": "Singapore", "city": "Singapore", "state": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198},
    "dubai": {"name": "Dubai", "city": "Dubai", "state": "Dubai", "country": "United Arab Emirates", "lat": 25.2048, "lon": 55.2708},
    "san francisco": {"name": "San Francisco", "city": "San Francisco", "state": "California", "country": "United States", "lat": 37.7749, "lon": -122.4194},
}


def geocode_location(query: str) -> dict:
    """
    Resolve location query to coordinates and metadata.
    Attempts:
      1. Open-Meteo Geocoding API (Fast, cloud-friendly, zero rate-limit blocks)
      2. OpenStreetMap Nominatim API
      3. Built-in catalog fallback
    """
    global _last_request_time

    if not query or not query.strip():
        raise ValueError("Location query cannot be empty")

    query = query.strip()
    clean_q = query.lower().strip()

    # ── 1. Try Open-Meteo Geocoding API (Primary) ─────────────────────────────
    try:
        om_url = "https://geocoding-api.open-meteo.com/v1/search"
        om_params = {
            "name": query,
            "count": 5,
            "language": "en",
            "format": "json"
        }
        res = requests.get(om_url, params=om_params, timeout=5)
        if res.status_code == 200:
            om_data = res.json()
            results = om_data.get("results", [])
            if results:
                top = results[0]
                city = top.get("name", "")
                state = top.get("admin1", "")
                country = top.get("country", "")
                display_parts = [p for p in [city, state, country] if p]
                return {
                    "found": True,
                    "query": query,
                    "display_name": ", ".join(display_parts),
                    "latitude": float(top["latitude"]),
                    "longitude": float(top["longitude"]),
                    "country": country,
                    "state": state,
                    "city": city,
                    "source": "Open-Meteo Geocoding",
                    "attribution": "© Open-Meteo & OpenStreetMap contributors",
                }
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"Open-Meteo geocoding fallback for '{query}': {e}")

    # ── 2. Try OpenStreetMap Nominatim ────────────────────────────────────────
    try:
        now = time.time()
        elapsed = now - _last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)

        base_url = current_app.config.get("GEOCODING_API_BASE_URL", "https://nominatim.openstreetmap.org") if current_app else "https://nominatim.openstreetmap.org"
        user_agent = current_app.config.get("GEOCODING_USER_AGENT", "AgriSmartAI/1.0 (contact: sampath.grc4558@gmail.com)") if current_app else "AgriSmartAI/1.0"

        headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": 5,
        }

        _last_request_time = time.time()
        res = requests.get(f"{base_url.rstrip('/')}/search", params=params, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data:
                top = data[0]
                addr = top.get("address", {})
                city = (addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality") or addr.get("county") or "")
                state = addr.get("state") or addr.get("region") or ""
                country = addr.get("country") or ""
                return {
                    "found": True,
                    "query": query,
                    "display_name": top.get("display_name"),
                    "latitude": float(top["lat"]),
                    "longitude": float(top["lon"]),
                    "country": country,
                    "state": state,
                    "city": city,
                    "source": "OSM Nominatim",
                    "attribution": "© OpenStreetMap contributors (ODbL license)",
                }
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"Nominatim geocoding fallback for '{query}': {e}")

    # ── 3. Try Local Catalog ──────────────────────────────────────────────────
    for key, val in CITY_CATALOG.items():
        if key in clean_q or clean_q in key:
            return {
                "found": True,
                "query": query,
                "display_name": f"{val['city']}, {val['state']}, {val['country']}",
                "latitude": val["lat"],
                "longitude": val["lon"],
                "country": val["country"],
                "state": val["state"],
                "city": val["city"],
                "source": "AgriSmart Knowledge Base",
                "attribution": "AgriSmart Geocoding Catalog",
            }

    # ── 4. Not Found (Clean Return, No Exception) ─────────────────────────────
    return {
        "found": False,
        "query": query,
        "message": f"Location '{query}' not found. Please specify a nearby city or country name."
    }