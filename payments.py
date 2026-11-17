"""
Lost Bitcoin — Payments (Priority 4, prepared for Stripe).

Products and prices come from investigation_controller (Mark's approved
pricing — the single source of truth):
  investigation_report  $9.99
  ai_walkthrough        $6.99
  wallet_report         $4.99 first address + $1.99 each additional

Two modes:
  LIVE (Stripe): if STRIPE_SECRET_KEY is set, create_checkout() creates
  a real Stripe Checkout Session (test-mode key = test money) and the
  purchase is recorded ONLY when Stripe's webhook calls back and the
  signature verifies. Card details never touch this server.
  DEMO: if no Stripe key is configured, create_checkout() returns a
  demo checkout so the full purchase flow can be reviewed end-to-end.
  Demo purchases are recorded with a 'demo_' payment reference and are
  unmistakably not real money. Demo mode disables itself the moment a
  Stripe key is configured.
"""

import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request

import master_investigation_record as record
import investigation_controller as controller

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
# Stripe Tax (GST) — decided by Mark 2026-11-14. Automatic tax is only
# requested from Stripe when this flag is on, because Stripe rejects
# sessions with automatic_tax until Stripe Tax is activated in the
# dashboard. Off = checkout behaves exactly as before.
STRIPE_TAX_ENABLED = os.environ.get("STRIPE_TAX_ENABLED", "") == "1"

# Optional Stripe catalogue products (created per environment — sandbox
# and live have different IDs). When set, checkout attaches the amount
# to the real product instead of creating a throwaway product per sale.
STRIPE_PRODUCT_IDS = {
    "investigation_report": os.environ.get("STRIPE_PRODUCT_INVESTIGATION_REPORT", ""),
    "ai_walkthrough": os.environ.get("STRIPE_PRODUCT_AI_WALKTHROUGH", ""),
    "wallet_report": os.environ.get("STRIPE_PRODUCT_WALLET_REPORT", ""),
}
DEMO_SECRET = os.environ.get("LOST_BITCOIN_SECRET", "DEV-ONLY-CHANGE-ME").encode()

PRODUCTS = {
    "investigation_report": {
        "name": "Lost Bitcoin — Investigation Report",
        "amount_cents": controller.INVESTIGATION_REPORT_PRICE_CENTS,
    },
    "ai_walkthrough": {
        "name": "Lost Bitcoin — AI Guided Next Steps",
        "amount_cents": controller.AI_WALKTHROUGH_PRICE_CENTS,
    },
    "wallet_report": {
        "name": "Lost Bitcoin — Wallet Report",
        "amount_cents": None,  # depends on address count
    },
}


def stripe_configured():
    return bool(STRIPE_SECRET_KEY)


def price_for(product, address_count=0):
    if product == "wallet_report":
        if address_count < 1:
            raise ValueError("A Wallet Report needs at least one address.")
        return controller.address_report_price_cents(address_count)
    if product not in PRODUCTS:
        raise ValueError("Unknown product.")
    return PRODUCTS[product]["amount_cents"]


