"""
Lost Bitcoin — Central Investigation Controller.

Option B architecture: rules control the investigation, AI assists.
This controller is deterministic. It:
  - reads the Master Investigation Record,
  - decides which steps apply (address checks only when addresses exist,
    lost-Bitcoin assessment only from the customer's own answers),
  - runs the blockchain provider for addresses,
  - saves discoveries, evidence (with confidence classifications),
    recommendations and timeline events back to the record,
  - works out what is still missing and which paid offer, if any,
    the approved pricing allows.

It NEVER invents blockchain data. If the provider fails, the finding
is recorded as UNKNOWN. Customer statements are leads, not proof.
A balance never proves ownership or recoverability.
"""

import master_investigation_record as record
from blockchain_provider import BlockchainUnavailable, fetch_address_info

# --- Approved pricing (USD cents). Do not change without founder approval. ---
INVESTIGATION_REPORT_PRICE_CENTS = 999  # Investigation Report $9.99
GUIDE_PRICE_CENTS = INVESTIGATION_REPORT_PRICE_CENTS  # legacy alias
AI_WALKTHROUGH_PRICE_CENTS = 699        # AI chat bot walkthrough of next steps $6.99
ADDRESS_REPORT_FIRST_CENTS = 499   # First address $4.99
ADDRESS_REPORT_EXTRA_CENTS = 199   # Each additional address $1.99

CONFIRMED = "confirmed"
STRONG = "strong_possibility"
LEAD = "possible_lead"
UNKNOWN = "unknown"


def address_report_price_cents(address_count):
    if address_count <= 0:
        return 0
    return ADDRESS_REPORT_FIRST_CENTS + ADDRESS_REPORT_EXTRA_CENTS * (address_count - 1)


# ---------------------------------------------------------------- addresses
class _Dedup:
    """Tracks what's already in the record so re-running an investigation
    refreshes the caller's view without duplicating saved findings."""

    def __init__(self, full):
        self._disc = {d["description"] for d in full["discoveries"]}
        self._evid = {e["description"] for e in full["evidence"]}
        self._recs = {r["title"] for r in full["recommendations"]}

    def discovery(self, investigation_id, description, source_type="customer_statement"):
        if description in self._disc:
            return None
        self._disc.add(description)
        return record.save_discovery(investigation_id, description, source_type)

    def evidence(self, investigation_id, evidence_type, description, **kw):
        if description in self._evid:
            return None
        self._evid.add(description)
        return record.save_evidence(investigation_id, evidence_type, description, **kw)

    def recommendation(self, investigation_id, title, details, priority="medium"):
        if title in self._recs:
            return None
        self._recs.add(title)
        return record.save_recommendation(investigation_id, title, details, priority)


def run_address_investigation(investigation_id, provider=fetch_address_info):
    """
    Check every saved address for this investigation against the
    blockchain provider. `provider` is injectable for testing.
    Returns a list of per-address result dicts.
    """
    full = record.get_complete_investigation(investigation_id)
    if full is None:
        raise ValueError("Investigation not found.")

    dedup = _Dedup(full)
    results = []
    for entry in full["addresses"]:
        address = entry["address"]
        try:
            info = provider(address)
        except BlockchainUnavailable as error:
            dedup.evidence(
                investigation_id, "blockchain_check",
                f"Address {address}: blockchain check could not be completed ({error}) "
                "No conclusion can be drawn from this attempt.",
                confidence=UNKNOWN,
            )
            results.append({"address": address, "status": "unknown", "info": None})
            continue

        balance_btc = info["balance_satoshis"] / 100_000_000
        dedup.discovery(
            investigation_id,
            f"Blockchain check for {address}: {info['tx_count']} confirmed "
            f"transaction(s), balance {balance_btc:.8f} BTC "
            f"(source: {info['source']}).",
            source_type="blockchain_api",
        )
        if info["is_genesis_address"]:
            dedup.evidence(
                investigation_id, "blockchain_address",
                "This is the Bitcoin Genesis address. Its original 50 BTC block "
                "reward is permanently unspendable and must not be treated as "
                "recoverable Bitcoin.",
                confidence=CONFIRMED, verification_status="verified",
            )
        elif info["tx_count"] == 0:
            dedup.evidence(
                investigation_id, "blockchain_address",
                f"Address {address} has no confirmed blockchain activity. "
                "This address itself holds no Bitcoin history we can act on; "
                "it may be unused, or the customer may be remembering a different address.",
                confidence=CONFIRMED, verification_status="verified",
            )
            dedup.recommendation(
                investigation_id,
                "Double-check this address",
                "The address is valid but has never been used on-chain. Ask the "
                "customer to re-check the source (old wallet, email, exchange "
                "withdrawal record) for the exact address.",
                priority="medium",
            )
        else:
            dedup.evidence(
                investigation_id, "blockchain_address",
                f"Address {address} has confirmed blockchain activity: "
                f"{info['tx_count']} transaction(s), confirmed balance "
                f"{balance_btc:.8f} BTC. A balance does not prove the customer "
                "owns this address or can access it.",
                confidence=CONFIRMED, verification_status="verified",
            )
            if info["balance_satoshis"] > 0 and not info["is_genesis_address"]:
                dedup.recommendation(
                    investigation_id,
                    "Work out how this address was controlled",
                    "A positive confirmed balance remains. The next step is "
                    "identifying the wallet, device, backup or exchange account "
                    "that controlled this address — not moving any funds.",
                    priority="high",
                )
        results.append({"address": address, "status": "checked", "info": info})
    return results


