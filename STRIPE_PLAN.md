# Stripe Integration Plan — Lost Bitcoin

Tailored plan generated for Mark's business context (2026-11-12), with a
review of the existing integration in `payments.py` / `app.py`.

**Business:** lostbitcoin.org — investigative software that helps customers
begin retrieving lost or inaccessible Bitcoin. Sells investigation and
evidence, never guaranteed recovery.
**Stripe need:** one-time Payments only. No subscriptions, no Connect,
no in-person, no stored payment methods.

## Products (fixed catalog, USD — Mark's approved prices)
| Product | Price | Notes |
|---|---|---|
| Investigation Report | $9.99 | Offered only when a credible lead is identified |
| AI Guided Next Steps | $6.99 | Add-on walkthrough |
| Wallet Report | $4.99 first address + $1.99 each additional | Price varies by address count (1–n) |

## Recommended architecture (already the design in code)
1. **Stripe-hosted Checkout** (`mode=payment`). Card data never touches our server → PCI SAQ-A, the lightest compliance tier. ✅ in code.
2. **Prices:** the two fixed products map cleanly to Stripe Products/Prices; the Wallet Report's per-address pricing is computed server-side and passed as an amount, so all three launch as Checkout line items without a product-catalog dependency. Optional post-launch cleanup: create the two fixed Products/Prices in the dashboard for cleaner reporting.
3. **Purchase truth = webhook, never the browser.** A purchase is recorded only from a signature-verified `checkout.session.completed` event with `payment_status=paid`. The success redirect is UX only. ✅ in code (HMAC verification, 5-min timestamp tolerance).
4. **Idempotency in two places:** Checkout creation sends a deterministic `Idempotency-Key` per investigation+product+amount (double-click safe) ✅ added 2026-11-12; webhook deliveries are deduplicated by the record module's unique payment-reference guard, and duplicates are acknowledged so Stripe stops retrying ✅ in code.
5. **Metadata everywhere:** `investigation_id`, `customer_id`, `product` on the session *and* mirrored onto the PaymentIntent ✅ added 2026-11-12 — refunds/disputes in the dashboard can be traced to an investigation in seconds.
6. **Customer email prefilled** from the investigation record ✅ added 2026-11-12 (also feeds Stripe's receipt email; enable receipts in the Stripe dashboard instead of building our own).
7. **Keys:** test-mode keys first (`sk_test_…`). Secret key + webhook secret live only as server environment variables (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`) — never in code, never in chat. Demo checkout disables itself automatically the moment a secret key is configured ✅ in code.

## Go-live sequence (once Mark's account exists)
1. Mark creates the Stripe account (Canada, sole proprietor/business as applicable), completes identity verification — **start early; verification can take 1–2 days**.
2. Payout currency decision: USD prices + default CAD payout = ~2% conversion on each sale (keep ≈ $9.20 of $9.99). If Mark already holds a USD bank account, add it as a USD payout account to skip conversion (keep ≈ $9.40). Not worth a new account for 10 customers.
3. Muse wires test keys → runs a full test-mode checkout against the review server (card 4242…), confirms the webhook records exactly one purchase, confirms a duplicate webhook delivery records nothing new, confirms reports unlock.
4. In the Stripe dashboard: create the live webhook endpoint (`https://lostbitcoin.org/api/stripe/webhook`, event `checkout.session.completed`), enable customer receipt emails, set the business name/statement descriptor to LOST BITCOIN so cards show a recognizable charge.
5. Swap test keys for live keys at deploy (Railway env vars, per Mark's hosting pick), one $4.99 live self-purchase + refund as the final smoke test.

## Review of the existing integration (vs. this plan)
Already correct: hosted Checkout; webhook-only purchase recording with signature verification; server-side price computation (the browser can never name its own price — amounts come from the controller constants); report/walkthrough gating server-side (HTTP 402 until purchased); duplicate-payment protection; no card data anywhere near our code.
Fixed during this review: missing idempotency key on session creation; customer email not prefilled; success URL lacked the session ID; PaymentIntent had no metadata.
Deliberately not built (wrong for this business): subscriptions, saved cards, Stripe Tax (digital reports to consumers — Mark should confirm his GST/HST obligations with his accountant; that's a tax question, not a code one), PayPal as a second rail for the first 10 customers.

## Note on tools
The pasted setup steps (Claude plugin / `stripe_implementation_planner`) target Claude Code, which this environment (Muse) doesn't use. The equivalent here is the built-in Stripe connector, which talks to Stripe's official MCP server (https://mcp.stripe.com) over OAuth — Mark connects his account with the connect link, no API keys are ever pasted into chat. Once connected, Muse can create the dashboard Products/Prices and check payments/balances directly.
