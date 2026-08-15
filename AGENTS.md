# COT Dashboard — Handoff Cheat Sheet (for another AI)

Everything you need to understand, run, verify, or continue work on this project.
Read [`README.md`](README.md) and [`SPEC.md`](SPEC.md) for full context.

## What it is

A **live web dashboard** that turns the CFTC's weekly **Commitment of Traders (COT)**
report into a cross-market "positioning extremes" view: which of **41 futures markets
across 6 sectors** (FX, Rates, Equities, Energy, Metals, Ag) have speculative
positioning crowded near a 3-year extreme, where commercials sit at the opposite
extreme (the classical contrarian setup), and how positioning flowed week-over-week.

**Report type: CFTC Legacy futures-and-options COMBINED** (options included, so FX and
every sector show full positioning). Descriptive tool — **not** a trading-signal generator.

## Where it is

| Thing | Location |
|---|---|
| Local project | `cot-dash/` (on Desktop) |
| Dashboard file (single-file app) | `cot-dash/index.html` |
| Python pipeline | `cot-dash/src/` |
| Artifacts (heatmap PNG, live JSON) | `cot-dash/artifacts/` |
| Hosted URL (GitHub Pages) | https://huskytradingltd.github.io/cot-dash/ |
| GitHub repo | `huskytradingltd/cot-dash` |

> ⚠️ The local `cot-dash/` folder is **not** a git repo. The hosted URL currently
> serves a DIFFERENT, older build ("Positioning Ledger — COT Report"). The local
> build is newer and not yet deployed.

## Data source

- CFTC Socrata API: `https://publicreporting.cftc.gov/resource/srt6-5q2f.json` (Legacy_All)
- Filtered to `futonly_or_combined = 'Combined'` (futures + options)
- `$where` on `cftc_contract_market_code` (41 codes) and 4 years of history
- Same field names as futures-only: `open_interest_all`, `noncomm_positions_long_all`,
  `noncomm_positions_short_all`, `comm_positions_long_all`, `comm_positions_short_all`
- Free/public, CORS-enabled (works directly from the browser)

## Metrics (causal, trailing-window only)

1. Net position = long − short (spec / commercial)
2. OI normalization = net ÷ open interest
3. Rolling z-score — 156-week (3yr) window, min 52 weeks history
4. Rolling percentile — rank within own trailing 156-week window
5. Extreme = pct ≥ 90 → Extreme Long; ≤ 10 → Extreme Short
6. Confluence = spec extreme AND commercial extreme in opposing directions
7. WoW change = this week's net% − last week's, in percentage points of OI

## Key files

| File | Role |
|---|---|
| [`index.html`](index.html) | The whole dashboard: registry (41 markets), metric engine, live fetch, render, "How to read" guide |
| [`src/fetch.py`](src/fetch.py) | Live CFTC fetch (stdlib only) — `BASE`, `REPORT_TYPE='Combined'` |
| [`src/metrics.py`](src/metrics.py) | Python metric engine (reference implementation) |
| [`src/cli.py`](src/cli.py) | CLI summary (`--live`, `--top N`, `--out data.json`) |
| [`src/heatmap.py`](src/heatmap.py) | matplotlib heatmap → `artifacts/cot_heatmap.png` |
| [`src/market_registry.py`](src/market_registry.py) | 41-market registry (single source of truth) |
| [`src/sample.py`](src/sample.py) | Seeded synthetic fallback data |
| [`src/notebook.ipynb`](src/notebook.ipynb) | Jupyter walkthrough |

## How to run

```bash
# Dashboard — no build, open in a browser
open cot-dash/index.html

# Python pipeline (from cot-dash/src)
python3 cli.py --live --top 12          # ranked table, live combined data
python3 cli.py --live --out ../artifacts/live_data.json
python3 heatmap.py --live --out ../artifacts/cot_heatmap.png
```

## How to verify (do this before claiming it works)

Both engines (JS `computeMetrics` in `index.html` and Python `metrics.py`) must agree on
live data. Two checks already pass 41/41 for spec_pct AND confluence:
1. `python3 cli.py --live --out ../artifacts/live_data.json`
2. Run the JS engine from `index.html` in Node against the same CFTC rows and compare
   each market's `specPct`/`confluence` to the Python JSON (tolerance ±0.1 pp).

## Recent work (what was built/fixed)

- **2026-08-15 — Switched to futures-and-options COMBINED report** (`srt6-5q2f`,
  filtered `Combined`) so FX/all sectors include options. Report date went
  2026-08-04 → 2026-08-11; picture changed (e.g. EUR now Extreme Short + confluence).
- **2026-08-15 — Fixed a critical metric-engine bug** in `index.html::computeMetrics`:
  the rolling pass wrote percentiles back into the same array it was ranking, so every
  market collapsed to the 0.6th percentile. Fixed by using separate raw-net% /
  percentile / z arrays (matches `metrics.py`).
- **2026-08-15 — Added a "How to read this dashboard" guide** (collapsible panel) to
  `index.html`.
- **2026-08-11 — MVP built + hosted**: live CFTC fetch, ledger diverging bars,
  click-to-expand sparklines, WoW tracking.

## Gotchas / caveats

- **DeepSeek `deepseek-v4-flash` cannot accept images.** Never open/read
  `artifacts/cot_heatmap.png` (or any PNG) with an image-viewing step in a session on a
  non-vision model — the tool renders it into the conversation as an `image_url` part
  and the NEXT request 400s ("unknown variant `image_url`, expected `text`"). Verify
  images programmatically (magic bytes, dimensions, distinct colors) instead.
- Registry `cftc_contract_market_code`s can shift; a stale code shows "no data" for one
  market only. Verify against the current CFTC report periodically.
- Legacy "commercial" category in commodities blends hedgers with swap dealers
  (Disaggregated report would be sharper there).
- Percentiles need ≥ 52 weeks of history.
- Descriptive, not a signal: an extreme can persist through a long trend.
