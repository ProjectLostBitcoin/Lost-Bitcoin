"""Lost Bitcoin test suite — fictional data only. Run: python3 -m unittest discover -s tests -v"""
import sys, tempfile, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import master_investigation_record as record
from bitcoin_address_validation import validate_bitcoin_address
from blockchain_provider import BlockchainUnavailable
import investigation_controller as controller
import report_generator

GENESIS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
LEGACY = "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"
BECH32 = "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4"
TAPROOT = "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0"


class DbTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        record.set_database_path(Path(self.tmp.name) / "test.db")
        record.initialize_database()
        self.cust = record.create_customer("Test Person", "test@example.com", "lost_bitcoin")
        self.inv = self.cust["investigation_id"]

    def tearDown(self):
        self.tmp.cleanup()


class TestAddressValidation(unittest.TestCase):
    def test_valid_addresses(self):
        for addr, kind in [(GENESIS, "p2pkh"), (LEGACY, "p2pkh"),
                           (BECH32, "segwit_v0"), (TAPROOT, "taproot")]:
            result = validate_bitcoin_address(addr)
            self.assertTrue(result["valid"], addr)
            self.assertEqual(result["type"], kind, addr)

    def test_invalid_addresses(self):
        for bad in ["", "hello", "1BoatSLRHtKNngkdXEeobR76b53LETtpyU",
                    "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t5",
                    "not an address", None, 42]:
            with self.assertRaises(ValueError, msg=str(bad)):
                validate_bitcoin_address(bad)


class TestMasterRecord(DbTestCase):
    def test_duplicate_email_rejected(self):
        with self.assertRaises(ValueError):
            record.create_customer("Copy", "TEST@example.com")

    def test_bad_email_rejected(self):
        with self.assertRaises(ValueError):
            record.create_customer("X", "not-an-email")

    def test_resume_finds_most_recent(self):
        found = record.resume_customer_investigation("test@example.com")
        self.assertEqual(found["investigation_id"], self.inv)

    def test_same_email_different_starting_point_gets_separate_investigation(self):
        # Regression: 2026-11-14, a paid Wallet Report was stranded because
        # starting the address flow silently resumed the customer's older
        # lost-Bitcoin investigation instead of starting its own record.
        wallet = record.create_customer("Test Person", "test@example.com", "bitcoin_address")
        self.assertEqual(wallet["customer_id"], self.cust["customer_id"])
        self.assertNotEqual(wallet["investigation_id"], self.inv)
        self.assertEqual(wallet["starting_point"], "bitcoin_address")

    def test_resume_filtered_by_starting_point(self):
        wallet = record.create_customer("Test Person", "test@example.com", "bitcoin_address")
        found_wallet = record.resume_customer_investigation("test@example.com", "bitcoin_address")
        self.assertEqual(found_wallet["investigation_id"], wallet["investigation_id"])
        found_lost = record.resume_customer_investigation("test@example.com", "lost_bitcoin")
        self.assertEqual(found_lost["investigation_id"], self.inv)

    def test_duplicate_same_starting_point_still_rejected(self):
        with self.assertRaises(ValueError):
            record.create_customer("Test Person", "test@example.com", "bitcoin_address")
            record.create_customer("Test Person", "test@example.com", "bitcoin_address")

    def test_answer_requires_real_investigation(self):  # NEW validation
        with self.assertRaises(ValueError):
            record.save_answer("no-such-id", "device", "Yes")

    def test_discovery_requires_real_investigation(self):  # NEW
        with self.assertRaises(ValueError):
            record.save_discovery("no-such-id", "something")

    def test_report_requires_real_investigation(self):  # NEW
        with self.assertRaises(ValueError):
            record.save_report("no-such-id", "investigation_report")

    def test_evidence_discovery_ownership(self):
        other = record.create_customer("Other", "other@example.com")
        disc = record.save_discovery(other["investigation_id"], "theirs")
        with self.assertRaises(ValueError):
            record.save_evidence(self.inv, "note", "x", discovery_id=disc)

    def test_seed_phrase_refused(self):  # NEW security guard
        seed = ("abandon ability able about above absent absorb abstract "
                "absurd abuse access accident")
        with self.assertRaises(ValueError):
            record.save_answer(self.inv, "notes", seed)

    def test_invalid_address_refused(self):  # NEW format validation
        with self.assertRaises(ValueError):
            record.save_bitcoin_address(self.inv, "definitely-not-an-address")

    def test_valid_address_saved_and_deduped(self):
        record.save_bitcoin_address(self.inv, LEGACY, "old wallet")
        with self.assertRaises(Exception):
            record.save_bitcoin_address(self.inv, LEGACY)

    def test_purchase_ownership_and_duplicate_payment(self):  # ownership existed; duplicate ref NEW
        record.save_purchase(self.cust["customer_id"], "guide", 999,
                             investigation_id=self.inv, status="completed",
                             payment_provider_reference="pi_test_123")
        with self.assertRaises(ValueError):
            record.save_purchase(self.cust["customer_id"], "guide", 999,
                                 investigation_id=self.inv, status="completed",
                                 payment_provider_reference="pi_test_123")
        other = record.create_customer("Other2", "o2@example.com")
        with self.assertRaises(ValueError):
            record.save_purchase(other["customer_id"], "guide", 999,
                                 investigation_id=self.inv)

    def test_purchase_unknown_customer(self):  # NEW
        with self.assertRaises(ValueError):
            record.save_purchase("ghost", "guide", 999)

    def test_complete_investigation_roundtrip(self):
        record.save_answer(self.inv, "device", "Yes")
        full = record.get_complete_investigation(self.inv)
        self.assertEqual(full["customer"]["email"], "test@example.com")
        self.assertEqual(len(full["answers"]), 1)
        self.assertTrue(full["timeline"])


