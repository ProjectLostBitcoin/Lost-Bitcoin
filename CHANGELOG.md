# Changelog

## 2026-11-12 (afternoon) — Stripe connected; catalogue products created

- Founder connected Stripe to Muse (OAuth). The connected account is
  his sandbox, "Project Lost Bitcoin sandbox" (livemode: false) — the
  right environment for test-mode checkout verification.
- Created the three catalogue products in the sandbox:
  Investigation Report `prod_VcLHCFWh1IubZv` ($9.99),
  AI Guided Next Steps `prod_VcLHV3tsGVLWEa` ($6.99),
  Wallet Report `prod_VcLH73zkbFZcag` ($4.99 first / $1.99 extra address).
  No tax code set — GST/HST treatment stays an open founder/accountant
  question, deliberately untouched.
- `payments.py`: checkout now attaches to the catalogue product when
  `STRIPE_PRODUCT_*` env vars are set (per environment), instead of
  creating a throwaway product per sale; inline product name remains
  the fallback. New test covers both paths — 36/36 tests pass.

## 2026-11-12 (afternoon) — Deployment preparation

- Founder completed Stripe setup (account activated, bank linked); chose
  prebuilt hosted Checkout, full-page mode — matches the built integration.
- `app.py`: bind address now from `HOST` env (default 127.0.0.1 for local
  review; hosts set 0.0.0.0), reports dir overridable via
  `LOST_BITCOIN_REPORTS_DIR`, created at startup if missing.
- Added `Dockerfile`, `.dockerignore`, `railway.json` (health check
  `/api/health`), `fly.toml` (fallback host, /data volume, yyz),
  `scripts/backup_db.sh` (SQLite online backup, keeps 14), `DEPLOY.md`
  (env-var checklist, Namecheap DNS steps, test-mode go-live sequence).
- Verified: 35/35 unit/API tests pass; deploy-config smoke test booted
  with HOST/PORT/DB/reports env vars against a scratch volume — health
  and pricing endpoints correct, backup script produced a valid copy.
- Domain check: lostbitcoin.org DNS is at Namecheap (registrar-servers
  nameservers), currently on Namecheap's parking page; DNS records for
  the chosen host get added there at deploy time.

## 2026-11-12 — Audit + Priority 1 fixes + Priority 2 controller (Muse, technical lead)

### Audit findings
- All main scripts pass Python syntax. Three old pre-repair backup snapshots in the ZIP fail syntax (IndentationError/SyntaxError) — expected, they predate their fixes; moved to `backups_archive/`, preserved.
- `master_investigation_record.py` (1,286 lines) is sound overall: 10 tables, FK integrity, email/duplicate/ownership validations as described in the handover.
- Issues found in the master record:
  1. `save_answer`, `save_discovery`, `save_report` did not verify the investigation exists (inconsistent raw FK errors instead of a clear ValueError).
  2. `save_evidence` only validated the investigation indirectly via a discovery.
  3. `save_purchase` did not verify the customer exists when no investigation was attached, and had no duplicate protection on `payment_provider_reference` (needed for safe Stripe webhook handling).
  4. `save_bitcoin_address` accepted any non-empty string — no format/checksum validation.
  5. No guard against a customer pasting a seed phrase/private key into an answer field.
  6. `rows_to_dictionaries` defined twice; `import uuid` mid-file; DB path hard-coded (untestable); no WAL/busy timeout.
- Five CLI tools duplicate the same Blockstream API calls; all are interactive `input()` scripts, none return structured data — unsuitable as-is for a backend.
- `index.html` showed a stale **$6.99** price conflicting with approved $9.99 pricing.

### Fixes applied to `master_investigation_record.py` (original preserved in ../backups/)
- Investigation-existence validation in save_answer / save_discovery / save_evidence / save_report; customer-existence + duplicate-payment-reference validation in save_purchase.
- Real Bitcoin address format validation on save (new `bitcoin_address_validation.py`).
- Seed-phrase / WIF private-key refusal in save_answer (`contains_sensitive_secret`).
- Duplicate function removed, imports tidied, DB path configurable (`LOST_BITCOIN_DB` / `set_database_path`), WAL + busy_timeout enabled.

### New modules
- `blockchain_provider.py`, `investigation_controller.py`, `report_generator.py` (see README).
- `tests/test_all.py` — 21 tests, all passing. Live smoke test against Blockstream for the Genesis address passed end-to-end (real balance/tx count returned, Genesis unspendable warning recorded as CONFIRMED evidence).

### Website
- `index.html` prototype price corrected to $9.99 with approved product wording.

### Not done yet (next priorities)
- Priority 3: backend + website connection, passwordless email sign-in, customer resume in the UI.
- Priority 4: Stripe test-mode checkout + webhook verification.
- Priority 6: terms/privacy/refund policy, private beta.

## 2026-11-12 (later) — Pricing correction from Mark
Mark clarified there are THREE products, and the website's $6.99 was never stale:
- Investigation Report: $9.99 (free initial assessment first; charged when a credible lead is found)
- AI Guided Next Steps (AI chat bot walkthrough of proposed next steps): $6.99
- Wallet Report: $4.99 first address + $1.99 each additional
The earlier dev-copy change of index.html $6.99 → $9.99 was wrong and has been reverted; the page now labels all three products distinctly. Controller now exposes `investigation_report_offer_cents` (999) and `ai_walkthrough_offer_cents` (699) alongside the wallet-report pricing. Tests updated (22 passing).

