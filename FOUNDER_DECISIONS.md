# Founder decisions — ready for Mark's evening review (prepared 2026-11-12, morning)

## Decisions log

- **2026-11-12 — Hosting: Railway.** Mark picked Railway over Fly.io
  (Fly.io config stays in the repo as the checked fallback). Deploy
  conditions from the addendum apply: $10 hard usage limit, database
  backups pulled off Railway. Stripe was completed the same day
  (prebuilt hosted Checkout, full-page mode; sandbox connected to
  Muse; catalogue products created). Still open: USD-vs-CAD payout
  (unanswered — CAD assumed from the bank he linked), Resend/email
  step, legal draft review.

## Update — verified 2026-11-12 afternoon, before Mark picks tonight

Two unknowns from this morning are now checked against the providers' own
pages, plus one new fact that arrived after the sheet was written. None of
this changes the three recommendations, but two numbers in the sheet below
need correcting, and the Railway item needs a judgement call from Mark.

### 1. Stripe — the $9.40 figure was optimistic unless Mark adds a USD payout account

Verified against Stripe's Canada pricing (stripe.com/en-ca/pricing, via
rate round-ups checked Oct 2026) and Stripe's payout docs
(docs.stripe.com/payouts): Canada domestic card **2.9% + CA$0.30**,
international card **+0.8%**, currency conversion **+2%** when the charge
currency differs from the settlement currency. Those add up.

Mark's prices are in USD. With the default CAD payout account, a USD charge
is converted, so the +2% applies on top:

- $9.99 report — US card, CAD payout: ~5.7% + CA$0.30 → keep **~$9.20**
  (not ~$9.40). Canadian card, CAD payout: ~4.9% + CA$0.30 → keep **~$9.28**.
- $6.99 walkthrough — US card, CAD payout: keep **~$6.37**; $4.99 wallet
  report: keep **~$4.49**. (CA$0.30 is roughly US$0.21–0.22; exact figure
  moves with the exchange rate, so treat these as ~, not to the cent.)

**The fix, if Mark has a USD bank account:** Stripe lets a Canadian
account settle USD charges into a USD bank account in Canada with no
conversion — "charges that are presented in any enabled settlement currency
settle without currency conversion" (Stripe payout docs). With that set
up, the US-card $9.99 keep is back to **~$9.40**, and the +2% disappears
on every USD sale. Worth doing at Stripe setup if he already has a USD
account; not worth opening a new bank account just for the first 10
customers — the difference is ~20¢ a sale.

### 2. Railway — $5 is a floor, not a cap; and there was a serious security incident in October

Verified against Railway's pricing (via round-ups checked Oct–Nov 2026):
Hobby is **$5/mo minimum, including $5 of usage credit** — the bill is
whichever is higher, the $5 or actual usage. Meters: **$20/vCPU/mo,
$10/GB RAM/mo, $0.15/GB volume, $0.05/GB egress**, billed per second.
The sheet's ~$5 estimate still holds *only if* this app stays light
(~0.1 vCPU + ~0.25 GB RAM ≈ $4.50 + volume). If it averages 0.25 vCPU +
0.5 GB RAM, the bill is ~$10. Mitigation when setting up: set a hard
usage limit (minimum $10) in Railway billing so it can never run away
unnoticed.

**New fact — Railway security incident, Oct 20–21, 2026; full report
published Nov 10, 2026 (blog.railway.com, via SecQuill 2026-11-10):**
an attacker escaped build-system isolation and decrypted a subset of
customer environment variables — at most 1.85% of workspaces (~100,000),
targeting AI provider keys, with ~$740,000 of unauthorised spend on
stolen keys. Railway evicted the attacker Oct 21, invalidated all
sessions/tokens, moved builds to per-build VMs, and restored builds by
Oct 22. Signups reopened Nov 2; new customers must subscribe to a paid
plan (Hobby/Pro) before deploying — no free-trial deploy for now.
For Lost Bitcoin this matters more than for a hobby app: Stripe keys
and the app secret would live as Railway environment variables — exactly
what was exposed. The incident is resolved and the fix is structural,
so the recommendation (Railway) stands, but Mark should know before
he puts customer data and payment keys there. If he'd rather not, the
fallback is Fly.io: smallest always-on machine $2.19/mo (256 MB) +
$0.15/GB volume, so ~$2.50–$2.70/mo for this app, no monthly minimum —
but it needs a Dockerfile/`fly.toml` and has no spending cap by default,
so it's more setup for ~$2.50/mo saved. Say the word and I'll re-price
and re-plan around Fly.io instead; otherwise I'll proceed with Railway
plus a usage limit and off-Railway DB backups.

### 3. Resend — confirmed, no change

Free plan confirmed: **$0, 3,000 emails/mo, hard-capped at 100/day, no
overage** — the 101st email of a day fails rather than charging. Fine
for the first 10 customers; just don't plan a bulk send on launch day.

---

# Founder decisions — ready for Mark's evening review (prepared 2026-11-12, morning)

Private-beta v2 is built and tested. These are the only three founder decisions
blocking launch. Nothing here changes pricing — all three products stay as Mark
approved: Investigation Report $9.99, AI Guided Next Steps $6.99, Wallet Report
$4.99 + $1.99 per extra address.

Prices below were checked 2026-11-12 from vendor pricing pages / recent
price round-ups. Confirm on the provider's own pricing page before paying;
rates change.

