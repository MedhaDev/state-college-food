import requests
import json
import time

API_KEY = "AIzaSyBTtQGZtGJsXlcm5W2fHgTOE739N2WHz6o"

INPUT_FILE  = "/Users/medhasharma/state-college-food/data/raw/restaurants_raw.json"
OUTPUT_FILE = "/Users/medhasharma/state-college-food/data/raw/restaurants_detailed.json"

FIELDS = ",".join([
    "place_id",
    "name",
    "formatted_address",
    "formatted_phone_number",
    "website",
    "rating",
    "user_ratings_total",
    "price_level",
    "business_status",
    "opening_hours",
    "reviews",
    "types",
    "geometry"
])

def fetch_details(place_id, api_key):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": FIELDS,
        "key": api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("result", {})

def main():
    # Load the raw restaurant list
    with open(INPUT_FILE, "r") as f:
        restaurants = json.load(f)

    print(f"📋 Found {len(restaurants)} restaurants to enrich...\n")

    detailed = []

    for i, r in enumerate(restaurants):
        place_id = r.get("place_id")
        name     = r.get("name", "Unknown")

        if not place_id:
            print(f"  ⚠️  Skipping {name} — no place_id")
            continue

        print(f"  [{i+1}/{len(restaurants)}] Fetching details for: {name}")
        details = fetch_details(place_id, API_KEY)
        detailed.append(details)

        # Be polite to the API — don't hammer it
        time.sleep(0.3)

    # Save results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(detailed, f, indent=2)

    print(f"\n✅ Saved detailed data for {len(detailed)} restaurants to:")
    print(f"   {OUTPUT_FILE}")

    # Quick preview of one restaurant's reviews
    print("\n── SAMPLE REVIEWS (first restaurant with reviews) ──")
    for r in detailed:
        reviews = r.get("reviews", [])
        if reviews:
            print(f"\n📍 {r.get('name')}")
            for rev in reviews[:3]:
                stars = "⭐" * rev.get("rating", 0)
                text  = rev.get("text", "")[:120]
                date  = rev.get("relative_time_description", "")
                print(f"  {stars} ({date}): {text}...")
            break

if __name__ == "__main__":
    main()