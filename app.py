import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── CONFIG ────────────────────────────────────────────────
st.set_page_config(
    page_title="Happy Valley Eats",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

DATA_PATH = "data/clean/restaurants_tagged.csv"

# ── PALETTE ───────────────────────────────────────────────
# Background
BG       = "#F0EDE8"      # warm light grey — readable base
WHITE    = "#FFFFFF"
# Text
INK      = "#111827"      # near-black — high contrast on any background
INK2     = "#374151"      # secondary text
MUTED    = "#6B7280"

# Brand colors
BLUE     = "#1B3A6B"      # primary / sidebar
CORAL    = "#C94C3A"      # accent warm
TEAL     = "#1D7A6A"      # accent cool
GOLD     = "#B8860B"      # accent yellow-gold (dark enough to read)
PURPLE   = "#5C3F8F"      # accent purple

# Category palette — distinct, high contrast, colorblind-safe-ish
CAT_COLORS = {
    "Food":             BLUE,
    "Drinks":           TEAL,
    "Dessert & Snacks": CORAL,
    "Fast Food":        MUTED,
    "Campus Dining":    GOLD,
}

# Sequential palette for cuisine-level charts
MULTI = [BLUE, CORAL, TEAL, GOLD, PURPLE,
         "#2D6A9F", "#A0522D", "#1A6B45", "#8B2252", "#4A7A6B",
         "#6B4E2A", "#2A5F8F", "#8B4513", "#1E5F5F", "#6B3A6B"]

SWEET_PAL = [CORAL, "#E8907A", GOLD, "#A8D8C8", PURPLE]

# ── CSS ───────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {INK};
}}
.stApp {{ background-color: {BG}; }}
.block-container {{ padding-top: 1.8rem; max-width: 1440px; }}

/* ── Hide Streamlit Cloud chrome ── */
header[data-testid="stHeader"] {{
    display: none !important;
}}
[data-testid="manage-app-button"],
.st-emotion-cache-h5rgaw,
footer,
#MainMenu {{
    display: none !important;
    visibility: hidden !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {BLUE};
    border-right: none;
}}
section[data-testid="stSidebar"] > div {{
    padding-top: 1.5rem;
}}
/* All sidebar text light */
section[data-testid="stSidebar"] * {{ color: #E8EDF5 !important; }}
/* Sidebar labels */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * {{
    color: #93B8E0 !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.12);
}}
section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] span {{
    color: #93B8E0 !important;
    font-size: 0.65rem !important;
}}
/* Sidebar selectbox — lighter navy bg, light text */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="select"] > div > div {{
    background-color: rgba(255,255,255,0.1) !important;
    border-color: rgba(255,255,255,0.2) !important;
    border-radius: 6px !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] div[data-baseweb="select"] div {{
    color: #E8EDF5 !important;
    background-color: transparent !important;
}}
/* Sidebar dropdown option list */
section[data-testid="stSidebar"] div[data-baseweb="popover"],
section[data-testid="stSidebar"] ul[data-baseweb="menu"] {{
    background-color: #1B3A6B !important;
}}
section[data-testid="stSidebar"] ul[data-baseweb="menu"] li {{
    color: #E8EDF5 !important;
}}
section[data-testid="stSidebar"] ul[data-baseweb="menu"] li:hover {{
    background-color: rgba(255,255,255,0.1) !important;
}}
/* Sidebar multiselect tags */
section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
    background-color: rgba(255,255,255,0.15) !important;
    color: #E8EDF5 !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}}
section[data-testid="stSidebar"] span[data-baseweb="tag"] span {{
    color: #E8EDF5 !important;
}}
/* Sidebar checkbox */
section[data-testid="stSidebar"] .stCheckbox label span {{
    color: #E8EDF5 !important;
}}

/* ── Typography ── */
h1, h2, h3 {{
    font-family: 'Libre Baskerville', Georgia, serif !important;
    color: {INK} !important;
    letter-spacing: -0.02em;
}}

/* ── KPI cards ── */
.kpi-row {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 10px;
    margin-bottom: 1.4rem;
}}
.kpi {{
    background: {WHITE};
    border-radius: 6px;
    padding: 14px 16px 12px;
    border-left: 4px solid {BLUE};
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}
.kpi.coral  {{ border-left-color: {CORAL}; }}
.kpi.teal   {{ border-left-color: {TEAL};  }}
.kpi.gold   {{ border-left-color: {GOLD};  }}
.kpi.purple {{ border-left-color: {PURPLE};}}
.kpi .val {{
    font-family: 'Libre Baskerville', serif;
    font-size: 1.65rem;
    font-weight: 700;
    color: {INK};
    line-height: 1;
    letter-spacing: -0.03em;
}}
.kpi .lbl {{
    font-size: 0.67rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {MUTED};
    margin-top: 5px;
}}
.kpi .sub {{
    font-size: 0.72rem;
    color: {INK2};
    margin-top: 2px;
}}

/* ── Section labels ── */
.overline {{
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    color: {CORAL};
    margin-bottom: 2px;
}}
.section-head {{
    font-family: 'Libre Baskerville', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: {INK};
    margin-bottom: 0.9rem;
    padding-bottom: 6px;
    border-bottom: 2px solid {CORAL};
    display: inline-block;
}}
.chart-title {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: {INK2} !important;
    margin-bottom: 2px;
}}
.chart-sub {{
    font-size: 0.72rem;
    color: {MUTED} !important;
    margin-bottom: 8px;
}}

