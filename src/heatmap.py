#!/usr/bin/env python3
"""matplotlib heatmap: sectors × markets, colored by latest spec percentile.

Uses the dashboard palette (brick -> steel -> amber) with a teal outline on
confluence cells. Writes PNG to the path given by --out.

Examples
--------
  python heatmap.py                       # synthetic sample
  python heatmap.py --live                # live CFTC data
  python heatmap.py --out ../artifacts/cot_heatmap.png
"""

import argparse
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.colors as mcolors  # noqa: E402
import matplotlib.pyplot as plt      # noqa: E402
import numpy as np                   # noqa: E402

from fetch import fetch_market_frames  # noqa: E402
from market_registry import MARKETS, SECTOR_ORDER  # noqa: E402
from metrics import compute_metrics, latest_row  # noqa: E402
from sample import build_sample_data  # noqa: E402

# dashboard palette
LONG = "#D3A24C"
SHORT = "#BD5B45"
STEEL = "#3E5060"
CONFLUENCE = "#5FAE9E"
PAPER = "#ECE8DD"
FONT = "DejaVu Sans"

CMAP = mcolors.LinearSegmentedColormap.from_list(
    "cot", [SHORT, STEEL, LONG], N=256
)


def build_matrix():
    if args.live:
        frames = fetch_market_frames(years=4)
    else:
        frames = build_sample_data()

    sectors = SECTOR_ORDER
    markets = sorted(MARKETS, key=lambda m: sectors.index(m["sector"]))
    n_sector = len(sectors)
    n_market = len(markets)

    data = np.full((n_sector, n_market), np.nan)
    confluent = np.zeros((n_sector, n_market), dtype=bool)
    tickers = []
    for j, meta in enumerate(markets):
        tickers.append(meta["ticker"])
        df = frames.get(meta["code"])
        if df is None or df.empty:
            continue
        row = latest_row(compute_metrics(df))
        if row is None:
            continue
        i = sectors.index(meta["sector"])
        data[i, j] = float(row["spec_pct"])
        confluent[i, j] = bool(row["confluence"])

    return data, confluent, sectors, tickers, markets


def plot(data, confluent, sectors, tickers):
    n_sector, n_market = data.shape
    fig, ax = plt.subplots(figsize=(0.34 * n_market + 2.5, 0.8 * n_sector + 2.0),
                           dpi=150)
    fig.patch.set_facecolor("#0F1720")
    ax.set_facecolor("#16212C")

    # NaN cells -> dark slate
    norm = mcolors.TwoSlopeNorm(vmin=0, vcenter=50, vmax=100)
    ax.imshow(data, cmap=CMAP, norm=norm, aspect="auto",
              interpolation="nearest")

    for i in range(n_sector):
        for j in range(n_market):
            v = data[i, j]
            if np.isnan(v):
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           facecolor="#141F29", edgecolor="#2C3B4A"))
            else:
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        fontsize=8, color="#0F1720", fontweight="bold")
            if confluent[i, j]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                           fill=False, edgecolor=CONFLUENCE, lw=2.5))

    ax.set_xticks(range(n_market))
    ax.set_xticklabels(tickers, rotation=90, fontsize=8, color=PAPER)
    ax.set_yticks(range(n_sector))
    ax.set_yticklabels([f"{s}  ·  {sum(1 for m in MARKETS if m['sector']==s)}"
                        for s in sectors], fontsize=9, color=PAPER)
    ax.set_title("Speculative positioning percentile by sector & market "
                 "(teal outline = confluence)", color=PAPER, fontsize=11)

    for spine in ax.spines.values():
        spine.set_color("#2C3B4A")
    ax.tick_params(colors=PAPER)

    cbar = fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap=CMAP), ax=ax, fraction=0.03, pad=0.02
    )
    cbar.ax.tick_params(colors=PAPER)
    cbar.outline.set_edgecolor("#2C3B4A")
    cbar.set_label("Spec percentile (3y rolling)", color=PAPER)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="COT positioning heatmap.")
    parser.add_argument("--live", action="store_true", help="fetch live CFTC data")
    parser.add_argument("--out", type=str, default="../artifacts/cot_heatmap.png",
                        help="output PNG path")
    args = parser.parse_args()

    data, confluent, sectors, tickers, _ = build_matrix()
    fig = plot(data, confluent, sectors, tickers)
    fig.savefig(args.out, facecolor=fig.get_facecolor())
    print(f"Wrote {args.out}")