# ------------------------------------------------------------ lost bitcoin
# Rules over the questionnaire answers (keys from index.html + free text).
_LEAD_SIGNALS = {
    "device": ("Yes", "I have an external drive or backup"),
    "records": ("Purchase confirmation emails", "Bank or credit card statements",
                "Transaction IDs or wallet addresses", "Several of these"),
    "account": ("Yes", "I haven't tried"),
}


def _compute_leads(full):
    """
    Read-only lead computation shared by the assessment and by checkout
    eligibility: which credible leads do this record's own answers and
    addresses support right now? Returns (leads, missing, latest).
    """
    latest = {}
    for answer in full["answers"]:
        latest[answer["question_key"]] = answer["answer_value"]

    leads, missing = [], []
    for key, good_values in _LEAD_SIGNALS.items():
        value = latest.get(key)
        if value is None:
            missing.append(key)
        elif any(v in value for v in good_values):
            leads.append(key)

    if full["addresses"]:
        leads.append("bitcoin_address")
    if latest.get("exchange") and "not sure" not in latest["exchange"].lower():
        leads.append("exchange_named")
    return leads, missing, latest


def has_credible_lead(investigation_id):
    """
    True when the record currently supports a credible lead — the same
    test the assessment uses before offering any paid product. Checkout
    enforces it server-side so a report is never sold without one.
    """
    full = record.get_complete_investigation(investigation_id)
    if full is None:
        raise ValueError("Investigation not found.")
    leads, _missing, _latest = _compute_leads(full)
    return bool(leads)


def assess_lost_bitcoin(investigation_id):
    """
    Rules-based preliminary assessment from the customer's own answers.
    Everything from the customer is a POSSIBLE LEAD at best — none of it
    is confirmed until checked against records or the blockchain.
    Returns a summary dict and saves recommendations + the assessment
    as a discovery/evidence trail.
    """
    full = record.get_complete_investigation(investigation_id)
    if full is None:
        raise ValueError("Investigation not found.")

    leads, missing, latest = _compute_leads(full)

    credible_lead = bool(leads)

    dedup = _Dedup(full)
    if "device" in leads:
        dedup.recommendation(
            investigation_id, "Preserve the original device or backup",
            "Do not wipe, update or keep using a device that may hold a wallet. "
            "Make a copy first and work from the copy.", priority="high")
    if "records" in leads:
        dedup.recommendation(
            investigation_id, "Gather the records you mentioned",
            "Purchase confirmations, statements or transaction IDs can pin down "
            "dates, exchanges and addresses — the strongest starting evidence.",
            priority="high")
    if "exchange_named" in leads or "account" in leads:
        dedup.recommendation(
            investigation_id, "Try the original account first",
            "Attempt sign-in / account recovery with the original email before "
            "assuming the Bitcoin left the exchange.", priority="medium")
    if missing:
        dedup.recommendation(
            investigation_id, "Answer the remaining questions",
            "Still unknown: " + ", ".join(sorted(missing)) +
            ". Each answer narrows the search.", priority="low")

    dedup.evidence(
        investigation_id, "preliminary_assessment",
        "Preliminary assessment is based only on the customer's own answers. "
        + ("Credible lead(s) identified: " + ", ".join(leads) + "."
           if credible_lead else
           "No credible actionable lead identified yet from the answers so far."),
        confidence=LEAD if credible_lead else UNKNOWN,
    )

    return {
        "investigation_id": investigation_id,
        "credible_lead": credible_lead,
        "leads": leads,
        "missing_information": sorted(missing),
        "investigation_report_offer_cents": (
            INVESTIGATION_REPORT_PRICE_CENTS if credible_lead else None
        ),
        "guide_offer_cents": GUIDE_PRICE_CENTS if credible_lead else None,
        # AI walkthrough is offered once there are recommendations to walk
        # through (i.e. alongside/after the investigation report).
        "ai_walkthrough_offer_cents": (
            AI_WALKTHROUGH_PRICE_CENTS if credible_lead else None
        ),
        "address_report_offer_cents": (
            address_report_price_cents(len(full["addresses"]))
            if full["addresses"] else None
        ),
    }


def run_investigation(investigation_id, provider=fetch_address_info):
    """Run every step that applies to this investigation, in order."""
    full = record.get_complete_investigation(investigation_id)
    if full is None:
        raise ValueError("Investigation not found.")
    outcome = {"investigation_id": investigation_id}
    if full["addresses"]:
        outcome["address_results"] = run_address_investigation(
            investigation_id, provider=provider)
    if full["starting_point"] == "lost_bitcoin" or full["answers"]:
        outcome["assessment"] = assess_lost_bitcoin(investigation_id)
    return outcome