## 1. Payments — Stripe (recommended: yes, Stripe only to start)

- **What it is:** the checkout already built into `payments.py` switches from
  demo to live Stripe automatically once keys are set. No code change needed.
- **Cost:** no setup or monthly fee. Canada domestic card: **2.9% + CA$0.30**
  per successful charge; international cards +0.8%; currency conversion +2%
  if charged in a currency other than the payout currency.
- **What Mark keeps per sale (approx., USD card, before any FX):**
  - $9.99 report → ~$0.59 fee → ~**$9.40**
  - $6.99 walkthrough → ~$0.50 fee → ~**$6.49**
  - $4.99 wallet report → ~$0.44 fee → ~**$4.55**
- **Mark's job (~15 min + ID/bank details):** create the Stripe account,
  add business + bank details, copy the secret key + webhook secret to Muse.
  Start this early — Stripe identity verification can take a day or two,
  so don't leave it to launch day.
- **Muse's job after:** paste keys into env vars, run a live test-mode
  checkout end-to-end, confirm the webhook records the purchase.
- **Alternative considered:** PayPal — similar fees in Canada, but the code
  is already built for Stripe and Stripe's hosted checkout keeps card
  details off our server. Not recommended as a second provider for the
  first 10 customers.

## 2. Email — Resend, Free plan (recommended)

Needed for emailed magic links (resume) and report delivery. Today the
resume token is returned to the browser — fine for private review, not
for real customers.

- **Cost:** **$0** — Free plan: 3,000 emails/month, capped at 100/day,
  1–3 verified domains. First 10 customers need only a few dozen emails
  total (magic link + report + receipt each), so free covers launch with
  huge headroom. Next step up is Pro $20/mo for 50,000 — only if volume
  ever justifies it.
- **Why Resend over the alternatives:** simple HTTP API, so it fits the
  zero-dependency backend (no SDK to install); domain verification for
  lostbitcoin.org is a few DNS records; sender is hello@lostbitcoin.org.
  Postmark ($15/mo, no comparable free tier) and Amazon SES (cheapest at
  scale, but more setup) are both fine later — neither beats free + simple
  for 10 customers.
- **Mark's job (~20 min):** create a Resend account, verify lostbitcoin.org
  as a sending domain (add the DNS records Resend shows), copy the API key
  to Muse.
- **Muse's job after:** wire magic-link + report emails into `app.py`
  (send via Resend's HTTP API), test with a real address, keep the
  browser-token fallback for review only.

## 3. Hosting — Railway, Hobby $5/mo (recommended)

What the app needs (checked against `app.py` / `payments.py`): a long-lived
Python process, persistent disk for the SQLite database + generated reports,
HTTPS, and env vars (`LOST_BITCOIN_SECRET`, `STRIPE_SECRET_KEY`,
`STRIPE_WEBHOOK_SECRET`, `PORT`, `LOST_BITCOIN_DB`).

- **Cost:** Hobby **$5/mo**, which includes $5 of usage credit. A small
  always-on Python app like this (~256 MB RAM) runs to about $4.50–$5.25/mo,
  so the bill should land at ~**$5/mo** at launch volume. Volumes cost
  ~$0.15/GB/mo on top (the database is tiny at this scale).
- **Why Railway over Fly.io:** Railway auto-detects Python (no Dockerfile
  needed), git-push deploys, one-click persistent volume, managed HTTPS and
  env vars in the dashboard. Fly.io is cheaper (~$2.19/mo for the smallest
  machine + $0.15/GB volume, pay-as-you-go, free tier retired Oct 2024)
  but needs a Dockerfile/`fly.toml`, and a single volume isn't replicated —
  more setup and more for Mark/Muse to maintain for ~$2.50/mo saved.
  A plain VPS (e.g. DigitalOcean droplet) is also possible but means
  managing the server ourselves — not worth it for the first 10 customers.
- **One deployment change still needed (Muse, ~30 min, after Mark picks):**
  `app.py` currently binds `127.0.0.1` (correct for local review) — it must
  bind `0.0.0.0` on a host, with `PORT` from the environment, the database
  and `generated_reports/` on the persistent volume, and a real
  `LOST_BITCOIN_SECRET`. Plus a backup routine for the SQLite file, since
  the customer record is the business.
- **Mark's job (~15 min):** create a Railway account, connect the repo /
  give Muse access, point lostbitcoin.org DNS at Railway when ready.
- **Muse's job after:** make the bind/volume changes, deploy, smoke-test
  both journeys + demo checkout on the live URL, set up the DB backup.

## Suggested order (lowest risk first)

1. **Stripe account now** — verification is the slowest step; everything
   else can wait for it.
2. **Resend** — unblocks emailed magic links + report delivery.
3. **Railway** — deploy once the first two are in hand.

Total founder time: ~50 minutes across the three, none of it coding.
Total running cost at launch: ~**$5/mo hosting + $0 email + Stripe fees
only when a customer pays**.

## What Mark does NOT need to decide tonight

- Colours: already changed to Cloud Dancer / Transformative Teal per his
  feedback — he just gives a verdict on the review server.
- Legal pages: privacy/terms drafts are in the footer for review, marked
  DRAFT, not legal advice.
- Anything technical about the investigation engine: already built and
  tested (180 journeys, 0 failures).
