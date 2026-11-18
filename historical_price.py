"""
Lost Bitcoin — Historical Bitcoin price lookup.

Used only for dated valuations in reports (e.g. an estate's date of
death). Primary source: Coinbase's public daily candle for BTC-USD
(full history, no key) converted at the Bank of Canada's official
daily USD/CAD rate. Fallback: CoinGecko's public history endpoint
(free tier covers roughly the last 365 days). Returns the real
published price for the date, or None when it cannot be retrieved —
callers must then omit the fiat figure entirely, never estimate one.
"""

import json
import urllib.request
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError

_CACHE = {}
_SOURCE_LABEL = "Coinbase daily close, Bank of Canada USD/CAD rate"


def _get_json(url):
    request = urllib.request.Request(
        url, headers={"User-Agent": "LostBitcoinInvestigator/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _coinbase_usd_close(day):
    start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    url = ("https://api.exchange.coinbase.com/products/BTC-USD/candles"
           f"?granularity=86400&start={start.strftime('%Y-%m-%dT%H:%M:%SZ')}"
           f"&end={end.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    candles = _get_json(url)
    target = int(start.timestamp())
    for candle in candles:
        # [time, low, high, open, close, volume]
        if int(candle[0]) == target:
            return float(candle[4])
    return None


def _bank_of_canada_rate(day):
    start = day - timedelta(days=10)
    url = ("https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json"
           f"?start_date={start.isoformat()}&end_date={day.isoformat()}")
    data = _get_json(url)
    best = None
    for obs in data.get("observations", []):
        if obs.get("d", "") <= day.isoformat():
            value = (obs.get("FXUSDCAD") or {}).get("v")
            if value:
                best = float(value)
    return best


def _coingecko(day):
    url = ("https://api.coingecko.com/api/v3/coins/bitcoin/history"
           f"?date={day.strftime('%d-%m-%Y')}")
    data = _get_json(url)
    prices = data["market_data"]["current_price"]
    return {"cad": float(prices["cad"]), "usd": float(prices["usd"]),
            "source": "coingecko.com"}


def price_on(date_iso):
    """
    Return {"cad": float, "usd": float, "source": str} for YYYY-MM-DD,
    or None if the price cannot be retrieved from any source.
    """
    if date_iso in _CACHE:
        return _CACHE[date_iso]
    result = None
    try:
        day = datetime.strptime(date_iso, "%Y-%m-%d").date()
        usd = _coinbase_usd_close(day)
        rate = _bank_of_canada_rate(day) if usd else None
        if usd and rate:
            result = {"cad": usd * rate, "usd": usd, "source": _SOURCE_LABEL}
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError,
            KeyError, TypeError, ValueError, IndexError):
        result = None
    if result is None:
        try:
            day = datetime.strptime(date_iso, "%Y-%m-%d").date()
            result = _coingecko(day)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError,
                KeyError, TypeError, ValueError):
            result = None
    _CACHE[date_iso] = result
    return result
