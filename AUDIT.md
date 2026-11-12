# Lost Bitcoin — Full Audit (12 Nov 2026)

Original ZIP preserved untouched (`../backups/`, sha256 e59a7302…). Full-project backup taken before this round of changes: `../backups/full-backup-20261112_074012.zip` (77 files, verified).

## File-by-file verdicts

### Core (keep, strengthen)
- **master_investigation_record.py** (1,286 lines) — The foundation. 10 SQLite tables, FK integrity, email/duplicate/ownership validation. Issues found and fixed 12 Nov: missing investigation-existence checks in save_answer/save_discovery/save_report; purchase customer check + duplicate payment-reference protection; no address format validation; no seed-phrase storage guard; duplicated helper; hard-coded DB path. **Status: production-track, patched and tested.**
- **index.html** (845 lines) — Clean, reassuring questionnaire prototype with sound disclaimers ("does not verify ownership", seed-phrase warning). Weaknesses: standalone (no backend, no saving, no resume), only covers the lost-Bitcoin path (no address starting point), upgrade text was vague about products. Pricing now correctly labelled ($9.99 report / $6.99 AI walkthrough). **Status: being connected to the backend in this round.**

### Blockchain tools (absorb into provider/controller, then retire as standalone scripts)
All five call the same Blockstream API, print to terminal, take `input()`, and return nothing structured — good research code, unusable as backend components as-is. Their logic now lives in `blockchain_provider.py` + `investigation_controller.py`.
- **bitcoin_address_investigator.py** — urllib version; correct balance/activity logic. Absorbed.
- **bitcoin_address_intelligence.py** — requests version; adds the Genesis-address unspendable warning (kept — it fired correctly in live testing). Absorbed.
- **bitcoin_transaction_tracer.py** — address summary + transaction detail display. Logic absorbed; detailed tx listing is a future report enhancement.
- **bitcoin_history_timeline.py** — full paginated history + first/last activity analysis. Pagination approach noted for the Wallet Report v2; basic activity absorbed.
- **multiple_address_investigator.py** — loops the single-address check; superseded by the controller + approved per-address pricing. Absorbed.

### Questionnaire / guide prototypes (mine for content, retire the code)
- **lost_bitcoin_investigator_v4.py** — The richest of these: branching question sets per starting point and prioritized, well-worded recommendation text (preserve-the-device, verify-the-purchase, honest no-guarantee language). **Best content source after index.html** — its recommendation wording should be absorbed into the controller in a later section.
- **lost_bitcoin_investigator_v5.py** — Profile questions + a keyword-matching "investigator chat" loop. This is the conceptual ancestor of the $6.99 AI Guided Next Steps product, but it is keyword matching, not AI. Retire code; keep the concept.
- **lost_bitcoin_investigator.py / lost_bitcoin_guide.py** — Early CLI questionnaires, superseded by v4 and the website. Retire.
- **lost_bitcoin_report_v6.py** — CLI questionnaire that builds a personal report; superseded by `report_generator.py`. Retire.
- **lost_bitcoin_scanner.py** — Scans a folder for wallet-like filenames (wallet.dat, electrum, etc.), correctly labelled "leads, not proof". Interesting future lead-generation tool for the Recovery Guide, but it uses a hard-coded home path and is not customer-safe yet. Park it — do not ship in MVP.
- **bitcoin_research.py** — Block lookup experiments. Learning code. Retire.

### Backups inside the ZIP (17 files)
Pre-repair snapshots of the master record. Three have syntax errors (they predate their fixes). All moved to `backups_archive/`, preserved exactly as received. They are history, not runnable code.

## What already worked before this round
Customer creation/resume, answer/discovery/evidence/recommendation/address/report/purchase storage, complete-record retrieval, timeline — all verified by tests against the real module, not just read.

## What was incomplete before this round
Tool integration (done — controller), website↔backend connection (this round), customer authentication (token-based resume this round; emailed magic links need an email provider — founder decision), payments (Stripe, next round), report delivery, legal pages, deployment.
