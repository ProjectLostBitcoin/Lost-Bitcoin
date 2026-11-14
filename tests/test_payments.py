"""Payments unit tests — no Stripe keys, no network."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import payments

class TestPayments(unittest.TestCase):
    def test_prices_match_approved(self):
        self.assertEqual(payments.price_for("investigation_report"), 999)
        self.assertEqual(payments.price_for("ai_walkthrough"), 699)
        self.assertEqual(payments.price_for("wallet_report", address_count=1), 499)
        self.assertEqual(payments.price_for("wallet_report", address_count=3), 897)
        with self.assertRaises(ValueError):
            payments.price_for("wallet_report", address_count=0)
        with self.assertRaises(ValueError):
            payments.price_for("nonsense")

    def test_session_form_best_practices(self):
        form = payments.build_session_form("inv1", "cust1", "investigation_report", 999,
                                           customer_email="a@example.com")
        self.assertEqual(form["mode"], "payment")
        self.assertIn("{CHECKOUT_SESSION_ID}", form["success_url"])
        self.assertEqual(form["customer_email"], "a@example.com")
        self.assertEqual(form["metadata[investigation_id]"], "inv1")
        self.assertEqual(form["payment_intent_data[metadata][product]"], "investigation_report")
        self.assertEqual(form["line_items[0][price_data][unit_amount]"], "999")
        form2 = payments.build_session_form("inv1", "cust1", "ai_walkthrough", 699)
        self.assertNotIn("customer_email", form2)

    def test_session_form_uses_catalogue_product_when_configured(self):
        saved = payments.STRIPE_PRODUCT_IDS["wallet_report"]
        try:
            payments.STRIPE_PRODUCT_IDS["wallet_report"] = "prod_test123"
            form = payments.build_session_form("inv1", "cust1", "wallet_report", 897)
            self.assertEqual(form["line_items[0][price_data][product]"], "prod_test123")
            self.assertNotIn("line_items[0][price_data][product_data][name]", form)
            self.assertEqual(form["line_items[0][price_data][unit_amount]"], "897")
        finally:
            payments.STRIPE_PRODUCT_IDS["wallet_report"] = saved
        form = payments.build_session_form("inv1", "cust1", "wallet_report", 499)
        self.assertIn("line_items[0][price_data][product_data][name]", form)

    def test_session_form_tax_only_when_enabled(self):
        saved = payments.STRIPE_TAX_ENABLED
        try:
            payments.STRIPE_TAX_ENABLED = False
            form = payments.build_session_form("inv1", "cust1", "investigation_report", 999)
            self.assertNotIn("automatic_tax[enabled]", form)
            payments.STRIPE_TAX_ENABLED = True
            form = payments.build_session_form("inv1", "cust1", "investigation_report", 999)
            self.assertEqual(form["automatic_tax[enabled]"], "true")
            self.assertEqual(form["billing_address_collection"], "required")
        finally:
            payments.STRIPE_TAX_ENABLED = saved

    def test_idempotency_key_stable_and_scoped(self):
        k1 = payments.idempotency_key("inv1", "investigation_report", 999)
        self.assertEqual(k1, payments.idempotency_key("inv1", "investigation_report", 999))
        self.assertNotEqual(k1, payments.idempotency_key("inv1", "ai_walkthrough", 699))
        self.assertNotEqual(k1, payments.idempotency_key("inv2", "investigation_report", 999))

    def test_demo_token_roundtrip_and_tamper(self):
        token = payments._demo_token("inv1", "ai_walkthrough", 699)
        data = payments.verify_demo_token(token)
        self.assertEqual(data["product"], "ai_walkthrough")
        self.assertIsNone(payments.verify_demo_token(token[:-4] + "0000"))
        self.assertIsNone(payments.verify_demo_token("junk"))

if __name__ == "__main__":
    unittest.main()
