import csv
import os
from collections import Counter

INPUT_FILE  = "/Users/medhasharma/state-college-food/data/clean/restaurants_clean.csv"
OUTPUT_FILE = "/Users/medhasharma/state-college-food/data/clean/restaurants_tagged.csv"

# ── TWO-LEVEL TAXONOMY ────────────────────────────────────────────────────────
# cuisine_type → category
CATEGORY_MAP = {
    # Food
    "Pizza":                "Food",
    "American":             "Food",
    "Chinese":              "Food",
    "Japanese":             "Food",
    "Thai":                 "Food",
    "Vietnamese":           "Food",
    "Indian":               "Food",
    "Halal":                "Food",
    "Halal/Middle Eastern": "Food",
    "Mediterranean":        "Food",
    "Mexican":              "Food",
    "Sandwiches":           "Food",
    "Asian Fusion":         "Food",
    "Bowls & Healthy":      "Food",
    "Seafood":              "Food",
    "Bistro":               "Food",
    "Venezuelan":           "Food",
    "Deli & Specialty":     "Food",
    "Other":                "Food",
    # Drinks
    "Bar & Pub":            "Drinks",
    "Nightlife / Club":     "Drinks",
    "Coffee & Tea":         "Drinks",
    # Dessert & Snacks
    "Boba & Tea":           "Dessert & Snacks",
    "Ice Cream & Dessert":  "Dessert & Snacks",
    "Bakery":               "Dessert & Snacks",
    "Late Night Snacks":    "Dessert & Snacks",
    # Fast Food
    "Fast Food":            "Fast Food",
    # Campus
    "Campus Dining":        "Campus Dining",
    # Breakfast treated as food
    "Breakfast":            "Food",
    "Breakfast & Cafe":     "Drinks",   # cafes skew drinks
}

