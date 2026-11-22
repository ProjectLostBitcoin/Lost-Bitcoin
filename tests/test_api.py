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
                            {"name": "Api Test", "email": email, "starting_point": starting,
                             "consent": True})
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

    def test_stats_counter(self):
        import urllib.request as u
        # Stats are secret-gated.
        status, _ = call(self.base, "GET", "/api/stats")
        self.assertEqual(status, 403)
        def read_stats():
            req = u.Request(self.base + "/api/stats")
            req.add_header("X-Stats-Key", "test-secret")
            with u.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        # A normal browser view with a referrer gets counted.
        req = u.Request(self.base + "/?utm_source=youtube&utm_medium=shorts")
        req.add_header("User-Agent", "Mozilla/5.0 (Macintosh) Safari/605.1")
        req.add_header("Referer", "https://www.youtube.com/")
        with u.urlopen(req, timeout=10) as r:
            self.assertEqual(r.status, 200)
        stats = read_stats()
        refs = [x["referrer"] for x in stats["top_referrers"]]
        self.assertIn("www.youtube.com", refs)
        srcs = [x["source"] for x in stats["utm_sources"]]
        self.assertIn("youtube", srcs)
        # ...while an obvious bot does not move the total.
        before = stats["total_views"]
        req = u.Request(self.base + "/")
        req.add_header("User-Agent", "curl/8.0")
        with u.urlopen(req, timeout=10) as r:
            self.assertEqual(r.status, 200)
        self.assertEqual(read_stats()["total_views"], before)

    def test_event_counters(self):
        import urllib.request as u
        def read_stats():
            req = u.Request(self.base + "/api/stats")
            req.add_header("X-Stats-Key", "test-secret")
            with u.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        before = read_stats()["events"]["totals"].get("assessment_started", 0)
        status, data = call(self.base, "POST", "/api/start", {
            "name": "Event Person", "email": "events@example.com",
            "starting_point": "bitcoin_address", "consent": True})
        self.assertEqual(status, 200)
        token, inv = data["token"], data["investigation_id"]
        status, _ = call(self.base, "POST", "/api/address",
                         {"investigation_id": inv, "address": GENESIS,
                          "label": ""}, token=token)
        self.assertEqual(status, 200)
        after = read_stats()["events"]["totals"]
        self.assertEqual(after.get("assessment_started", 0), before + 1)
        self.assertGreaterEqual(after.get("address_checked", 0), 1)

    def test_hero_click_event(self):
        import urllib.request as u
        def read_stats():
            req = u.Request(self.base + "/api/stats")
            req.add_header("X-Stats-Key", "test-secret")
            with u.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        before = read_stats()["events"]["totals"].get("hero_click_lost_bitcoin", 0)
        status, data = call(self.base, "POST", "/api/event",
                            {"event": "hero_click", "kind": "lost_bitcoin"})
        self.assertEqual(status, 200)
        self.assertTrue(data.get("recorded"))
        after = read_stats()["events"]["totals"]
        self.assertEqual(after.get("hero_click_lost_bitcoin", 0), before + 1)
        # Unknown events are refused and record nothing.
        status, _ = call(self.base, "POST", "/api/event",
                         {"event": "purchase", "kind": "lost_bitcoin"})
        self.assertEqual(status, 400)
        self.assertEqual(
            read_stats()["events"]["totals"].get("hero_click_lost_bitcoin", 0),
            before + 1)

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

    def test_same_email_two_flows_get_separate_investigations(self):
        # Regression: 2026-11-14, starting the Wallet Report flow with an
        # email that already had a lost-Bitcoin investigation silently
        # resumed the old record and stranded a paid Wallet Report.
        lost = self.start_customer("both@example.com", "lost_bitcoin")
        wallet = self.start_customer("both@example.com", "bitcoin_address")
        self.assertFalse(wallet["resumed"])
        self.assertEqual(wallet["customer_id"], lost["customer_id"])
        self.assertNotEqual(wallet["investigation_id"], lost["investigation_id"])
        self.assertEqual(wallet["starting_point"], "bitcoin_address")
        again = self.start_customer("both@example.com", "lost_bitcoin")
        self.assertTrue(again["resumed"])
        self.assertEqual(again["investigation_id"], lost["investigation_id"])

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

    def test_stripe_webhook_thin_payload_records_purchase(self):
        # Stripe destinations created with the 'thin' payload style send
        # only the session ID. The webhook must fetch the full session
        # from Stripe and still record the purchase exactly once.
        import hashlib, hmac, time as _time
        import payments as pay_mod
        saved_secret, saved_key = pay_mod.STRIPE_WEBHOOK_SECRET, pay_mod.STRIPE_SECRET_KEY
        saved_fetch = pay_mod._fetch_checkout_session
        s = self.start_customer("thinhook@example.com")
        full_session = {"id": "cs_live_thin_1", "payment_status": "paid",
                        "amount_total": 499, "currency": "usd",
                        "metadata": {"customer_id": s["customer_id"],
                                     "investigation_id": s["investigation_id"],
                                     "product": "wallet_report"}}
        try:
            pay_mod.STRIPE_WEBHOOK_SECRET = "whsec_test_e2e"
            pay_mod.STRIPE_SECRET_KEY = "sk_test_dummy"
            pay_mod._fetch_checkout_session = lambda sid: full_session
            event = {"id": "evt_thin_1", "type": "checkout.session.completed",
                     "data": {"related_object": {"id": "cs_live_thin_1",
                                                  "type": "checkout.session",
                                                  "url": "/v1/checkout/sessions/cs_live_thin_1"}}}
            raw = json.dumps(event).encode()
            ts = str(int(_time.time()))
            sig = hmac.new(b"whsec_test_e2e", f"{ts}.".encode() + raw, hashlib.sha256).hexdigest()
            req = urllib.request.Request(self.base + "/api/stripe/webhook", method="POST", data=raw)
            req.add_header("Stripe-Signature", f"t={ts},v1={sig}")
            with urllib.request.urlopen(req, timeout=10) as r:
                self.assertEqual(r.status, 200)
            status, data = call(self.base, "GET",
                                f"/api/purchases?investigation_id={s['investigation_id']}", token=s["token"])
            paid = [x for x in data["purchases"] if x["status"] == "completed"]
            self.assertEqual(len(paid), 1)
            self.assertEqual(paid[0]["product"], "wallet_report")
            self.assertEqual(paid[0]["amount_minor"], 499)
        finally:
            pay_mod.STRIPE_WEBHOOK_SECRET = saved_secret
            pay_mod.STRIPE_SECRET_KEY = saved_key
            pay_mod._fetch_checkout_session = saved_fetch

    def test_bad_email_rejected(self):
        status, _ = call(self.base, "POST", "/api/start",
                         {"name": "X", "email": "nope", "starting_point": "lost_bitcoin",
                          "consent": True})
        self.assertEqual(status, 400)

    def test_start_requires_consent(self):
        status, data = call(self.base, "POST", "/api/start",
                            {"name": "No Consent", "email": "noconsent@example.com",
                             "starting_point": "lost_bitcoin"})
        self.assertEqual(status, 400)
        self.assertIn("consent", data["error"])

    def test_checkout_refused_without_credible_lead(self):
        s = self.start_customer("nolead@example.com")
        inv, tok = s["investigation_id"], s["token"]
        status, _ = call(self.base, "POST", "/api/run", {"investigation_id": inv}, tok)
        self.assertEqual(status, 200)
        for product in ("investigation_report", "ai_walkthrough"):
            status, data = call(self.base, "POST", "/api/checkout",
                                {"investigation_id": inv, "product": product}, tok)
            self.assertEqual(status, 400, (product, data))
            self.assertIn("credible lead", data["error"])

    def test_checkout_product_must_match_flow(self):
        s = self.start_customer("mismatch@example.com", "bitcoin_address")
        inv, tok = s["investigation_id"], s["token"]
        status, data = call(self.base, "POST", "/api/checkout",
                            {"investigation_id": inv, "product": "investigation_report"}, tok)
        self.assertEqual(status, 400)
        self.assertIn("Wallet Report", data["error"])
        s = self.start_customer("mismatch2@example.com")
        inv, tok = s["investigation_id"], s["token"]
        call(self.base, "POST", "/api/answer",
             {"investigation_id": inv, "question_key": "device", "answer_value": "Yes"}, tok)
        status, data = call(self.base, "POST", "/api/checkout",
                            {"investigation_id": inv, "product": "wallet_report"}, tok)
        self.assertEqual(status, 400)
        self.assertIn("Investigation Report", data["error"])

    def start_anonymous(self, starting="lost_bitcoin"):
        status, data = call(self.base, "POST", "/api/start",
                            {"anonymous": True, "starting_point": starting})
        self.assertEqual(status, 200, data)
        self.assertTrue(data["anonymous"])
        self.assertIn("token", data)
        return data

    def test_anonymous_flow_claim_then_purchase(self):
        s = self.start_anonymous()
        inv, tok = s["investigation_id"], s["token"]
        # Answers save against the anonymous record with its token.
        status, _ = call(self.base, "POST", "/api/answer",
                         {"investigation_id": inv, "question_key": "device",
                          "answer_value": "Yes"}, tok)
        self.assertEqual(status, 200)
        # Anonymous records cannot buy, and reports stay purchase-gated.
        status, data = call(self.base, "POST", "/api/checkout",
                            {"investigation_id": inv,
                             "product": "investigation_report"}, tok)
        self.assertEqual(status, 403)
        self.assertIn("Save your investigation", data["error"])
        status, _ = call(self.base, "POST", "/api/report",
                         {"investigation_id": inv}, tok)
        self.assertEqual(status, 402)
        # Claim without consent is refused, same gate as /api/start.
        status, data = call(self.base, "POST", "/api/claim",
                            {"investigation_id": inv, "name": "Anon Person",
                             "email": "anon@example.com"}, tok)
        self.assertEqual(status, 400)
        self.assertIn("consent", data["error"])
        # Claim with consent: the record becomes the customer's own.
        status, claimed = call(self.base, "POST", "/api/claim",
                               {"investigation_id": inv, "name": "Anon Person",
                                "email": "anon@example.com", "consent": True}, tok)
        self.assertEqual(status, 200, claimed)
        self.assertFalse(claimed["resumed"])
        self.assertFalse(claimed["anonymous"])
        self.assertEqual(claimed["investigation_id"], inv)
        self.assertEqual(claimed["customer_id"], s["customer_id"])
        # The pre-claim token still works (same customer), and so does
        # the token returned by the claim.
        for t in (tok, claimed["token"]):
            status, full = call(self.base, "GET",
                                f"/api/investigation?investigation_id={inv}", token=t)
            self.assertEqual(status, 200)
            self.assertEqual(full["customer"]["email"], "anon@example.com")
        # From here the paid flow works exactly as for a named start.
        tok = claimed["token"]
        status, out = call(self.base, "POST", "/api/run",
                           {"investigation_id": inv}, tok)
        self.assertEqual(status, 200)
        self.assertTrue(out["assessment"]["credible_lead"])
        status, co = call(self.base, "POST", "/api/checkout",
                          {"investigation_id": inv,
                           "product": "investigation_report"}, tok)
        self.assertEqual((status, co["mode"], co["amount_cents"]), (200, "demo", 999))
        status, _ = call(self.base, "POST", "/api/demo-pay",
                         {"investigation_id": inv, "demo_token": co["demo_token"]}, tok)
        self.assertEqual(status, 200)
        status, rep = call(self.base, "POST", "/api/report",
                           {"investigation_id": inv}, tok)
        self.assertEqual(status, 200)
        self.assertIn("Investigation Report", rep["markdown"])
        # A claimed record cannot be claimed again.
        status, _ = call(self.base, "POST", "/api/claim",
                         {"investigation_id": inv, "name": "Second",
                          "email": "second@example.com", "consent": True}, tok)
        self.assertEqual(status, 400)

    def test_anonymous_stranger_cannot_read_or_claim(self):
        mine = self.start_anonymous()
        other = self.start_anonymous()
        inv, otok = mine["investigation_id"], other["token"]
        status, _ = call(self.base, "GET",
                         f"/api/investigation?investigation_id={inv}", token=otok)
        self.assertEqual(status, 403)
        status, _ = call(self.base, "POST", "/api/answer",
                         {"investigation_id": inv, "question_key": "device",
                          "answer_value": "Yes"}, otok)
        self.assertEqual(status, 403)
        status, _ = call(self.base, "POST", "/api/claim",
                         {"investigation_id": inv, "name": "Stranger",
                          "email": "stranger@example.com", "consent": True}, otok)
        self.assertEqual(status, 403)
        status, _ = call(self.base, "POST", "/api/claim",
                         {"investigation_id": inv, "name": "No Token",
                          "email": "notoken@example.com", "consent": True})
        self.assertEqual(status, 401)
        # The rightful anonymous owner is unaffected by the attempts.
        status, full = call(self.base, "GET",
                            f"/api/investigation?investigation_id={inv}",
                            token=mine["token"])
        self.assertEqual(status, 200)
        self.assertIsNone(full["customer"]["email"])

    def test_claim_attaches_to_existing_customer_of_other_flow(self):
        # The 2026-11-14 hijack rule, applied to claiming: an email that
        # owns a lost-Bitcoin investigation claims an anonymous Wallet
        # Report investigation — it attaches as its own record and the
        # lost-Bitcoin record is never touched.
        named = self.start_customer("attach@example.com", "lost_bitcoin")
        anon = self.start_anonymous("bitcoin_address")
        inv, tok = anon["investigation_id"], anon["token"]
        status, _ = call(self.base, "POST", "/api/address",
                         {"investigation_id": inv, "address": GENESIS}, tok)
        self.assertEqual(status, 200)
        status, claimed = call(self.base, "POST", "/api/claim",
                               {"investigation_id": inv, "name": "Api Test",
                                "email": "attach@example.com", "consent": True}, tok)
        self.assertEqual(status, 200, claimed)
        self.assertFalse(claimed["resumed"])
        self.assertEqual(claimed["investigation_id"], inv)
        self.assertEqual(claimed["customer_id"], named["customer_id"])
        # The placeholder customer row is gone; both records are the
        # real customer's, each under its own starting point.
        self.assertIsNone(app.record.get_customer_record(anon["customer_id"]))
        status, data = call(self.base, "POST", "/api/resume",
                            {"email": "attach@example.com",
                             "starting_point": "lost_bitcoin"})
        self.assertEqual(data["investigation_id"], named["investigation_id"])
        status, data = call(self.base, "POST", "/api/resume",
                            {"email": "attach@example.com",
                             "starting_point": "bitcoin_address"})
        self.assertEqual(data["investigation_id"], inv)
        # The claimed address record can now buy its Wallet Report.
        status, co = call(self.base, "POST", "/api/checkout",
                          {"investigation_id": inv, "product": "wallet_report"},
                          token=claimed["token"])
        self.assertEqual((status, co["amount_cents"]), (200, 499))

    def test_claim_with_same_flow_email_resumes_existing(self):
        # Resume semantics, exactly like /api/start: claiming with an
        # email that already has an active investigation of the SAME
        # starting point returns that record; the anonymous one is
        # left unclaimed and unmerged.
        named = self.start_customer("resumeclaim@example.com", "lost_bitcoin")
        anon = self.start_anonymous("lost_bitcoin")
        status, claimed = call(self.base, "POST", "/api/claim",
                               {"investigation_id": anon["investigation_id"],
                                "name": "Api Test",
                                "email": "resumeclaim@example.com",
                                "consent": True}, anon["token"])
        self.assertEqual(status, 200, claimed)
        self.assertTrue(claimed["resumed"])
        self.assertEqual(claimed["investigation_id"], named["investigation_id"])
        self.assertEqual(claimed["customer_id"], named["customer_id"])
        full = app.record.get_complete_investigation(anon["investigation_id"])
        self.assertIsNone(full["customer"]["email"])

    def test_seed_phrase_in_address_field_gets_protective_message(self):
        s = self.start_customer("seedaddr@example.com", "bitcoin_address")
        inv, tok = s["investigation_id"], s["token"]
        seed = ("abandon ability able about above absent absorb abstract "
                "absurd abuse access accident")
        status, data = call(self.base, "POST", "/api/address",
                            {"investigation_id": inv, "address": seed}, tok)
        self.assertEqual(status, 400)
        self.assertIn("seed phrase", data["error"])
        self.assertIn("never asks", data["error"])


if __name__ == "__main__":
    unittest.main()