def _demo_token(investigation_id, product, amount):
    payload = f"{investigation_id}.{product}.{amount}.{int(time.time()) + 3600}"
    sig = hmac.new(DEMO_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def verify_demo_token(token):
    try:
        inv, product, amount, expiry, sig = token.split(".")
        payload = f"{inv}.{product}.{amount}.{expiry}"
        expected = hmac.new(DEMO_SECRET, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig) or int(expiry) < int(time.time()):
            return None
        return {"investigation_id": inv, "product": product, "amount_cents": int(amount)}
    except (ValueError, AttributeError):
        return None


def build_session_form(investigation_id, customer_id, product, amount,
                       customer_email="", success_url="", cancel_url=""):
    """
    The Checkout Session payload, built as a pure function so it can be
    tested without Stripe keys. Best practices applied:
    - hosted Checkout (card details never touch our server)
    - success_url carries {CHECKOUT_SESSION_ID} so the customer's return
      can be matched to the session (the purchase itself is only ever
      recorded from the verified webhook, never from the redirect)
    - metadata mirrors onto the PaymentIntent for dashboard/refund lookups
    - the customer's email is prefilled when we already know it
    """
    form = {
        "mode": "payment",
        "success_url": success_url or
            "https://lostbitcoin.org/?paid=1&session_id={CHECKOUT_SESSION_ID}",
        "cancel_url": cancel_url or "https://lostbitcoin.org/",
        "line_items[0][quantity]": "1",
        "line_items[0][price_data][currency]": "usd",
        "line_items[0][price_data][unit_amount]": str(amount),
        "line_items[0][price_data][product_data][name]": PRODUCTS[product]["name"],
        "metadata[investigation_id]": investigation_id,
        "metadata[customer_id]": customer_id,
        "metadata[product]": product,
        "payment_intent_data[metadata][investigation_id]": investigation_id,
        "payment_intent_data[metadata][customer_id]": customer_id,
        "payment_intent_data[metadata][product]": product,
    }
    if STRIPE_PRODUCT_IDS.get(product):
        del form["line_items[0][price_data][product_data][name]"]
        form["line_items[0][price_data][product]"] = STRIPE_PRODUCT_IDS[product]
    if customer_email:
        form["customer_email"] = customer_email
    if STRIPE_TAX_ENABLED:
        # Stripe Tax computes GST by the customer's location; Checkout
        # needs a billing address to place the customer. Prices stay as
        # listed and tax is added on top (dashboard default tax code and
        # exclusive tax behavior apply to the inline product).
        form["automatic_tax[enabled]"] = "true"
        form["billing_address_collection"] = "required"
    return form


def idempotency_key(investigation_id, product, amount):
    """One checkout per investigation+product+amount within Stripe's
    24h idempotency window: a double-click or a retried request returns
    the same session instead of creating duplicates. Safe here because
    each product is sold once per investigation (enforced by gating)."""
    raw = f"lostbitcoin:{investigation_id}:{product}:{amount}"
    return hashlib.sha256(raw.encode()).hexdigest()


def create_checkout(investigation_id, customer_id, product, address_count=0,
                    success_url="", cancel_url="", customer_email=""):
    """Return {'mode': 'stripe', 'url': ...} or {'mode': 'demo', 'demo_token': ...}."""
    amount = price_for(product, address_count)
    if stripe_configured():
        form = build_session_form(investigation_id, customer_id, product, amount,
                                  customer_email=customer_email,
                                  success_url=success_url, cancel_url=cancel_url)
        request = urllib.request.Request(
            "https://api.stripe.com/v1/checkout/sessions",
            data=urllib.parse.urlencode(form).encode(),
            headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}",
                     "Idempotency-Key": idempotency_key(investigation_id, product, amount)},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            session = json.loads(response.read().decode())
        return {"mode": "stripe", "url": session["url"], "amount_cents": amount}
    return {
        "mode": "demo",
        "demo_token": _demo_token(investigation_id, product, amount),
        "amount_cents": amount,
        "product_name": PRODUCTS[product]["name"],
    }


def complete_demo_payment(demo_token, customer_id):
    """Record a demo purchase. Refuses to run once Stripe is configured."""
    if stripe_configured():
        raise ValueError("Demo payments are disabled when Stripe is configured.")
    data = verify_demo_token(demo_token)
    if data is None:
        raise ValueError("Invalid or expired demo checkout.")
    return record.save_purchase(
        customer_id, data["product"], data["amount_cents"],
        investigation_id=data["investigation_id"], currency="USD",
        status="completed",
        payment_provider_reference="demo_" + hashlib.sha256(demo_token.encode()).hexdigest()[:24],
    )


def verify_stripe_signature(raw_body, signature_header, secret=None, tolerance=300):
    """Standard Stripe webhook signature check (HMAC-SHA256, stdlib only)."""
    secret = secret if secret is not None else STRIPE_WEBHOOK_SECRET
    if not secret or not signature_header:
        return False
    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        timestamp, signature = parts["t"], parts["v1"]
        if abs(int(time.time()) - int(timestamp)) > tolerance:
            return False
        signed = f"{timestamp}.".encode() + raw_body
        expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    except (ValueError, KeyError):
        return False


