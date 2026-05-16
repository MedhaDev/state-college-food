# Happy Valley Eats

A data project about the State College restaurant scene. Built because I wanted to actually understand what's good around here, not just scroll Yelp.

**Live dashboard: [state-college-food.streamlit.app](https://state-college-food.streamlit.app)**

## What it does

I pulled data on 145+ restaurants using the Google Places API across five search areas in State College, cleaned and structured it, built a custom classification system for cuisine types, and cross-referenced Reddit posts from r/StateCollege and r/PennStateUniversity to see which spots people actually talk about. Everything feeds into a Streamlit dashboard.

## What I found

The average rating is 4.17, which sounds high until you realize Google ratings are inflated everywhere. More interesting things:

- 32 restaurants are open past midnight, but the options are pretty uneven by category
- There are no upscale ($$$$) restaurants in State College at all. It's entirely $ to $$
- The halal scene is genuinely good and underrecognized. Fatema's Kitchen, Mosul Grill, Fatoum Bistro all have strong ratings with relatively few reviews
- Budget and mid-range restaurants have nearly identical average ratings. Paying more does not get you better food here

## Dashboard

Six tabs, all connected to a global sidebar filter:

| Tab | What it covers |
|---|---|
| Overview | Category breakdown, rating spread, price distribution, price vs. quality |
| Find a Spot | Filter by vibe, cuisine, price, hours. Includes a map |
| Rankings | Top rated spots, hidden gems, best value |
| Drinks and Nightlife | Bars, pubs, coffee shops, clubs |
| Desserts and Boba | Ice cream, boba, bakeries, late night snacks |
| Late Night | What is actually open after midnight |

## Stack

| | |
|---|---|
| Data collection | Google Places API, Reddit API, Python requests |
| Cleaning | pandas, csv, json |
| Classification | Custom keyword taxonomy (27 cuisine types, 5 categories) |
| Dashboard | Streamlit, Plotly |
| Deployment | Streamlit Cloud |

## Project structure

```
state-college-food/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── scripts/
│   ├── fetch_restaurants.py
│   ├── fetch_details.py
│   ├── clean_data.py
│   ├── tag_cuisines.py
│   ├── analyze.py
│   ├── fetch_reddit.py
│   └── analyze_reddit.py
└── data/
    └── clean/
        ├── restaurants_tagged.csv
        └── reddit_mentions.csv
```

## Run it locally

```bash
git clone https://github.com/MedhaDev/state-college-food.git
cd state-college-food
pip install -r requirements.txt
streamlit run app.py
```

## A few methodology notes

Classification works by matching keywords in restaurant names against a priority-ordered map, so more specific terms like "penn kebab" match before a generic "kebab". Anything that doesn't match gets flagged as "Other" for review.

Hidden gems are defined as rating >= 4.3 with fewer than 150 reviews. The idea is high quality relative to how discoverable the place is.

Reddit analysis is simple substring matching of restaurant names against post titles and body text. It's not perfect but it captures genuine word-of-mouth pretty well.

## What's next

- Penn State academic calendar overlay to see if game days affect ratings
- PA health inspection data
- Tableau version of the dashboard
- Automated refresh with GitHub Actions
