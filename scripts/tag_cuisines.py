import csv
import os

INPUT_FILE  = "/Users/medhasharma/state-college-food/data/clean/restaurants_clean.csv"
OUTPUT_FILE = "/Users/medhasharma/state-college-food/data/clean/restaurants_tagged.csv"

# Maps keywords in restaurant names + Google types to cuisine labels
NAME_KEYWORDS = {
    "pizza": "Pizza",
    "pizzeria": "Pizza",
    "waffle": "Breakfast",
    "bagel": "Breakfast & Cafe",
    "cafe": "Breakfast & Cafe",
    "coffee": "Breakfast & Cafe",
    "bistro": "Bistro",
    "sushi": "Japanese",
    "hibachi": "Japanese",
    "japanese": "Japanese",
    "tadashi": "Japanese",
    "sakura": "Japanese",
    "tokyo": "Japanese",
    "chinese": "Chinese",
    "szechuan": "Chinese",
    "beijing": "Chinese",
    "lychee": "Chinese",
    "gudong": "Chinese",
    "hot pot": "Chinese",
    "dagu": "Chinese",
    "yummy cafe": "Chinese",
    "uncle chen": "Chinese",
    "thai": "Thai",
    "cozy thai": "Thai",
    "my thai": "Thai",
    "pho": "Vietnamese",
    "vietnamese": "Vietnamese",
    "indian": "Indian",
    "india": "Indian",
    "masala": "Indian",
    "halal": "Halal",
    "kebab": "Halal/Middle Eastern",
    "pide": "Halal/Middle Eastern",
    "mosul": "Halal/Middle Eastern",
    "fatoum": "Halal/Middle Eastern",
    "fatema": "Halal/Middle Eastern",
    "fuego": "Halal/Middle Eastern",
    "mediterranean": "Mediterranean",
    "greek": "Mediterranean",
    "kitchen garden": "Mediterranean",
    "fire & fig": "Mediterranean",
    "mexican": "Mexican",
    "lupita": "Mexican",
    "plaza": "Mexican",
    "moe's": "Mexican",
    "taco": "Mexican",
    "chipotle": "Mexican",
    "burger": "American",
    "five guys": "American",
    "big chicken": "American",
    "cluck": "American",
    "wings": "American",
    "chicken": "American",
    "primanti": "American",
    "local whiskey": "American",
    "champs": "American",
    "triplett": "American",
    "trophy room": "American",
    "federal taphouse": "American",
    "tavern": "American",
    "corner room": "American",
    "allen street grill": "American",
    "sowers": "American",
    "bistrozine": "American",
    "brothers": "American",
    "arena": "American",
    "sheetz": "American",
    "subway": "Sandwiches",
    "jersey mike": "Sandwiches",
    "penn pide": "Halal/Middle Eastern",
    "penn kebab": "Halal/Middle Eastern",
    "mcalister": "Sandwiches",
    "toasted bagel": "Breakfast & Cafe",
    "irvings": "Breakfast & Cafe",
    "rothrock": "Breakfast & Cafe",
    "webster": "Breakfast & Cafe",
    "dunkin": "Breakfast & Cafe",
    "starbucks": "Breakfast & Cafe",
    "domino": "Pizza",
    "papa john": "Pizza",
    "canyon pizza": "Pizza",
    "monte pizza": "Pizza",
    "faccia luna": "Pizza",
    "margarita": "Pizza",
    "allen street pizza": "Pizza",
    "benny leone": "Pizza",
    "snap custom pizza": "Pizza",
    "700 degree": "Pizza",
    "marzoni": "Pizza",
    "brothers pizza": "Pizza",
    "d.p. dough": "Late Night Snacks",
    "dp dough": "Late Night Snacks",
    "zen wings": "Late Night Snacks",
    "kondu": "Asian Fusion",
    "teadori": "Asian Fusion",
    "green bowl": "Asian Fusion",
    "big bowl": "Asian Fusion",
    "playa bowls": "Bowls & Healthy",
    "snap": "Bowls & Healthy",
    "dairy queen": "Fast Food",
    "mcdonald": "Fast Food",
    "wendy": "Fast Food",
    "burger king": "Fast Food",
    "sbarro": "Fast Food",
    "honey baked": "Deli & Specialty",
    "penn state halal guys": "Halal",
    "pita cabana": "Mediterranean",
    "little szechuan": "Chinese",
    "big dean": "American",
    "cafe alina": "Breakfast & Cafe",
    "cafe laura": "Breakfast & Cafe",
    "lionne": "American",
    "phyrst": "Bar & Pub",
    "sharkies": "Bar & Pub",
     "pollock commons": "Campus Dining",
    "panda express": "Chinese",
    "fiddlehead": "American",
    "osaka": "Japanese",
    "famous ernie": "Sandwiches",
    "sichuan house": "Chinese",
    "celebrities": "Bar & Pub",
    "kfc": "Fast Food",
    "manna bbq": "Asian Fusion",
    "rita's": "Dessert",
    "hoss's": "American",
    "red lobster": "Seafood",
    "cc peppers": "American",
    "penang": "Asian Fusion",
    "suzie wong": "Asian Fusion",
    "college buffet": "Chinese",
    "poke": "Asian Fusion",
    "juana": "Venezuelan",
    "sauly boy": "American",
    "chick 2": "American",
}

def tag_cuisine(name, current_type):
    name_lower = name.lower()
    for keyword, cuisine in NAME_KEYWORDS.items():
        if keyword in name_lower:
            return cuisine
    # Fall back to existing type if already specific
    if current_type not in ["Restaurant", "Delivery", "Takeout"]:
        return current_type
    return "Other"

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"🏷️  Tagging cuisines for {len(rows)} restaurants...\n")

    untagged = []
    for row in rows:
        original = row["cuisine_type"]
        row["cuisine_type"] = tag_cuisine(row["name"], original)
        if row["cuisine_type"] == "Other":
            untagged.append(row["name"])

    # Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Saved tagged data to: {OUTPUT_FILE}")

    # Show cuisine distribution
    from collections import Counter
    counts = Counter(r["cuisine_type"] for r in rows)
    print("\n── CUISINE DISTRIBUTION ─────────────────────────")
    for cuisine, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * count
        print(f"  {cuisine:<25} {bar} ({count})")

    if untagged:
        print(f"\n⚠️  Still untagged ({len(untagged)}) — review these:")
        for name in untagged:
            print(f"    - {name}")

if __name__ == "__main__":
    main()