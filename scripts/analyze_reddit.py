import json
import csv
import os
from collections import defaultdict

REDDIT_FILE      = "/Users/medhasharma/state-college-food/data/raw/reddit_posts.json"
RESTAURANTS_FILE = "/Users/medhasharma/state-college-food/data/clean/restaurants_tagged.csv"
OUTPUT_FILE      = "/Users/medhasharma/state-college-food/data/clean/reddit_mentions.csv"

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

def load_restaurants():
    with open(RESTAURANTS_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def load_posts():
    with open(REDDIT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def count_mentions(restaurant_name, posts):
    name_lower = restaurant_name.lower()
    mentions = []
    for post in posts:
        text = (post.get("title", "") + " " + post.get("selftext", "")).lower()
        if name_lower in text:
            mentions.append({
                "post_id":   post["id"],
                "subreddit": post["subreddit"],
                "title":     post["title"],
                "score":     post["score"],
                "url":       post["url"]
            })
    return mentions

def main():
    restaurants = load_restaurants()
    posts       = load_posts()

    print(f"📊 Analyzing {len(posts)} Reddit posts against {len(restaurants)} restaurants...\n")

    results  = []
    mentioned = []

    for r in restaurants:
        name     = r["name"]
        mentions = count_mentions(name, posts)
        count    = len(mentions)
        total_score = sum(m["score"] for m in mentions)
        subs = list(set(m["subreddit"] for m in mentions))

        results.append({
            "name":            name,
            "cuisine_type":    r["cuisine_type"],
            "rating":          r["rating"],
            "review_count":    r["review_count"],
            "price_level":     r["price_level"],
            "reddit_mentions": count,
            "reddit_score":    total_score,
            "subreddits":      ", ".join(subs) if subs else "",
            "sample_post":     mentions[0]["title"][:100] if mentions else ""
        })

        if count > 0:
            mentioned.append((name, count, total_score, r["rating"]))

    mentioned.sort(key=lambda x: x[1], reverse=True)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"✅ Saved to {OUTPUT_FILE}\n")

    print("── MOST MENTIONED ON REDDIT ─────────────────────────────")
    print(f"  {'Restaurant':<33} {'Mentions':>8} {'Score':>8} {'⭐':>6}")
    print("  " + "-" * 60)
    for name, count, score, rating in mentioned[:20]:
        print(f"  {name:<33} {count:>8} {score:>8} {rating:>6}")

    print(f"\n── NOT MENTIONED — but highly rated ─────────────────────")
    not_mentioned = [(r["name"], r["rating"]) for r in results
                     if r["reddit_mentions"] == 0 and float(r["rating"] or 0) >= 4.5]
    not_mentioned.sort(key=lambda x: float(x[1]) if x[1] else 0, reverse=True)
    for name, rating in not_mentioned:
        print(f"  {name:<35} ⭐{rating}")

    print(f"\n── HYPE VS REALITY ──────────────────────────────────────")
    print("  Talked about but lower rated (overhyped?):")
    overhyped = [(r["name"], r["reddit_mentions"], r["rating"])
                 for r in results
                 if r["reddit_mentions"] > 2 and float(r["rating"] or 0) < 4.0]
    overhyped.sort(key=lambda x: x[1], reverse=True)
    for name, mentions, rating in overhyped[:5]:
        print(f"  {name:<35} {mentions} mentions  ⭐{rating}")

    print("\n  High rated but nobody talks about (underrated?):")
    underrated = [(r["name"], r["reddit_mentions"], r["rating"])
                  for r in results
                  if r["reddit_mentions"] == 0 and float(r["rating"] or 0) >= 4.5]
    underrated.sort(key=lambda x: float(x[2]) if x[2] else 0, reverse=True)
    for name, mentions, rating in underrated[:10]:
        print(f"  {name:<35} {mentions} mentions  ⭐{rating}")

if __name__ == "__main__":
    main()
