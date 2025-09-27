# gen_ics.py — minimal, no JSON needed
# Requires: ics, python-dateutil  (workflow already installs)

import csv, io
from pathlib import Path
from dateutil import parser, tz
from ics import Calendar, Event

# ---- EDIT THESE IF YOU WANT ----
TOKEN = "work-abc123xyz"               # becomes docs/feeds/<TOKEN>.ics
CAL_NAME = "My Work Shifts"
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

    cal = Calendar()
    cal.extra.append(("X-WR-CALNAME", CAL_NAME))
    tzinfo = tz.gettz(DEFAULT_TZ) if DEFAULT_TZ else None

    for row in reader:
        title = row.get("title")
        start = row.get("start")
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

        e.location = row.get("location", "")
        e.description = row.get("description", "")
        if row.get("uid"):
            e.uid = str(row["uid"])

        cal.events.add(e)

    out = Path("docs/feeds") / f"{TOKEN}.ics"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(str(cal), encoding="utf-8")
    print(f"[ok] wrote {out}")

if __name__ == "__main__":
    main()
