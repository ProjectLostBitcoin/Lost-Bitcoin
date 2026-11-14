"""API tests for app.py — fictional data only, server on an ephemeral port."""
import json, os, sys, tempfile, threading, unittest, urllib.request, urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["LOST_BITCOIN_DB"] = str(Path(tempfile.mkdtemp()) / "api_test.db")
os.environ["LOST_BITCOIN_SECRET"] = "test-secret"

import app  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402

GENESIS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"


def call(base, method, path, body=None, token=None):
    req = urllib.request.Request(base + path, method=method)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, data=data, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Point the record module at this suite's own DB explicitly:
        # under `unittest discover` other suites may have imported the
        # module (and changed its path) first.
        app.record.set_database_path(Path(tempfile.mkdtemp()) / "api_test.db")
        app.record.initialize_database()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def start_customer(self, email="api@example.com", starting="lost_bitcoin"):
        status, data = call(self.base, "POST", "/api/start",
                            {"name": "Api Test", "email": email, "starting_point": starting})
        self.assertEqual(status, 200, data)
        return data

    def test_exchange_suggestions_with_test_geo(self):
        os.environ["LOST_BITCOIN_TEST_GEO"] = "1"
        try:
            status, data = call(self.base, "GET",
                                "/api/exchange-suggestions?era=2016%E2%80%932017")
        finally:
            del os.environ["LOST_BITCOIN_TEST_GEO"]
        self.assertEqual(status, 200, data)
        self.assertEqual(data["detected"]["country_code"], "CA")
        self.assertEqual(data["detected"]["region"], "British Columbia")
        names = [s["name"] for s in data["suggestions"]]
        self.assertEqual(names[0], "Einstein Exchange")  # BC-specific first
        self.assertIn("QuadrigaCX", names)

    def test_exchange_suggestions_without_geo_still_answer(self):
        # Loopback test client: detection returns None, globals still offered.
        status, data = call(self.base, "GET",
                            "/api/exchange-suggestions?era=2014%E2%80%932015")
        self.assertEqual(status, 200, data)
        self.assertIsNone(data["detected"])
        self.assertIn("Mt. Gox", [s["name"] for s in data["suggestions"]])

    def test_seo_routes_and_meta(self):
        import urllib.request as u
        with u.urlopen(self.base + "/robots.txt", timeout=10) as r:
            self.assertEqual(r.status, 200)
            self.assertIn("sitemap.xml", r.read().decode())
        with u.urlopen(self.base + "/sitemap.xml", timeout=10) as r:
            self.assertIn("https://lostbitcoin.org/", r.read().decode())
        with u.urlopen(self.base + "/", timeout=10) as r:
            page = r.read().decode()
        self.assertIn('name="description"', page)
        self.assertIn("application/ld+json", page)
        self.assertIn("Will Lost Bitcoin ever ask for my seed phrase?", page)

    def test_guides_routes(self):
        import urllib.request as u
        import urllib.error
        with u.urlopen(self.base + "/guides", timeout=10) as r:
            self.assertEqual(r.status, 200)
            index = r.read().decode()
        self.assertIn("wallet-dat-forgot-password", index)
        self.assertIn("spouse-parent-passed-away-bitcoin", index)
        self.assertIn("bitcoin-recovery-service-scams", index)
        with u.urlopen(self.base + "/guides/wallet-dat-forgot-password", timeout=10) as r:
            post = r.read().decode()
        self.assertIn("Don't experiment on the only copy", post)
        self.assertIn("application/ld+json", post)
        self.assertIn("never ask for seed phrases", post)
        with u.urlopen(self.base + "/sitemap.xml", timeout=10) as r:
            self.assertIn("/guides/wallet-dat-forgot-password", r.read().decode())
        with u.urlopen(self.base + "/llms.txt", timeout=10) as r:
            llms = r.read().decode()
        self.assertIn("never guaranteed", llms)
        self.assertIn("$9.99", llms)
        try:
            u.urlopen(self.base + "/guides/no-such-guide", timeout=10)
            self.fail("unknown guide should 404")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)

    def test_health_and_pricing(self):
        status, data = call(self.base, "GET", "/api/health")
        self.assertEqual((status, data["status"]), (200, "ok"))
        status, prices = call(self.base, "GET", "/api/pricing")
        self.assertEqual(prices["investigation_report_cents"], 999)
        self.assertEqual(prices["ai_walkthrough_cents"], 699)
        self.assertEqual(prices["wallet_report_first_address_cents"], 499)
        self.assertEqual(prices["wallet_report_extra_address_cents"], 199)

    def test_full_lost_bitcoin_flow(self):
        s = self.start_customer()
        inv, tok = s["investigation_id"], s["token"]
        status, _ = call(self.base, "POST", "/api/answer",
                         {"investigation_id": inv, "question_key": "device", "answer_value": "Yes"}, tok)
        self.assertEqual(status, 200)
        status, out = call(self.base, "POST", "/api/run", {"investigation_id": inv}, tok)
        self.assertEqual(status, 200)
        self.assertTrue(out["assessment"]["credible_lead"])
        self.assertEqual(out["assessment"]["investigation_report_offer_cents"], 999)
        self.assertEqual(out["assessment"]["ai_walkthrough_offer_cents"], 699)
        status, _ = call(self.base, "POST", "/api/report", {"investigation_id": inv}, tok)
        self.assertEqual(status, 402)  # paid product: gated before purchase
        status, co = call(self.base, "POST", "/api/checkout",
                          {"investigation_id": inv, "product": "investigation_report"}, tok)
        self.assertEqual((status, co["mode"], co["amount_cents"]), (200, "demo", 999))
        status, _ = call(self.base, "POST", "/api/demo-pay",
                         {"investigation_id": inv, "demo_token": co["demo_token"]}, tok)
        self.assertEqual(status, 200)
        status, rep = call(self.base, "POST", "/api/report", {"investigation_id": inv}, tok)
        self.assertEqual(status, 200)
        self.assertIn("Investigation Report", rep["markdown"])

    def test_start_twice_resumes_not_duplicates(self):
        first = self.start_customer("twice@example.com")
        second = self.start_customer("twice@example.com")
        self.assertTrue(second["resumed"])
        self.assertEqual(first["customer_id"], second["customer_id"])

    def test_resume_endpoint(self):
        self.start_customer("resume@example.com")
        status, data = call(self.base, "POST", "/api/resume", {"email": "resume@example.com"})
        self.assertEqual(status, 200)
        self.assertIn("token", data)
        status, _ = call(self.base, "POST", "/api/resume", {"email": "ghost@example.com"})
        self.assertEqual(status, 404)

    def test_auth_required_and_ownership_enforced(self):
        mine = self.start_customer("owner@example.com")
        other = self.start_customer("intruder@example.com")
        status, _ = call(self.base, "GET", f"/api/investigation?investigation_id={mine['investigation_id']}")
        self.assertEqual(status, 401)  # no token
        status, _ = call(self.base, "GET", f"/api/investigation?investigation_id={mine['investigation_id']}", token=other["token"])
        self.assertEqual(status, 403)  # someone else's investigation
        status, full = call(self.base, "GET", f"/api/investigation?investigation_id={mine['investigation_id']}", token=mine["token"])
        self.assertEqual(status, 200)
        self.assertEqual(full["customer"]["email"], "owner@example.com")

    def test_address_validation_and_seed_guard_via_api(self):
        s = self.start_customer("addr@example.com", "bitcoin_address")
        inv, tok = s["investigation_id"], s["token"]
        status, data = call(self.base, "POST", "/api/address",
                            {"investigation_id": inv, "address": "not-a-real-address"}, tok)
        self.assertEqual(status, 400)
        status, _ = call(self.base, "POST", "/api/address",
                         {"investigation_id": inv, "address": GENESIS}, tok)
        self.assertEqual(status, 200)
        seed = ("abandon ability able about above absent absorb abstract "
                "absurd abuse access accident")
        status, data = call(self.base, "POST", "/api/answer",
                            {"investigation_id": inv, "question_key": "notes", "answer_value": seed}, tok)
        self.assertEqual(status, 400)
        self.assertIn("seed phrase", data["error"])

    def test_walkthrough_gated_and_grounded(self):
        s = self.start_customer("walk@example.com")
        inv, tok = s["investigation_id"], s["token"]
        call(self.base, "POST", "/api/answer",
             {"investigation_id": inv, "question_key": "device", "answer_value": "Yes"}, tok)
        call(self.base, "POST", "/api/run", {"investigation_id": inv}, tok)
        status, _ = call(self.base, "POST", "/api/walkthrough",
                         {"investigation_id": inv, "message": "next step"}, tok)
        self.assertEqual(status, 402)
        status, co = call(self.base, "POST", "/api/checkout",
                          {"investigation_id": inv, "product": "ai_walkthrough"}, tok)
        self.assertEqual(co["amount_cents"], 699)
        call(self.base, "POST", "/api/demo-pay",
             {"investigation_id": inv, "demo_token": co["demo_token"]}, tok)
        status, out = call(self.base, "POST", "/api/walkthrough",
                           {"investigation_id": inv, "message": "next step"}, tok)
        self.assertEqual(status, 200)
        self.assertIn("Preserve the original device", out["reply"])
        status, out = call(self.base, "POST", "/api/walkthrough",
                           {"investigation_id": inv, "message": "can you guarantee recovery?"}, tok)
        self.assertIn("no one can guarantee", out["reply"])
        seed = ("abandon ability able about above absent absorb abstract "
                "absurd abuse access accident")
        status, out = call(self.base, "POST", "/api/walkthrough",
                           {"investigation_id": inv, "message": seed}, tok)
        self.assertIn("don't send that here", out["reply"].lower())

    def test_stripe_webhook_signature_and_recording(self):
        import hashlib, hmac, time as _time
        import payments as pay_mod
        pay_mod.STRIPE_WEBHOOK_SECRET = "whsec_test_e2e"
        s = self.start_customer("hook@example.com")
        event = {"type": "checkout.session.completed",
                 "data": {"object": {"id": "cs_test_123", "payment_status": "paid",
                                     "amount_total": 999, "currency": "usd",
                                     "metadata": {"customer_id": s["customer_id"],
                                                  "investigation_id": s["investigation_id"],
                                                  "product": "investigation_report"}}}}
        raw = json.dumps(event).encode()
        ts = str(int(_time.time()))
        sig = hmac.new(b"whsec_test_e2e", f"{ts}.".encode() + raw, hashlib.sha256).hexdigest()
        req = urllib.request.Request(self.base + "/api/stripe/webhook", method="POST", data=raw)
        req.add_header("Stripe-Signature", f"t={ts},v1={sig}")
        with urllib.request.urlopen(req, timeout=10) as r:
            self.assertEqual(r.status, 200)
        # duplicate delivery must be acknowledged, not double-recorded
        req = urllib.request.Request(self.base + "/api/stripe/webhook", method="POST", data=raw)
        req.add_header("Stripe-Signature", f"t={ts},v1={sig}")
        with urllib.request.urlopen(req, timeout=10) as r:
            self.assertEqual(r.status, 200)
        status, data = call(self.base, "GET",
                            f"/api/purchases?investigation_id={s['investigation_id']}", token=s["token"])
        paid = [x for x in data["purchases"] if x["status"] == "completed"]
        self.assertEqual(len(paid), 1)
        # forged signature rejected
        req = urllib.request.Request(self.base + "/api/stripe/webhook", method="POST", data=raw)
        req.add_header("Stripe-Signature", f"t={ts},v1={'0' * 64}")
        with self.assertRaises(urllib.error.HTTPError) as cm:
            urllib.request.urlopen(req, timeout=10)
        self.assertEqual(cm.exception.code, 400)

    def test_bad_email_rejected(self):
        status, _ = call(self.base, "POST", "/api/start",
                         {"name": "X", "email": "nope", "starting_point": "lost_bitcoin"})
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