def fake_provider_with_balance(address):
    return {"address": address, "tx_count": 12, "received_satoshis": 150_000_000,
            "sent_satoshis": 50_000_000, "balance_satoshis": 100_000_000,
            "unconfirmed_satoshis": 0, "latest_confirmed_timestamp": 1_600_000_000,
            "is_genesis_address": False, "source": "test-double"}


def fake_provider_down(address):
    raise BlockchainUnavailable("offline in tests")


class TestController(DbTestCase):
    def test_address_check_saves_confirmed_evidence_only_from_provider(self):
        record.save_bitcoin_address(self.inv, LEGACY)
        results = controller.run_address_investigation(self.inv, provider=fake_provider_with_balance)
        self.assertEqual(results[0]["status"], "checked")
        full = record.get_complete_investigation(self.inv)
        confirmed = [e for e in full["evidence"] if e["confidence"] == "confirmed"]
        self.assertTrue(any("1.00000000 BTC" in e["description"] for e in confirmed))
        self.assertTrue(any("does not prove" in e["description"] for e in confirmed))

    def test_provider_failure_records_unknown_never_fabricates(self):
        record.save_bitcoin_address(self.inv, LEGACY)
        results = controller.run_address_investigation(self.inv, provider=fake_provider_down)
        self.assertEqual(results[0]["status"], "unknown")
        full = record.get_complete_investigation(self.inv)
        self.assertFalse([e for e in full["evidence"] if e["confidence"] == "confirmed"])
        self.assertTrue([e for e in full["evidence"] if e["confidence"] == "unknown"])

    def test_three_products_pricing(self):
        self.assertEqual(controller.INVESTIGATION_REPORT_PRICE_CENTS, 999)
        self.assertEqual(controller.AI_WALKTHROUGH_PRICE_CENTS, 699)

    def test_pricing_math_approved_prices(self):
        self.assertEqual(controller.address_report_price_cents(1), 499)
        self.assertEqual(controller.address_report_price_cents(3), 499 + 2 * 199)

    def test_assessment_lead_and_guide_offer(self):
        record.save_answer(self.inv, "device", "Yes")
        record.save_answer(self.inv, "records", "Purchase confirmation emails")
        out = controller.assess_lost_bitcoin(self.inv)
        self.assertTrue(out["credible_lead"])
        self.assertEqual(out["guide_offer_cents"], 999)
        self.assertEqual(out["investigation_report_offer_cents"], 999)
        self.assertEqual(out["ai_walkthrough_offer_cents"], 699)

    def test_assessment_no_lead_no_charge(self):
        out = controller.assess_lost_bitcoin(self.inv)
        self.assertFalse(out["credible_lead"])
        self.assertIsNone(out["guide_offer_cents"])
        self.assertIsNone(out["investigation_report_offer_cents"])
        self.assertIsNone(out["ai_walkthrough_offer_cents"])

    def test_report_generation(self):
        record.save_answer(self.inv, "device", "Yes")
        record.save_answer(self.inv, "records", "Purchase confirmation emails")
        controller.assess_lost_bitcoin(self.inv)
        out = report_generator.generate_report(self.inv, Path(self.tmp.name) / "reports")
        self.assertTrue(Path(out["file_path"]).exists())
        self.assertIn("Recovery is never guaranteed", out["markdown"])
        self.assertIn("Possible leads", out["markdown"])
        self.assertIn("How to read this report", out["markdown"])
        self.assertIn("Detailed action checklists", out["markdown"])
        self.assertIn("Make a verified copy before searching it", out["markdown"])
        self.assertIn("Search the original email account for", out["markdown"])


