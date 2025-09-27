# gen_ics.py — no JSON needed; builds .ics from a CSV or a published Google Sheet
import csv, io
from pathlib import Path
from dateutil import tz, parser
from ics import Calendar, Event

# <<< EDIT THESE 3 VALUES IF YOU WANT >>>
CONFIG = [{
    "token": "work-abc123xyz",                 # this becomes feeds/<token>.ics
    "name":  "My Work Shifts",                 # calendar display name
    "csv_url": "schedule_template.csv",        # or paste a published Google Sheets CSV URL
    "timezone": "America/New_York",            # default TZ if rows don't have a timezone column
}]

def _truthy(v): return str(v or "").strip().lower() in ("true","1","yes","y")

def fetch_text(src: str) -> str:
    if src.startswith(("http://","https://")):
        import requests
        r = requests.get(src, timeout=20); r.raise_for_status()
        return r.text
    return Path(src).read_text(encoding="utf-8")

def row_to_event(row: dict, default_tz: str | None):
    e = Event()
    e.name = (row.get("title") or "Untitled").strip()
    tzname = (row.get("timezone") or default_tz or "").strip()
    tzinfo = tz.gettz(tzname) if tzname else None
    if _truthy(row.get("all_day")):
        e.begin = parser.parse(row["start"]).date()
        if row.get("end"): e.end = parser.parse(row["end"]).date()
        e.make_all_day()
    else:
        start = parser.parse(row["start"])
        if tzinfo: start = start.replace(tzinfo=tzinfo)
        e.begin = start
        if row.get("end"):
            end = parser.parse(row["end"])
            if tzinfo: end = end.replace(tzinfo=tzinfo)
            e.end = end
    e.location = (row.get("location") or "").strip()
    e.description = (row.get("description") or "").strip()
    if row
