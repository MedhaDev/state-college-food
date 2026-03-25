import requests
import json
import time

API_KEY = "YOUR_GOOGLE_API_KEY_HERE"

OUTPUT_RAW      = "/Users/medhasharma/state-college-food/data/raw/restaurants_raw.json"
OUTPUT_DETAILED = "/Users/medhasharma/state-college-food/data/raw/restaurants_detailed.json"

# Multiple search points covering all of State College
SEARCH_POINTS = [
    {"name": "Downtown",         "lat": 40.7934, "lng": -77.8600},
    {"name": "South Atherton",   "lat": 40.7847, "lng": -77.8380},
    {"name": "North Atherton",   "lat": 40.8035, "lng": -77.8880},
    {"name": "West College Ave", "lat": 40.7895, "lng": -77.8750},
    {"name": "East College Ave", "lat": 40.7985, "lng": -77.8530},
]
RADIUS = 1500  # smaller radius per point = more precise, less overlap

DETAIL_FIELDS = ",".join([
    "place_id", "name", "formatted_address", "formatted_phone_number",
    "website", "rating", "user_ratings_total", "price_level",
    "business_status", "opening_hours", "reviews", "types", "geometry"
])


def fetch_nearby(lat, lng, radius, api_key):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": api_key
    }
    results = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        results.extend(data.get("results", []))
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
        time.sleep(2)
        params = {"pagetoken": next_page_token, "key": api_key}
    return results


def fetch_details(place_id, api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "fields": DETAIL_FIELDS, "key": api_key}
    response = requests.get(url, params=params)
    return response.json().get("result", {})


def main():
    # Step 1 — fetch from all search points, deduplicate by place_id
    print("🔍 Fetching restaurants from multiple locations...\n")
    seen_ids = set()
    all_results = []

    for point in SEARCH_POINTS:
        print(f"  Searching: {point['name']}...")
        results = fetch_nearby(point["lat"], point["lng"], RADIUS, API_KEY)
        new = 0
        for r in results:
            pid = r.get("place_id")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                all_results.append(r)
                new += 1
        print(f"    → {new} new restaurants (running total: {len(all_results)})")
        time.sleep(1)

    print(f"\n✅ Total unique restaurants found: {len(all_results)}")

    # Save raw
    with open(OUTPUT_RAW, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"   Saved to {OUTPUT_RAW}")

    # Step 2 — fetch details for each
    print(f"\n📋 Fetching details for {len(all_results)} restaurants...\n")
    detailed = []
    for i, r in enumerate(all_results):
        pid  = r.get("place_id")
        name = r.get("name", "Unknown")
        print(f"  [{i+1}/{len(all_results)}] {name}")
        details = fetch_details(pid, API_KEY)
        detailed.append(details)
        time.sleep(0.3)

    with open(OUTPUT_DETAILED, "w") as f:
        json.dump(detailed, f, indent=2)
    print(f"\n✅ Saved detailed data for {len(detailed)} restaurants")
    print(f"   Saved to {OUTPUT_DETAILED}")


if __name__ == "__main__":
    main()