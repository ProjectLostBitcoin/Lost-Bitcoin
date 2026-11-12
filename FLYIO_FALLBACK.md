# Fly.io fallback — DRAFT deployment plan (only if Mark picks Fly.io)

Prepared 2026-11-12 (morning, America/Vancouver) as quiet groundwork for
tonight's hosting pick. **Do not deploy from this file unless Mark chooses
Fly.io over Railway.** Railway is still the recommendation in
`FOUNDER_DECISIONS.md`; this exists so a Fly.io pick costs no extra prep
time — the plan is ready, the files below are copy-paste-ready.

Status: **draft, untested** — no Fly.io account exists yet, nothing has been
deployed, and the two code changes in §3 have NOT been made. `app.py` is
untouched by this file.

## 1. Cost (from FOUNDER_DECISIONS.md, verified 2026-11-12)

- Smallest always-on machine, shared-cpu-1x / 256 MB: **$2.19/mo**
- 1 GB persistent volume: **$0.15/mo** → machine + volume ≈ **$2.34/mo**
- Planning range in the decision sheet: **~$2.50–$2.70/mo** (allows for a
  little egress). No monthly minimum, but **no spending cap by default** —
  unlike the $10 hard limit planned for Railway, this needs watching.
- Saving vs Railway (~$5–$10/mo): roughly **$2.50–$7/mo**.

## 2. Files to create in `dev/` (contents ready below)

### `Dockerfile`

```dockerfile
# Lost Bitcoin — Fly.io fallback ONLY. Do not build/deploy unless Mark picks Fly.io.
FROM python:3.12-slim
WORKDIR /app
COPY *.py ./
COPY *.html ./
RUN mkdir -p generated_reports
ENV PORT=8765
ENV LOST_BITCOIN_DB=/data/lost_bitcoin.db
VOLUME /data
EXPOSE 8765
CMD ["python3", "app.py"]
```

Notes: the backend is standard-library only (`app.py` docstring), so there
is no `requirements.txt` to install. Python 3.12 matches the local
environment (3.12.3).

### `fly.toml`

```toml
app = "lost-bitcoin" # PLACEHOLDER — Fly.io app names are globally unique; expect to rename (e.g. lost-bitcoin-mvp)
primary_region = "yyz" # Toronto — keeps data in Canada. Confirm with Mark; customers are anywhere, Mark is in BC.

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8765"
  LOST_BITCOIN_DB = "/data/lost_bitcoin.db"

[http_service]
  internal_port = 8765
  force_https = true
  auto_stop_machines = false # must stay always-on: SQLite DB + in-memory state live on this machine
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  size = "shared-cpu-1x"
  memory = "256mb"

[[mounts]]
  source = "lostbitcoin_data"
  destination = "/data"
```

### `.dockerignore`

```
backups_archive/
tests/
generated_reports/
*.db
__pycache__/
```

## 3. Code changes still needed before ANY deploy (same for Railway)

1. **`app.py` line ~350 — bind address.** It currently binds
   `127.0.0.1` (correct for local review). A host must bind `0.0.0.0`:
   `ThreadingHTTPServer(("0.0.0.0", port), Handler)`. `PORT` is already
   read from the environment (default 8765), so no other change there.
2. **`app.py` line ~43 — reports directory.** `REPORTS_DIR` is hardcoded
   to `BASE_DIR / "generated_reports"` (inside the app folder, ephemeral
   on Fly.io). It needs an env override (e.g. honour
   `LOST_BITCOIN_REPORTS_DIR`, defaulting as today) so generated reports
   live on the volume at `/data/generated_reports`. The database is
   already env-configurable (`LOST_BITCOIN_DB`, `master_investigation_record.py`
   line 20), so the DB on the volume works with no code change.
3. **Backups:** the SQLite file is the business (customer records). Copy
   `/data/lost_bitcoin.db` off Fly.io on a schedule — same requirement as
   the Railway plan (backups kept off the host).

## 4. Deploy steps (once Mark picks Fly.io)

```bash
cd ~/workspace/lost-bitcoin/dev
# 1. Make the two code changes in §3, re-run tests: python3 -m unittest discover -s tests
# 2. Create the three files in §2 (Dockerfile, fly.toml, .dockerignore)
fly auth login
fly launch --no-deploy   # or: fly apps create <final-name>; then fly volumes create lostbitcoin_data --size 1 --region yyz
fly secrets set LOST_BITCOIN_SECRET=<generated> STRIPE_SECRET_KEY=<key> STRIPE_WEBHOOK_SECRET=<secret>
fly deploy
fly open                 # smoke-test both journeys + demo checkout on the live URL
```

Secrets note: the same warning as Railway applies — these keys live as
environment variables on the host. Railway's Oct 20–21, 2026 incident
(decrypted env vars, report published Nov 10) is the reason this fallback
exists; Fly.io has no equivalent incident on file in the decision sheet.

## 5. What this does NOT cover

- DNS for lostbitcoin.org (point at Fly.io when ready — same step as Railway).
- Stripe/Resend setup — unchanged, per `FOUNDER_DECISIONS.md`.
- No Fly.io account, app, or volume has been created; no money spent.
