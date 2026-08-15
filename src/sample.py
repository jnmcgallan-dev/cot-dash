"""Synthetic sample data generator (mirrors the JS generator in index.html).

Deterministic per market (seeded), so the CLI and heatmap are reproducible.
Sample data is clearly synthetic — used for offline/analytical work and as
the dashboard's offline fallback.
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd

from market_registry import MARKETS

N_WEEKS = 210  # ~4 years


def last_friday(d):
    offset = (d.weekday() - 4) % 7  # days back to Friday (Mon=0 .. Fri=4)
    return d - timedelta(days=offset)


def gen_sample_series(rng, n_weeks=N_WEEKS):
    end = last_friday(date.today())

    spec_drift = (rng.random() - 0.5) * 0.0006
    comm_drift = (rng.random() - 0.5) * 0.0004
    spec_vol = 0.004 + rng.random() * 0.012
    comm_vol = 0.004 + rng.random() * 0.010
    base_oi = 150000 + int(rng.random() * 2000000)
    oi_growth = 0.001 + rng.random() * 0.003
    mean_spec = (rng.random() - 0.5) * 0.10
    mean_comm = -mean_spec * (0.6 + rng.random() * 0.8)

    # regime shifts so a handful of markets reach extremes
    regimes = []
    for _ in range(1 + int(rng.random() * 3)):
        regimes.append((int(rng.random() * n_weeks * 0.8), (rng.random() - 0.5) * 0.24))

    spec_net, comm_net, oi = mean_spec, mean_comm, float(base_oi)
    rows = []
    for i in range(n_weeks):
        for start, level in regimes:
            if i == start:
                spec_net = level

        spec_net += spec_drift + (rng.random() - 0.5) * 2 * spec_vol
        comm_net += comm_drift + (rng.random() - 0.5) * 2 * comm_vol
        comm_net = (
            -spec_net * 0.55
            + (comm_net + spec_net * 0.55) * 0.95
            + (rng.random() - 0.5) * comm_vol * 0.4
        )
        oi *= (1 + oi_growth) * (0.98 + rng.random() * 0.04)

        spec_net = max(-0.45, min(0.45, spec_net))
        comm_net = max(-0.45, min(0.45, comm_net))

        d = end - timedelta(days=(n_weeks - 1 - i) * 7)
        spec_share = 0.5 + spec_net / 2
        comm_share = 0.5 + comm_net / 2

        rows.append(
            {
                "date": d.isoformat(),
                "oi": int(round(oi)),
                "spec_long": int(round(oi * spec_share * (0.10 + rng.random() * 0.12))),
                "spec_short": int(round(oi * (1 - spec_share) * (0.10 + rng.random() * 0.12))),
                "comm_long": int(round(oi * comm_share * (0.14 + rng.random() * 0.12))),
                "comm_short": int(round(oi * (1 - comm_share) * (0.14 + rng.random() * 0.12))),
            }
        )

    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def build_sample_data():
    out = {}
    for idx, meta in enumerate(MARKETS):
        rng = np.random.default_rng(0xC07 + idx * 7919)
        out[meta["code"]] = gen_sample_series(rng)
    return out
