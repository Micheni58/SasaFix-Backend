# Google Maps API calls: geocoding, reverse geocoding, places autocomplete
# All functions are async — they use httpx for non-blocking HTTP calls

import httpx
import os
from math import radians, sin, cos, sqrt, atan2
from typing import Optional

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

GEOCODE_URL     = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES_AC_URL   = "https://maps.googleapis.com/maps/api/place/autocomplete/json"


def calculate_distance_km(lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two lat/lng pairs (in km).
    Used to filter providers within radius and show "X km away" on cards.
    """
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return round(R * c, 2)


async def geocode_address(address: str) -> Optional[dict]:
    """
    Convert a text address to lat/lng.
    Called when user types a location in the filter sidebar.

    Returns:
        { "latitude": float, "longitude": float, "formatted_address": str }
        or None if the address could not be geocoded.
    """
    if not GOOGLE_MAPS_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY not set in .env")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(GEOCODE_URL, params={
            "address": address,
            "key": GOOGLE_MAPS_API_KEY,
            "region": "KE",              # bias toward Kenya
            "components": "country:KE",
        })

    data = response.json()

    if data.get("status") != "OK" or not data.get("results"):
        return None

    result   = data["results"][0]
    location = result["geometry"]["location"]

    return {
        "latitude":          location["lat"],
        "longitude":         location["lng"],
        "formatted_address": result["formatted_address"],
    }

async def autocomplete_location(query: str) -> list:
    """
    Return up to 5 location suggestions for a partial search string.
    Powers the dropdown that appears when typing in the location filter.

    Returns:
        List of { "place_id": str, "description": str }
    """
    if not GOOGLE_MAPS_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(PLACES_AC_URL, params={
            "input":      query,
            "key":        GOOGLE_MAPS_API_KEY,
            "components": "country:ke",
            "types":      "geocode",
        })

    data = response.json()

    if data.get("status") not in ("OK", "ZERO_RESULTS"):
        return []

    return [
        {
            "place_id":    p["place_id"],
            "description": p["description"],
        }
        for p in data.get("predictions", [])
    ]