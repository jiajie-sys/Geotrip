import json
from pathlib import Path


PLACES_PATH = Path(
    "data/places/attractions.json"
)


def load_places():

    return json.loads(
        PLACES_PATH.read_text(
            encoding="utf-8"
        )
    )


def search_places(country: str, keyword: str = ""):
    places = load_places()

    results = []

    for place in places:
        if place["country"].lower() != country.lower():
            continue

        if keyword and keyword.lower() not in str(place).lower():
            continue

        results.append(place)

    return results