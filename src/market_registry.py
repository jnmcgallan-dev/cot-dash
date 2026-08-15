"""Market registry — single source of truth shared by CLI, notebook and heatmap.

Ticker -> CFTC Legacy (Futures-Only) contract code -> sector.

NOTE: verify codes against the live CFTC report; legacy contract codes can
shift over time. A stale code returns no data for that market only.
"""

MARKETS = [
    # FX (9)
    {"ticker": "EUR", "name": "Euro FX",              "code": "099741", "sector": "FX"},
    {"ticker": "GBP", "name": "British Pound",        "code": "096742", "sector": "FX"},
    {"ticker": "JPY", "name": "Japanese Yen",         "code": "097741", "sector": "FX"},
    {"ticker": "CHF", "name": "Swiss Franc",          "code": "092741", "sector": "FX"},
    {"ticker": "CAD", "name": "Canadian Dollar",      "code": "090741", "sector": "FX"},
    {"ticker": "AUD", "name": "Australian Dollar",    "code": "232741", "sector": "FX"},
    {"ticker": "MXN", "name": "Mexican Peso",         "code": "095741", "sector": "FX"},
    {"ticker": "BRL", "name": "Brazilian Real",       "code": "102741", "sector": "FX"},
    {"ticker": "NZD", "name": "New Zealand Dollar",   "code": "112741", "sector": "FX"},
    # Rates (7)
    {"ticker": "TU",  "name": "2-Year T-Note",        "code": "042601", "sector": "Rates"},
    {"ticker": "FV",  "name": "5-Year T-Note",        "code": "044601", "sector": "Rates"},
    {"ticker": "TY",  "name": "10-Year T-Note",       "code": "043602", "sector": "Rates"},
    {"ticker": "US",  "name": "30-Year T-Bond",       "code": "020601", "sector": "Rates"},
    {"ticker": "UB",  "name": "Ultra T-Bond",         "code": "020604", "sector": "Rates"},
    {"ticker": "FF",  "name": "30-Day Federal Funds", "code": "045601", "sector": "Rates"},
    {"ticker": "SR3", "name": "3-Month SOFR",         "code": "134741", "sector": "Rates"},
    # Equities (5)
    {"ticker": "ES",  "name": "E-mini S&P 500",       "code": "13874A", "sector": "Equities"},
    {"ticker": "NQ",  "name": "NASDAQ-100 (Consol.)", "code": "20974+", "sector": "Equities"},
    {"ticker": "YM",  "name": "E-mini Dow Jones",     "code": "124603", "sector": "Equities"},
    {"ticker": "RTY", "name": "Russell 2000",         "code": "239742", "sector": "Equities"},
    {"ticker": "NKD", "name": "Nikkei 225",           "code": "240743", "sector": "Equities"},
    # Energy (5)
    {"ticker": "CL",  "name": "WTI Crude Oil",        "code": "067651", "sector": "Energy"},
    {"ticker": "HO",  "name": "ULSD Heating Oil",     "code": "022651", "sector": "Energy"},
    {"ticker": "RB",  "name": "RBOB Gasoline",        "code": "111659", "sector": "Energy"},
    {"ticker": "NG",  "name": "Natural Gas",          "code": "023651", "sector": "Energy"},
    {"ticker": "BZ",  "name": "Brent (Last Day)",     "code": "06765T", "sector": "Energy"},
    # Metals (5)
    {"ticker": "GC",  "name": "Gold",                 "code": "088691", "sector": "Metals"},
    {"ticker": "SI",  "name": "Silver",               "code": "084691", "sector": "Metals"},
    {"ticker": "HG",  "name": "Copper (COMEX)",       "code": "085692", "sector": "Metals"},
    {"ticker": "PL",  "name": "Platinum",             "code": "076651", "sector": "Metals"},
    {"ticker": "PA",  "name": "Palladium",            "code": "075651", "sector": "Metals"},
    # Ag (10)
    {"ticker": "C",   "name": "Corn",                 "code": "002602", "sector": "Ag"},
    {"ticker": "S",   "name": "Soybeans",             "code": "005602", "sector": "Ag"},
    {"ticker": "BO",  "name": "Soybean Oil",          "code": "007601", "sector": "Ag"},
    {"ticker": "SM",  "name": "Soybean Meal",         "code": "026603", "sector": "Ag"},
    {"ticker": "W",   "name": "Chicago SRW Wheat",    "code": "001602", "sector": "Ag"},
    {"ticker": "KW",  "name": "KC Hard Red Wheat",    "code": "001612", "sector": "Ag"},
    {"ticker": "CT",  "name": "Cotton",               "code": "033661", "sector": "Ag"},
    {"ticker": "SB",  "name": "Sugar #11 (World)",    "code": "080732", "sector": "Ag"},
    {"ticker": "KC",  "name": "Coffee",               "code": "083731", "sector": "Ag"},
    {"ticker": "LC",  "name": "Live Cattle",          "code": "057642", "sector": "Ag"},
]

SECTOR_NAMES = {
    "FX": "Foreign Exchange",
    "Rates": "Interest Rates",
    "Equities": "Equity Indices",
    "Energy": "Energy",
    "Metals": "Metals",
    "Ag": "Agriculture",
}

SECTOR_ORDER = ["FX", "Rates", "Equities", "Energy", "Metals", "Ag"]

CODES = [m["code"] for m in MARKETS]
