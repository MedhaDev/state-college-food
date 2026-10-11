"""Shared settings for every pipeline script.

Paths are built from the repo folder, so the scripts run the same on any
computer. The Google key (only needed to re-pull data) is read from the
GOOGLE_PLACES_API_KEY environment variable and is never saved in code.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CLEAN = DATA / "clean"
REFERENCE = DATA / "reference"

for folder in (RAW, CLEAN, REFERENCE):
    folder.mkdir(parents=True, exist_ok=True)


def google_api_key():
    key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "GOOGLE_PLACES_API_KEY is not set.\n"
            "Set it with:  export GOOGLE_PLACES_API_KEY=your-key"
        )
    return key
