import csv
import os
from collections import Counter

from config import CLEAN

INPUT_FILE  = CLEAN / "restaurants_clean.csv"
OUTPUT_FILE = CLEAN / "restaurants_tagged.csv"

# ── KEYWORD → CUISINE_TYPE ────────────────────────────────────────────────────
# Matched against the restaurant name, first match wins, so more specific
# keywords come before generic ones.
NAME_KEYWORDS = {
    "boba":"Boba & Tea","bubble tea":"Boba & Tea","teadori":"Boba & Tea",
    "gong cha":"Boba & Tea","kung fu tea":"Boba & Tea","tiger sugar":"Boba & Tea",
    "one zoo":"Boba & Tea","happy lemon":"Boba & Tea","vivi":"Boba & Tea",
    "ice cream":"Ice Cream","creamery":"Ice Cream","gelato":"Ice Cream",
    "rita's":"Ice Cream","cold stone":"Ice Cream","yogurt":"Ice Cream",
    "froyo":"Ice Cream","dessert":"Ice Cream","cheesecake":"Ice Cream",
    "dairy queen":"Ice Cream",
    "bakery":"Bakery","bagel":"Bakery","waffle":"Bakery","donut":"Bakery",
    "pastry":"Bakery","croissant":"Bakery","muffin":"Bakery",
    "nightclub":"Nightlife","lounge":"Nightlife","263":"Nightlife",
    "indigo":"Nightlife","zeno's":"Nightlife","zenos":"Nightlife",
    "taphouse":"Bar & Pub","taproom":"Bar & Pub","brewery":"Bar & Pub",
    "phyrst":"Bar & Pub","sharkies":"Bar & Pub","champs":"Bar & Pub",
    "whiskey":"Bar & Pub","trophy room":"Bar & Pub","celebrities":"Bar & Pub",
    "federal taphouse":"Bar & Pub","arena":"Bar & Pub",
    "coffee":"Coffee & Tea","starbucks":"Coffee & Tea","dunkin":"Coffee & Tea",
    "espresso":"Coffee & Tea","rothrock":"Coffee & Tea","webster":"Coffee & Tea",
    "irvings":"Coffee & Tea","cafe alina":"Coffee & Tea","cafe laura":"Coffee & Tea",
    "pizza":"Pizza","pizzeria":"Pizza","domino":"Pizza","papa john":"Pizza",
    "faccia luna":"Pizza","marzoni":"Pizza","benny leone":"Pizza",
    "700 degree":"Pizza","brothers pizza":"Pizza","canyon pizza":"Pizza",
    "burger":"American","five guys":"American","big chicken":"American",
    "wings":"American","primanti":"American","corner room":"American",
    "allen street grill":"American","sowers":"American","fiddlehead":"American",
    "hoss's":"American","lionne":"American","cc peppers":"American",
    "big dean":"American","triplett":"American",
    "subway":"Sandwiches","jersey mike":"Sandwiches",
    "mcalister":"Sandwiches","famous ernie":"Sandwiches",
    "chinese":"Chinese","szechuan":"Chinese","sichuan":"Chinese",
    "beijing":"Chinese","gudong":"Chinese","hot pot":"Chinese","dagu":"Chinese",
    "yummy cafe":"Chinese","uncle chen":"Chinese","panda express":"Chinese",
    "college buffet":"Chinese","sichuan house":"Chinese","little szechuan":"Chinese",
    "sushi":"Japanese","hibachi":"Japanese","japanese":"Japanese",
    "tadashi":"Japanese","sakura":"Japanese","osaka":"Japanese","ramen":"Japanese",
    "thai":"Thai","cozy thai":"Thai","my thai":"Thai",
    "pho":"Vietnamese","vietnamese":"Vietnamese",
    "indian":"Indian","india":"Indian","masala":"Indian",
    "halal":"Halal","kebab":"Middle Eastern","pide":"Middle Eastern",
    "mosul":"Middle Eastern","fatoum":"Middle Eastern","fatema":"Middle Eastern",
    "fuego":"Middle Eastern","penn pide":"Middle Eastern","penn kebab":"Middle Eastern",
    "pita cabana":"Mediterranean","mediterranean":"Mediterranean",
    "greek":"Mediterranean","kitchen garden":"Mediterranean","fire & fig":"Mediterranean",
    "mexican":"Mexican","lupita":"Mexican","taco":"Mexican",
    "chipotle":"Mexican","moe's":"Mexican",
    "kondu":"Asian Fusion","green bowl":"Asian Fusion","big bowl":"Asian Fusion",
    "penang":"Asian Fusion","suzie wong":"Asian Fusion","manna bbq":"Asian Fusion",
    "poke":"Asian Fusion","playa bowls":"Bowls & Healthy","snap":"Bowls & Healthy",
    "red lobster":"Seafood","seafood":"Seafood",
    "mcdonald":"Fast Food","wendy":"Fast Food","burger king":"Fast Food",
    "sbarro":"Fast Food","kfc":"Fast Food","sheetz":"Fast Food",
    "chick-fil-a":"Fast Food",
    "d.p. dough":"Late Night Snacks","dp dough":"Late Night Snacks",
    "zen wings":"Late Night Snacks",
    "pollock":"Campus Dining","berkey":"Campus Dining","findlay":"Campus Dining",
    "waring":"Campus Dining","redifer":"Campus Dining",
    "bistro":"Bistro","honey baked":"Deli","juana":"Venezuelan","cafe":"Cafe",
}

# Hand-checked names that the keywords above don't catch.
MANUAL_OVERRIDES = {
    "The Tavern": "American",
    "Sher Hot Chicken": "American",
    "Brothers Bar & Grill": "American",
    "CLUCK & CATCH": "American",
    "Sauly Boy's": "American",
    "Chick 2": "American",
}

# cuisine_type → category (anything not listed is "Food")
CATEGORY_MAP = {
    "Bar & Pub":"Drinks","Nightlife":"Drinks",
    "Coffee & Tea":"Drinks","Cafe":"Drinks",
    "Boba & Tea":"Dessert & Snacks","Ice Cream":"Dessert & Snacks",
    "Bakery":"Dessert & Snacks","Late Night Snacks":"Dessert & Snacks",
    "Fast Food":"Fast Food","Campus Dining":"Campus Dining",
}


def tag_cuisine(name, current_type):
    if name in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[name]
    name_lower = name.lower()
    for keyword, cuisine in NAME_KEYWORDS.items():
        if keyword in name_lower:
            return cuisine
    if current_type not in ["Restaurant", "Delivery", "Takeout", "Bar", ""]:
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
