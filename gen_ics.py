# gen_ics.py — minimal & stable (no JSON file needed)
# Requires: ics, python-dateutil, requests

import csv, io
from pathlib import Path
from dateutil import parser, tz
from ics import Calendar, Event

# ---- EDIT THESE IF YOU WANT ----
TOKEN = "work-abc123xyz"               # becomes docs/feeds/<TOKEN>.ics
CSV_SRC = "schedule_template.csv"      # or a published Google Sheets CSV URL
DEFAULT_TZ = "America/New_York"
# ---------------------------------

def truthy(v) -> bool:
    return str(v or "").strip().lower() in ("true", "1", "yes", "y")

def fetch_text(src: str) -> str:
    if src.startswith(("http://", "https://")):
        import requests
        r = requests.get(src, timeout=20)
        r.raise_for_status()
        return r.text
    return Path(src).read_text(encoding="utf-8")

def main():
    text = fetch_text(CSV_SRC)
    reader = csv.DictReader(io.StringIO(text))

    cal = Calendar()                    # NOTE: no cal.extra.append(...)

    tzinfo = tz.gettz(DEFAULT_TZ) if DEFAULT_TZ else None
    for row in reader:
        title = row.get("title"); start = row.get("start")
        if not title or not start:
            cont