/* ── Cards ── */
.r-card {{
    background: {WHITE};
    border-radius: 6px;
    padding: 11px 15px;
    margin-bottom: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-left: 3px solid #D1D5DB;
    display: flex;
    align-items: center;
    gap: 12px;
}}
.r-card:hover {{ border-left-color: {CORAL}; }}
.r-rank {{
    font-family: 'Libre Baskerville', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #D1D5DB;
    min-width: 28px;
}}
.r-name {{
    font-weight: 600;
    font-size: 0.88rem;
    color: {INK};
}}
.r-meta {{
    font-size: 0.74rem;
    color: {MUTED};
    margin-top: 1px;
}}
.badge {{
    display: inline-block;
    border-radius: 3px;
    padding: 1px 7px;
    font-size: 0.64rem;
    font-weight: 700;
    margin-right: 3px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    background: #E8EDF5;
    color: {BLUE};
}}
.badge-red   {{ background: #FDECEA; color: {CORAL}; }}
.badge-green {{ background: #E6F4F0; color: {TEAL};  }}
.badge-gold  {{ background: #FDF6E3; color: {GOLD};  }}

/* ── Rating pill ── */
.rating {{
    font-family: 'Libre Baskerville', serif;
    font-size: 0.88rem;
    font-weight: 700;
    color: {BLUE};
    background: #E8EDF5;
    border-radius: 4px;
    padding: 2px 8px;
    white-space: nowrap;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    border-bottom: 2px solid #D1D5DB;
    background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    padding: 10px 20px;
    color: {MUTED};
    border-radius: 0;
    background: transparent;
}}
.stTabs [aria-selected="true"] {{
    color: {INK} !important;
    border-bottom: 3px solid {CORAL} !important;
    background: transparent !important;
}}

/* ── Divider ── */
hr {{ border-color: #D1D5DB; }}

/* ── Expander ── */
details > summary,
details > summary p,
details > summary span,
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
.streamlit-expanderHeader,
.streamlit-expanderHeader p {{
    color: {INK} !important;
    background-color: #E8E4DE !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
}}
[data-testid="stExpander"] > div > div {{
    background-color: #E8E4DE !important;
}}
/* Force ALL text in main content dark */
div[data-testid="stMain"] p,
div[data-testid="stMain"] span,
div[data-testid="stMain"] li,
div[data-testid="stMain"] a,
div[data-testid="stMain"] .stMarkdown p,
div[data-testid="stMain"] [data-testid="stMetricValue"],
div[data-testid="stMain"] [data-testid="stMetricLabel"],
div[data-testid="stMain"] [data-testid="stMetricDelta"] {{
    color: {INK} !important;
}}
div[data-testid="stMain"] [data-testid="stMetricValue"] {{
    font-family: 'Libre Baskerville', serif !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    color: {BLUE} !important;
}}

/* ══ NUCLEAR: force ALL text dark in main content ══ */
div[data-testid="stMain"] * {{
    color: {INK} !important;
}}
/* Restore sidebar white text */
section[data-testid="stSidebar"] * {{
    color: #E8EDF5 !important;
}}
section[data-testid="stSidebar"] label {{
    color: #93B8E0 !important;
}}
/* Widgets: beige background, dark text */
div[data-testid="stMain"] div[data-baseweb="select"] > div,
div[data-testid="stMain"] div[data-baseweb="select"] > div > div {{
    background-color: #E8E4DE !important;
    border-color: #C5BFB7 !important;
}}
div[data-baseweb="popover"],
div[data-baseweb="popover"] * {{
    background-color: #E8E4DE !important;
}}
ul[data-baseweb="menu"] li:hover {{
    background-color: #D8D3CC !important;
}}
/* Multiselect tags */
span[data-baseweb="tag"] {{
    background-color: #D4D0E8 !important;
}}
/* Sliders: keep accent color on track */
div[data-testid="stMain"] [data-testid="stSlider"] [role="slider"] {{
    background-color: {CORAL} !important;
}}
/* Restore intentional accent colors */
div[data-testid="stMain"] .overline {{ color: {CORAL} !important; }}
div[data-testid="stMain"] .section-head {{ color: {INK} !important; }}
div[data-testid="stMain"] .chart-sub {{ color: {MUTED} !important; }}
div[data-testid="stMain"] .chart-title {{ color: {INK2} !important; }}
div[data-testid="stMain"] .r-rank {{ color: #B0B7C3 !important; }}
div[data-testid="stMain"] .badge {{ color: {BLUE} !important; }}
div[data-testid="stMain"] .badge-red {{ color: {CORAL} !important; }}
div[data-testid="stMain"] .badge-green {{ color: {TEAL} !important; }}

/* ── Catch-all for remaining white text issues ── */
/* Selectbox / dropdown labels and values */
[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] div,
[data-testid="stSelectbox"] span,
[data-testid="stMultiSelect"] label,
[data-testid="stMultiSelect"] div,
[data-testid="stMultiSelect"] span,
[data-testid="stSlider"] label,
[data-testid="stSlider"] div,
[data-testid="stSlider"] span,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stMarkdownContainer"] *,
[data-testid="stText"] * {{
    color: {INK} !important;
}}
/* Dropdown container backgrounds */
[data-testid="stSelectbox"] > div > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
    background-color: #E8E4DE !important;
    border-color: #C5BFB7 !important;
}}
/* Plotly legend text — force dark via SVG */
.js-plotly-plot .plotly .legend text {{
    fill: {INK} !important;
}}
.js-plotly-plot .plotly .g-gtitle text,
.js-plotly-plot .plotly .xtitle,
.js-plotly-plot .plotly .ytitle,
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text {{
    fill: {INK2} !important;
}}
</style>
""", unsafe_allow_html=True)


# ── CLASSIFICATION ────────────────────────────────────────
KEYWORD_MAP = {
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

CATEGORY_MAP = {
    "Bar & Pub":"Drinks","Nightlife":"Drinks",
    "Coffee & Tea":"Drinks","Cafe":"Drinks",
    "Boba & Tea":"Dessert & Snacks","Ice Cream":"Dessert & Snacks",
    "Bakery":"Dessert & Snacks","Late Night Snacks":"Dessert & Snacks",
    "Fast Food":"Fast Food","Campus Dining":"Campus Dining",
}

PRICE_LABEL = {1: "$", 2: "$$", 3: "$$$"}


def classify(name, existing):
    n = str(name).lower()
    for kw, cuisine in KEYWORD_MAP.items():
        if kw in n:
            return cuisine
    if str(existing) not in ["Restaurant","Delivery","Takeout","Bar",""]:
        return existing
    return "Other"


# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data(ttl=0)
def load_data():
    df = pd.read_csv(DATA_PATH)
    for col in ["rating","review_count","price_level","lat","lng"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df[df["status"] == "OPERATIONAL"].copy()
    df["cuisine_type"]  = df.apply(lambda r: classify(r["name"], r.get("cuisine_type","")), axis=1)
    df["category"]      = df["cuisine_type"].map(CATEGORY_MAP).fillna("Food")
    df["is_late_night"] = df["is_late_night"].astype(str).str.strip().eq("True")
    df["opens_sunday"]  = df["opens_sunday"].astype(str).str.strip().eq("True")
    df["price_str"]     = df["price_level"].map(PRICE_LABEL).fillna("?")
    return df

df = load_data()


# ── CHART DEFAULTS ────────────────────────────────────────
CL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_family="IBM Plex Sans",
    font_color=INK,
    margin=dict(t=16, b=8, l=8, r=8),
    title_text="",
)

GRID = dict(gridcolor="#E5E7EB", gridwidth=0.8, zeroline=False)
NO_GRID = dict(showgrid=False, zeroline=False)


def fmt_axis(fig, x_grid=True, y_grid=True, tick_size=10):
    fig.update_xaxes(**(GRID if x_grid else NO_GRID), tickfont_size=tick_size,
                     tickfont_color=INK2, title_font_size=10, title_font_color=MUTED)
    fig.update_yaxes(**(GRID if y_grid else NO_GRID), tickfont_size=tick_size,
                     tickfont_color=INK2, title_font_size=10, title_font_color=MUTED)
    return fig


# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding: 0 0 18px;">
      <div style="font-family:'Libre Baskerville',serif;font-size:1.25rem;
                  font-weight:700;color:#FFFFFF;line-height:1.15;
                  letter-spacing:-0.02em;">
        Happy Valley<br>Eats
      </div>
      <div style="font-size:0.65rem;font-weight:700;color:#93B8E0;
                  margin-top:5px;text-transform:uppercase;letter-spacing:0.14em;">
        State College · 145 Restaurants
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div style="font-size:0.65rem;font-weight:700;'
                'text-transform:uppercase;letter-spacing:0.12em;'
                f'color:#93B8E0;margin-bottom:6px;">Filters</div>', unsafe_allow_html=True)

    all_cats = ["All"] + sorted(df["category"].dropna().unique())
    sel_cat  = st.selectbox("Category", all_cats)

    pool = (df[df["category"]==sel_cat]["cuisine_type"].dropna().unique()
            if sel_cat != "All" else df["cuisine_type"].dropna().unique())
    sel_cuisines = st.multiselect("Cuisine type", sorted(pool), placeholder="All cuisines")

    st.divider()
    min_rating = st.slider("Min rating", 1.0, 5.0, 3.5, 0.1)
    price_opts = st.multiselect("Price", [1,2,3], default=[1,2,3],
                                format_func=lambda x: PRICE_LABEL[x])
    st.divider()
    late_only   = st.checkbox("Late night only")
    sunday_only = st.checkbox("Open Sundays only")
    st.divider()
    st.markdown(f'<div style="font-size:0.66rem;color:#93B8E0;">'
                f'Source: Google Places API &middot; 2025</div>', unsafe_allow_html=True)


# ── APPLY FILTERS ─────────────────────────────────────────
def apply_filters(data):
    f = data.copy()
    if sel_cat != "All":       f = f[f["category"]==sel_cat]
    if sel_cuisines:           f = f[f["cuisine_type"].isin(sel_cuisines)]
    if price_opts:             f = f[f["price_level"].isin(price_opts)]
    f = f[f["rating"] >= min_rating]
    if late_only:              f = f[f["is_late_night"]]
    if sunday_only:            f = f[f["opens_sunday"]]
    return f

fdf = apply_filters(df)


# ── HEADER ────────────────────────────────────────────────
hc1, hc2 = st.columns([4, 1])
with hc1:
    st.markdown(f"""
    <div style="margin-bottom: 0.25rem;">
      <span style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                   letter-spacing:0.16em;color:{CORAL};">
        A data portrait of State College, PA
      </span>
    </div>
    <div style="font-family:'Libre Baskerville',serif;font-size:2.2rem;
                font-weight:700;color:{INK};line-height:1.1;letter-spacing:-0.03em;">
      Happy Valley Eats
    </div>
    <div style="font-size:0.86rem;color:{INK2};margin-top:7px;">
      What 145 restaurants, real reviews, and actual data say about eating in State College.
      Source: Google Places API &middot; Reddit &middot; 2025
    </div>
    """, unsafe_allow_html=True)
with hc2:
    st.markdown(f"""
    <div style="background:{BLUE};border-radius:6px;padding:16px 18px;
                margin-top:8px;border-left:4px solid {CORAL};">
      <div style="font-family:'Libre Baskerville',serif;font-size:2rem;
                  font-weight:700;color:#FFFFFF;line-height:1;">
        {len(fdf)}
      </div>
      <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.12em;color:#93B8E0;margin-top:4px;">
        Restaurants shown
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

# ── KPI ROW ───────────────────────────────────────────────
avg_r     = fdf["rating"].mean() if not fdf.empty else 0
late_ct   = int(fdf["is_late_night"].sum())
sun_ct    = int(fdf["opens_sunday"].sum())
budget_ct = int((fdf["price_level"]==1).sum())
gem_ct    = int(((fdf["review_count"]<150)&(fdf["rating"]>=4.3)).sum())
top_r     = fdf[fdf["review_count"]>=50]["rating"].max() if not fdf.empty else 0

def kpi_html(val, lbl, sub="", accent=""):
    return (f'<div class="kpi {accent}">'
            f'<div class="val">{val}</div>'
            f'<div class="lbl">{lbl}</div>'
            + (f'<div class="sub">{sub}</div>' if sub else "")
            + '</div>')

st.markdown(f"""
<div class="kpi-row">
  {kpi_html(f"{avg_r:.2f}", "Avg Rating", "out of 5.0")}
  {kpi_html(int(late_ct), "Open Late Night", "past midnight", "coral")}
  {kpi_html(int(sun_ct), "Open Sundays", "confirmed open", "teal")}
  {kpi_html(int(budget_ct), "Budget Options", "price level $", "gold")}
  {kpi_html(int(gem_ct), "Hidden Gems", "high rating, low reviews", "purple")}
  {kpi_html(f"{top_r:.1f}", "Best Rated", "50+ reviews required")}
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ── TABS ──────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "OVERVIEW", "FIND A SPOT", "RANKINGS",
    "DRINKS & NIGHTLIFE", "DESSERTS & BOBA", "LATE NIGHT"
])


# ════════════════════════════════════════════════════════════
# TAB 1  OVERVIEW
# ════════════════════════════════════════════════════════════
with tab1:

    st.markdown(f'<div class="overline">At a glance</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">The State College food scene</div>', unsafe_allow_html=True)

    r1c1, r1c2, r1c3 = st.columns(3)

    with r1c1:
        st.markdown(f'<div class="chart-title">Category mix</div>'
                    f'<div class="chart-sub">{len(fdf)} operational restaurants</div>',
                    unsafe_allow_html=True)
        cat_cnt = fdf["category"].value_counts().reset_index()
        cat_cnt.columns = ["Category","Count"]
        colors = [CAT_COLORS.get(c, MUTED) for c in cat_cnt["Category"]]
        fig = go.Figure(go.Pie(
            labels=cat_cnt["Category"], values=cat_cnt["Count"],
            hole=0.55, marker_colors=colors,
            textinfo="percent+label", textfont=dict(size=11, color=INK),
            insidetextorientation="radial",
            hovertemplate="<b>%{label}</b><br>%{value} restaurants (%{percent})<extra></extra>"
        ))
        fig.add_annotation(text=f"<b>{len(fdf)}</b>",
                           x=0.5, y=0.5, showarrow=False,
                           font=dict(size=18, family="Libre Baskerville", color=INK))
        fig.update_layout(**CL, showlegend=False, height=280)
        st.plotly_chart(fig, use_container_width=True)

    with r1c2:
        st.markdown(f'<div class="chart-title">Rating distribution</div>'
                    f'<div class="chart-sub">Most restaurants cluster 4.0 – 4.5</div>',
                    unsafe_allow_html=True)
        fig2 = px.histogram(fdf.dropna(subset=["rating"]), x="rating",
                            nbins=20, color_discrete_sequence=[BLUE])
        fig2.update_traces(marker_line_color=WHITE, marker_line_width=1)
        fig2.update_layout(**CL, height=280, bargap=0.08,
                           xaxis_title="Rating", yaxis_title="Count")
        fmt_axis(fig2, x_grid=False, y_grid=True)
        # Add mean line
        mean_r = fdf["rating"].mean()
        fig2.add_vline(x=mean_r, line_dash="dash", line_color=CORAL, line_width=1.5)
        fig2.add_annotation(x=mean_r, y=1, yref="paper",
                            text=f"avg {mean_r:.2f}", showarrow=False,
                            font=dict(size=10, color=CORAL),
                            xanchor="left", xshift=6)
        st.plotly_chart(fig2, use_container_width=True)

    with r1c3:
        st.markdown(f'<div class="chart-title">Price breakdown</div>'
                    f'<div class="chart-sub">State College skews budget to mid-range</div>',
                    unsafe_allow_html=True)
        pc = fdf.dropna(subset=["price_level"]).copy()
        pc["price_label"] = pc["price_level"].map({1:"$ Budget",2:"$$ Mid-range",3:"$$$ Upscale"})
        pcnt = pc["price_label"].value_counts().reset_index()
        pcnt.columns = ["Price","Count"]
        fig3 = px.bar(pcnt, x="Price", y="Count",
                      color="Price",
                      color_discrete_map={
                          "$ Budget":TEAL,
                          "$$ Mid-range":BLUE,
                          "$$$ Upscale":CORAL},
                      text="Count")
        fig3.update_traces(textposition="outside",
                           textfont=dict(size=11, color=INK, family="IBM Plex Sans"))
        fig3.update_layout(**CL, height=280, showlegend=False,
                           xaxis_title="", yaxis_title="Restaurants")
        fmt_axis(fig3, x_grid=False, y_grid=True)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    r2c1, r2c2 = st.columns(2)

    with r2c1:
        food_only = fdf[fdf["category"]=="Food"]
        st.markdown(f'<div class="chart-title">Cuisines represented (Food only)</div>'
                    f'<div class="chart-sub">{len(food_only)} food restaurants across '
                    f'{food_only["cuisine_type"].nunique()} cuisine types</div>',
                    unsafe_allow_html=True)
        cuis_cnt = food_only["cuisine_type"].value_counts().head(14).reset_index()
        cuis_cnt.columns = ["Cuisine","Count"]
        fig4 = px.bar(cuis_cnt, x="Count", y="Cuisine", orientation="h",
                      color="Count",
                      color_continuous_scale=[[0,"#93B8E0"],[1,BLUE]],
                      text="Count")
        fig4.update_traces(textposition="outside",
                           textfont=dict(size=10, color=INK))
        fig4.update_layout(**CL, height=420, showlegend=False,
                           coloraxis_showscale=False,
                           yaxis={"categoryorder":"total ascending"},
                           xaxis_title="Number of restaurants", yaxis_title="")
        fmt_axis(fig4, x_grid=True, y_grid=False)
        st.plotly_chart(fig4, use_container_width=True)

    with r2c2:
        st.markdown(f'<div class="chart-title">Rating by category</div>'
                    f'<div class="chart-sub">Median, spread, and outliers per category</div>',
                    unsafe_allow_html=True)
        fig5 = px.box(fdf.dropna(subset=["rating"]),
                      x="category", y="rating",
                      color="category", color_discrete_map=CAT_COLORS,
                      points="outliers",
                      hover_name="name")
        fig5.update_layout(**CL, showlegend=False, height=420,
                           xaxis_title="", yaxis_title="Rating (1 – 5)")
        fmt_axis(fig5, x_grid=False, y_grid=True)
        fig5.update_xaxes(tickangle=-12)
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="overline">The honest question</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">Does paying more get you better food?</div>',
                unsafe_allow_html=True)

    df_sc = fdf.dropna(subset=["price_level","rating"]).copy()
    df_sc["price_label"] = df_sc["price_level"].map(
        {1:"$ Budget", 2:"$$ Mid-range", 3:"$$$ Upscale"})
    df_sc["category"] = df_sc["category"].fillna("Food")
    CAT_ORDER = ["$ Budget","$$ Mid-range","$$$ Upscale"]
    PRICE_CLR  = {"$ Budget":TEAL,"$$ Mid-range":BLUE,"$$$ Upscale":CORAL}

    # Summary stats per tier
    summary = (df_sc.groupby("price_label")["rating"]
               .agg(["mean","median","std","count"])
               .reset_index())
    summary.columns = ["price_label","mean","median","std","count"]

    pc1, pc2 = st.columns([3, 2])

    with pc1:
        st.markdown('<div class="chart-title">Rating distribution by price tier</div>'
                    '<div class="chart-sub">Box shows 25th–75th percentile &middot; '
                    'line = median &middot; dots = individual restaurants</div>',
                    unsafe_allow_html=True)
        fig6 = px.box(df_sc, x="price_label", y="rating",
                      color="price_label",
                      color_discrete_map=PRICE_CLR,
                      points="all",
                      hover_name="name",
                      hover_data={"cuisine_type":True,"review_count":True,
                                  "price_label":False,"rating":True},
                      category_orders={"price_label":CAT_ORDER},
                      labels={"price_label":"","rating":"Rating (1–5)"})
        fig6.update_traces(
            marker=dict(size=5, opacity=0.5),
            line=dict(width=2),
            boxmean=True        # shows mean as dashed line
        )
        fig6.update_layout(**CL, height=420, showlegend=False,
                           yaxis_title="Rating (1–5)")
        fig6.update_xaxes(showgrid=False, zeroline=False,
                          tickfont=dict(size=13, color=INK, family="Libre Baskerville"))
        fig6.update_yaxes(**GRID, range=[2.8, 5.4],
                          tickfont=dict(size=11, color=INK2))
        # Annotate avg + n above each box
        for _, row in summary.iterrows():
            fig6.add_annotation(
                x=row["price_label"], y=5.35,
                text=f"avg {row['mean']:.2f}  &bull;  n={int(row['count'])}",
                showarrow=False,
                font=dict(size=10, color=INK2, family="IBM Plex Sans"),
                align="center"
            )
        st.plotly_chart(fig6, use_container_width=True)

    with pc2:
        st.markdown('<div class="chart-title">Average rating vs. price</div>'
                    '<div class="chart-sub">Higher price does not mean better food here</div>',
                    unsafe_allow_html=True)
        fig7 = go.Figure()
        for _, row in summary.iterrows():
            clr = PRICE_CLR.get(row["price_label"], BLUE)
            fig7.add_trace(go.Bar(
                x=[row["price_label"]],
                y=[row["mean"]],
                name=row["price_label"],
                marker_color=clr,
                text=[f"{row['mean']:.2f}"],
                textposition="outside",
                textfont=dict(size=13, color=INK, family="Libre Baskerville"),
                hovertemplate=(f"<b>{row['price_label']}</b><br>"
                               f"Avg rating: {row['mean']:.2f}<br>"
                               f"Restaurants: {int(row['count'])}<extra></extra>")
            ))
        # Overall avg reference line
        overall_avg = df_sc["rating"].mean()
        fig7.add_hline(y=overall_avg, line_dash="dot",
                       line_color=MUTED, line_width=1.5)
        fig7.add_annotation(
            x=1, y=overall_avg, xref="paper",
            text=f"overall avg {overall_avg:.2f}",
            showarrow=False, xanchor="right",
            font=dict(size=9, color=MUTED)
        )
        # n= label below each bar
        for _, row in summary.iterrows():
            fig7.add_annotation(
                x=row["price_label"], y=0.1,
                text=f"n = {int(row['count'])}",
                showarrow=False,
                font=dict(size=10, color=INK2),
                yref="y"
            )
        fig7.update_layout(**CL, height=420, showlegend=False,
                           xaxis_title="", yaxis_title="Average Rating",
                           xaxis=dict(categoryorder="array",
                                      categoryarray=CAT_ORDER,
                                      tickfont=dict(size=11, color=INK),
                                      showgrid=False),
                           yaxis=dict(**GRID, range=[0, 5.8],
                                      tickfont=dict(size=11, color=INK2)))
        st.plotly_chart(fig7, use_container_width=True)

    st.markdown('<div class="chart-sub">'
                'The median and average tell the same story: paying more does not reliably '
                'buy you a better meal in State College.</div>',
                unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 2  FIND A SPOT
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'<div class="overline">Personalized</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">Find your next meal</div>', unsafe_allow_html=True)

    fa, fb = st.columns(2)
    with fa:
        vibe = st.selectbox("What are you looking for?", [
            "Everything","Date night","Group hangout",
            "Quick and solo","Late night","Dessert run","Coffee and work",
        ])
    with fb:
        sort_by = st.selectbox("Sort by", [
            "Highest rated","Most reviewed",
            "Price: low to high","Price: high to low"
        ])

    results = fdf.copy()
    if vibe == "Date night":
        results = results[(results["price_level"]>=2) &
                          (~results["cuisine_type"].isin(["Fast Food","Late Night Snacks","Campus Dining"]))]
    elif vibe == "Late night":
        results = results[results["is_late_night"]]
    elif vibe == "Quick and solo":
        results = results[results["price_level"]==1]
    elif vibe == "Dessert run":
        results = results[results["category"]=="Dessert & Snacks"]
    elif vibe == "Coffee and work":
        results = results[results["cuisine_type"].isin(["Coffee & Tea","Boba & Tea","Bakery","Cafe"])]
    elif vibe == "Group hangout":
        results = results[results["category"].isin(["Drinks","Food"])]

    sort_map = {
        "Highest rated":      ("rating", False),
        "Most reviewed":      ("review_count", False),
        "Price: low to high": ("price_level", True),
        "Price: high to low": ("price_level", False),
    }
    scol, sasc = sort_map[sort_by]
    results = results.sort_values(scol, ascending=sasc)

    st.markdown(f'<div class="chart-sub">{len(results)} restaurants match</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    for _, r in results.iterrows():
        px_str  = r["price_str"]
        late_b  = '<span class="badge badge-red">Late Night</span>' if r["is_late_night"] else ""
        sun_b   = '<span class="badge badge-green">Open Sunday</span>' if r["opens_sunday"] else ""
        cat_b   = f'<span class="badge">{r["category"]}</span>'
        cuis_b  = f'<span class="badge">{r["cuisine_type"]}</span>'

        website_html = (f'<a href="{r["website"]}" target="_blank" ' 
                        f'style="font-size:0.74rem;color:{BLUE};font-weight:600;' 
                        f'text-decoration:none;border-bottom:1px solid {BLUE};">View website</a>' 
                        if pd.notna(r.get("website")) and r["website"] else "")
        phone_html = (f'<div style="font-size:0.74rem;color:{INK2};margin-top:2px;">{r["phone"]}</div>' 
                      if r.get("phone") else "")
        st.markdown(f"""
        <div class="r-card" style="flex-direction:column;align-items:flex-start;gap:6px;">
          <div style="display:flex;justify-content:space-between;width:100%;align-items:center;">
            <div>
              <span style="font-family:'Libre Baskerville',serif;font-size:1rem;
                           font-weight:700;color:{BLUE};">{r["rating"]:.1f}</span>
              <span style="font-size:0.92rem;font-weight:600;color:{INK};margin-left:6px;">{r["name"]}</span>
            </div>
            <span style="font-size:0.82rem;font-weight:700;color:{INK2};">{px_str}</span>
          </div>
          <div style="font-size:0.78rem;color:{INK2};">{r["address"]}</div>
          {phone_html}
          <div style="margin-top:4px;">{cat_b}{cuis_b}{late_b}{sun_b}</div>
          <div style="margin-top:2px;">{website_html}</div>
        </div>
        """, unsafe_allow_html=True)

    map_df = results.dropna(subset=["lat","lng"])
    if not map_df.empty:
        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        st.markdown(f'<div class="chart-title">Map</div>', unsafe_allow_html=True)
        fig_m = px.scatter_mapbox(map_df, lat="lat", lon="lng",
                                  hover_name="name",
                                  hover_data={"rating":True,"cuisine_type":True,
                                              "category":True,"lat":False,"lng":False},
                                  color="category", color_discrete_map=CAT_COLORS,
                                  zoom=13, height=440, mapbox_style="carto-positron")
        fig_m.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_m, use_container_width=True)


# ════════════════════════════════════════════════════════════
# TAB 3  RANKINGS
# ════════════════════════════════════════════════════════════
with tab3:
    rc1, rc2 = st.columns(2)

    with rc1:
        st.markdown(f'<div class="overline">Earned their stars</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-head">Top Rated</div>', unsafe_allow_html=True)
        min_rev = st.slider("Minimum reviews to qualify", 10, 500, 50, key="top_rev")
        top = fdf[fdf["review_count"]>=min_rev].sort_values("rating",ascending=False).head(15)

        st.markdown(f'<div class="chart-title">Top {len(top)} restaurants by rating</div>'
                    f'<div class="chart-sub">Minimum {min_rev} reviews required</div>',
                    unsafe_allow_html=True)
        fig_top = px.bar(top, x="rating", y="name", orientation="h",
                         color="cuisine_type",
                         color_discrete_sequence=MULTI,
                         hover_data=["review_count","category","price_str"],
                         text="rating")
        fig_top.update_traces(texttemplate="%{text:.1f}",
                              textposition="outside",
                              textfont=dict(size=10, color=INK))
        fig_top.update_layout(**CL, height=520,
                              yaxis={"categoryorder":"total ascending"},
                              xaxis_title="Rating", yaxis_title="",
                              showlegend=False)
        fig_top.update_xaxes(range=[3.5,5.4], showgrid=False)
        fig_top.update_yaxes(showgrid=False, tickfont=dict(size=11, color=INK))
        st.plotly_chart(fig_top, use_container_width=True)

    with rc2:
        st.markdown(f'<div class="overline">Flying under the radar</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-head">Hidden Gems</div>', unsafe_allow_html=True)
        max_rev   = st.slider("Max reviews (lower = more hidden)", 20, 300, 150, key="gem_rev")
        min_gem_r = st.slider("Min rating", 4.0, 5.0, 4.3, 0.1, key="gem_r")
        gems = fdf[(fdf["review_count"]<=max_rev)&(fdf["rating"]>=min_gem_r)].sort_values("rating",ascending=False)

        st.markdown(f'<div class="chart-title">Rating vs. review count</div>'
                    f'<div class="chart-sub">{len(gems)} gems &mdash; high quality, low profile</div>',
                    unsafe_allow_html=True)
        fig_g = px.scatter(gems, x="review_count", y="rating",
                           color="cuisine_type",
                           hover_name="name",
                           hover_data={"price_str":True,"address":True,"review_count":True},
                           color_discrete_sequence=MULTI,
                           size_max=10, opacity=0.9,
                           labels={"review_count":"Reviews","rating":"Rating"})
        fig_g.update_traces(marker=dict(size=10))
        fig_g.update_layout(**CL, height=360, showlegend=False,
                            xaxis_title="Number of Reviews", yaxis_title="Rating")
        fmt_axis(fig_g)
        st.plotly_chart(fig_g, use_container_width=True)

        for i, (_, r) in enumerate(gems.iterrows(), 1):
            st.markdown(
                f'<div class="r-card">'
                f'<div class="r-rank">#{i}</div>'
                f'<div><div class="r-name">{r["name"]}</div>'
                f'<div class="r-meta">{r["cuisine_type"]} &nbsp;&middot;&nbsp; '
                f'{r["price_str"]} &nbsp;&middot;&nbsp; '
                f'{r["rating"]:.1f} / 5.0 &nbsp;&middot;&nbsp; '
                f'{int(r["review_count"])} reviews</div></div>'
                f'</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<div class="overline">Best value</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">High quality, budget price</div>', unsafe_allow_html=True)
    value = fdf[(fdf["price_level"]==1)&(fdf["rating"]>=4.0)].sort_values("rating",ascending=False)
    vc1, vc2, vc3 = st.columns(3)
    for i, (_, r) in enumerate(value.iterrows(), 1):
        [vc1,vc2,vc3][i%3].markdown(
            f'<div class="r-card">'
            f'<div class="r-rank">#{i}</div>'
            f'<div><div class="r-name">{r["name"]}</div>'
            f'<div class="r-meta">{r["cuisine_type"]} &nbsp;&middot;&nbsp; '
            f'{r["rating"]:.1f} / 5.0 &nbsp;&middot;&nbsp; '
            f'{int(r["review_count"])} reviews</div></div>'
            f'</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 4  DRINKS & NIGHTLIFE
# ════════════════════════════════════════════════════════════
with tab4:
    drinks = fdf[fdf["category"]=="Drinks"].sort_values("rating",ascending=False)
    st.markdown(f'<div class="overline">Bars &middot; Pubs &middot; Coffee &middot; Nightlife</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">Drinks & Nightlife</div>', unsafe_allow_html=True)

    if drinks.empty:
        st.info("No venues match current filters.")
    else:
        dk1,dk2,dk3 = st.columns(3)
        for col, val, lbl, sub, acc in [
            (dk1, len(drinks), "Total Venues", f"{drinks['cuisine_type'].nunique()} types", ""),
            (dk2, f"{drinks['rating'].mean():.2f}", "Avg Rating", "out of 5.0", "teal"),
            (dk3, int(drinks['is_late_night'].sum()), "Open Late Night", "past midnight", "coral"),
        ]:
            col.markdown(kpi_html(val, lbl, sub, acc), unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        dc1, dc2 = st.columns(2)

        with dc1:
            st.markdown(f'<div class="chart-title">Venue types</div>', unsafe_allow_html=True)
            tc = drinks["cuisine_type"].value_counts().reset_index()
            tc.columns = ["Type","Count"]
            fig_dt = px.bar(tc, x="Count", y="Type", orientation="h",
                            color="Count",
                            color_continuous_scale=[[0,"#93C9C0"],[1,TEAL]],
                            text="Count")
            fig_dt.update_traces(textposition="outside",
                                 textfont=dict(size=10,color=INK))
            fig_dt.update_layout(**CL, height=300, showlegend=False,
                                 coloraxis_showscale=False,
                                 yaxis={"categoryorder":"total ascending"},
                                 xaxis_title="Venues", yaxis_title="")
            fmt_axis(fig_dt, x_grid=True, y_grid=False)
            st.plotly_chart(fig_dt, use_container_width=True)

        with dc2:
            st.markdown(f'<div class="chart-title">Top rated venues</div>', unsafe_allow_html=True)
            fig_dr = px.bar(drinks.head(12), x="rating", y="name", orientation="h",
                            color="cuisine_type",
                            color_discrete_sequence=MULTI,
                            hover_data=["review_count"],
                            text="rating")
            fig_dr.update_traces(texttemplate="%{text:.1f}",
                                 textposition="outside",
                                 textfont=dict(size=10,color=INK))
            fig_dr.update_layout(**CL, height=300, showlegend=False,
                                 yaxis={"categoryorder":"total ascending"},
                                 xaxis_title="Rating", yaxis_title="")
            fig_dr.update_xaxes(range=[3,5.5], showgrid=False)
            fig_dr.update_yaxes(showgrid=False, tickfont=dict(size=10,color=INK))
            st.plotly_chart(fig_dr, use_container_width=True)

        dm = drinks.dropna(subset=["lat","lng"])
        if not dm.empty:
            st.markdown(f'<div class="chart-title">Map &mdash; Drinks & Nightlife</div>',
                        unsafe_allow_html=True)
            fig_dmap = px.scatter_mapbox(dm, lat="lat", lon="lng",
                hover_name="name",
                hover_data={"rating":True,"cuisine_type":True,"lat":False,"lng":False},
                color="cuisine_type", zoom=13, height=360,
                mapbox_style="carto-positron",
                color_discrete_sequence=MULTI)
            fig_dmap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_dmap, use_container_width=True)

        st.markdown(f'<div class="chart-title">All venues</div>', unsafe_allow_html=True)
        for i, (_, r) in enumerate(drinks.iterrows(), 1):
            late_b = '<span class="badge badge-red">Late Night</span>' if r["is_late_night"] else ""
            st.markdown(
                f'<div class="r-card">'
                f'<div class="r-rank">#{i}</div>'
                f'<div style="flex:1"><div class="r-name">{r["name"]}</div>'
                f'<div class="r-meta">{r["cuisine_type"]} &nbsp;&middot;&nbsp; '
                f'{r["price_str"]} &nbsp;&middot;&nbsp; '
                f'{r["rating"]:.1f} / 5.0 {late_b}</div></div>'
                f'</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 5  DESSERTS & BOBA
# ════════════════════════════════════════════════════════════
with tab5:
    sweets = fdf[fdf["category"]=="Dessert & Snacks"].sort_values("rating",ascending=False)
    st.markdown(f'<div class="overline">Ice Cream &middot; Boba &middot; Bakeries &middot; Snacks</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">Desserts & Boba</div>', unsafe_allow_html=True)

    if sweets.empty:
        st.info("No spots match current filters.")
    else:
        sw1,sw2,sw3 = st.columns(3)
        for col, val, lbl, sub, acc in [
            (sw1, len(sweets), "Total Spots", f"{sweets['cuisine_type'].nunique()} types", "coral"),
            (sw2, f"{sweets['rating'].mean():.2f}", "Avg Rating", "out of 5.0", ""),
            (sw3, int(sweets['is_late_night'].sum()), "Open Late Night", "past midnight", "gold"),
        ]:
            col.markdown(kpi_html(val, lbl, sub, acc), unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)

        with sc1:
            st.markdown(f'<div class="chart-title">Types of sweet spots</div>', unsafe_allow_html=True)
            stype = sweets["cuisine_type"].value_counts().reset_index()
            stype.columns = ["Type","Count"]
            fig_spie = go.Figure(go.Pie(
                labels=stype["Type"], values=stype["Count"],
                hole=0.52,
                marker_colors=SWEET_PAL[:len(stype)],
                textinfo="percent+label",
                textfont=dict(size=11, color=INK),
                hovertemplate="<b>%{label}</b><br>%{value} spots<extra></extra>"
            ))
            fig_spie.add_annotation(text=f"<b>{len(sweets)}</b>",
                                    x=0.5, y=0.5, showarrow=False,
                                    font=dict(size=16,family="Libre Baskerville",color=INK))
            fig_spie.update_layout(**CL, showlegend=False, height=290)
            st.plotly_chart(fig_spie, use_container_width=True)

        with sc2:
            st.markdown(f'<div class="chart-title">Ratings</div>', unsafe_allow_html=True)
            fig_sbar = px.bar(sweets, x="rating", y="name", orientation="h",
                              color="cuisine_type",
                              color_discrete_sequence=SWEET_PAL,
                              hover_data=["review_count","price_str"],
                              text="rating")
            fig_sbar.update_traces(texttemplate="%{text:.1f}",
                                   textposition="outside",
                                   textfont=dict(size=10,color=INK))
            fig_sbar.update_layout(**CL, height=290,
                                   yaxis={"categoryorder":"total ascending"},
                                   xaxis_title="Rating", yaxis_title="",
                                   showlegend=False)
            fig_sbar.update_xaxes(range=[3,5.5], showgrid=False)
            fig_sbar.update_yaxes(showgrid=False, tickfont=dict(size=10,color=INK))
            st.plotly_chart(fig_sbar, use_container_width=True)

        sm = sweets.dropna(subset=["lat","lng"])
        if not sm.empty:
            st.markdown(f'<div class="chart-title">Map &mdash; Desserts & Boba</div>',
                        unsafe_allow_html=True)
            fig_smap = px.scatter_mapbox(sm, lat="lat", lon="lng",
                hover_name="name",
                hover_data={"rating":True,"cuisine_type":True,"lat":False,"lng":False},
                color="cuisine_type", zoom=13, height=340,
                mapbox_style="carto-positron",
                color_discrete_sequence=SWEET_PAL)
            fig_smap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_smap, use_container_width=True)

        st.markdown(f'<div class="chart-title">All spots</div>', unsafe_allow_html=True)
        for i, (_, r) in enumerate(sweets.iterrows(), 1):
            st.markdown(
                f'<div class="r-card">'
                f'<div class="r-rank">#{i}</div>'
                f'<div><div class="r-name">{r["name"]}</div>'
                f'<div class="r-meta">{r["cuisine_type"]} &nbsp;&middot;&nbsp; '
                f'{r["price_str"]} &nbsp;&middot;&nbsp; '
                f'{r["rating"]:.1f} / 5.0 &nbsp;&middot;&nbsp; '
                f'{int(r["review_count"])} reviews</div></div>'
                f'</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 6  LATE NIGHT
# ════════════════════════════════════════════════════════════
with tab6:
    late = fdf[fdf["is_late_night"]].sort_values("rating",ascending=False)
    st.markdown(f'<div class="overline">Open past midnight</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-head">Late Night State College</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-sub" style="margin-top:-8px;margin-bottom:14px;">'
                f'Definition: closes between 12 AM and 6 AM on at least one night per week.</div>',
                unsafe_allow_html=True)

    if late.empty:
        st.info("No late night options match current filters.")
    else:
        ll1,ll2,ll3 = st.columns(3)
        for col, val, lbl, sub, acc in [
            (ll1, len(late), "Late Night Options", f"{late['category'].nunique()} categories", "coral"),
            (ll2, f"{late['rating'].mean():.2f}", "Avg Rating", "out of 5.0", ""),
            (ll3, int((late["price_level"]==1).sum()), "Budget Options", "price level $", "teal"),
        ]:
            col.markdown(kpi_html(val, lbl, sub, acc), unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
        lc1, lc2 = st.columns(2)

        with lc1:
            st.markdown(f'<div class="chart-title">What categories are open late?</div>',
                        unsafe_allow_html=True)
            lcat = late["category"].value_counts().reset_index()
            lcat.columns = ["Category","Count"]
            colors_l = [CAT_COLORS.get(c, MUTED) for c in lcat["Category"]]
            fig_lcat = go.Figure(go.Pie(
                labels=lcat["Category"], values=lcat["Count"],
                hole=0.52, marker_colors=colors_l,
                textinfo="percent+label",
                textfont=dict(size=11,color=INK),
                hovertemplate="<b>%{label}</b><br>%{value} venues<extra></extra>"
            ))
            fig_lcat.add_annotation(text=f"<b>{len(late)}</b>",
                                    x=0.5,y=0.5,showarrow=False,
                                    font=dict(size=16,family="Libre Baskerville",color=INK))
            fig_lcat.update_layout(**CL, showlegend=False, height=300)
            st.plotly_chart(fig_lcat, use_container_width=True)

        with lc2:
            st.markdown(f'<div class="chart-title">Top rated late night spots</div>',
                        unsafe_allow_html=True)
            fig_lb = px.bar(late.head(12), x="rating", y="name", orientation="h",
                            color="category", color_discrete_map=CAT_COLORS,
                            hover_data=["review_count","cuisine_type","price_str"],
                            text="rating")
            fig_lb.update_traces(texttemplate="%{text:.1f}",
                                 textposition="outside",
                                 textfont=dict(size=10,color=INK))
            fig_lb.update_layout(**CL, height=300,
                                 yaxis={"categoryorder":"total ascending"},
                                 xaxis_title="Rating", yaxis_title="",
                                 showlegend=False)
            fig_lb.update_xaxes(range=[3,5.5], showgrid=False)
            fig_lb.update_yaxes(showgrid=False, tickfont=dict(size=10,color=INK))
            st.plotly_chart(fig_lb, use_container_width=True)

        lm = late.dropna(subset=["lat","lng"])
        if not lm.empty:
            st.markdown(f'<div class="chart-title">Map &mdash; Late Night options</div>',
                        unsafe_allow_html=True)
            fig_lmap = px.scatter_mapbox(lm, lat="lat", lon="lng",
                hover_name="name",
                hover_data={"rating":True,"cuisine_type":True,
                            "category":True,"lat":False,"lng":False},
                color="category", color_discrete_map=CAT_COLORS,
                zoom=13, height=360, mapbox_style="carto-positron")
            fig_lmap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_lmap, use_container_width=True)

        st.markdown(f'<div class="chart-title">All late night options</div>', unsafe_allow_html=True)
        for i, (_, r) in enumerate(late.iterrows(), 1):
            cat_b = f'<span class="badge">{r["category"]}</span>'
            st.markdown(
                f'<div class="r-card">'
                f'<div class="r-rank">#{i}</div>'
                f'<div style="flex:1"><div class="r-name">{r["name"]}</div>'
                f'<div class="r-meta">{r["cuisine_type"]} &nbsp;&middot;&nbsp; '
                f'{r["price_str"]} &nbsp;&middot;&nbsp; '
                f'{r["rating"]:.1f} / 5.0 &nbsp;&middot;&nbsp; '
                f'{int(r["review_count"])} reviews {cat_b}</div></div>'
                f'</div>', unsafe_allow_html=True)
