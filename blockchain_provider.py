"""
Lost Bitcoin — Blockchain data provider (Blockstream Esplora API).

This is the ONLY place live blockchain data enters the system.
Everything it returns came from the public API response. If the API
cannot be reached, callers get an exception — never invented data.

Consolidates the API logic that was previously duplicated across
bitcoin_address_investigator.py, bitcoin_address_intelligence.py,
bitcoin_transaction_tracer.py, bitcoin_history_timeline.py and
multiple_address_investigator.py (all stdlib urllib, no extra deps).
"""

import json
import urllib.request
from urllib.error import HTTPError, URLError

BASE_URL = "https://blockstream.info/api"
GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
SATOSHI = 100_000_000


class BlockchainUnavailable(Exception):
    """The blockchain API could not provide data. Nothing is known."""


def _api_request(endpoint):
    request = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        headers={"User-Agent": "LostBitcoinInvestigator/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 400:
            raise BlockchainUnavailable(
                "The blockchain API rejected this address."
            ) from error
        raise BlockchainUnavailable(
            f"Blockchain API error (HTTP {error.code})."
        ) from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise BlockchainUnavailable(
            "Could not reach the blockchain API."
        ) from error


def fetch_address_info(address):
    """
    Return a plain dict of facts reported by the API for one address:
    balance / received / sent in satoshis, confirmed tx count,
    unconfirmed net change, and the most recent confirmed activity
    timestamp (or None). Raises BlockchainUnavailable on any failure.
    """
    data = _api_request(f"/address/{address}")
    try:
        chain = data["chain_stats"]
        mempool = data["mempool_stats"]
    except (KeyError, TypeError) as error:
        raise BlockchainUnavailable(
            "Unexpected response from the blockchain API."
        ) from error

    history = _api_request(f"/address/{address}/txs")
    latest_confirmed = None
    for tx in history or []:
        status = tx.get("status", {})
        if status.get("confirmed") and status.get("block_time"):
            latest_confirmed = status["block_time"]
            break

    received = chain["funded_txo_sum"]
    spent = chain["spent_txo_sum"]
    return {
        "address": address,
        "tx_count": chain["tx_count"],
        "received_satoshis": received,
        "sent_satoshis": spent,
        "balance_satoshis": received - spent,
        "unconfirmed_satoshis": (
            mempool["funded_txo_sum"] - mempool["spent_txo_sum"]
        ),
        "latest_confirmed_timestamp": latest_confirmed,
        "is_genesis_address": address == GENESIS_ADDRESS,
        "source": "blockstream.info",
    }


def _tx_delta_for_address(tx, address):
    """Net satoshi change one transaction caused for one address."""
    delta = 0
    for vout in tx.get("vout", []):
        if vout.get("scriptpubkey_address") == address:
            delta += vout.get("value", 0)
    for vin in tx.get("vin", []):
        prev = vin.get("prevout") or {}
        if prev.get("scriptpubkey_address") == address:
            delta -= prev.get("value", 0)
    return delta


def fetch_balance_on_date(address, date_iso):
    """
    Confirmed balance (satoshis) the address held at the end of
    `date_iso` (YYYY-MM-DD, UTC). Computed as the current confirmed
    balance minus the net effect of every confirmed transaction after
    that date — all from the same public API data. Raises
    BlockchainUnavailable on any failure or if the history is too long
    to page through completely (the figure is then simply not stated,
    never estimated).
    """
    from datetime import datetime, time, timezone

    try:
        day = datetime.strptime(date_iso, "%Y-%m-%d").date()
    except (TypeError, ValueError) as error:
        raise BlockchainUnavailable("Invalid valuation date.") from error
    cutoff = int(datetime.combine(day, time.max, tzinfo=timezone.utc).timestamp())

    info = fetch_address_info(address)
    after_delta = 0
    after_txid = None
    for _page in range(40):
        endpoint = f"/address/{address}/txs"
        if after_txid:
            endpoint += f"?after_txid={after_txid}"
        txs = _api_request(endpoint) or []
        if not txs:
            break
        reached_cutoff = False
        for tx in txs:
            status = tx.get("status", {})
            if not status.get("confirmed"):
                continue
            block_time = status.get("block_time")
            if block_time is None:
                continue
            if block_time <= cutoff:
                reached_cutoff = True
                break
            after_delta += _tx_delta_for_address(tx, address)
        if reached_cutoff or len(txs) < 25:
            break
        after_txid = txs[-1].get("txid")
        if not after_txid:
            break
    else:
        raise BlockchainUnavailable(
            "Address history too long to value on a past date.")
    return info["balance_satoshis"] - after_delta
