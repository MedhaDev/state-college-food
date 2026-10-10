"""Weekly snapshot: record each restaurant's review count, rating and hours.

Run every week (by GitHub Actions), these snapshots build a time series. The
change in review count from one week to the next is a rough measure of how
many people visited, which can then be compared with the Penn State calendar
(game weeks vs. breaks vs. normal weeks).

Output: data/snapshots/places_YYYY-MM-DD.csv

Cost guardrail: each restaurant is one "Place Details Enterprise" call in
Google's Places API (New), which has 1,000 free calls per month. The script
refuses to run if this run would push the month past MONTHLY_CALL_LIMIT.

Usage:
    python scripts/snapshot_places.py            # real run (needs the API key)
    python scripts/snapshot_places.py --dry-run  # no API calls, just shows the plan
"""
import argparse
import sys
import time
from datetime import date

import pandas as pd
import requests

from config import CLEAN, SNAPSHOTS, google_api_key

RESTAURANTS_FILE = CLEAN / "restaurants_clean.csv"

# Stay safely under Google's 1,000 free Enterprise calls per month.
MONTHLY_CALL_LIMIT = 900

# Every field here is billed at the same (Enterprise) level, so asking for all
# of them costs one call per restaurant. Adding reviews or photos would cost more.
FIELD_MASK = ",".join([
    "id",
    "displayName",
    "businessStatus",
    "rating",
    "userRatingCount",
    "currentOpeningHours.weekdayDescriptions",
    "currentOpeningHours.specialDays",
])
URL = "https://places.googleapis.com/v1/places/{place_id}"


def places_to_track():
    df = pd.read_csv(RESTAURANTS_FILE, usecols=["place_id", "name", "status"])
    df = df[df["status"] != "CLOSED_PERMANENTLY"]
    return df.drop_duplicates("place_id")


def calls_used_this_month(today):
    """Count the API calls already made this month from earlier snapshot files."""
    used = 0
    for f in SNAPSHOTS.glob(f"places_{today:%Y-%m}-*.csv"):
        used += len(pd.read_csv(f, usecols=["place_id"]))
    return used


def fetch(place_id, api_key):
    response = requests.get(
        URL.format(place_id=place_id),
        headers={"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": FIELD_MASK},
        timeout=20,
    )
    return response.status_code, response.json() if response.content else {}


def to_row(today, place_id, name, status, data):
    hours = data.get("currentOpeningHours", {})
    return {
        "snapshot_date": today.isoformat(),
        "place_id": place_id,
        "name": data.get("displayName", {}).get("text", name),
        "fetch_status": "ok" if status == 200 else f"error {status}",
        "business_status": data.get("businessStatus"),
        "rating": data.get("rating"),
        "user_rating_count": data.get("userRatingCount"),
        "has_special_hours": bool(hours.get("specialDays")),
        "week_hours": " | ".join(hours.get("weekdayDescriptions", [])),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="plan only, no API calls")
    args = parser.parse_args()

    today = date.today()
    out_file = SNAPSHOTS / f"places_{today.isoformat()}.csv"
    places = places_to_track()
    used = calls_used_this_month(today)

    print(f"Restaurants to check: {len(places)}")
    print(f"Calls already used in {today:%B %Y}: {used} (limit {MONTHLY_CALL_LIMIT})")

    if out_file.exists():
        print(f"{out_file.name} already exists, nothing to do.")
        return
    if used + len(places) > MONTHLY_CALL_LIMIT:
        sys.exit("Stopping: this run would go over the monthly free-tier limit.")
    if args.dry_run:
        print(f"Dry run: would make {len(places)} calls and write {out_file.name}")
        return

    api_key = google_api_key()
    rows = []
    for i, place in enumerate(places.itertuples(), start=1):
        try:
            status, data = fetch(place.place_id, api_key)
        except requests.RequestException as e:
            status, data = 0, {}
            print(f"  network error for {place.name}: {e}")
        if status != 200:
            message = data.get("error", {}).get("message", "") if isinstance(data, dict) else ""
            print(f"  [{i}/{len(places)}] {place.name}: HTTP {status} {message}")
        rows.append(to_row(today, place.place_id, place.name, status, data))
        time.sleep(0.2)

    snapshot = pd.DataFrame(rows)
    ok = (snapshot["fetch_status"] == "ok").sum()
    # If most calls failed (bad key, API not enabled), don't save a broken file.
    if ok < len(snapshot) / 2:
        sys.exit(f"Only {ok} of {len(snapshot)} calls worked. Not saving. Check the API key.")

    snapshot.to_csv(out_file, index=False)
    print(f"Saved {ok} of {len(snapshot)} restaurants to {out_file}")


if __name__ == "__main__":
    main()