## 2026-11-12 — Priority 3: website connected to backend
- Full backup before changes: `../backups/full-backup-20261112_074012.zip` (77 files, sha256 2b3adbb4…).
- `AUDIT.md`: file-by-file verdicts for every Python file and the website (keep / absorb / retire / park).
- `PLAN.md`: prioritized plan — P4 Stripe test mode, P5 report delivery + AI walkthrough, P6 launch prep; three founder decisions listed, none blocking.
- NEW `app.py`: zero-dependency (stdlib) web backend. Endpoints: /api/start, /api/resume, /api/answer, /api/address, /api/run, /api/investigation, /api/report, /api/pricing, /api/health. Signed expiring resume tokens with per-customer ownership checks (403 for someone else's investigation), body-size limit, throttling on identity endpoints, security headers. Production note in code: tokens must move to emailed magic links once an email provider is chosen.
- `index.html` connected: two starting points on the homepage, name/email start form, questionnaire answers save to the server as they're given (seed-phrase refusal surfaces to the customer), full Bitcoin-address flow with live results and correct Wallet Report pricing, resume-by-email restoring saved answers, preliminary assessment + the $9.99 / $6.99 offers shown from the server's own assessment. Opening the file without the server still works in a clearly-labelled unsaved demo mode.
- Tests: 29 passing (22 unit/controller + 7 API), including auth/ownership, duplicate-start resume, address validation and seed-phrase refusal through the real HTTP API.

## 2026-11-12 — Finish-line session (while Mark at work)
### Testing at scale (new)
- NEW `tests/e2e_random_customers.py`: randomized full-journey tester (random emails/names/answers, both starting points, resume, cross-customer attacks, seed phrases, XSS payloads, duplicate/invalid addresses, double runs, checkout, walkthrough). Baseline run: 78 failures — found real bugs below.
- BUG FIXED (all journeys): investigation runs were not idempotent — every re-run duplicated discoveries/evidence/recommendations in the customer's record. Controller now dedupes by existing content; re-runs refresh the view without duplicating the record.
- BUG FIXED: adding the same address twice returned HTTP 500. Now a friendly "already saved" 400 (record-level check + API backstop).
- BUG FOUND BY SCALE + FIXED: identity rate limit (30/hr per IP) locked out legitimate customers sharing one NAT IP and broke journeys at ~#38. Raised to 120/hr (env-configurable).
- SECURITY FIXED: questionnaire answers were rendered into the report page unescaped (stored-XSS via a crafted text answer). All user-derived rendering now escaped, including walkthrough chat.
- UX FIXED: resume dumped completed-or-not customers onto the report page; now resumes at the first unanswered question. Enter key now submits text answers / resume / address / walkthrough inputs; inputs autofocus.
### Colours (Mark disliked the old cold blue-grey)
- Researched 2026 trends (Pantone COTY Cloud Dancer warm off-white #F0EEE9; WGSN/Coloro COTY Transformative Teal #0F5C63; fintech guidance: deep anchor + gold accent sparingly, never gold text on white).
- New palette: Cloud Dancer page base, warm-white cards, deep teal header/buttons (white text, ~7.5:1), solar amber #E8A838 reserved for logo/progress/badges with dark text. Favicon added.
### Priority 4 — Payments (prepared + reviewable)
- NEW `payments.py`: Stripe Checkout Session creation when STRIPE_SECRET_KEY is set; webhook signature verification (stdlib HMAC) with duplicate-delivery safety via the record's payment-reference protection; reports gated server-side (HTTP 402 until purchased). Without a Stripe key, a clearly-labelled DEMO checkout exercises the identical flow and disables itself once Stripe is configured. Founder action remaining: create Stripe account + paste keys.
### Priority 5 — AI Guided Next Steps ($6.99)
- NEW `walkthrough.py` + chat UI: deterministic, record-grounded walkthrough (next-step coaching, step lists, confirmed-evidence summaries, pricing, honest no-guarantee answers, seed-phrase refusal + safety warning, customer updates saved as discoveries). Gated behind the $6.99 purchase.
### Priority 6 — drafts
- `privacy.html` / `terms.html`: plain-English drafts (products/prices, no-guarantee, refund policy, never-collect-secrets) linked from the footer, banner-marked DRAFT — not legal advice.
### Final verification
- Unit/API: 31/31 passing. E2E: 3 final clean runs × 60 journeys = 180 journeys, 3,286 checks, 0 failures (results in tests/e2e_results_run{1,2,3}.json).
- Live smoke test (real Blockstream, real server): address → run → $4.99 demo checkout → paid report generated containing the Genesis unspendable warning; new palette and legal pages served correctly.

## 2026-11-12 — Stripe setup started (Mark: "starting with the first step")
- Stripe connector (official MCP, OAuth) checked: not yet connected; connect link given to Mark. No API keys in chat — ever.
- `STRIPE_PLAN.md`: tailored integration plan for the business + review of the existing integration.
- payments.py best-practice fixes: deterministic Idempotency-Key on Checkout creation; customer email prefilled (passed from the record via app.py); success_url now carries {CHECKOUT_SESSION_ID}; metadata mirrored onto the PaymentIntent; session-form building extracted to a pure, tested function. Tests: 35/35 unit+API, plus a 30-journey E2E regression.