# Diagnostic snapshot of the most recent webhook event, filled in by
# handle_stripe_event / _session_from_event and surfaced (secret-gated)
# via /api/stats, so the operator can see exactly what Stripe delivered
# and why an event did or did not record. Contains no secrets: event
# type, payload shape, payment status, metadata key names, our own
# product key and the session ID's last characters only.
LAST_EVENT_DIAG = {}


def _note_diag(**fields):
    LAST_EVENT_DIAG.update(fields)


def _fetch_checkout_session(session_id):
    """Fetch the full Checkout Session from Stripe's API, server-side
    with our secret key. Used when a webhook arrives in Stripe's short
    'thin' payload style, which carries only the session's ID.
    A failed fetch raises, so the webhook answers 500 and Stripe
    retries later instead of the payment being silently dropped."""
    request = urllib.request.Request(
        "https://api.stripe.com/v1/checkout/sessions/" + urllib.parse.quote(session_id),
        headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode())


def _session_from_event(event):
    """Return the event's full Checkout Session object. Snapshot
    payloads already carry it; thin payloads carry only an ID (either
    as a bare object or as data.related_object), so fetch the rest
    from Stripe. Without a key or an ID there is nothing to fetch —
    the partial object is returned and the caller treats the event
    as not recordable."""
    data = event.get("data", {})
    _note_diag(data_keys=sorted(data.keys()))
    session = data.get("object") or {}
    if session.get("payment_status") is not None and "metadata" in session:
        _note_diag(payload_shape="snapshot")
        return session
    session_id = session.get("id") or (data.get("related_object") or {}).get("id")
    _note_diag(payload_shape="thin", session_id_found=bool(session_id))
    if not session_id or not stripe_configured():
        _note_diag(fetch="skipped")
        return session
    try:
        full = _fetch_checkout_session(session_id)
    except Exception as error:
        _note_diag(fetch="failed", fetch_error=error.__class__.__name__)
        raise
    _note_diag(fetch="ok")
    return full


def handle_stripe_event(event):
    """Record a purchase for a verified checkout.session.completed event.
    Duplicate deliveries are safely rejected by the record module."""
    global LAST_EVENT_DIAG
    LAST_EVENT_DIAG = {
        "event_type": event.get("type"),
        "livemode": event.get("livemode"),
        "event_keys": sorted(event.keys()),
    }
    if event.get("type") != "checkout.session.completed":
        _note_diag(outcome="ignored_event_type")
        return None
    session = _session_from_event(event)
    meta = session.get("metadata") or {}
    _note_diag(
        session_id_tail=(session.get("id") or "")[-10:],
        payment_status=session.get("payment_status"),
        amount_total=session.get("amount_total"),
        metadata_keys=sorted(meta.keys()),
        product=meta.get("product"),
        has_customer_id=bool(meta.get("customer_id")),
        has_investigation_id=bool(meta.get("investigation_id")),
    )
    if session.get("payment_status") != "paid":
        _note_diag(outcome="not_paid")
        return None
    if not meta.get("customer_id") or not meta.get("product"):
        # A paid session without our metadata is not one of our sales
        # (e.g. a session created by another tool on the same account).
        # Acknowledge it instead of erroring, so Stripe stops retrying.
        _note_diag(outcome="missing_metadata")
        return None
    _note_diag(outcome="record_attempted")
    result = record.save_purchase(
        meta["customer_id"], meta["product"],
        int(session["amount_total"]),
        investigation_id=meta.get("investigation_id") or None,
        currency=(session.get("currency") or "usd").upper(),
        status="completed",
        payment_provider_reference=session["id"],
    )
    _note_diag(outcome="recorded")
    return result


def has_purchased(investigation_id, product):
    full = record.get_complete_investigation(investigation_id)
    if full is None:
        return False
    return any(p["product"] == product and p["status"] == "completed"
               for p in full["purchases"])
