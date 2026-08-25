# COT Positioning Dashboard

A single-file web dashboard that turns the CFTC's free weekly Commitment of
Traders (COT) report into a cross-market **positioning-extremes** view: which
of 41 futures markets have speculative positioning crowded near a 3-year
extreme, where commercial hedgers sit at the *opposite* extreme (the classical
contrarian setup), and how positioning is flowing week-over-week.

**Status:** MVP built. Descriptive tool — not a trading signal generator.

---

## What it does

- Displays all 41 markets across 6 sectors (FX, Rates, Equities, Energy,
  Metals, Ag), grouped and ranked by positioning percentile.
- **Refresh live data** button fetches the current CFTC Legacy futures-and-options
  combined report (`publicreporting.cftc.gov`, dataset `srt6-5q2f`, filtered to
  Combined) and recomputes all metrics in the browser.
- Falls back to embedded synthetic **sample data** on first load / offline,
  clearly labeled.
- Click any market to expand a 3-year sparkline (spec vs. commercial vs.
  non-reportable) plus a full stat breakdown.
- Flags markets in the top/bottom decile of their **own** 3-year positioning
  history, and "confluence" cases where specs and commercials are extreme in
  opposing directions.
- Shows week-over-week change in net positioning (% of open interest).
- Tracks non-reportable (small trader) positioning alongside spec/commercial
  for context — not part of the confluence signal, which is specifically the
  spec-vs-hedger contrarian setup.

## Metrics (causal — trailing window only)

1. **Net position** = long − short (spec / commercial / non-reportable).
2. **OI normalization** = net ÷ open interest.
3. **Rolling z-score** = (x − mean) ÷ std, 156-week (3-year) window, min 52
   weeks of history required.
4. **Rolling percentile** = current value's rank within its own trailing
   156-week window — deliberately rolling, so a market's structural range can
   drift without producing false extremes.
5. **Extreme** = percentile ≥ 90 → "Extreme Long"; ≤ 10 → "Extreme Short".
6. **Confluence** = spec and commercial extremes in opposing directions.
7. **WoW change** = this week's OI-normalized net% − last week's (pp).

## Repository layout

```
cot-dash/
├── index.html            # single-file dashboard (open in any browser)
├── SPEC.md               # specification / design contract
├── README.md
└── src/                  # companion Python pipeline (offline / analytical)
    ├── market_registry.py  # 41-market registry (single source of truth)
    ├── metrics.py          # metric engine (mirrors the JS logic)
    ├── fetch.py            # live CFTC Socrata fetch (stdlib)
    ├── sample.py           # synthetic sample-data generator (seeded)
    ├── cli.py              # command-line summary
    ├── heatmap.py          # matplotlib sectors×markets heatmap
    ├── notebook.ipynb      # Jupyter notebook walkthrough
    └── requirements.txt
```

## Run it

**Dashboard** — no build step. Open `index.html` in a browser, or host it on
GitHub Pages / Netlify Drop. The live refresh works directly from the browser
because CFTC's Socrata platform supports CORS.

**Python pipeline** (offline / analytical use):

```bash
cd src
pip install -r requirements.txt

python cli.py                 # synthetic sample, ranked table
python cli.py --live          # live CFTC data
python cli.py --live --out data.json --json
python cli.py --top 12        # 12 most extreme markets

python heatmap.py --live --out ../artifacts/cot_heatmap.png
jupyter notebook notebook.ipynb
```

## Hosting

Host `index.html` on GitHub Pages (free, permanent, version history) or
Netlify Drop (faster first deploy). To update: replace `index.html` and commit
— static hosting redeploys automatically.

## Limitations & caveats

- **Not a trading signal.** Flags conditions worth investigating; no price/
  momentum filter — a market can stay extreme through a long trend.
- Legacy report's *commercial* category in commodities blends hedgers with
  swap dealers — Disaggregated would be sharper for Ag/Energy/Metals.
- No historical backtesting of how extremes resolve. Descriptive, not
  predictive.
- Public URL — anyone with the link can view.
- Verify `market_registry.py` / `MARKET_REGISTRY` codes against the current
  CFTC report periodically; legacy contract codes can shift.

## Roadmap (backlog)

- Historical study of how extremes resolve (the open evidence gap)
- Price momentum overlay
- Disaggregated report option for Ag/Energy/Metals
- Adjustable thresholds / z-window
- Alerts on new extremes or confluence
- Watchlist / pinned markets
