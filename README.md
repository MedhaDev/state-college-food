# Table for 100,000

**Where to eat in State College, planned around the Penn State calendar.**

When 100,000+ fans fill Beaver Stadium, downtown State College changes completely. When students leave for winter break, it empties out. This project combines restaurant data with the Penn State academic and football calendar so visiting families, students and locals can decide *when* and *where* to eat, not just what's rated well.

**Read it: [medhadev.github.io/state-college-food](https://medhadev.github.io/state-college-food/)**

The site is styled like an old reference book and has five pages:

| Page | What it does |
|---|---|
| **Article** | The case study: the question, the data, findings, planning by occasion, methods and limitations |
| **Plan a meal** | Pick a date and time; see the expected crowd and every restaurant open then (runs in the browser) |
| **The calendar** | Every day of 2026–27 shaded by expected crowd, plus all key dates with sources |
| **Directory** | Every restaurant by cuisine, classifieds-style |
| **Data & methods** | Downloads and the full data dictionary |

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

Full column-by-column documentation is in the **[data dictionary](docs/data_dictionary.md)**.

## What I found

- **Half the town eats within ten minutes of College & Allen.** 71 of 139 open restaurants are downtown, holding 49% of all Google reviews. On game days, nearly all visitor demand lands on that one grid.
- **Paying more barely buys better food.** There are no $$$ restaurants at all; $$ places average 4.15 stars against 4.03 for $ places.
- **The best-kept secret is Middle Eastern food.** The seven Middle Eastern and halal restaurants average 4.69 stars against 4.12 for the town, and four of them have fewer than 150 reviews.
- **Sunday mornings are thin.** Only 36 open restaurants serve at 10 a.m. on a Sunday, the morning after every home game.
- **Late night is real.** 33 restaurants serve past midnight on Saturdays.

## Cost: $0

Everything runs on data already collected (Google Places, March 2026) plus free public calendars. No API keys or paid services are needed to rebuild the tables or the site.

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
│   └── build_calendar.py             daily Penn State calendar
├── data/
│   ├── raw/                          API responses
│   ├── reference/                    hand-curated Penn State events, with sources
│   └── clean/                        analysis-ready tables
├── site/                             the Quarto website (one .qmd file per page)
├── docs/data_dictionary.md
└── .github/workflows/publish-site.yml  rebuilds the site on every push to main
```

## Run it locally

```bash
git clone https://github.com/MedhaDev/state-college-food.git
cd state-college-food
pip install -r requirements.txt

# Rebuild the calendar and hours/distance tables (no API key needed)
python scripts/build_calendar.py
python scripts/build_hours_and_locations.py

# Preview the website (needs Quarto: https://quarto.org)
quarto preview site
```

To edit the site's text, change the `.qmd` files in `site/`. They're plain text with headings and paragraphs, and the site rebuilds itself when changes reach `main`.

## Methodology notes

**Cuisine classification** matches keywords in restaurant names against a priority-ordered map, so more specific terms like "penn kebab" match before a generic "kebab". A short list of hand-checked overrides covers names that don't reveal their cuisine.

**Hidden gems** are rated 4.5 or higher with 20–150 reviews: high quality relative to how discoverable the place is, with enough reviews to trust.

**Reddit mentions** use substring matching of restaurant names against post titles and text. Mentions turned out to be rare (no place appears in more than two posts), so Reddit is a qualitative check, not a ranking signal.

**Crowd levels** are a rule-based estimate (breaks = very quiet, home games = packed, etc.), documented in the data dictionary. They're assumptions, stated openly so they can be tested later.

**Walking times** are straight-line distance × 1.3 at 5 km/h. That's an approximation, not routed directions.

## Roadmap

- [x] Clean up pipeline: portable paths, API key out of the code
- [x] Penn State 2026–27 calendar dataset with sources
- [x] Opening-hours and walking-distance tables
- [x] Quarto website: case-study article, interactive planner, calendar, directory, data page
- [ ] AI dining guide (Gemini Gem) grounded in this data, with a written evaluation of its answers
- [ ] Future idea: measure how the calendar actually moves demand (would need repeated data pulls over a semester)