class TestBalanceOnDate(unittest.TestCase):
    def test_balance_on_date_subtracts_later_activity(self):
        import blockchain_provider as bp
        from datetime import datetime, timezone
        from unittest import mock

        addr = GENESIS
        after = int(datetime(2024, 6, 1, tzinfo=timezone.utc).timestamp())
        before = int(datetime(2024, 1, 1, tzinfo=timezone.utc).timestamp())

        def tx(txid, block_time, vout=None, vin=None):
            return {"txid": txid, "status": {"confirmed": True,
                                             "block_time": block_time},
                    "vout": vout or [], "vin": vin or []}

        txs = [
            tx("new", after, vout=[{"scriptpubkey_address": addr,
                                    "value": 50000}]),
            tx("mid", after, vin=[{"prevout": {"scriptpubkey_address": addr,
                                               "value": 20000}}]),
            tx("old", before, vout=[{"scriptpubkey_address": addr,
                                     "value": 170000}]),
        ]

        def fake_api(endpoint):
            if endpoint == f"/address/{addr}":
                return {"chain_stats": {"tx_count": 3,
                                        "funded_txo_sum": 300000,
                                        "spent_txo_sum": 100000},
                        "mempool_stats": {"funded_txo_sum": 0,
                                          "spent_txo_sum": 0}}
            if endpoint.startswith(f"/address/{addr}/txs"):
                return txs
            raise AssertionError(endpoint)

        with mock.patch.object(bp, "_api_request", side_effect=fake_api):
            self.assertEqual(bp.fetch_balance_on_date(addr, "2024-01-15"),
                             170000)


class TestValuationReport(DbTestCase):
    def test_wallet_report_includes_dated_valuation(self):
        import blockchain_provider as bp
        import historical_price as hp
        from unittest import mock

        cust = record.create_customer(
            "Estate Person", "estate@example.com", "bitcoin_address")
        inv = cust["investigation_id"]
        record.save_bitcoin_address(inv, GENESIS, "estate wallet")
        record.save_answer(inv, "valuation_date", "2024-01-15")
        with mock.patch.object(bp, "fetch_balance_on_date",
                               return_value=170000), \
             mock.patch.object(hp, "price_on",
                               return_value={"cad": 50000.0, "usd": 37000.0,
                                             "source": "coingecko.com"}):
            md = report_generator.build_report_markdown(inv)
        self.assertIn("Valuation on 2024-01-15", md)
        self.assertIn("0.0017 BTC", md)
        self.assertIn("$85.00 CAD", md)
        self.assertIn("not tax or legal advice", md)


class TestScamCheckAndZeroGuide(unittest.TestCase):
    def test_scam_check_renders_with_rules(self):
        import guides
        page = guides.render_scam_check()
        self.assertIn("CHECK THIS MESSAGE", page)
        self.assertIn("seed phrase", page)
        self.assertIn("never sent or stored", page)

    def test_zero_guide_live_in_index(self):
        import guides
        post = guides.render_post("restored-bitcoin-wallet-shows-zero")
        self.assertIsNotNone(post)
        self.assertIn("derivation path", post)
        self.assertIn("restored-bitcoin-wallet-shows-zero",
                      guides.render_index())


if __name__ == "__main__":
    unittest.main()
