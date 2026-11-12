# Lost Bitcoin — Development Copy

This is the working development copy. The original uploaded ZIP is preserved
untouched in `../backups/` and `../original_unzipped/` — never edit those.

## Layout
- `master_investigation_record.py` — central SQLite record (10 tables). Patched 2026-11-12, see CHANGELOG.md.
- `bitcoin_address_validation.py` — NEW. Pure-stdlib address format validation (Base58Check + Bech32/Bech32m).
- `blockchain_provider.py` — NEW. The single place live chain data enters (Blockstream API, stdlib only). Consolidates the API code previously duplicated in five CLI scripts.
- `investigation_controller.py` — NEW. Priority 2: rules-controlled controller (Option B). Inject a fake provider in tests; never fabricates data — provider failure = UNKNOWN evidence.
- `report_generator.py` — NEW. Markdown reports separated into Confirmed / Strong possibilities / Possible leads / Unknowns, registered via `save_report()`.
- `index.html` — the customer website, connected to `app.py`. New 2026 palette (Cloud Dancer + Transformative Teal + solar amber) 12 Nov.
- `app.py` — zero-dependency web backend (start/resume/answers/addresses/run/report/checkout/walkthrough/webhook).
- `payments.py` — Stripe-ready checkout + webhook verification; demo checkout when no Stripe key is set. Reports gated until purchased.
- `walkthrough.py` — AI Guided Next Steps ($6.99): deterministic, record-grounded chat.
- `privacy.html` / `terms.html` — DRAFT legal pages.
- Older CLI tools (`bitcoin_address_investigator.py`, `bitcoin_address_intelligence.py`, `bitcoin_transaction_tracer.py`, `bitcoin_history_timeline.py`, `multiple_address_investigator.py`, `lost_bitcoin_investigator*.py`, `lost_bitcoin_report_v6.py`, `lost_bitcoin_guide.py`, `lost_bitcoin_scanner.py`, `bitcoin_research.py`) — reference material. Their logic is being absorbed into the provider/controller; do not build new features on the interactive `input()` scripts.
- `backups_archive/` — pre-repair snapshots from the original ZIP, preserved as received (three have syntax errors; they are history, not code to run).

## Run tests
```
cd dev && python3 -m unittest discover -s tests -v   # 21 tests, fictional data only
```
Database path can be overridden with the `LOST_BITCOIN_DB` environment variable or `master_investigation_record.set_database_path(...)`.

## Pricing (approved — do not change without founder approval)
- Investigation Report: $9.99 USD, only when a credible lead is identified. Initial assessment free.
- AI Guided Next Steps (AI chat bot walkthrough): $6.99 USD.
- Address Report: $4.99 USD first address, $1.99 USD each additional.

## Hard rules
Never request/store seed phrases, private keys, or wallet passwords (the record module now refuses seed-phrase-like answers). Never promise recovery. A balance ≠ ownership. Verify Stripe payments server-side via webhooks (not yet integrated — Priority 4).
