from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import requests
from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from urllib.parse import quote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIRECTORY = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIRECTORY))

from app.core.database import SessionLocal
from app.models.place import Place


OVERPASS_URL = "https://overpass-api.de/api/interpreter"

OVERPASS_HEADERS = {
    "Accept": "*/*",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://overpass-api.de",
    "Referer": "https://overpass-api.de/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Apple Silicon Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36 "
        "Spottr/0.1 (college project)"
    ),
}

AMENITY_CATEGORIES = {
    "cafe": "Cafe",
    "restaurant": "Restaurant",
    "fast_food": "Restaurant",
    "food_court": "Restaurant",
    "ice_cream": "Cafe",
    "bar": "Hangout",
    "pub": "Hangout",
    "cinema": "Entertainment",
    "theatre": "Entertainment",
    "library": "Books",
}

LEISURE_CATEGORIES = {
    "park": "Park",
    "playground": "Recreation",
    "fitness_centre": "Fitness",
    "sports_centre": "Recreation",
    "stadium": "Recreation",
}

TOURISM_CATEGORIES = {
    "museum": "Culture",
    "gallery": "Art",
    "attraction": "Attraction",
    "zoo": "Attraction",
}


def build_overpass_query(
    south: float,
    west: float,
    north: float,
    east: float,
) -> str:
    bounding_box = f"{south},{west},{north},{east}"

    return f"""
[out:json][timeout:90];
(
  nwr["name"]["amenity"~"^(cafe|restaurant|fast_food|food_court|ice_cream|bar|pub|cinema|theatre|library)$"]({bounding_box});
  nwr["name"]["leisure"~"^(park|playground|fitness_centre|sports_centre|stadium)$"]({bounding_box});
  nwr["name"]["tourism"~"^(museum|gallery|attraction|zoo)$"]({bounding_box});
);
out center;
"""


def get_category(tags: dict[str, str]) -> str | None:
    amenity = tags.get("amenity")
    if amenity in AMENITY_CATEGORIES:
        return AMENITY_CATEGORIES[amenity]

    leisure = tags.get("leisure")
    if leisure in LEISURE_CATEGORIES:
        return LEISURE_CATEGORIES[leisure]

    tourism = tags.get("tourism")
    if tourism in TOURISM_CATEGORIES:
        return TOURISM_CATEGORIES[tourism]

    return None


def get_coordinates(
    element: dict[str, Any],
) -> tuple[float, float] | None:
    latitude = element.get("lat")
    longitude = element.get("lon")

    if latitude is not None and longitude is not None:
        return float(latitude), float(longitude)

    center = element.get("center")
    if center is None:
        return None

    latitude = center.get("lat")
    longitude = center.get("lon")

    if latitude is None or longitude is None:
        return None

    return float(latitude), float(longitude)


def build_address(tags: dict[str, str]) -> str | None:
    address_parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb"),
        tags.get("addr:city"),
        tags.get("addr:postcode"),
    ]

    address = ", ".join(
        part.strip()
        for part in address_parts
        if part and part.strip()
    )

    return address or None


def normalize_place(
    element: dict[str, Any],
) -> dict[str, Any] | None:
    tags = element.get("tags", {})
    name = tags.get("name", "").strip()
    category = get_category(tags)
    coordinates = get_coordinates(element)

    if not name or category is None or coordinates is None:
        return None

    latitude, longitude = coordinates

    return {
        "osm_id": f"{element['type']}/{element['id']}",
        "name": name,
        "category": category,
        "description": tags.get("description"),
        "address": build_address(tags),
        "latitude": latitude,
        "longitude": longitude,
        "location": WKTElement(
            f"POINT({longitude} {latitude})",
            srid=4326,
        ),
    }


def upsert_places(
    normalized_places: list[dict[str, Any]],
) -> tuple[int, int]:
    created_count = 0
    updated_count = 0

    with SessionLocal() as db:
        try:
            for place_data in normalized_places:
                existing_place = db.scalar(
                    select(Place).where(
                        Place.osm_id == place_data["osm_id"]
                    )
                )

                if existing_place is None:
                    db.add(Place(**place_data))
                    created_count += 1
                    continue

                for field_name, value in place_data.items():
                    setattr(existing_place, field_name, value)

                updated_count += 1

            db.commit()
        except Exception:
            db.rollback()
            raise

    return created_count, updated_count


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import OpenStreetMap places into Spottr.",
    )

    parser.add_argument("--south", type=float, required=True)
    parser.add_argument("--west", type=float, required=True)
    parser.add_argument("--north", type=float, required=True)
    parser.add_argument("--east", type=float, required=True)

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    query = build_overpass_query(
        south=args.south,
        west=args.west,
        north=args.north,
        east=args.east,
    )

    response = requests.post(
    OVERPASS_URL,
    data=f"data={quote(query)}",
    headers=OVERPASS_HEADERS,
    timeout=120,
)
    response.raise_for_status()

    elements = response.json().get("elements", [])

    places_by_osm_id: dict[str, dict[str, Any]] = {}

    for element in elements:
        normalized_place = normalize_place(element)

        if normalized_place is not None:
            places_by_osm_id[
                normalized_place["osm_id"]
            ] = normalized_place

    created_count, updated_count = upsert_places(
        list(places_by_osm_id.values())
    )

    print(f"Fetched {len(elements)} OSM elements.")
    print(f"Imported {len(places_by_osm_id)} valid named places.")
    print(f"Created: {created_count}")
    print(f"Updated: {updated_count}")


if __name__ == "__main__":
    main()