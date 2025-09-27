# gen_ics.py — robust header handling
# Requires: ics==0.7.2, python-dateutil, requests

import csv, io
from pathlib import Path
from dateutil import parser, tz
from ics import Calendar, Event

# ---- CONFIG ----
TOKEN = "work-abc123xyz"               # becomes docs/feeds/<TOKEN>.ics
CSV_SRC = "schedule_template.csv"      # or a published Google Sheets CSV URL
DEFAULT_TZ = "America/New_York"
# ---------------

def truthy(v) -> bool:
    return str(v or "").strip().lower() in ("true", "1", "yes", "y")

def fetch_text(src: str) -> str:
    if src.startswith(("http://", "https://")):
        import requests
        r = requests.get(src, timeout=20); r.raise_for_status()
        return r.text
    return Path(src).read_text(encoding="utf-8")

def _norm_header(s: str) -> str:
    # strip BOM, trim, lowercase, unify separators, drop '?' (e.g., "All Day?")
    return (s or "").lstrip("\ufeff").strip().lower().replace(" ", "_").replace("-", "_").replace("?", "")

def main():
    text = fetch_text(CSV_SRC)
    reader = csv.DictReader(io.StringIO(text))

    # Normalize the header names so minor differences don’t break parsing
    if reader.fieldnames:
        normalized = [_norm_header(h) for h in reader.fieldnames]
        # Map common aliases to canonical names
        aliases = {
            "allday": "all_day",
            "all_day": "all_day",
            "time_zone": "timezone",
            "tz": "timezone",
        }
        normalized = [aliases.get(h, h) for h in normalized]
        reader.fieldnames = normalized

    cal = Calendar()
    tzinfo = tz.gettz(DEFAULT_TZ) if DEFAULT_TZ else None

    total_rows = 0
    added = 0

    for row in reader:
        total_rows += 1

        # keys are now normalized (e.g., title,start,end,all_day,location,description,timezone,uid)
        title = (row.get("title") or "").strip()
        start = (row.get("start") or "").strip()
        if not title or not start:
            continue

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
        added += 1

    out = Path("docs/feeds") / f"{TOKEN}.ics"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(cal.serialize(), encoding="utf-8")
    print(f"[ok] wrote {out} with {added} event(s) from {total_rows} row(s)")

if __name__ == "__main__":
    main()
