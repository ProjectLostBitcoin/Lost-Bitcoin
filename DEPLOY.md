# DEPLOY.md — Lost Bitcoin go-live checklist

Written 2026-11-12. The app is deploy-ready: `app.py` binds `HOST`/`PORT`
from the environment (defaults stay local: 127.0.0.1:8765), the database
and generated reports can live on a mounted volume, and both host
configs below build from the same `Dockerfile`.

## Environment variables (set on the host, never in code or chat)

| Variable | Required | Notes |
|---|---|---|
| `LOST_BITCOIN_SECRET` | Yes | Long random string; signs customer resume tokens. Changing it logs out every returning customer. |
| `STRIPE_SECRET_KEY` | For real payments | Start with the **test** key (`sk_test_…`); swap to `sk_live_…` only at the live step. Without it the site runs the labelled demo checkout. |
| `STRIPE_WEBHOOK_SECRET` | With Stripe | From the webhook endpoint created in the Stripe dashboard (`whsec_…`). |
| `STRIPE_PRODUCT_INVESTIGATION_REPORT` | Recommended | Catalogue product ID for the $9.99 report. Sandbox: `prod_VcLHCFWh1IubZv`. Live needs its own (IDs differ per environment). |
| `STRIPE_PRODUCT_AI_WALKTHROUGH` | Recommended | Catalogue product ID for the $6.99 walkthrough. Sandbox: `prod_VcLHV3tsGVLWEa`. |
| `STRIPE_PRODUCT_WALLET_REPORT` | Recommended | Catalogue product ID for the Wallet Report. Sandbox: `prod_VcLH73zkbFZcag`. |
| `HOST` / `PORT` | Set by config | `0.0.0.0` / `8080` in both host configs. |
| `LOST_BITCOIN_DB` | Set by config | `/data/lost_bitcoin.db` (on the volume). |
| `LOST_BITCOIN_REPORTS_DIR` | Set by config | `/data/generated_reports` (on the volume). |

## Option A — Railway (recommended; see FOUNDER_DECISIONS.md addendum)

1. Mark creates the Railway account (Hobby plan).
2. New project → deploy from this repo/folder (Dockerfile build).
3. Add a **volume mounted at `/data`** (1 GB is plenty).
4. Set the env vars above. Set a **$10 hard usage limit** in settings.
5. Add the custom domain `lostbitcoin.org` (+ `www`) in Railway; it
   shows the exact DNS records to add at **Namecheap** (the domain's
   current DNS host — nameservers are `dns1/dns2.registrar-servers.com`,
   and the domain currently shows Namecheap's parking page).
6. Health check is `/api/health` (already in `railway.json`).

## Option B — Fly.io (fallback, ~$2.50–$2.70/mo)

1. Mark creates the Fly.io account.
2. `fly volumes create lost_bitcoin_data --size 1 --region yyz`
3. `fly deploy` (uses `fly.toml` + `Dockerfile`).
4. `fly secrets set LOST_BITCOIN_SECRET=… STRIPE_SECRET_KEY=… STRIPE_WEBHOOK_SECRET=…`
5. `fly certs add lostbitcoin.org` and `www.lostbitcoin.org`; add the
   DNS records Fly shows at Namecheap.

## After the site answers on its real domain (test mode first)

1. Stripe dashboard → create webhook endpoint
   `https://lostbitcoin.org/api/stripe/webhook`, event
   `checkout.session.completed`; copy its `whsec_…` into
   `STRIPE_WEBHOOK_SECRET` and redeploy.
2. Run a full test-mode purchase with card `4242 4242 4242 4242`:
   confirm the report unlocks and exactly one purchase is recorded;
   replaying the webhook must record nothing new.
3. Enable Stripe receipt emails + statement descriptor `LOST BITCOIN`.
4. Only then swap to live keys and do the $4.99 live
   self-purchase-and-refund smoke test (see STRIPE_PLAN.md).

## Backups

`scripts/backup_db.sh` makes a safe online backup of the SQLite DB
(keeps 14). Schedule it daily on the volume **and download copies
off-host weekly** — the customer investigation records are the business.

## Still required before real customers (not deploy blockers)

- Resend (email) wiring: magic-link sign-in replaces the review-only
  browser resume token, and reports get delivered by email.
- Founder review of `privacy.html` / `terms.html` drafts.
