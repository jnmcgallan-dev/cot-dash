#!/usr/bin/env python3
"""COT dashboard CLI — fetch (live or synthetic) and summarize positioning.

Examples
--------
  python cli.py                      # synthetic sample data, ranked table
  python cli.py --live               # fetch live from the CFTC Socrata API
  python cli.py --live --out data.json
  python cli.py --top 12             # show the 12 most extreme markets
  python cli.py --json               # machine-readable output
"""

import argparse
import json
import sys

import pandas as pd

from fetch import fetch_market_frames
from market_registry import MARKETS, SECTOR_ORDER
from metrics import compute_metrics, latest_row
from sample import build_sample_data

EXT_LABEL = {"L": "Ext Long", "S": "Ext Short", "N": "Neutral", None: "-"}


def collect(markets, frames):
    """Compute metrics for every available market and return summary rows."""
    rows = []
    for meta in markets:
        df = frames.get(meta["code"])
        if df is None or df.empty:
            continue
        mdf = compute_metrics(df)
        row = latest_row(mdf)
        if row is None:
            continue
        rows.append(
            {
                "ticker": meta["ticker"],
                "name": meta["name"],
                "sector": meta["sector"],
                "code": meta["code"],
                "date": str(row["date"]),
                "spec_pct": round(float(row["spec_pct"]), 1),
                "comm_pct": round(float(row["comm_pct"]), 1),
                "spec_z": round(float(row["spec_z"]), 2),
                "comm_z": round(float(row["comm_z"]), 2),
                "spec_extreme": row["spec_extreme"],
                "comm_extreme": row["comm_extreme"],
                "confluence": bool(row["confluence"]),
                "spec_wow": (
                    None if pd.isna(row["spec_wow"]) else round(float(row["spec_wow"]), 2)
                ),
                "spec_net_pct": round(float(row["spec_net_pct"]), 2),
                "comm_net_pct": round(float(row["comm_net_pct"]), 2),
            }
        )
    return rows


def print_table(rows, top=None):
    if top:
        rows = sorted(rows, key=lambda r: abs(r["spec_pct"] - 50), reverse=True)[:top]
    else:
        rows = sorted(rows, key=lambda r: r["spec_pct"], reverse=True)

    header = f"{'SECTOR':<10}{'TICK':<6}{'NAME':<22}{'SPEC%':>7}{'COMM%':>7}{'Z':>7}{'EXT':>10}{'WOW':>8}  {'CF':<3}"
    print(header)
    print("-" * len(header))
    for r in rows:
        wow = f"{r['spec_wow']:+.2f}" if r["spec_wow"] is not None else "  -"
        cf = "CF" if r["confluence"] else ""
        print(
            f"{r['sector']:<10}{r['ticker']:<6}{r['name']:<22}"
            f"{r['spec_pct']:>7.1f}{r['comm_pct']:>7.1f}{r['spec_z']:>7.2f}"
            f"{EXT_LABEL[r['spec_extreme']]:>10}{wow:>8}  {cf:<3}"
        )
    print(f"\n{len(rows)} markets · most extreme first"
          + (" (top " + str(top) + ")" if top else ""))
    n_cf = sum(1 for r in rows if r["confluence"])
    if n_cf:
        print(f"Confluence flags: {n_cf}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="COT positioning summary (live CFTC or synthetic sample)."
    )
    parser.add_argument("--live", action="store_true", help="fetch from CFTC Socrata")
    parser.add_argument("--years", type=int, default=4, help="years of history to fetch")
    parser.add_argument("--top", type=int, default=None, help="show only the N most extreme")
    parser.add_argument("--out", type=str, default=None, help="write JSON summary to a file")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)

    if args.live:
        print("Fetching live CFTC data…", file=sys.stderr)
        frames = fetch_market_frames(years=args.years)
        source = "live"
    else:
        frames = build_sample_data()
        source = "sample (synthetic)"

    rows = collect(MARKETS, frames)

    if args.json or args.out:
        payload = {"source": source, "markets": rows}
        text = json.dumps(payload, indent=2)
        if args.out:
            with open(args.out, "w") as fh:
                fh.write(text + "\n")
            print(f"Wrote {len(rows)} markets to {args.out}", file=sys.stderr)
        if args.json:
            print(text)
    else:
        print(f"Source: {source}")
        print_table(rows, top=args.top)

    return 0


if __name__ == "__main__":
    sys.exit(main())
