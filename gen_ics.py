# gen_ics.py — minimal & stable (no JSON file needed)
# Requires: ics==0.7.2, python-dateutil, requests

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
        r = requests.get(src, timeout=20); r.raise_for_status()
        return r.text
    return Path(src).read_text(encoding="utf-8")

def main():
    text = fetch_text(CSV_SRC)
    reader = csv.DictReader(io.StringIO(text))

    cal = Calendar()  # NOTE: capital C

    tzinfo = tz.gettz(DEFAULT_TZ) if DEFAULT_TZ else None
    for row in reader:
        title = row.get("title"); start = row.get("start")
        if not title or not start:
            continue  # NOTE: full word

        e = Event()
        e.name = title

        if truthy(row.get("all_day")):
            e.begin = parser.parse(start).date()
            if row.get("end"):
                e.end = parser.parse(row["end"]).date()
            e.make_all_day()
        else:
            s = parser.parse(start)
            if tzinfo:
                s = s.replace(tzinfo=tzinfo)
            e.begin = s

            if row.get("end"):
                end = parser.parse(row["end"])
                if tzinfo:
                    end = end.replace(tzinfo=tzinfo)
                e.end = end

        e.location = row.get("location", "") or ""
        e.description = row.get("description", "") or ""
        if row.get("uid"):
            e.uid = str(row["uid"])

        cal.events.add(e)

    out = Path("docs/feeds") / f"{TOKEN}.ics"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(cal.serialize(), encoding="utf-8")
    print(f"[ok] wrote {out
