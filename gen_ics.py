# gen_ics.py — hard-coded config; no JSON file needed
# Requires: ics, python-dateutil, requests (workflow installs them)

import csv, io, sys
from pathlib import Path
from dateutil import tz, parser
from ics import Calendar, Event

# ---- EDIT THESE IF YOU WANT ----
CONFIG = [
    {
        "token": "work-abc123xyz",          # becomes docs/feeds/<token>.ics
        "name":  "My Work Shifts",
        "csv_url": "schedule_template.csv", # or a published Google Sheet CSV URL
        "timezone": "America/New_York",
    }
]
# --------------------------------

def truthy(v) -> bool:
    return str(v or "").strip().lower() in ("true", "1", "yes", "y")

def fetch_text(src: str) -> str:
    if src.startswith(("http://", "https://")):
        import requests
        r = requests.get(src, timeout=20)
        r.raise_for_status()
        return r.text
    return Path(src).read_text(encoding="utf-8")

def row_to_event(row: dict, default_tz: str_
