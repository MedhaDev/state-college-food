"""Shared data loading and chart styling for every page of the site."""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
REPO = "https://github.com/MedhaDev/state-college-food/blob/main"

PRICE = {1: "$", 2: "$$", 3: "$$$"}
CROWD_COLORS = {1: "#cde2fb", 2: "#86b6ef", 3: "#3987e5", 4: "#1c5cab", 5: "#0d366b"}
CROWD_LABELS = {1: "Very quiet", 2: "Quiet", 3: "Normal", 4: "Busy", 5: "Packed"}
INK, MUTED, RULE, SERIES = "#202122", "#54595d", "#c8ccd1", "#2a78d6"


def restaurants(include_closed=False):
    """One row per restaurant: tags, location and Reddit mentions joined together."""
    df = pd.read_csv(DATA / "clean" / "restaurants_tagged.csv")
    loc = pd.read_csv(DATA / "clean" / "restaurant_locations.csv").drop(columns=["name", "lat", "lng"])
    reddit = pd.read_csv(DATA / "clean" / "reddit_mentions.csv")[["name", "reddit_mentions"]]
    df = df.merge(loc, on="place_id", how="left")
    df = df.merge(reddit.drop_duplicates("name"), on="name", how="left")
    df["price"] = df["price_level"].map(PRICE).fillna("")
    df["reddit_mentions"] = df["reddit_mentions"].fillna(0).astype(int)
    if not include_closed:
        df = df[df["status"] == "OPERATIONAL"]
    return df.drop(columns=["review_texts"]).reset_index(drop=True)


def hours():
    return pd.read_csv(DATA / "clean" / "restaurant_hours.csv")


def calendar():
    return pd.read_csv(DATA / "clean" / "calendar_days.csv", parse_dates=["date"])


def events():
    return pd.read_csv(DATA / "reference" / "psu_events_2026_27.csv", parse_dates=["start_date", "end_date"])


def open_at(day_name, minute):
    """place_ids open on `day_name` at `minute` after midnight (1440+ = after midnight that night)."""
    h = hours()
    same_day = h[(h["day_of_week"] == day_name) & (h["open_minute"] <= minute) & (h["close_minute"] > minute)]
    return set(same_day["place_id"])


def chart_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Georgia", "DejaVu Serif", "Times New Roman"],
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "axes.edgecolor": RULE,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "x",
        "grid.color": "#eaecf0",
        "grid.linewidth": 0.8,
        "xtick.color": MUTED,
        "ytick.color": INK,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "svg.fonttype": "path",
    })


def link(name, website):
    if isinstance(website, str) and website.startswith("http"):
        return f'<a href="{website}">{name}</a>'
    return name


def html_table(df, numeric=()):
    """A plain bordered table, like a reference book."""
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = []
    for _, r in df.iterrows():
        cells = "".join(
            f'<td class="num">{r[c]}</td>' if c in numeric else f"<td>{r[c]}</td>" for c in df.columns
        )
        rows.append(f"<tr>{cells}</tr>")
    return raw(f'<table class="wikitable"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>')


def raw(html):
    """Wrap HTML so Quarto passes it through untouched (print it from an `output: asis` cell)."""
    return f"\n```{{=html}}\n{html}\n```\n"
