"""Metric engine — mirrors cot-dash/index.html computeMetrics().

For each market, per week (causal — trailing window only), computed for
spec (non-commercial), commercial, and non-reportable:
  1. net position      = long - short
  2. OI normalization  = net / open interest
  3. rolling z-score   = (x - mean) / std, 156-week window, min 52 weeks
  4. rolling percentile = rank of x within trailing 156-week window
  5. extreme           = pct >= 90 -> "L" (Extreme Long), <= 10 -> "S", else "N"
  6. confluence        = spec & commercial extremes in opposing directions
                         (non-reportable is context only, not part of this —
                         it isn't the "smart money" side of the classic
                         spec-vs-hedger contrarian setup)
  7. WoW change        = this week's net% - last week's, in percentage points
"""

import numpy as np
import pandas as pd

WINDOW = 156
MIN_HISTORY = 52
EXT_HI = 90.0
EXT_LO = 10.0


def _pctile(values):
    s = np.asarray(values, dtype=float)
    return float((s <= s[-1]).mean() * 100.0)


def _z(values):
    s = np.asarray(values, dtype=float)
    std = s.std(ddof=0)
    if std == 0:
        return 0.0
    return float((s[-1] - s.mean()) / std)


def compute_metrics(df):
    """Compute all metrics for one market's weekly frame.

    Parameters
    ----------
    df : pandas.DataFrame
        Sorted (or unsorted) rows with columns:
        date, oi, spec_long, spec_short, comm_long, comm_short

    Returns
    -------
    pandas.DataFrame
        Input frame plus metric columns. Rows before MIN_HISTORY weeks have
        NaN metric values (None when read via latest_row()).
    """
    df = df.sort_values("date").reset_index(drop=True).copy()
    oi = df["oi"].replace(0, 1)

    spec_net = df["spec_long"] - df["spec_short"]
    comm_net = df["comm_long"] - df["comm_short"]
    nonrept_long = df["nonrept_long"] if "nonrept_long" in df else 0
    nonrept_short = df["nonrept_short"] if "nonrept_short" in df else 0
    nonrept_net = nonrept_long - nonrept_short

    df["spec_net_contracts"] = spec_net
    df["comm_net_contracts"] = comm_net
    df["nonrept_net_contracts"] = nonrept_net
    df["spec_net_pct"] = spec_net / oi * 100.0
    df["comm_net_pct"] = comm_net / oi * 100.0
    df["nonrept_net_pct"] = nonrept_net / oi * 100.0

    spec_roll = df["spec_net_pct"].rolling(WINDOW, min_periods=MIN_HISTORY)
    comm_roll = df["comm_net_pct"].rolling(WINDOW, min_periods=MIN_HISTORY)
    nonrept_roll = df["nonrept_net_pct"].rolling(WINDOW, min_periods=MIN_HISTORY)

    df["spec_pct"] = spec_roll.apply(_pctile, raw=True)
    df["comm_pct"] = comm_roll.apply(_pctile, raw=True)
    df["nonrept_pct"] = nonrept_roll.apply(_pctile, raw=True)
    df["spec_z"] = spec_roll.apply(_z, raw=True)
    df["comm_z"] = comm_roll.apply(_z, raw=True)
    df["nonrept_z"] = nonrept_roll.apply(_z, raw=True)

    def _ext(p):
        if pd.isna(p):
            return None
        if p >= EXT_HI:
            return "L"
        if p <= EXT_LO:
            return "S"
        return "N"

    df["spec_extreme"] = df["spec_pct"].apply(_ext)
    df["comm_extreme"] = df["comm_pct"].apply(_ext)
    # Context only — NOT part of confluence (see confluence definition below).
    df["nonrept_extreme"] = df["nonrept_pct"].apply(_ext)

    both = df["spec_extreme"].notna()
    df["confluence"] = False
    df.loc[both, "confluence"] = (
        ((df.loc[both, "spec_extreme"] == "L") & (df.loc[both, "comm_extreme"] == "S"))
        | ((df.loc[both, "spec_extreme"] == "S") & (df.loc[both, "comm_extreme"] == "L"))
    )

    df["spec_wow"] = df["spec_net_pct"].diff()
    df["comm_wow"] = df["comm_net_pct"].diff()
    df["nonrept_wow"] = df["nonrept_net_pct"].diff()
    return df


def latest_row(df):
    """Return the most recent row with a computed percentile, or None."""
    m = df.dropna(subset=["spec_pct"])
    return m.iloc[-1] if len(m) else None
