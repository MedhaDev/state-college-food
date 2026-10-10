"""Shared settings for every pipeline script.

Paths are built from the repo folder, so the scripts run the same on any
computer (or in GitHub Actions). The Google key is read from the
GOOGLE_PLACES_API_KEY environment variable and is never saved in code.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CLEAN = DATA / "clean"
REFERENCE = DATA / "reference"
SNAPSHOTS = DATA / "snapshots"

for folder in (RAW, CLEAN, REFERENCE, SNAPSHOTS):
    folder.mkdir(parents=True, exist_ok=True)


def google_api_key():
    key = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "GOOGLE_PLACES_API_KEY is not set.\n"
            "Locally:  export GOOGLE_PLACES_API_KEY=your-key\n"
            "GitHub:   add it under Settings > Secrets and variables > Actions"
        )
    return key
