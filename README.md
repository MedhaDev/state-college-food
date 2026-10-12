# Table for 100,000

When I moved to State College, I was looking for places to eat like everyone does. But I quickly realized *where* was only half the question. The other half was *when*.

This town runs on the Penn State calendar. On a home football Saturday, over 100,000 people show up and downtown is packed for hours. Over winter break, the students leave and places keep odd hours. Nobody tells you this when you're new. When you've just arrived and don't have a community yet, it's hard to keep up with local news, events and the unwritten stuff: what the rush hours are, which spots locals actually like, and when to stay away from College Ave.

So I did a massive internet search: restaurant data, Reddit threads, the academic calendar, the football schedule, THON, Arts Fest. Then I put it all in one place. It's a fun little personal project, built out of curiosity.

**→ [medhadev.github.io/state-college-food](https://medhadev.github.io/state-college-food/)**

## What's on my website

- **Article:** what I found, and how to plan around game days, breaks and graduation
- **Plan a meal:** pick a date and time, see how busy town will be and what's open
- **The calendar:** every day of the 2026–27 school year, shaded by how crowded it'll be
- **Directory:** every restaurant by cuisine, no ads, no algorithm
- **Data & methods:** the data and how it fits together

## How I built it

- Pulled 145 restaurants from the Google Places API, plus posts from r/StateCollege and r/PennStateUniversity
- Cleaned it with pandas and tagged cuisines with my own keyword taxonomy
- Built the 2026–27 calendar by hand from official Penn State sources and gave each day a crowd level from 1 to 5 (my best guess, not a measurement)
- Made the site with Quarto; GitHub Actions rebuilds it whenever I change something
- Total cost: $0

Column-by-column details are in the [data dictionary](docs/data_dictionary.md).

## Run it yourself

```bash
git clone https://github.com/MedhaDev/state-college-food.git
cd state-college-food
pip install -r requirements.txt
python scripts/build_calendar.py
python scripts/build_hours_and_locations.py
quarto preview site
```
