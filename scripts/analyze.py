import csv
import json
from collections import defaultdict

INPUT_FILE = "/Users/medhasharma/state-college-food/data/clean/restaurants_clean.csv"

def load_data():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def safe_float(val):
    try:
        return float(val)
    except:
        return None

def safe_int(val):
    try:
        return int(val)
    except:
        return None

def print_section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")

def analyze(data):

    # ── 1. OVERVIEW ───────────────────────────────────────────
    print_section("DATASET OVERVIEW")
    operational = [r for r in data if r["status"] == "OPERATIONAL"]
    closed      = [r for r in data if r["status"] != "OPERATIONAL"]
    rated       = [r for r in data if safe_float(r["rating"])]
    late_night  = [r for r in data if r["is_late_night"] == "True"]
    open_sunday = [r for r in data if r["opens_sunday"] == "True"]

    print(f"  Total restaurants     : {len(data)}")
    print(f"  Currently operational : {len(operational)}")
    print(f"  Closed/temporarily    : {len(closed)}")
    print(f"  Late night (past 12am): {len(late_night)}")
    print(f"  Open on Sundays       : {len(open_sunday)}")

    ratings = [safe_float(r["rating"]) for r in rated]
    avg_rating = round(sum(ratings) / len(ratings), 2)
    print(f"  Average rating        : {avg_rating} ⭐")

    # ── 2. CUISINE BREAKDOWN ──────────────────────────────────
    print_section("CUISINE BREAKDOWN")
    cuisine_counts = defaultdict(int)
    for r in operational:
        cuisine_counts[r["cuisine_type"]] += 1
    sorted_cuisines = sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)
    for cuisine, count in sorted_cuisines:
        bar = "█" * count
        print(f"  {cuisine:<15} {bar} ({count})")

    # ── 3. TOP RATED (min 50 reviews) ────────────────────────
    print_section("TOP RATED — Established spots (50+ reviews)")
    qualified = [r for r in operational
                 if safe_float(r["rating"]) and safe_int(r["review_count"])
                 and safe_int(r["review_count"]) >= 50]
    top_rated = sorted(qualified, key=lambda x: safe_float(x["rating"]), reverse=True)[:10]
    for i, r in enumerate(top_rated, 1):
        print(f"  {i:>2}. {r['name']:<35} ⭐{r['rating']}  ({r['review_count']} reviews)  💰{'x'*safe_int(r['price_level']) if r['price_level'] else '?'}")

    # ── 4. HIDDEN GEMS ────────────────────────────────────────
    print_section("HIDDEN GEMS — High rating, under the radar (<150 reviews)")
    gems = [r for r in operational
            if safe_float(r["rating"]) and safe_int(r["review_count"])
            and safe_float(r["rating"]) >= 4.3
            and safe_int(r["review_count"]) < 150]
    gems_sorted = sorted(gems, key=lambda x: safe_float(x["rating"]), reverse=True)
    for r in gems_sorted:
        print(f"  {r['name']:<35} ⭐{r['rating']}  ({r['review_count']} reviews)")

    # ── 5. BEST VALUE ─────────────────────────────────────────
    print_section("BEST VALUE — High rating + budget friendly (price level 1)")
    value = [r for r in operational
             if safe_float(r["rating"]) and r["price_level"] == "1"
             and safe_float(r["rating"]) >= 4.0]
    value_sorted = sorted(value, key=lambda x: safe_float(x["rating"]), reverse=True)
    for r in value_sorted:
        print(f"  {r['name']:<35} ⭐{r['rating']}  ({r['review_count']} reviews)")

    # ── 6. LATE NIGHT OPTIONS ─────────────────────────────────
    print_section("LATE NIGHT — Open past midnight, ranked by rating")
    late = [r for r in operational
            if r["is_late_night"] == "True" and safe_float(r["rating"])]
    late_sorted = sorted(late, key=lambda x: safe_float(x["rating"]), reverse=True)
    for r in late_sorted:
        print(f"  {r['name']:<35} ⭐{r['rating']}  ({r['review_count']} reviews)")

    # ── 7. SUSPICIOUS RATINGS ─────────────────────────────────
    print_section("SUSPICIOUS RATINGS — High stars but very few reviews (<20)")
    suspicious = [r for r in operational
                  if safe_float(r["rating"]) and safe_int(r["review_count"])
                  and safe_float(r["rating"]) >= 4.5
                  and safe_int(r["review_count"]) < 20]
    suspicious_sorted = sorted(suspicious, key=lambda x: safe_float(x["rating"]), reverse=True)
    if suspicious_sorted:
        for r in suspicious_sorted:
            print(f"  {r['name']:<35} ⭐{r['rating']}  ({r['review_count']} reviews) ⚠️")
    else:
        print("  None found — ratings look trustworthy!")

    # ── 8. PRICE DISTRIBUTION ────────────────────────────────
    print_section("PRICE DISTRIBUTION")
    price_map = {"1": "💰 Budget", "2": "💰💰 Mid-range", "3": "💰💰💰 Upscale", "4": "💰💰💰💰 Fine dining"}
    price_counts = defaultdict(int)
    for r in operational:
        label = price_map.get(r["price_level"], "Unknown")
        price_counts[label] += 1
    for label, count in sorted(price_counts.items()):
        bar = "█" * count
        print(f"  {label:<20} {bar} ({count})")

    # ── 9. DATE NIGHT PICKS ───────────────────────────────────
    print_section("DATE NIGHT PICKS — Mid-range, high rating, not a bar/takeout")
    date_night = [r for r in operational
                  if safe_float(r["rating"]) and r["price_level"] in ["2", "3"]
                  and safe_float(r["rating"]) >= 4.2
                  and r["cuisine_type"] not in ["Bar", "Takeout", "Delivery"]
                  and safe_int(r["review_count"]) and safe_int(r["review_count"]) >= 30]
    date_sorted = sorted(date_night, key=lambda x: safe_float(x["rating"]), reverse=True)
    for r in date_sorted[:10]:
        print(f"  {r['name']:<35} ⭐{r['rating']}  💰{'x'*safe_int(r['price_level'])}  ({r['review_count']} reviews)")

    print(f"\n{'='*55}")
    print("  Analysis complete.")
    print(f"{'='*55}\n")

if __name__ == "__main__":
    data = load_data()
    analyze(data)