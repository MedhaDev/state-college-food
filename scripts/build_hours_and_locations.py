"""Build two lookup tables the planner needs: opening hours and walking distance.

Input:  data/raw/restaurants_detailed.json
Output: data/clean/restaurant_hours.csv      one row per restaurant per opening window
        data/clean/restaurant_locations.csv  distance to Beaver Stadium and downtown

Walking times are estimates: straight-line distance x 1.3 (streets are not
straight) at 5 km/h. Good enough to say "walkable before kickoff" or not.
"""
import json
import math

import pandas as pd

from config import CLEAN, RAW

INPUT_FILE = RAW / "restaurants_detailed.json"
HOURS_FILE = CLEAN / "restaurant_hours.csv"
LOCATIONS_FILE = CLEAN / "restaurant_locations.csv"

# Google numbers days 0 = Sunday ... 6 = Saturday
DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

LANDMARKS = {
    "stadium": (40.8122, -77.8561),   # Beaver Stadium
    "downtown": (40.7943, -77.8607),  # College Ave & Allen St
}
DETOUR_FACTOR = 1.3
WALK_KMH = 5.0


def to_minutes(hhmm):
    return int(hhmm[:2]) * 60 + int(hhmm[2:])


def hours_rows(place):
    periods = place.get("opening_hours", {}).get("periods", [])
    rows = []
    # A single period with no close time means open 24 hours, every day.
    if len(periods) == 1 and "close" not in periods[0]:
        for day in range(7):
            rows.append((day, 0, 24 * 60, True))
        return rows
    for p in periods:
        if "open" not in p or "close" not in p:
            continue
        open_day = p["open"]["day"]
        start = to_minutes(p["open"]["time"])
        # Days between open and close (e.g. Fri 8pm -> Sat 2am is 1 day later)
        days_later = (p["close"]["day"] - open_day) % 7
        end = to_minutes(p["close"]["time"]) + days_later * 24 * 60
        rows.append((open_day, start, end, False))
    return rows


def fmt(minutes):
    minutes %= 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def walk_km(a, b):
    lat1, lng1, lat2, lng2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2)
    return 2 * 6371 * math.asin(math.sqrt(h)) * DETOUR_FACTOR


def area_for(minutes_to_downtown, minutes_to_stadium):
    if minutes_to_downtown <= 10:
        return "Downtown"
    if minutes_to_stadium <= 20:
        return "Near the stadium"
    if minutes_to_downtown <= 25:
        return "Walkable from downtown"
    return "Drive or bus"


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        places = json.load(f)

    hours, locations = [], []
    for place in places:
        pid, name = place.get("place_id"), place.get("name")
        if not pid:
            continue

        for day, start, end, all_day in hours_rows(place):
            hours.append({
                "place_id": pid,
                "name": name,
                "day_of_week": DAY_NAMES[day],
                "opens": fmt(start),
                "closes": "24:00" if all_day else fmt(end),
                "open_minute": start,
                "close_minute": end,
                "closes_after_midnight": end > 24 * 60,
                "open_24_hours": all_day,
            })

        loc = place.get("geometry", {}).get("location", {})
        if "lat" in loc:
            here = (loc["lat"], loc["lng"])
            row = {"place_id": pid, "name": name, "lat": loc["lat"], "lng": loc["lng"]}
            for key, point in LANDMARKS.items():
                km = walk_km(here, point)
                row[f"walk_km_to_{key}"] = round(km, 2)
                row[f"walk_min_to_{key}"] = round(km / WALK_KMH * 60)
            row["area"] = area_for(row["walk_min_to_downtown"], row["walk_min_to_stadium"])
            row["walkable_to_stadium"] = row["walk_min_to_stadium"] <= 30
            locations.append(row)

    pd.DataFrame(hours).to_csv(HOURS_FILE, index=False)
    loc_df = pd.DataFrame(locations)
    loc_df.to_csv(LOCATIONS_FILE, index=False)

    with_hours = len({h["place_id"] for h in hours})
    print(f"Saved {len(hours)} opening windows for {with_hours} restaurants to {HOURS_FILE}")
    print(f"Saved {len(loc_df)} locations to {LOCATIONS_FILE}")
    print(loc_df["area"].value_counts().to_string())


if __name__ == "__main__":
    main()
