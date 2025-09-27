import csv, io, json, sys
from pathlib import Path
from dateutil import tz, parser
from ics import Calendar, Event

try:
    import requests
except Exception:
    requests = None

CFG_PATH = Path("config.json")
OUT_DIR = Path("docs/feeds")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_text(src: str) -> str:
    # Allow http(s) URLs or a local repo path (e.g., data/schedule.csv)
    if src.startswith("http://") or src.startswith("https://"):
        if requests is None:
            raise RuntimeError("requests is not installed. pip install requests")
        import requests as rq
        r = rq.get(src, timeout=20)
        r.raise_for_status()
        return r.text
    else:
        p = Path(src)
        if not p.exists():
            raise FileNotFoundError(f"Missing CSV: {src}")
        return p.read_text(encoding="utf-8")

def row_to_event(row: dict, default_tz: str | None) -> Event:
    e = Event()
    e.name = row.get("title") or "Untitled"
    tzname = (row.get("timezone") or default_tz or "").strip()
    tzinfo = tz.gettz(tzname) if tzname else None
    all_day = str(row.get("all_day","")).strip().lower() in ("true","1","yes")

    if all_day:
        e.begin = parser.parse(row["start"]).date()
        if row.get("end"):
            e.end = parser.parse(row["end"]).date()
        e.make_all_day()
    else:
        start = parser.parse(row["start"])
        if tzinfo:
            start = start.replace(tzinfo=tzinfo)
        e.begin = start
        end_str = row.get("end")
        if end_str:
            end = parser.parse(end_str)
            if tzinfo:
                end = end.replace(tzinfo=tzinfo)
            e.end = end

    e.location = row.get("location") or ""
    e.description = row.get("description") or ""
    if row.get("uid"):
        e.uid = str(row["uid"])
    return e

def build_feed(name: str, csv_src: str, outpath: Path, default_tz: str | None):
    text = fetch_text(csv_src)
    cal = Calendar()
    cal.extra.append(("X-WR-CALNAME", name))
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        if not row.get("title") or not row.get("start"):
            continue
        try:
            cal.events.add(row_to_event(row, default_tz))
        except Exception as ex:
            # Skip bad rows; print minimal hint
            print(f"[warn] Skipping row due to error: {ex}", file=sys.stderr)
            continue
    outpath.write_text(str(cal), encoding="utf-8")

def main():
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))
    for entry in cfg:
        token = entry["token"]
        name = entry.get("name","My Calendar")
        csv_url = entry["csv_url"]
        default_tz = entry.get("timezone")
        outpath = OUT_DIR / f"{token}.ics"
        build_feed(name, csv_url, outpath, default_tz)
        print(f"[ok] Wrote {outpath}")

if __name__ == "__main__":
    main()
