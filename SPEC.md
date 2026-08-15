# COT Positioning Dashboard — Specification

**Status:** MVP Shipped, hosted, live-data verified
**Owner:** [you]
**Last updated:** 2026-08-11
**Repo / live URL:** github.com/huskytradingltd/cot-dash · huskytradingltd.github.io/cot-dash

---

## 1. Overview

A web dashboard that turns the CFTC's free weekly Commitment of Traders (COT)
report into a cross-market positioning-extremes signal. It shows, at a
glance, which of 41 futures markets (FX, Rates, Equities, Energy, Metals,
Ag) have speculative positioning crowded near a 3-year extreme, flags cases
where commercial hedgers are simultaneously positioned at the opposite
extreme (the classical contrarian setup), and tracks week-over-week
positioning flow. Built for a non-technical user to check weekly with no
coding required.

## 2. Goals

- Non-technical user can open the dashboard and identify crowded markets in under 30 seconds, with no setup beyond a browser.
- Data refreshes on demand from the live CFTC source, not a stale export.
- Works as a single portable artifact — no server, no database, no maintenance burden.
- Free to run and free to host, indefinitely.
- Visual design that reads as intentional and specific to the subject, not a generic dashboard template.

## 3. Non-Goals

- **Not a trading signal generator.** Flags conditions worth investigating; does not recommend trades or size positions.
- **No price/momentum overlay in MVP** — deliberately deferred (see §12). Positioning extremes can persist through a strong trend; this dashboard does not filter for that yet.
- **No user accounts, no saved preferences, no multi-user features.** Single-viewer tool.
- **No private/authenticated hosting in MVP.** The GitHub Pages URL is public to anyone with the link.
- **No historical backtesting of how extremes resolved.** Descriptive, not predictive.

## 4. Users & Context

One primary user: non-technical, comfortable following clear step-by-step
instructions (VS Code, GitHub) but not writing or debugging code
independently. Checks positioning periodically (roughly weekly, aligned to
the Friday 3:30pm ET CFTC release) from desktop or phone browser.

## 5. Requirements

### Functional
1. Display all 41 markets across 6 sectors, grouped and visually ranked by positioning percentile.
2. "Refresh live data" button fetches the current CFTC Legacy report and recomputes all metrics client-side.
3. Falls back to embedded sample data on first load / offline, clearly labeled as such.
4. Click any market to expand a 3-year sparkline (spec vs. commercial) plus full stat breakdown.
5. Visually flag markets in the top/bottom decile of their own 3-year positioning history.
6. Flag "confluence" cases — spec extreme and commercial extreme in opposing directions.
7. Show week-over-week change in net positioning (% of open interest) per market, both in the row list and detail view.

### Non-Functional
- Runs as a single `.html` file — no build step, no install, no dependencies beyond a browser.
- Mobile-responsive down to ~390px viewport.
- Graceful, human-readable error message if the live fetch fails (e.g. no internet).
- No use of `localStorage`/`sessionStorage` — all state is in-memory per page load.

## 6. Data Sources & Integrations

| Source | Provides | Auth needed | Failure behavior |
|---|---|---|---|
| CFTC Socrata API (`publicreporting.cftc.gov`, dataset `srt6-5q2f`, Legacy futures-and-options combined, filtered to `Combined`) | Weekly net long/short positions by trader category, per market, since inception, including options | None (public; optional free app token removes throttling) | Refresh button shows an inline error banner; dashboard keeps showing last-good data (sample or previously fetched) |

Fetched directly from the browser via `fetch()` — CFTC's Socrata platform
supports CORS natively, so no backend/proxy is required.

## 7. Architecture & Tech Stack

- **Delivery:** single self-contained HTML file (`cot_dashboard.html` / `index.html`), inline CSS + vanilla JS. No frameworks, no build tooling.
- **Where it runs:** entirely in the browser — hosting is static file serving only (GitHub Pages).
- **Companion Python pipeline** (`src/`): a separate, parallel implementation for offline/analytical use (Jupyter notebook + CLI), sharing the same market registry and metric logic. Not required for the live dashboard to function; useful for deeper ad-hoc analysis.
- **Key components (JS):**
  - `MARKET_REGISTRY` — ticker → CFTC contract code → sector mapping (41 markets)
  - `computeSeriesMetrics()` — net position, OI normalization, rolling z-score, rolling percentile, extreme/confluence classification, week-over-week change
  - `fetchLiveData()` — single batched Socrata query across all 41 codes
  - `render()` — builds the sector-grouped ledger UI from a summary array

## 8. Core Logic

