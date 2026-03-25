import requests
import json
import time
import os

OUTPUT_FILE = "/Users/medhasharma/state-college-food/data/raw/reddit_posts.json"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

HEADERS = {"User-Agent": "state-college-food-research/1.0"}

SEARCHES = [
    {"sub": "StateCollege",       "query": "restaurant food eat"},
    {"sub": "StateCollege",       "query": "best food where to eat"},
    {"sub": "StateCollege",       "query": "pizza burger coffee brunch"},
    {"sub": "PennStateUniversity","query": "restaurant food eat"},
    {"sub": "PennStateUniversity","query": "best food where to eat downtown"},
    {"sub": "PennStateUniversity","query": "pizza coffee brunch late night"},
]

def fetch_posts(subreddit, query, limit=100):
    url = f"https://www.reddit.com/r/{subreddit}/search.json"
    params = {
        "q": query,
        "limit": limit,
        "sort": "relevance",
        "restrict_sr": "true",
        "t": "all"
    }
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            return [p["data"] for p in posts]
        else:
            print(f"  ⚠️  Status {response.status_code} for r/{subreddit} — {query}")
            return []
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []

def main():
    print("🔍 Fetching Reddit posts...\n")
    all_posts = []
    seen_ids = set()

    for search in SEARCHES:
        sub   = search["sub"]
        query = search["query"]
        print(f"  r/{sub} — '{query}'")
        posts = fetch_posts(sub, query)
        new = 0
        for p in posts:
            pid = p.get("id")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                all_posts.append({
                    "id":        p.get("id"),
                    "subreddit": p.get("subreddit"),
                    "title":     p.get("title", ""),
                    "selftext":  p.get("selftext", ""),
                    "score":     p.get("score", 0),
                    "url":       p.get("url", ""),
                    "created":   p.get("created_utc", 0),
                    "num_comments": p.get("num_comments", 0)
                })
                new += 1
        print(f"    → {new} new posts (total: {len(all_posts)})")
        time.sleep(2)  # be polite to Reddit

    with open(OUTPUT_FILE, "w") as f:
        json.dump(all_posts, f, indent=2)

    print(f"\n✅ Saved {len(all_posts)} posts to {OUTPUT_FILE}")

    # Quick preview
    print("\n── SAMPLE POSTS ─────────────────────────────────")
    for p in all_posts[:5]:
        print(f"  r/{p['subreddit']} | ⬆️{p['score']} | {p['title'][:70]}")

if __name__ == "__main__":
    main()