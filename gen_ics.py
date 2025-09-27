# gen_ics.py
# Build .ics calendars from CSV/Google Sheets.
# Requires: ics, python-dateutil, requests

import csv
import io
import json
import sys
from pathlib import Path

from dateutil import tz, parser
from ics import Calendar, Event

# Optional import: requests (only needed for http(s) CSV)
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # workflow installs it; local runs can skip web URLs

CFG_PATH = Path("config.json")
OUT_DIR = Path("docs/feeds")

# Keep this in sync with your workflow's "Write clean config.json" step.
FALLBACK_CFG = [{
    "token": "work-abc123xyz",
    "name": "My Work Shifts",
    "csv_url": "schedule_template.csv",
    "timezone": "America/New_York",
}]


def load_config() -> list[dict]:
    """
    Load config.json. If it is missing/empty/invalid, use FALLBACK_CFG.
    """
    try:
        text = CFG_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("[warn] config.json not found; using fallback", file=sys.stderr)
        return FALLBACK_CFG

    text = text.strip()
    if not text:
        print("[warn] config.json is empty; using fallback", file=sys.stderr)
        return FALLBACK_CFG

    try:
        cfg = json.loads(text)
        if not isinstance(cfg, list):
            raise ValueError("config.json must be a JSON list []")
        return cfg
    except Exception as e:
        print(f"[warn] config.json parse failed ({e}); using fallback", file=sys.stderr)
        return FALLBACK_CFG


def fetch_text(src: str) -> str:
    """
    Return CSV text from a local path or an http(s) URL.
    """
    if src.startswith(("http://", "https://")):
        if requests is None:
            raise RuntimeError("requests is not installed; cannot fetch web URL")
        r = requests.get(src, timeout=20)
        r.raise_for_status()
        return r.text
    p = Path(src)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {src}")
    return p.read_text(encoding="utf-8")


def _truth_