# ── KEYWORD → CUISINE_TYPE ────────────────────────────────────────────────────
# Order matters: more specific entries first
NAME_KEYWORDS = {
    # ── BOBA & TEA ────────────────────────────────────────
    "boba":           "Boba & Tea",
    "bubble tea":     "Boba & Tea",
    "teadori":        "Boba & Tea",
    "gong cha":       "Boba & Tea",
    "kung fu tea":    "Boba & Tea",
    "tiger sugar":    "Boba & Tea",
    "one zoo":        "Boba & Tea",
    "happy lemon":    "Boba & Tea",
    "tealive":        "Boba & Tea",
    "chatime":        "Boba & Tea",
    "vivi":           "Boba & Tea",
    "coco":           "Boba & Tea",

    # ── ICE CREAM & DESSERT ───────────────────────────────
    "ice cream":      "Ice Cream & Dessert",
    "creamery":       "Ice Cream & Dessert",   # Penn State Creamery
    "gelato":         "Ice Cream & Dessert",
    "rita's":         "Ice Cream & Dessert",
    "dairy queen":    "Ice Cream & Dessert",
    "cold stone":     "Ice Cream & Dessert",
    "yogurt":         "Ice Cream & Dessert",
    "froyo":          "Ice Cream & Dessert",
    "baskin":         "Ice Cream & Dessert",
    "sorbet":         "Ice Cream & Dessert",
    "dessert":        "Ice Cream & Dessert",
    "sweet":          "Ice Cream & Dessert",
    "cheesecake":     "Ice Cream & Dessert",
    "candy":          "Ice Cream & Dessert",
    "chocolate":      "Ice Cream & Dessert",

    # ── BAKERY ────────────────────────────────────────────
    "bakery":         "Bakery",
    "bagel":          "Bakery",
    "waffle":         "Bakery",
    "donut":          "Bakery",
    "pastry":         "Bakery",
    "croissant":      "Bakery",
    "bread":          "Bakery",
    "muffin":         "Bakery",

    # ── NIGHTLIFE / CLUB ──────────────────────────────────
    "nightclub":      "Nightlife / Club",
    "club":           "Nightlife / Club",
    "lounge":         "Nightlife / Club",
    "263":            "Nightlife / Club",
    "indigo":         "Nightlife / Club",
    "zeno's":         "Nightlife / Club",
    "zenos":          "Nightlife / Club",
    "mad mex":        "Nightlife / Club",

    # ── BARS & PUBS ───────────────────────────────────────
    "bar":            "Bar & Pub",
    "pub":            "Bar & Pub",
    "tavern":         "Bar & Pub",
    "brewery":        "Bar & Pub",
    "taphouse":       "Bar & Pub",
    "taproom":        "Bar & Pub",
    "federal taphouse": "Bar & Pub",
    "phyrst":         "Bar & Pub",
    "sharkies":       "Bar & Pub",
    "champs":         "Bar & Pub",
    "brewery":        "Bar & Pub",
    "whiskey":        "Bar & Pub",
    "local whiskey":  "Bar & Pub",
    "trophy room":    "Bar & Pub",
    "arena":          "Bar & Pub",
    "brothers":       "Bar & Pub",
    "celebrities":    "Bar & Pub",

    # ── COFFEE & TEA (non-boba) ───────────────────────────
    "coffee":         "Coffee & Tea",
    "cafe":           "Coffee & Tea",
    "starbucks":      "Coffee & Tea",
    "dunkin":         "Coffee & Tea",
    "espresso":       "Coffee & Tea",
    "latte":          "Coffee & Tea",
    "rothrock":       "Coffee & Tea",
    "webster":        "Coffee & Tea",
    "irvings":        "Coffee & Tea",
    "cafe alina":     "Coffee & Tea",
    "cafe laura":     "Coffee & Tea",
    "toasted bagel":  "Coffee & Tea",   # café context

    # ── PIZZA ─────────────────────────────────────────────
    "pizza":          "Pizza",
    "pizzeria":       "Pizza",
    "domino":         "Pizza",
    "papa john":      "Pizza",
    "canyon pizza":   "Pizza",
    "monte pizza":    "Pizza",
    "faccia luna":    "Pizza",
    "allen street pizza": "Pizza",
    "benny leone":    "Pizza",
    "snap custom pizza": "Pizza",
    "700 degree":     "Pizza",
    "marzoni":        "Pizza",
    "brothers pizza": "Pizza",

    # ── AMERICAN ──────────────────────────────────────────
    "burger":         "American",
    "five guys":      "American",
    "big chicken":    "American",
    "cluck":          "American",
    "wings":          "American",
    "chicken":        "American",
    "primanti":       "American",
    "corner room":    "American",
    "allen street grill": "American",
    "sowers":         "American",
    "fiddlehead":     "American",
    "hoss's":         "American",
    "bistrozine":     "American",
    "lionne":         "American",
    "cc peppers":     "American",
    "sauly boy":      "American",
    "chick 2":        "American",
    "triplett":       "American",
    "big dean":       "American",

    # ── SANDWICHES ────────────────────────────────────────
    "subway":         "Sandwiches",
    "jersey mike":    "Sandwiches",
    "mcalister":      "Sandwiches",
    "famous ernie":   "Sandwiches",

    # ── CHINESE ───────────────────────────────────────────
    "chinese":        "Chinese",
    "szechuan":       "Chinese",
    "sichuan":        "Chinese",
    "beijing":        "Chinese",
    "lychee":         "Chinese",
    "gudong":         "Chinese",
    "hot pot":        "Chinese",
    "dagu":           "Chinese",
    "yummy cafe":     "Chinese",
    "uncle chen":     "Chinese",
    "little szechuan": "Chinese",
    "panda express":  "Chinese",
    "college buffet": "Chinese",
    "sichuan house":  "Chinese",

    # ── JAPANESE ──────────────────────────────────────────
    "sushi":          "Japanese",
    "hibachi":        "Japanese",
    "japanese":       "Japanese",
    "tadashi":        "Japanese",
    "sakura":         "Japanese",
    "tokyo":          "Japanese",
    "osaka":          "Japanese",
    "ramen":          "Japanese",

    # ── THAI ──────────────────────────────────────────────
    "thai":           "Thai",
    "cozy thai":      "Thai",
    "my thai":        "Thai",

    # ── VIETNAMESE ────────────────────────────────────────
    "pho":            "Vietnamese",
    "vietnamese":     "Vietnamese",

    # ── INDIAN ────────────────────────────────────────────
    "indian":         "Indian",
    "india":          "Indian",
    "masala":         "Indian",

    # ── HALAL / MIDDLE EASTERN ────────────────────────────
    "halal":          "Halal",
    "kebab":          "Halal/Middle Eastern",
    "pide":           "Halal/Middle Eastern",
    "mosul":          "Halal/Middle Eastern",
    "fatoum":         "Halal/Middle Eastern",
    "fatema":         "Halal/Middle Eastern",
    "fuego":          "Halal/Middle Eastern",
    "penn pide":      "Halal/Middle Eastern",
    "penn kebab":     "Halal/Middle Eastern",
    "pita cabana":    "Mediterranean",

    # ── MEDITERRANEAN ─────────────────────────────────────
    "mediterranean":  "Mediterranean",
    "greek":          "Mediterranean",
    "kitchen garden": "Mediterranean",
    "fire & fig":     "Mediterranean",

    # ── MEXICAN ───────────────────────────────────────────
    "mexican":        "Mexican",
    "lupita":         "Mexican",
    "plaza":          "Mexican",
    "moe's":          "Mexican",
    "taco":           "Mexican",
    "chipotle":       "Mexican",

    # ── ASIAN FUSION ──────────────────────────────────────
    "kondu":          "Asian Fusion",
    "green bowl":     "Asian Fusion",
    "big bowl":       "Asian Fusion",
    "penang":         "Asian Fusion",
    "suzie wong":     "Asian Fusion",
    "manna bbq":      "Asian Fusion",
    "poke":           "Asian Fusion",

    # ── BOWLS & HEALTHY ───────────────────────────────────
    "playa bowls":    "Bowls & Healthy",
    "snap":           "Bowls & Healthy",

    # ── SEAFOOD ───────────────────────────────────────────
    "red lobster":    "Seafood",
    "seafood":        "Seafood",

    # ── FAST FOOD ─────────────────────────────────────────
    "mcdonald":       "Fast Food",
    "wendy":          "Fast Food",
    "burger king":    "Fast Food",
    "sbarro":         "Fast Food",
    "kfc":            "Fast Food",
    "sheetz":         "Fast Food",
    "chick-fil-a":    "Fast Food",

    # ── LATE NIGHT SNACKS ────────────────────────────────
    "d.p. dough":     "Late Night Snacks",
    "dp dough":       "Late Night Snacks",
    "zen wings":      "Late Night Snacks",

    # ── CAMPUS DINING ─────────────────────────────────────
    "pollock":        "Campus Dining",
    "berkey":         "Campus Dining",
    "findlay":        "Campus Dining",
    "waring":         "Campus Dining",
    "redifer":        "Campus Dining",
    "east food":      "Campus Dining",

    # ── OTHER ─────────────────────────────────────────────
    "bistro":         "Bistro",
    "honey baked":    "Deli & Specialty",
    "juana":          "Venezuelan",
    "teadori":        "Boba & Tea",
}


