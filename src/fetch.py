"""Live fetch from the CFTC Socrata API (Legacy futures and options combined).

Dataset srt6-5q2f (Legacy_All) contains both FutOnly and Combined rows per
market/date; we filter to ``futonly_or_combined = 'Combined'`` so options
positions are included for a fuller picture (e.g. FX options).

Uses only the Python standard library for the network call, so the pipeline
can pull data without installing anything beyond pandas.
"""

import json
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta

import pandas as pd

from market_registry import CODES

BASE = "https://publicreporting.cftc.gov/resource/srt6-5q2f.json"
REPORT_TYPE = "Combined"  # "Combined" (futures+options) | "FutOnly"
MAX_ROWS = 50000
MAX_RETRIES = 3
USER_AGENT = "cot-dash/1.0"


def _to_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def fetch_rows(codes=None, years=4, timeout=60):
    """Fetch CFTC Legacy futures-only rows for the given contract codes.

    Returns a list of JSON row dicts (causal: only historical data).
    """
    codes = codes or CODES
    cutoff = (date.today() - timedelta(days=365 * years)).isoformat()
    in_clause = ",".join(f"'{c}'" for c in codes)
    where = (
        f"cftc_contract_market_code in ({in_clause}) "
        f"and report_date_as_yyyy_mm_dd >= '{cutoff}' "
        f"and futonly_or_combined = '{REPORT_TYPE}'"
    )
    url = (
        f"{BASE}?$where={urllib.parse.quote(where)}"
        f"&$order=report_date_as_yyyy_mm_dd&$limit={MAX_ROWS}"
    )

    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                url, headers={"Accept": "application/json", "User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                rows = json.loads(resp.read().decode("utf-8"))
            if not isinstance(rows, list):
                raise ValueError("Unexpected CFTC response shape")
            return rows
        except Exception as err:  # noqa: BLE001
            last_err = err
            if attempt < MAX_RETRIES:
                time.sleep(0.7 * attempt)
    raise last_err


def rows_to_market_frames(rows):
    """Group CFTC rows into per-market weekly frames (ascending by date).

    CFTC publishes preliminary and final reports for the same date; the row
    with the more complete open interest (usually the final) is kept.
    """
    by_code = {}
    for r in rows:
        code = str(r.get("cftc_contract_market_code") or "").strip()
        d = str(r.get("report_date_as_yyyy_mm_dd") or "")[:10]
        if not code or not d:
            continue
        rec = {
            "date": d,
            "oi": _to_int(r.get("open_interest_all")),
            "spec_long": _to_int(r.get("noncomm_positions_long_all")),
            "spec_short": _to_int(r.get("noncomm_positions_short_all")),
            "comm_long": _to_int(r.get("comm_positions_long_all")),
            "comm_short": _to_int(r.get("comm_positions_short_all")),
            "nonrept_long": _to_int(r.get("nonrept_positions_long_all")),
            "nonrept_short": _to_int(r.get("nonrept_positions_short_all")),
        }
        week = by_code.setdefault(code, {})
        prev = week.get(d)
        if prev is None or rec["oi"] > prev["oi"]:
            week[d] = rec

    frames = {}
    for code, weeks in by_code.items():
        df = pd.DataFrame(list(weeks.values())).sort_values("date").reset_index(drop=True)
        frames[code] = df
    return frames


def fetch_market_frames(codes=None, years=4, timeout=60):
    """Fetch rows and convert to per-market frames in one call."""
    return rows_to_market_frames(fetch_rows(codes=codes, years=years, timeout=timeout))
