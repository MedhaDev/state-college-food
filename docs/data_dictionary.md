# Data Dictionary

Every dataset in this project: what one row means, where it comes from, how often it changes, and what each column holds.

## Pipeline at a glance

| Step | Script | Reads | Writes | Needs API key |
|---|---|---|---|---|
| 1 | `fetch_restaurants.py` | Google Places API | `raw/restaurants_raw.json`, `raw/restaurants_detailed.json` | Yes |
| 2 | `fetch_reddit.py` | Reddit search | `raw/reddit_posts.json` | No |
| 3 | `clean_data.py` | `raw/restaurants_detailed.json` | `clean/restaurants_clean.csv` | No |
| 4 | `tag_cuisines.py` | `clean/restaurants_clean.csv` | `clean/restaurants_tagged.csv` | No |
| 5 | `analyze_reddit.py` | Reddit posts + tagged restaurants | `clean/reddit_mentions.csv` | No |
| 6 | `build_hours_and_locations.py` | `raw/restaurants_detailed.json` | `clean/restaurant_hours.csv`, `clean/restaurant_locations.csv` | No |
| 7 | `build_calendar.py` | `reference/psu_events_2026_27.csv` | `clean/calendar_days.csv` | No |

Restaurant tables join on `place_id` (Google's ID for a place). The calendar table joins on `date`.

Only step 1 needs a Google API key, and it has already been run. Everything else is free and offline.

---

## Reference data (collected from official sources with an AI web scraper)

### `data/reference/psu_events_2026_27.csv`

**One row = one event or date range** that changes how busy State College is. Every row cites its official source.

| Column | Meaning |
|---|---|
| `event_id` | Short unique ID, e.g. `fb26-usc` |
| `event_name` | Human-readable name |
| `event_type` | `academic`, `move_in`, `football_home`, `football_away`, `holiday`, `break`, `finals`, `commencement`, `campus_event`, `community_event`, `summer` |
| `start_date`, `end_date` | Inclusive date range (YYYY-MM-DD) |
| `location` | Where it happens |
| `expected_crowd` | 1–5 crowd estimate for the event (see scale below) |
| `notes` | Kickoff times, results, caveats |
| `source_url` | Where the date came from |

**Sources:** [Penn State Registrar 2026–27 calendar](https://www.registrar.psu.edu/academic-calendars/2026-27.cfm), [Penn State Athletics 2026 football schedule](https://gopsusports.com/sports/football/schedule), [LiveOn move-in dates](https://liveon.psu.edu/university-park/news/university-park-important-dates-2026-27-academic-year), [THON 2027](https://www.psu.edu/news/campus-life/story/thon-weekend-2027-be-held-feb-19-21), [Arts Fest](https://arts-festival.com/plan-your-visit/). Checked October 2026.

**Update:** once a year, when the next academic year and football schedule are published. Not yet included: 2027 Blue-White Game (date not announced).

---

## Clean data

### `data/clean/calendar_days.csv`

**One row = one day**, from Aug 15, 2026 to Aug 14, 2027 (365 rows). Built by `build_calendar.py`.

| Column | Meaning |
|---|---|
| `date` | The day |
| `day_name`, `is_weekend` | Monday…Sunday; True on Saturday and Sunday |
| `academic_term` | `Fall 2026`, `Winter break`, `Spring 2027`, `Summer 2026/2027` |
| `term_phase` | `move_in`, `in_session`, `finals`, `commencement`, `break`, `summer` |
| `classes_in_session` | True on weekdays with classes (not holidays or breaks) |
| `is_home_game` | True on home football game days |
| `events` | All events covering that day, separated by `;` |
| `expected_crowd` | 1–5 crowd estimate (below) |
| `crowd_label` | Very quiet, Quiet, Normal, Busy, Packed |
| `crowd_reason` | What set the level |

**Crowd scale (rule-based estimate, not measured yet):**

| Level | Label | Rule |
|---|---|---|
| 1 | Very quiet | Thanksgiving, winter and spring breaks |
| 2 | Quiet | Summer |
| 3 | Normal | Regular semester days and finals |
| 4 | Busy | Move-in, fall commencement, THON, the Friday before a home game |
| 5 | Packed | Home football games, spring commencement, Arts Fest |

Each day starts from its term phase's level. Big events can raise it but never lower it. These are stated assumptions, not measurements.

### `data/clean/restaurant_hours.csv`

**One row = one opening window for one restaurant on one day.** A place that closes for an afternoon break has two rows for that day. 136 of the 145 restaurants have hours; 9 have none listed on Google.

| Column | Meaning |
|---|---|
| `place_id`, `name` | Restaurant |
| `day_of_week` | Day the window **opens** |
| `opens`, `closes` | Clock times (HH:MM, 24-hour) |
| `open_minute`, `close_minute` | Minutes after midnight of the opening day. `close_minute` goes past 1440 if the place closes after midnight (Fri 5 PM–2 AM = 1020 → 1560), which makes "is it open at 11 PM?" a simple comparison |
| `closes_after_midnight` | True if the window runs past midnight |
| `open_24_hours` | True for 24-hour places (Sheetz, McDonald's) |

**Data date:** these are regular weekly hours from the March 2026 data pull. Holiday hours are not included.

### `data/clean/restaurant_locations.csv`

**One row = one restaurant.**

| Column | Meaning |
|---|---|
| `place_id`, `name`, `lat`, `lng` | Restaurant and coordinates |
| `walk_km_to_stadium`, `walk_min_to_stadium` | Estimated walk to Beaver Stadium |
| `walk_km_to_downtown`, `walk_min_to_downtown` | Estimated walk to College Ave & Allen St |
| `area` | `Downtown` (≤10 min from downtown), `Near the stadium` (≤20 min from the stadium), `Walkable from downtown` (≤25 min), `Drive or bus` |
| `walkable_to_stadium` | True if ≤30 min walk to the stadium |

**Method:** straight-line distance × 1.3 (streets aren't straight) at 5 km/h. This is an approximation, not routed directions.

### `data/clean/restaurants_clean.csv` / `restaurants_tagged.csv`

**One row = one restaurant** (145) from the Google Places pull in March 2026.

| Column | Meaning |
|---|---|
| `place_id`, `name`, `address`, `lat`, `lng`, `phone`, `website` | Basics |
| `rating` | Google star rating (lifetime average, 1–5) |
| `review_count` | Total Google reviews at pull time |
| `price_level` | 1 = $, 2 = $$, 3 = $$$ (blank if unknown) |
| `status` | `OPERATIONAL` (139) or `CLOSED_TEMPORARILY` (6) |
| `cuisine_type` | Cuisine label (keyword taxonomy in `tag_cuisines.py`) |
| `category` | Food, Drinks, Dessert & Snacks, Fast Food or Campus Dining (`restaurants_tagged.csv` only) |
| `is_late_night` | True if it closes between midnight and 6 AM on any day |
| `opens_sunday` | True if open on Sundays |
| `avg_review_rating` | Average of the 5 most recent reviews Google returned |
| `review_texts` | Those reviews, first 200 characters each, separated by `|` |

### `data/clean/reddit_mentions.csv`

**One row = one restaurant**, with how often it's named in r/StateCollege and r/PennStateUniversity posts.

| Column | Meaning |
|---|---|
| `name`, `cuisine_type`, `rating`, `review_count`, `price_level` | From the restaurant table |
| `reddit_mentions` | Number of posts naming the restaurant |
| `reddit_score` | Sum of those posts' upvotes |
| `subreddits` | Where it was mentioned |
| `sample_post` | Title of one matching post |

---

## Known data quality notes

- **Cuisine tags are name-based.** `tag_cuisines.py` matches keywords in restaurant names, with a short list of hand-checked overrides. A place whose name doesn't reveal its cuisine falls back to Google's type tag.
- **Reviews are thin:** Google returns only 5 reviews per place, so `avg_review_rating` and `review_texts` are a small sample.
- **Ratings barely move:** `rating` is a lifetime average, so calendar effects show up in review *counts*, not ratings.
- **Reddit coverage is sparse:** 139 posts over 15 years. This is useful for word-of-mouth, too thin for time trends.
- **Static data is from March 2026.** Some restaurants may have closed or changed hours since.
