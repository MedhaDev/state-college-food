# State College Food Intelligence

> What 145 restaurants, real reviews, and actual data say about eating in Happy Valley.

A end-to-end data analytics project built to explore the restaurant ecosystem 
in State College, PA - combining Google Places API data, cuisine analysis, and 
an interactive Streamlit dashboard.

---

## What This Project Does

- Scrapes **145 restaurants** across State College using the Google Places API
- Cleans, structures, and tags cuisine types across 27 categories
- Analyzes ratings, review counts, pricing, and operating hours
- Surfaces **hidden gems**, **late night options**, and **best value** spots
- Presents findings in an interactive **5-tab Streamlit dashboard**

---

## Key Findings

- Average restaurant rating in State College: **4.12 ⭐**
- **40 restaurants** open past midnight
- **63 budget-friendly** options (price level 1)
- The halal food scene is thriving and underrecognized - 6 strong options
  across Penn Kebab, Fatema's Kitchen, Mosul Grill, Fatoum Bistro and more
- Top rated with 50+ reviews: **Sowers Harvest Café (4.9)** and 
  **Allen Street Pizza (4.8)**
- No upscale (price level 3-4) restaurants exist - State College is 
  entirely budget to mid-range

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Collection | Google Places API, Python `requests` |
| Data Cleaning | Python `csv`, `json`, `pandas` |
| Analysis | Python, custom scoring logic |
| Dashboard | Streamlit, Plotly |
| Version Control | Git, GitHub |

---

## Project Structure
```
state-college-food/
├── app.py                        # Streamlit dashboard
├── scripts/
│   ├── fetch_restaurants.py      # Google Places nearby search
│   ├── fetch_details.py          # Detailed info per restaurant
│   ├── clean_data.py             # Raw JSON → structured CSV
│   ├── tag_cuisines.py           # Cuisine classification
│   ├── analyze.py                # Core analysis & findings
│   ├── fetch_reddit.py           # Reddit data collection
│   └── analyze_reddit.py        # Reddit mention analysis
├── data/
│   ├── raw/                      # Raw API responses
│   └── clean/                    # Processed, analysis-ready CSVs
└── .env                          # API keys (not committed)
```

---

## How to Run

**1. Clone the repo**
```bash
git clone https://github.com/MedhaDev/state-college-food.git
cd state-college-food
```

**2. Install dependencies**
```bash
pip install requests pandas plotly streamlit
```

**3. Add your Google Places API key**
```bash
echo 'GOOGLE_API_KEY="your_key_here"' > .env
```

**4. Run the dashboard**
```bash
streamlit run app.py
```

---

## Roadmap

- [ ] Reddit integration (r/StateCollege + r/PennStateUniversity) 
      for word-of-mouth analysis
- [ ] PA health inspection data layer
- [ ] Penn State academic calendar overlay 
      (game days, move-in, THON effects on ratings)
- [ ] Deploy to Streamlit Cloud
