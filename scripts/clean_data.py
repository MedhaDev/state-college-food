import json
import csv
import os

INPUT_FILE  = "/Users/medhasharma/state-college-food/data/raw/restaurants_detailed.json"
OUTPUT_FILE = "/Users/medhasharma/state-college-food/data/clean/restaurants_clean.csv"

# Make sure output folder exists
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def get_cuisine_type(types):
    """Map Google's type tags to a readable cuisine category."""
    type_map = {
        "bar": "Bar",
        "cafe": "Cafe",
        "bakery": "Bakery",
        "meal_takeaway": "Takeout",
        "meal_delivery": "Delivery"
    }
    # Remove generic tags
    skip = {"restaurant", "food", "point_of_interest", "establishment", "store", "university"}
    meaningful = [t for t in types if t not in skip]
    if not meaningful:
        return "Restaurant"
    # Return first meaningful type, cleaned up
    first = meaningful[0]
    return type_map.get(first, first.replace("_", " ").title())

def is_late_night(opening_hours):
    """Returns True if any closing time is midnight or later."""
    if not opening_hours:
        return False
    periods = opening_hours.get("periods", [])
    for period in periods:
        close_time = period.get("close", {}).get("time", "0000")
        hour = int(close_time[:2])
        if hour < 6 and hour >= 0:  # closes between midnight and 6am
            return True
    return False

def opens_on_sunday(opening_hours):
    """Returns True if restaurant is open on Sunday."""
    if not opening_hours:
        return False
    weekday_text = opening_hours.get("weekday_text", [])
    for line in weekday_text:
        if line.startswith("Sunday") and "Closed" not in line:
            return True
    return False

def get_review_stats(reviews):
    """Returns average review rating and concatenated review text."""
    if not reviews:
        return None, ""
    ratings = [r.get("rating", 0) for r in reviews]
    avg = round(sum(ratings) / len(ratings), 2)
    texts = " | ".join([r.get("text", "")[:200] for r in reviews if r.get("text")])
    return avg, texts

def main():
    with open(INPUT_FILE, "r") as f:
        restaurants = json.load(f)

    print(f"📋 Cleaning {len(restaurants)} restaurants...\n")

    rows = []
    for r in restaurants:
        if not r:
            continue

        name        = r.get("name", "")
        address     = r.get("formatted_address", "")
        phone       = r.get("formatted_phone_number", "")
        website     = r.get("website", "")
        rating      = r.get("rating", None)
        review_count = r.get("user_ratings_total", 0)
        price_level = r.get("price_level", None)
        status      = r.get("business_status", "")
        place_id    = r.get("place_id", "")

        # Location
        geo = r.get("geometry", {}).get("location", {})
        lat = geo.get("lat", None)
        lng = geo.get("lng", None)

        # Hours
        hours = r.get("opening_hours", {})
        late_night = is_late_night(hours)
        open_sunday = opens_on_sunday(hours)

        # Cuisine
        types = r.get("types", [])
        cuisine = get_cuisine_type(types)

        # Reviews
        reviews = r.get("reviews", [])
        avg_review_rating, review_texts = get_review_stats(reviews)

        rows.append({
            "place_id": place_id,
            "name": name,
            "address": address,
            "lat": lat,
            "lng": lng,
            "phone": phone,
            "website": website,
            "rating": rating,
            "review_count": review_count,
            "price_level": price_level,
            "status": status,
            "cuisine_type": cuisine,
            "is_late_night": late_night,
            "opens_sunday": open_sunday,
            "avg_review_rating": avg_review_rating,
            "review_texts": review_texts
        })

    # Write CSV
    fieldnames = rows[0].keys()
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Saved clean data to: {OUTPUT_FILE}")
    print(f"   {len(rows)} restaurants, {len(fieldnames)} columns")

    # Quick preview
    print("\n── PREVIEW ──────────────────────────────────")
    for row in rows[:5]:
        print(f"{row['name']:<30} | {row['cuisine_type']:<12} | ⭐{row['rating']} | 💰{'x' * (row['price_level'] or 0)} | Late night: {row['is_late_night']}")

if __name__ == "__main__":
    main()