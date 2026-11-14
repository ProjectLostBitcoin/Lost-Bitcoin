"""
Lost Bitcoin — Web backend (Priority 3).

Zero-dependency (Python standard library only) HTTP API that connects
index.html to the Master Investigation Record and the investigation
controller.

Run:  python3 app.py            (serves http://127.0.0.1:8765)
Env:  LOST_BITCOIN_DB           database file path
      LOST_BITCOIN_REPORTS_DIR  generated-reports directory
      LOST_BITCOIN_SECRET       signing secret for resume tokens
                                (a development default is used if unset —
                                NEVER use the default in production)
      HOST                      bind address (default 127.0.0.1;
                                set 0.0.0.0 when deployed)
      PORT                      listen port (default 8765)

Customer resume (private-beta design): /api/start and /api/resume
return a signed, expiring resume token for the customer's own record.
The browser stores it and presents it on later calls, so a customer
can leave and return without repeating answers. PRODUCTION NOTE:
tokens must be delivered by emailed magic link (needs an email
provider); returning a token to whoever typed the email is only
acceptable for local review / private beta behind access control.
No seed phrases or private keys are ever accepted (enforced by the
record module), and no payment is taken by this server — Stripe
hosted checkout is Priority 4.
"""

import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import urllib.request
import ipaddress

import master_investigation_record as record
import investigation_controller as controller
import report_generator
import payments
import walkthrough
import guides
import exchange_guide

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = Path(os.environ.get("LOST_BITCOIN_REPORTS_DIR")
                   or BASE_DIR / "generated_reports")
SECRET = os.environ.get("LOST_BITCOIN_SECRET", "DEV-ONLY-CHANGE-ME").encode()
TOKEN_TTL_SECONDS = 30 * 24 * 3600
MAX_BODY_BYTES = 64 * 1024

PRICING = {
    "currency": "USD",
    "initial_assessment_cents": 0,
    "investigation_report_cents": controller.INVESTIGATION_REPORT_PRICE_CENTS,
    "ai_walkthrough_cents": controller.AI_WALKTHROUGH_PRICE_CENTS,
    "wallet_report_first_address_cents": controller.ADDRESS_REPORT_FIRST_CENTS,
    "wallet_report_extra_address_cents": controller.ADDRESS_REPORT_EXTRA_CENTS,
}


# ------------------------------------------------------------------ tokens
def issue_token(customer_id):
    expiry = int(time.time()) + TOKEN_TTL_SECONDS
    payload = f"{customer_id}.{expiry}"
    signature = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_token(token):
    try:
        customer_id, expiry, signature = token.split(".")
        payload = f"{customer_id}.{expiry}"
        expected = hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, signature):
            return None
        if int(expiry) < int(time.time()):
            return None
        return customer_id
    except (ValueError, AttributeError):
        return None


# ------------------------------------------------------- test provider
def _test_provider(address):
    """
    Deterministic OFFLINE provider for automated testing only, enabled
    with LOST_BITCOIN_TEST_PROVIDER=1. Returns clearly synthetic data
    derived from the address string so 50+ test journeys never hammer
    the real blockchain API. Never enabled by default.
    """
    digest = hashlib.sha256(address.encode()).digest()
    tx_count = digest[0] % 40
    balance = (digest[1] % 3) * 25_000_000 if tx_count else 0
    return {
        "address": address,
        "tx_count": tx_count,
        "received_satoshis": balance + 10_000_000,
        "sent_satoshis": 10_000_000,
        "balance_satoshis": balance,
        "unconfirmed_satoshis": 0,
        "latest_confirmed_timestamp": 1_700_000_000,
        "is_genesis_address": address == "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
        "source": "TEST-PROVIDER (synthetic, not blockchain data)",
    }


