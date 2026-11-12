# Lost Bitcoin — Prioritized Implementation Plan (12 Nov 2026)

Goal: first 10 paying customers, human-supervised MVP, 8–12 week window at 5–10 founder hrs/week (build work is Muse's; founder time is decisions and reviews).

## Done
- **P1 Audit & strengthen** ✅ Audit file-by-file (AUDIT.md); master record validation/security fixes; address checksum validation; seed-phrase storage guard; test suite (22 tests).
- **P2 Central investigation controller** ✅ Rules-controlled (Option B); Blockstream provider consolidated; evidence classified Confirmed/Strong/Possible/Unknown; pricing offers for all three products; report generator. Live-verified.

## This round
- **P3 Website ↔ backend** — Stdlib-only Python backend (`app.py`, zero dependencies to install): start/resume, save answers, save addresses, run investigation, get record, generate report. Signed, expiring resume tokens (customer can leave and return; token is the private-beta stand-in for emailed magic links). Website wired to it: two starting points, questionnaire saves as you go, address flow, saved-progress resume. API tests + live smoke test.

## Next, in order
- **P4 Payments (Stripe test mode)** — Hosted checkout for the three products ($9.99 / $6.99 / $4.99+$1.99), server-side webhook verification, purchase recorded against the right investigation (duplicate-reference protection already in place). *Founder action: create the Stripe account; everything else is prepared first.*
- **P5 Report delivery + AI walkthrough** — Email the generated report (needs an email provider decision — one question for Mark); build the $6.99 AI Guided Next Steps chat on top of the record + recommendations, with the same never-invent-facts rules.
- **P6 Controlled launch prep** — Terms, privacy, refund policy, disclaimers (drafts prepared for Mark's review, not legal advice), security pass (HTTPS/deployment choice), private beta with fictional-then-invited users, support inbox workflow for hello@lostbitcoin.org.

## Explicitly deferred (per brief)
Fully autonomous AI investigations, admin dashboards, mobile apps, subscriptions, advanced analytics, the file scanner product.

## Risks / open decisions for Mark (none block P3)
1. Email provider for magic links + report delivery (P5).
2. Where lostbitcoin.org will be hosted (affects deployment steps in P6).
3. Stripe account creation (P4) — Mark only; ~15 minutes when we get there.