For each market, per week:
1. **Net position** = long contracts − short contracts, separately for non-commercial (specs) and commercial (hedgers).
2. **OI normalization** = net position ÷ total open interest, making markets of very different size comparable.
3. **Rolling z-score** = (current value − trailing mean) ÷ trailing std dev, 156-week (3yr) window, minimum 52 weeks of history required before a value is produced.
4. **Rolling percentile rank** = current value's percentile within its own trailing 156-week window (not full-sample) — deliberately rolling so a market's structural positioning range can drift over time without producing false extremes.
5. **Extreme classification**: percentile ≥ 90 → "Extreme Long"; ≤ 10 → "Extreme Short"; else "Neutral". Applied independently to specs and commercials.
6. **Confluence flag**: spec "Extreme Long" + commercial "Extreme Short" (or vice versa) → flagged as a reversal-watch condition. This is the classical COT contrarian setup, since commercials are typically positioned opposite specs.
7. **Week-over-week change** = this week's OI-normalized net position − last week's, in percentage points — a direct read on positioning *flow*, independent of where the level sits in its historical range.

Report type: **CFTC Legacy futures-and-options combined** (not Disaggregated or
TFF) — the only report covering all six target sectors in one consistent schema,
with options positions included so forex and every sector show their full
positioning. Trade-off: Legacy's "commercial" category blends true hedgers with
swap dealers, which can mute the signal specifically in commodity markets
(see §10).

## 9. Design System

**Concept:** "Positioning Ledger" — an official-filing/trading-floor
aesthetic grounded in the subject (a regulatory report, read as data-dense
tabular records), avoiding generic AI-dashboard defaults (no cream+serif,
no black+neon, no broadsheet hairline cliché applied without reason).

- **Palette:** ink navy background (`#0F1720`), panel slate (`#16212C`), hairline (`#2C3B4A`), paper text (`#ECE8DD`), long/amber (`#D3A24C`), short/brick (`#BD5B45`), confluence teal (`#5FAE9E`).
- **Type:** Spectral (serif, display/headers) + IBM Plex Mono (data, ticker codes, figures) + Inter (UI/body).
- **Signature element:** diverging ledger bars — each market's percentile shown as a bar radiating from a center 50th-percentile line (not from zero), with ruler tick marks and a stamped monospace ticker code, so direction and magnitude read instantly across all 41 markets at once.

## 10. Known Limitations & Caveats

- No price/momentum filter — a market can stay positioned at an extreme through a long, strong trend. Do not treat an extreme flag alone as a timing signal.
- Legacy report's commercial category is not pure hedger data in commodities (swap dealers included) — Disaggregated report would sharpen this for Ag/Energy/Metals specifically, not yet implemented.
- Historical relationship between positioning extremes and reversals is not reliable in isolation — descriptive tool, not a predictive model.
- Public URL — no authentication. Anyone with the link can view (not edit) the dashboard.
- Live fetch pulls ~4 years of weekly data across 41 markets in one batched request; large but has run reliably in testing. No caching/retry-backoff beyond a single error message.

## 11. Hosting & Deployment

- **Host:** GitHub Pages (free), repository `huskytradingltd/cot-dash`, deployed from `main` branch root.
- **File served:** `index.html` (renamed from `cot_dashboard.html` at upload).
- **To update:** replace `index.html` in the repo (via GitHub's web UI, "edit" pencil icon or delete + re-upload) and commit — GitHub Pages redeploys automatically, typically within a minute.
- **Alternative considered:** Netlify Drop — faster initial deploy, but GitHub chosen for free permanent hosting plus built-in version history, consistent with wanting a spec/documentation habit across projects.

## 12. Future Roadmap / Backlog

- [ ] Price momentum overlay (originally in scope, deferred for MVP)
- [ ] Disaggregated report option for Ag/Energy/Metals (sharper commercial signal)
- [ ] Adjustable extreme thresholds (currently fixed at 90th/10th percentile) and z-score window
- [ ] Email/text alerts on new extremes or confluence signals
- [ ] Watchlist / pinned markets
- [ ] Multi-market overlay/comparison view
- [ ] Historical backtest of how extremes have resolved, market by market

## 13. Change Log

| Date | Change |
|---|---|
| 2026-08-11 | Initial Python pipeline (fetch, metrics, notebook, matplotlib heatmap) built and tested with synthetic data |
| 2026-08-11 | HTML dashboard built: live CFTC fetch, ledger-style diverging bar chart, click-to-expand detail sparklines |
| 2026-08-11 | Added week-over-week positioning change tracking (row badges + detail stats) |
| 2026-08-11 | Hosted live on GitHub Pages; live-data refresh verified working in production |
| 2026-08-11 | Spec template created; this spec written retroactively as first worked example |
| 2026-08-15 | Fixed computeMetrics percentile bug (raw net% was overwritten in place, collapsing every market to the 0.6th percentile) |
| 2026-08-15 | Added "How to read this dashboard" guide to the dashboard |
| 2026-08-15 | Switched to the Legacy futures-and-options combined report (dataset `srt6-5q2f`) so FX and all sectors include options |