# ------------------------------------------------------------------- http
class Handler(BaseHTTPRequestHandler):
    server_version = "LostBitcoin/0.3"
    # Simple per-IP throttle for identity endpoints: (ip -> [timestamps])
    _hits = {}

    def log_message(self, *args):  # keep review output clean
        pass

    # -- helpers
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, status, body, content_type):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self._security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline'",
        )

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            raise ValueError("Request too large.")
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8"))

    def _throttled(self, limit=None, window=3600):
        # Default 120/hour per IP: strict enough to slow email enumeration,
        # loose enough for households/offices sharing one NAT address
        # (a 30/hour cap broke legitimate multi-customer testing).
        if limit is None:
            limit = int(os.environ.get("LOST_BITCOIN_RATE_LIMIT", "120"))
        now = time.time()
        hits = [t for t in self._hits.get(self.client_address[0], []) if now - t < window]
        hits.append(now)
        self._hits[self.client_address[0]] = hits
        return len(hits) > limit

    # -- geolocation (country/region only, for exchange suggestions)
    _geo_cache = {}

    def _client_ip(self):
        forwarded = self.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.client_address[0]

    def _geo(self):
        """
        Best-effort country/region for the caller's IP, used only to
        tailor exchange suggestions. The IP itself is never stored;
        any failure returns None and the questionnaire carries on
        without suggestions.
        """
        if os.environ.get("LOST_BITCOIN_TEST_GEO") == "1":
            return {"country_code": "CA", "country_name": "Canada",
                    "region": "British Columbia"}
        ip = self._client_ip()
        try:
            parsed = ipaddress.ip_address(ip)
            if parsed.is_private or parsed.is_loopback or parsed.is_link_local:
                return None
        except ValueError:
            return None
        if ip in self._geo_cache:
            return self._geo_cache[ip]
        result = None
        try:
            request = urllib.request.Request(
                f"https://ipapi.co/{ip}/json/",
                headers={"User-Agent": "lost-bitcoin/1.0"})
            with urllib.request.urlopen(request, timeout=3) as response:
                data = json.loads(response.read().decode())
            if data.get("country_code"):
                result = {
                    "country_code": data.get("country_code", ""),
                    "country_name": data.get("country_name", ""),
                    "region": data.get("region", ""),
                }
        except Exception:
            result = None
        if len(self._geo_cache) > 512:
            self._geo_cache.clear()
        self._geo_cache[ip] = result
        return result

    def _authorized_investigation(self, investigation_id):
        """Return the record if the bearer token owns this investigation."""
        auth = self.headers.get("Authorization", "")
        customer_id = verify_token(auth[7:]) if auth.startswith("Bearer ") else None
        if not customer_id:
            return None, (401, {"error": "Missing or expired sign-in token. Please resume with your email."})
        customer = record.get_customer_record(customer_id)
        if not customer:
            return None, (401, {"error": "Unknown customer."})
        owned = {i["investigation_id"] for i in customer["investigations"]}
        if investigation_id not in owned:
            return None, (403, {"error": "This investigation belongs to a different customer."})
        full = record.get_complete_investigation(investigation_id)
        return full, None

    # -- routing
    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path in ("/privacy", "/privacy.html", "/terms", "/terms.html"):
                page = "privacy.html" if "privacy" in parsed.path else "terms.html"
                body = (BASE_DIR / page).read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self._security_headers()
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path in ("/", "/index.html"):
                body = (BASE_DIR / "index.html").read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self._security_headers()
                self.end_headers()
                self.wfile.write(body)
            elif parsed.path in ("/guides", "/guides/"):
                self._send_text(200, guides.render_index(),
                                "text/html; charset=utf-8")
            elif parsed.path.startswith("/guides/"):
                page = guides.render_post(parsed.path[len("/guides/"):].strip("/"))
                if page is None:
                    self._send_text(404,
                        "<h1>Guide not found</h1><p><a href=\"/guides\">All guides</a></p>",
                        "text/html; charset=utf-8")
                else:
                    self._send_text(200, page, "text/html; charset=utf-8")
            elif parsed.path == "/llms.txt":
                self._send_text(200,
                    "# Lost Bitcoin\n\n"
                    "> Lost Bitcoin (lostbitcoin.org) is a Canadian investigation "
                    "service for people who have lost access to Bitcoin: forgotten "
                    "wallets, old laptops and drives, defunct exchanges, and Bitcoin "
                    "in estates. It sells investigation, evidence and guidance — "
                    "recovery is never guaranteed. It never asks for seed phrases, "
                    "private keys, or wallet passwords.\n\n"
                    "## Services and prices (USD)\n"
                    "- Free initial assessment\n"
                    "- Investigation Report — $9.99 (offered only when a credible lead exists)\n"
                    "- AI Guided Next Steps — $6.99\n"
                    "- Wallet Report — $4.99 for the first address, $1.99 each additional address\n\n"
                    "## How findings are classified\n"
                    "CONFIRMED / STRONG POSSIBILITY / POSSIBLE LEAD / UNKNOWN. "
                    "A blockchain balance never by itself proves ownership or recoverability.\n\n"
                    "## Guides\n"
                    "- Guides index: https://lostbitcoin.org/guides\n"
                    "- Found a wallet.dat but forgot the password: https://lostbitcoin.org/guides/wallet-dat-forgot-password\n"
                    "- A spouse or parent passed away and had Bitcoin (executors and families): https://lostbitcoin.org/guides/spouse-parent-passed-away-bitcoin\n\n"
                    "## Contact\n"
                    "hello@lostbitcoin.org\n",
                    "text/plain; charset=utf-8")
            elif parsed.path == "/robots.txt":
                self._send_text(200,
                    "User-agent: *\nAllow: /\n"
                    "Sitemap: https://lostbitcoin.org/sitemap.xml\n",
                    "text/plain; charset=utf-8")
            elif parsed.path == "/sitemap.xml":
                guide_urls = "".join(
                    f"<url><loc>https://lostbitcoin.org/guides/{g['slug']}</loc></url>"
                    for g in guides.GUIDES)
                self._send_text(200,
                    '<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    "<url><loc>https://lostbitcoin.org/</loc></url>"
                    "<url><loc>https://lostbitcoin.org/guides</loc></url>"
                    + guide_urls +
                    "<url><loc>https://lostbitcoin.org/privacy</loc></url>"
                    "<url><loc>https://lostbitcoin.org/terms</loc></url>"
                    "</urlset>",
                    "application/xml; charset=utf-8")
            elif parsed.path == "/api/health":
                self._send_json(200, {"status": "ok", "service": "lost-bitcoin"})
            elif parsed.path == "/api/pricing":
                self._send_json(200, PRICING)
            elif parsed.path == "/api/exchange-suggestions":
                era = parse_qs(parsed.query).get("era", [""])[0]
                self._send_json(200, exchange_guide.suggestions_payload(
                    self._geo(), era))
            elif parsed.path == "/api/purchases":
                inv_id = parse_qs(parsed.query).get("investigation_id", [""])[0]
                full, error = self._authorized_investigation(inv_id)
                if error:
                    self._send_json(*error)
                else:
                    self._send_json(200, {"purchases": full["purchases"]})
            elif parsed.path == "/api/investigation":
                inv_id = parse_qs(parsed.query).get("investigation_id", [""])[0]
                full, error = self._authorized_investigation(inv_id)
                if error:
                    self._send_json(*error)
                else:
                    self._send_json(200, full)
            else:
                self._send_json(404, {"error": "Not found."})
        except Exception as error:  # never leak stack traces to customers
            self._send_json(500, {"error": f"Server error: {error}"})

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/stripe/webhook":
                return self._stripe_webhook()
            data = self._read_json()
            if parsed.path == "/api/start":
                self._start(data)
            elif parsed.path == "/api/resume":
                self._resume(data)
            elif parsed.path in ("/api/answer", "/api/address", "/api/run", "/api/report",
                                 "/api/checkout", "/api/demo-pay", "/api/walkthrough"):
                self._investigation_action(parsed.path, data)
            else:
                self._send_json(404, {"error": "Not found."})
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid request format."})
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
        except Exception as error:
            if error.__class__.__name__ == "IntegrityError":
                self._send_json(400, {"error": "That record already exists."})
            else:
                self._send_json(500, {"error": f"Server error: {error}"})

    def _stripe_webhook(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if not payments.verify_stripe_signature(raw, self.headers.get("Stripe-Signature", "")):
            return self._send_json(400, {"error": "Invalid webhook signature."})
        try:
            event = json.loads(raw.decode("utf-8"))
            payments.handle_stripe_event(event)
        except ValueError as error:
            if "already been recorded" not in str(error):
                return self._send_json(400, {"error": str(error)})
            # duplicate delivery: acknowledge so Stripe stops retrying
        self._send_json(200, {"received": True})

    # -- endpoints
    def _start(self, data):
        if self._throttled():
            return self._send_json(429, {"error": "Too many attempts. Please try again later."})
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip()
        starting_point = data.get("starting_point", "lost_bitcoin")
        try:
            created = record.create_customer(name, email, starting_point)
            created["resumed"] = False
        except ValueError as error:
            if "already has an account" not in str(error):
                raise
            resumed = record.resume_customer_investigation(email)
            if resumed is None:
                raise
            created = {
                "customer_id": resumed["customer_id"],
                "investigation_id": resumed["investigation_id"],
                "starting_point": resumed["starting_point"],
                "resumed": True,
            }
        created["token"] = issue_token(created["customer_id"])
        self._send_json(200, created)

    def _resume(self, data):
        if self._throttled():
            return self._send_json(429, {"error": "Too many attempts. Please try again later."})
        email = str(data.get("email", "")).strip()
        resumed = record.resume_customer_investigation(email) if email else None
        if resumed is None:
            return self._send_json(404, {"error": "No active investigation found for that email."})
        resumed["token"] = issue_token(resumed["customer_id"])
        resumed["resumed"] = True
        self._send_json(200, resumed)

    def _investigation_action(self, path, data):
        investigation_id = str(data.get("investigation_id", ""))
        full, error = self._authorized_investigation(investigation_id)
        if error:
            return self._send_json(*error)
        if path == "/api/answer":
            answer_id = record.save_answer(
                investigation_id,
                str(data.get("question_key", "")),
                data.get("answer_value"),
            )
            self._send_json(200, {"answer_id": answer_id})
        elif path == "/api/address":
            address_id = record.save_bitcoin_address(
                investigation_id,
                str(data.get("address", "")),
                str(data.get("label", "")),
            )
            self._send_json(200, {"address_id": address_id})
        elif path == "/api/run":
            if os.environ.get("LOST_BITCOIN_TEST_PROVIDER") == "1":
                outcome = controller.run_investigation(
                    investigation_id, provider=_test_provider)
            else:
                outcome = controller.run_investigation(investigation_id)
            self._send_json(200, outcome)
        elif path == "/api/report":
            required = ("wallet_report" if full["starting_point"] == "bitcoin_address"
                        else "investigation_report")
            if not payments.has_purchased(investigation_id, required):
                amount = payments.price_for(
                    required, address_count=len(full["addresses"]))
                return self._send_json(402, {
                    "error": "This report is a paid product. Complete checkout first.",
                    "product": required, "amount_cents": amount})
            result = report_generator.generate_report(investigation_id, REPORTS_DIR)
            self._send_json(200, {"report_id": result["report_id"], "markdown": result["markdown"]})
        elif path == "/api/checkout":
            product = str(data.get("product", ""))
            checkout = payments.create_checkout(
                investigation_id, full["customer"]["customer_id"], product,
                address_count=len(full["addresses"]),
                customer_email=full["customer"]["email"])
            checkout["product"] = product
            self._send_json(200, checkout)
        elif path == "/api/demo-pay":
            purchase_id = payments.complete_demo_payment(
                str(data.get("demo_token", "")), full["customer"]["customer_id"])
            self._send_json(200, {"purchase_id": purchase_id})
        elif path == "/api/walkthrough":
            if not payments.has_purchased(investigation_id, "ai_walkthrough"):
                return self._send_json(402, {
                    "error": "AI Guided Next Steps is a paid product. Complete checkout first.",
                    "product": "ai_walkthrough",
                    "amount_cents": payments.price_for("ai_walkthrough")})
            answer = walkthrough.reply(investigation_id, str(data.get("message", "")))
            self._send_json(200, {"reply": answer})


def main():
    record.initialize_database()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8765"))
    if SECRET == b"DEV-ONLY-CHANGE-ME":
        print("WARNING: using the development signing secret. Set LOST_BITCOIN_SECRET in production.")
    print(f"Lost Bitcoin server: http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
