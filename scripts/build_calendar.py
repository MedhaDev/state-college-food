"""Turn the hand-curated Penn State events list into a one-row-per-day calendar.

Input:  data/reference/psu_events_2026_27.csv   (curated, with a source URL per row)
Output: data/clean/calendar_days.csv            (Aug 15 2026 - Aug 14 2027)

Every day gets a term phase (in session, break, finals...) and an expected
crowd level from 1 (very quiet) to 5 (packed). The crowd level is a rule-based
estimate, written down here so it can be checked later against the weekly
review-count snapshots.
"""
import pandas as pd

from config import CLEAN, REFERENCE

EVENTS_FILE = REFERENCE / "psu_events_2026_27.csv"
OUTPUT_FILE = CLEAN / "calendar_days.csv"

START, END = "2026-08-15", "2027-08-14"

# Term phases, in priority order: a later rule overrides an earlier one.
PHASES = [
    ("2026-08-15", "2026-08-16", "summer",       "Summer 2026"),
    ("2026-08-17", "2026-08-23", "move_in",      "Fall 2026"),
    ("2026-08-24", "2026-12-11", "in_session",   "Fall 2026"),
    ("2026-11-22", "2026-11-28", "break",        "Fall 2026"),
    ("2026-12-12", "2026-12-18", "finals",       "Fall 2026"),
    ("2026-12-19", "2026-12-20", "commencement", "Fall 2026"),
    ("2026-12-21", "2027-01-10", "break",        "Winter break"),
    ("2027-01-11", "2027-04-30", "in_session",   "Spring 2027"),
    ("2027-03-07", "2027-03-13", "break",        "Spring 2027"),
    ("2027-05-01", "2027-05-07", "finals",       "Spring 2027"),
    ("2027-05-08", "2027-05-09", "commencement", "Spring 2027"),
    ("2027-05-10", "2027-08-14", "summer",       "Summer 2027"),
]

# Starting crowd level for each phase (students in town or not).
PHASE_CROWD = {
    "in_session": 3, "finals": 3, "move_in": 4, "commencement": 4,
    "summer": 2, "break": 1,
}

# Event types that can push a day's crowd level up (never down).
RAISING_TYPES = {"football_home", "campus_event", "community_event", "commencement", "move_in"}

PHASE_REASON = {
    "in_session": "Regular semester day", "finals": "Finals period",
    "move_in": "Move-in", "commencement": "Commencement weekend",
    "summer": "Summer, most students away", "break": "Break, most students away",
}

CROWD_LABELS = {1: "Very quiet", 2: "Quiet", 3: "Normal", 4: "Busy", 5: "Packed"}


def main():
    events = pd.read_csv(EVENTS_FILE, parse_dates=["start_date", "end_date"])
    days = pd.DataFrame({"date": pd.date_range(START, END, freq="D")})

    days["term_phase"] = None
    days["academic_term"] = None
    for start, end, phase, term in PHASES:
        mask = days["date"].between(start, end)
        days.loc[mask, "term_phase"] = phase
        days.loc[mask, "academic_term"] = term

    days["day_name"] = days["date"].dt.day_name()
    days["is_weekend"] = days["date"].dt.dayofweek >= 5

    rows = []
    for _, day in days.iterrows():
        d = day["date"]
        todays = events[(events["start_date"] <= d) & (events["end_date"] >= d)]
        tomorrow_home_game = (
            (events["event_type"] == "football_home")
            & (events["start_date"] == d + pd.Timedelta(days=1))
        ).any()

        level = PHASE_CROWD[day["term_phase"]]
        reason = PHASE_REASON[day["term_phase"]]

        raising = todays[todays["event_type"].isin(RAISING_TYPES)]
        if not raising.empty and raising["expected_crowd"].max() > level:
            top = raising.loc[raising["expected_crowd"].idxmax()]
            level, reason = int(top["expected_crowd"]), top["event_name"]
        if tomorrow_home_game and level < 4:
            level, reason = 4, "Eve of a home football game"

        no_class_today = todays["event_type"].isin(["holiday", "break"]).any()
        rows.append({
            "events": "; ".join(todays["event_name"]),
            "is_home_game": (todays["event_type"] == "football_home").any(),
            "classes_in_session": (
                day["term_phase"] == "in_session" and not day["is_weekend"] and not no_class_today
            ),
            "expected_crowd": level,
            "crowd_label": CROWD_LABELS[level],
            "crowd_reason": reason,
        })

    out = pd.concat([days, pd.DataFrame(rows)], axis=1)
    out["date"] = out["date"].dt.date
    out = out[[
        "date", "day_name", "is_weekend", "academic_term", "term_phase",
        "classes_in_session", "is_home_game", "events",
        "expected_crowd", "crowd_label", "crowd_reason",
    ]]
    out.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved {len(out)} days to {OUTPUT_FILE}")
    print(out["crowd_label"].value_counts().reindex(CROWD_LABELS.values()).to_string())


if __name__ == "__main__":
    main()