def tag_cuisine(name, current_type):
    name_lower = name.lower()
    for keyword, cuisine in NAME_KEYWORDS.items():
        if keyword in name_lower:
            return cuisine
    if current_type not in ["Restaurant", "Delivery", "Takeout", "Bar"]:
        return current_type
    return "Other"


def get_category(cuisine_type):
    return CATEGORY_MAP.get(cuisine_type, "Food")


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"🏷️  Tagging cuisines for {len(rows)} restaurants...\n")

    untagged = []
    for row in rows:
        original = row["cuisine_type"]
        row["cuisine_type"] = tag_cuisine(row["name"], original)
        row["category"]     = get_category(row["cuisine_type"])
        if row["cuisine_type"] == "Other":
            untagged.append(row["name"])

    # Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Saved tagged data to: {OUTPUT_FILE}\n")

    # Cuisine distribution
    cuisine_counts = Counter(r["cuisine_type"] for r in rows)
    print("── CUISINE DISTRIBUTION ─────────────────────────────────")
    for cuisine, count in sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {cuisine:<25} {bar} ({count})")

    # Category distribution
    category_counts = Counter(r["category"] for r in rows)
    print("\n── CATEGORY DISTRIBUTION ────────────────────────────────")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {cat:<20} {bar} ({count})")

    if untagged:
        print(f"\n⚠️  Still untagged ({len(untagged)}) — review these:")
        for name in untagged:
            print(f"    - {name}")

if __name__ == "__main__":
    main()
