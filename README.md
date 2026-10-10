# Table for 100,000

**Where to eat in State College, planned around the Penn State calendar.**

When 100,000+ fans fill Beaver Stadium, downtown State College changes completely. When students leave for winter break, it empties out. This project combines restaurant data with the Penn State academic and football calendar so visiting families, students and locals can decide *when* and *where* to eat, not just what's rated well.

> **Status: being rebuilt (Fall 2026).** The data foundation below is done. Next up is a Quarto website, replacing the original Streamlit dashboard ([still live here](https://state-college-food.streamlit.app)).

## The question

Most restaurant guides answer "what's good?" This one answers "**what works for this day?**"

- *Parents visiting for a home game:* what's walkable from the stadium, open Sunday morning, and not going to have a two-hour wait?
- *Students during finals or a break:* what's actually open late, or open at all?
- *Locals:* which weekends to avoid downtown, and where to go instead?

## What's in the data

| Layer | Source | What it adds |
|---|---|---|
| Restaurants | Google Places API | 145 restaurants: ratings, reviews, price, hours, location |
| Word of mouth | Reddit (r/StateCollege, r/PennStateUniversity) | Which places locals actually talk about |
| **Penn State calendar** | Registrar, Penn State Athletics, THON, Arts Fest (curated, every row sourced) | 365 days labeled by term phase and expected crowd level (1 = very quiet → 5 = packed) |
| **Hours & distance** | Derived from Google data | Opening windows per day (including after-midnight closes) and walking time to Beaver Stadium and downtown |
| **Weekly snapshots** | Google Places API (New), automated with GitHub Actions | Review counts every Monday, building a time series to measure how game weeks and breaks actually change demand |

Full column-by-column documentation is in the **[data dictionary](docs/data_dictionary.md)**.

## What I found so far

The average rating is 4.17, which sounds high until you realize Google ratings are inflated everywhere. More interesting things:

- 32 restaurants are open past midnight, but the options are pretty uneven by category
- There are no upscale ($$$$) restaurants in State College at all. It's entirely $ to $$
- The halal scene is genuinely good and underrecognized. Fatema's Kitchen, Mosul Grill, Fatoum Bistro all have strong ratings with relatively few reviews
- Budget and mid-range restaurants have nearly identical average ratings. Paying more does not get you better food here

## Measuring the calendar effect

Ratings are lifetime averages, so a game day will never move them. Instead, the project tracks **new reviews per week** as a stand-in for foot traffic. Snapshots started in October 2026, so by spring the data will cover home games, Thanksgiving break, finals and winter break. That's enough to test whether the crowd-level assumptions in the calendar hold up.

The weekly job has a built-in cost guardrail: it stays under Google's free monthly allowance and stops itself before going over.

## Project structure

```
state-college-food/
├── scripts/
│   ├── config.py                     shared paths + API key from environment
│   ├── fetch_restaurants.py          Google Places pull
│   ├── fetch_details.py
│   ├── fetch_reddit.py               Reddit pull
│   ├── clean_data.py
│   ├── tag_cuisines.py               keyword cuisine taxonomy
│   ├── analyze.py
│   ├── analyze_reddit.py
│   ├── build_hours_and_locations.py  hours + walking distance tables
│   ├── build_calendar.py             daily Penn State calendar
│   └── snapshot_places.py            weekly snapshot (run by GitHub Actions)
├── data/
│   ├── raw/                          API responses
│   ├── reference/                    hand-curated Penn State events, with sources
│   ├── clean/                        analysis-ready tables
│   └── snapshots/                    one file per weekly snapshot
├── docs/data_dictionary.md
├── .github/workflows/weekly-snapshot.yml
└── app.py                            original Streamlit dashboard (to be retired)
```

## Run it locally

```bash
git clone https://github.com/MedhaDev/state-college-food.git
cd state-college-food
pip install -r requirements.txt

# Rebuild the calendar and hours/distance tables (no API key needed)
python scripts/build_calendar.py
python scripts/build_hours_and_locations.py

# Anything that calls Google needs a key in your environment, never in the code
export GOOGLE_PLACES_API_KEY=your-key
python scripts/snapshot_places.py --dry-run   # shows what it would do, no calls
```

## Methodology notes

**Cuisine classification** matches keywords in restaurant names against a priority-ordered map, so more specific terms like "penn kebab" match before a generic "kebab". Anything that doesn't match gets flagged as "Other" for review.

**Hidden gems** are rated 4.3 or higher with fewer than 150 reviews: high quality relative to how discoverable the place is.

**Reddit mentions** use substring matching of restaurant names against post titles and text. It's not perfect, but it captures genuine word-of-mouth pretty well.

**Crowd levels** are a rule-based estimate (breaks = very quiet, home games = packed, etc.), documented in the data dictionary and meant to be checked against the snapshot data.

**Walking times** are straight-line distance × 1.3 at 5 km/h. That's an approximation, not routed directions.

## Roadmap

- [x] Clean up pipeline: portable paths, API key out of the code
- [x] Penn State 2026–27 calendar dataset with sources
- [x] Opening-hours and walking-distance tables
- [x] Automated weekly snapshots within the free tier
- [ ] Quarto website: case-study article plus an interactive "plan your day" page
- [ ] AI dining guide (Gemini Gem) grounded in this data, with a written evaluation of its answers
- [ ] Spring 2027: analysis of how the calendar actually moves demand
