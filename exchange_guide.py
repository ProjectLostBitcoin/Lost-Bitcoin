"""
Lost Bitcoin — Exchange suggestion guide.

Founder direction (2026-11-12): "location matters" — when a customer
can't remember which exchange they used, suggest the exchanges that
were actually popular in their country (and, where notable, their
region) during the era they bought.

Honesty rules:
- Suggestions are POSSIBLE LEADS, never findings. The UI labels them
  as guesses, and picking one is recorded as the customer's own answer.
- Defunct exchanges are first-class suggestions: for many customers
  (QuadrigaCX in Canada, Mt. Gox globally) the exchange being gone IS
  the story, and it changes the recommended path.
- The dataset is curated and conservative: well-known exchanges, the
  years they operated, and a one-line note only where the status is
  material (shut down, collapsed, merged).

Eras match the questionnaire's year options in index.html.
"""

ERAS = {
    "2009–2011": (2009, 2011),
    "2012–2013": (2012, 2013),
    "2014–2015": (2014, 2015),
    "2016–2017": (2016, 2017),
    "2018–2020": (2018, 2020),
    "2021 or later": (2021, 2100),
}
ALL_YEARS = (2009, 2100)

EU_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE",
    "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT",
    "RO", "SK", "SI", "ES", "SE",
}

# name, first_year, last_year (None = still operating), scope, note
# scope: "GLOBAL", a country code ("CA"), "EU", or ("CA", "British Columbia")
_EXCHANGES = [
    # ---- global / widely available
    ("Mt. Gox", 2010, 2014, "GLOBAL",
     "Collapsed in 2014 — the biggest exchange of the early years."),
    ("LocalBitcoins", 2012, 2023, "GLOBAL",
     "Peer-to-peer marketplace — many early purchases happened here. Closed in 2023."),
    ("Bitstamp", 2011, None, "GLOBAL", ""),
    ("Kraken", 2011, None, "GLOBAL", ""),
    ("Coinbase", 2012, None, "GLOBAL", ""),
    ("Bitfinex", 2012, None, "GLOBAL", ""),
    ("BTC-e", 2011, 2017, "GLOBAL",
     "Shut down by authorities in 2017."),
    ("Poloniex", 2014, None, "GLOBAL", ""),
    ("Bittrex", 2014, 2023, "GLOBAL",
     "Shut down in 2023."),
    ("Binance", 2017, None, "GLOBAL", ""),

    # ---- Canada
    ("QuadrigaCX", 2013, 2019, "CA",
     "Shut down in 2019 — if your Bitcoin was here, the path runs through "
     "the bankruptcy claims process."),
    ("Coinsquare", 2014, None, "CA",
     "Now part of WonderFi (merged in 2023)."),
    ("Canadian Bitcoins", 2012, None, "CA", ""),
    ("Bitbuy", 2016, None, "CA", ""),
    ("MyBTC.ca", 2016, None, "CA", ""),
    ("Newton", 2018, None, "CA", ""),
    ("VirgoCX", 2018, None, "CA", ""),
    ("Einstein Exchange", 2017, 2019, ("CA", "British Columbia"),
     "Vancouver-based — shut down in 2019."),

    # ---- United States
    ("Gemini", 2014, None, "US", ""),
    ("Binance.US", 2019, None, "US",
     "The US arm of Binance — US customers were moved here in 2019."),

    # ---- United Kingdom
    ("CEX.IO", 2013, None, "GB", ""),
    ("Coinfloor", 2013, 2021, "GB",
     "UK exchange — closed in 2021."),

    # ---- Europe
    ("bitcoin.de", 2011, None, "EU", ""),
    ("BTC Direct", 2013, None, "EU", ""),
    ("Bitpanda", 2014, None, "EU", ""),
    ("Zonda (formerly BitBay)", 2014, None, "EU", ""),
    ("Anycoin Direct", 2015, None, "EU", ""),

    # ---- Australia
    ("CoinJar", 2013, None, "AU", ""),
    ("CoinSpot", 2013, None, "AU", ""),
    ("BTC Markets", 2013, None, "AU", ""),
    ("Independent Reserve", 2013, None, "AU", ""),
    ("Swyftx", 2018, None, "AU", ""),

    # ---- Japan
    ("bitFlyer", 2014, None, "JP", ""),
    ("Coincheck", 2014, None, "JP", ""),
    ("Zaif", 2014, 2018, "JP",
     "Hacked in 2018 and taken over by another company."),

    # ---- South Korea
    ("Bithumb", 2013, None, "KR", ""),
    ("Korbit", 2013, None, "KR", ""),
    ("Coinone", 2014, None, "KR", ""),
    ("Upbit", 2017, None, "KR", ""),

    # ---- India
    ("Unocoin", 2013, None, "IN", ""),
    ("ZebPay", 2014, None, "IN",
     "Left India in 2019 and later returned."),
    ("Koinex", 2017, 2019, "IN",
     "Shut down in 2019."),
    ("WazirX", 2018, None, "IN",
     "Suffered a major hack in 2024."),
    ("CoinDCX", 2018, None, "IN", ""),

    # ---- Brazil
    ("Mercado Bitcoin", 2013, None, "BR", ""),
    ("Foxbit", 2014, None, "BR", ""),
    ("NovaDAX", 2018, None, "BR", ""),
]


def era_range(era_label):
    """Map a questionnaire era label to (first_year, last_year)."""
    return ERAS.get(era_label or "", ALL_YEARS)


def _active_in(entry, years):
    _, first, last, _, _ = entry
    y0, y1 = years
    return first <= y1 and (last is None or last >= y0)


def suggest(country_code="", region="", era_label="", limit=8):
    """
    Ordered suggestions: region-specific first, then country (or EU),
    then global — each filtered to exchanges active in the era.
    Returns a list of {"name", "note", "status"} dicts.
    """
    years = era_range(era_label)
    country_code = (country_code or "").upper()

    def bucket(scope):
        out = []
        for entry in _EXCHANGES:
            name, _, last, esc, note = entry
            if esc == scope and _active_in(entry, years):
                out.append({
                    "name": name,
                    "note": note,
                    "status": "defunct" if last is not None and last < 2025
                              else "operating",
                })
        return out

    regional = bucket((country_code, region)) if region else []
    if country_code in EU_COUNTRIES:
        national = bucket(country_code) + bucket("EU")
    elif country_code:
        national = bucket(country_code)
    else:
        national = []
    global_ = bucket("GLOBAL")

    seen, ordered = set(), []
    for group in (regional, national, global_):
        for item in group:
            if item["name"] not in seen:
                seen.add(item["name"])
                ordered.append(item)
    return ordered[:limit]


def suggestions_payload(geo, era_label):
    """
    Build the API payload. `geo` is {"country_code", "country_name",
    "region"} or None (detection failed / private network).
    """
    geo = geo or {}
    return {
        "detected": {
            "country_code": geo.get("country_code", ""),
            "country_name": geo.get("country_name", ""),
            "region": geo.get("region", ""),
        } if geo else None,
        "era": era_label or "",
        "suggestions": suggest(
            geo.get("country_code", ""), geo.get("region", ""), era_label),
        "note": ("Suggestions are based on the country detected from "
                 "your connection and the era you picked. They are "
                 "possible leads, not conclusions."),
    }
