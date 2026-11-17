"""
Lost Bitcoin — randomized end-to-end website tester.

Simulates real customers through the exact HTTP API the website uses:
homepage fetch, start, questionnaire answers, address submission,
investigation runs, resume, report generation, plus abuse cases
(cross-customer access, invalid addresses, duplicate addresses,
seed phrases, XSS payloads in text answers).

Usage: python3 tests/e2e_random_customers.py [journeys] [seed]
Starts its own server on an ephemeral port with a throwaway database
and the deterministic offline test provider. Writes a JSON summary
to tests/e2e_results.json and exits non-zero if any check fails.
"""
import json, random, string, subprocess, sys, tempfile, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from bitcoin_address_validation import validate_bitcoin_address  # noqa: E402

JOURNEYS = int(sys.argv[1]) if len(sys.argv) > 1 else 60
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20261112
rng = random.Random(SEED)

ADDRESS_POOL_RAW = [
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",   # genesis
    "1BoatSLRHtKNngkdXEeobR76b53LETtpyT",
    "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",   # P2SH
    "bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4",
    "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",
    "bc1p0xlxvlhemja6c4dqv22uapctqupfhlxm9h8z3k2e72q4k9hcz7vqzk5jj0",
    "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",
    "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
]
POOL = []
for a in ADDRESS_POOL_RAW:
    try:
        validate_bitcoin_address(a); POOL.append(a)
    except ValueError:
        print(f"pool address failed local validation, skipped: {a}")

QUESTIONS = {
    "source": ["I bought it through an exchange", "I stored it in a wallet on a computer",
               "I used a mobile or online wallet", "Someone sent Bitcoin to me",
               "I mined Bitcoin", "I'm not sure"],
    "year": ["2009–2011", "2012–2013", "2014–2015", "2016–2017", "2018–2020",
             "2021 or later", "I don't remember"],
    "purchase": ["I purchased it with money", "Someone transferred it to me",
                 "I mined it", "A combination of these", "I don't remember"],
    "email": ["Yes", "No", "I'm not sure"],
    "device": ["Yes", "No", "I have an external drive or backup", "I'm not sure"],
    "records": ["Purchase confirmation emails", "Bank or credit card statements",
                "Transaction IDs or wallet addresses", "Several of these",
                "None that I know of", "I'm not sure"],
    "withdrawal": ["Yes", "No", "Possibly", "I don't remember"],
    "account": ["Yes", "No", "I haven't tried", "The service may no longer exist"],
}
SEED_PHRASE = ("abandon ability able about above absent absorb abstract "
               "absurd abuse access accident")

failures, checks = [], 0
def check(cond, label, journey):
    global checks
    checks += 1
    if not cond:
        failures.append({"journey": journey, "check": label})

def call(base, method, path, body=None, token=None):
    req = urllib.request.Request(base + path, method=method)
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as r:
            raw = r.read().decode()
            try: return r.status, json.loads(raw)
            except json.JSONDecodeError: return r.status, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try: return e.code, json.loads(raw)
        except json.JSONDecodeError: return e.code, raw

def rand_email(i):
    name = "".join(rng.choices(string.ascii_lowercase, k=rng.randint(5, 10)))
    domain = rng.choice(["example.com", "testmail.ca", "mailinator.com", "demo.org"])
    return f"{name}{i}@{domain}"

def journey_lost(base, i):
    email = rand_email(i)
    st, s = call(base, "POST", "/api/start",
                 {"name": rng.choice(["Alex", "Sam O'Brien", "Jösé M", "Priya", "Tom <b>Test</b>"]),
                  "email": email, "starting_point": "lost_bitcoin", "consent": True})
    check(st == 200, "start lost_bitcoin", i)
    if st != 200: return
    inv, tok = s["investigation_id"], s["token"]
    answered = 0
    for key, options in QUESTIONS.items():
        if rng.random() < 0.85:
            st, _ = call(base, "POST", "/api/answer",
                         {"investigation_id": inv, "question_key": key,
                          "answer_value": rng.choice(options)}, tok)
            check(st == 200, f"answer {key}", i); answered += 1
    # text answers, incl. an XSS payload that must be stored inertly
    for key, val in [("exchange", rng.choice(["Coinbase", "<script>alert(1)</script>", "Mt. Gox"])),
                     ("amount", rng.choice(["2 BTC", "$500 worth", "I don't know"]))]:
        st, _ = call(base, "POST", "/api/answer",
                     {"investigation_id": inv, "question_key": key, "answer_value": val}, tok)
        check(st == 200, f"text answer {key}", i); answered += 1
    # seed phrase must be refused
    st, data = call(base, "POST", "/api/answer",
                    {"investigation_id": inv, "question_key": "notes", "answer_value": SEED_PHRASE}, tok)
    check(st == 400 and "seed phrase" in str(data), "seed phrase refused", i)
    # run twice: second run must not duplicate findings (idempotency)
    st, out1 = call(base, "POST", "/api/run", {"investigation_id": inv}, tok)
    check(st == 200 and "assessment" in out1, "run 1 assessment", i)
    st, full1 = call(base, "GET", f"/api/investigation?investigation_id={inv}", token=tok)
    st, out2 = call(base, "POST", "/api/run", {"investigation_id": inv}, tok)
    st, full2 = call(base, "GET", f"/api/investigation?investigation_id={inv}", token=tok)
    check(len(full2["evidence"]) == len(full1["evidence"]),
          f"run idempotent: evidence {len(full1['evidence'])} -> {len(full2['evidence'])}", i)
    check(len(full2["recommendations"]) == len(full1["recommendations"]),
          f"run idempotent: recommendations {len(full1['recommendations'])} -> {len(full2['recommendations'])}", i)
    check(len(full2["discoveries"]) == len(full1["discoveries"]),
          f"run idempotent: discoveries {len(full1['discoveries'])} -> {len(full2['discoveries'])}", i)
    # resume restores everything
    st, r = call(base, "POST", "/api/resume", {"email": email})
    check(st == 200 and r["investigation_id"] == inv, "resume same investigation", i)
    st, full = call(base, "GET", f"/api/investigation?investigation_id={inv}", token=r["token"])
    check(st == 200 and len(full["answers"]) == answered, "resume restores answers", i)
    # report is gated until checkout; demo-pay unlocks it
    st, _ = call(base, "POST", "/api/report", {"investigation_id": inv}, tok)
    check(st == 402, "report gated before payment", i)
    st, co = call(base, "POST", "/api/checkout",
                  {"investigation_id": inv, "product": "investigation_report"}, tok)
    check(st == 200 and co.get("amount_cents") == 999, "checkout investigation_report $9.99", i)
    if st == 200:
        st, _ = call(base, "POST", "/api/demo-pay",
                     {"investigation_id": inv, "demo_token": co["demo_token"]}, tok)
        check(st == 200, "demo-pay completes", i)
    st, rep = call(base, "POST", "/api/report", {"investigation_id": inv}, tok)
    check(st == 200 and "Investigation Report" in rep.get("markdown", ""), "report generated after payment", i)
    # walkthrough: gated, then grounded replies after purchase
    st, _ = call(base, "POST", "/api/walkthrough",
                 {"investigation_id": inv, "message": "next step"}, tok)
    check(st == 402, "walkthrough gated before payment", i)
    st, co = call(base, "POST", "/api/checkout",
                  {"investigation_id": inv, "product": "ai_walkthrough"}, tok)
    if st == 200:
        call(base, "POST", "/api/demo-pay",
             {"investigation_id": inv, "demo_token": co["demo_token"]}, tok)
        st, out = call(base, "POST", "/api/walkthrough",
                       {"investigation_id": inv, "message": "what's confirmed?"}, tok)
        check(st == 200 and "reply" in out, "walkthrough replies after payment", i)
        st, out = call(base, "POST", "/api/walkthrough",
                       {"investigation_id": inv, "message": SEED_PHRASE}, tok)
        check(st == 200 and "don't send that" in out.get("reply", "").lower(),
              "walkthrough refuses seed phrase", i)
    return s

def journey_address(base, i):
    email = rand_email(i)
    st, s = call(base, "POST", "/api/start",
                 {"name": "Case " + str(i), "email": email, "starting_point": "bitcoin_address", "consent": True})
    check(st == 200, "start bitcoin_address", i)
    if st != 200: return
    inv, tok = s["investigation_id"], s["token"]
    chosen = rng.sample(POOL, rng.randint(1, 3))
    for a in chosen:
        st, _ = call(base, "POST", "/api/address",
                     {"investigation_id": inv, "address": a, "label": "e2e"}, tok)
        check(st == 200, f"add address {a[:10]}", i)
    # duplicate address must be a friendly 4xx, never a 500
    st, _ = call(base, "POST", "/api/address",
                 {"investigation_id": inv, "address": chosen[0]}, tok)
    check(400 <= st < 500, f"duplicate address friendly error (got {st})", i)
    # invalid address rejected
    st, _ = call(base, "POST", "/api/address",
                 {"investigation_id": inv, "address": "definitely invalid!!"}, tok)
    check(st == 400, "invalid address 400", i)
    # run + pricing
    st, out = call(base, "POST", "/api/run", {"investigation_id": inv}, tok)
    check(st == 200 and len(out.get("address_results", [])) == len(chosen), "run checks all addresses", i)
    st, full1 = call(base, "GET", f"/api/investigation?investigation_id={inv}", token=tok)
    call(base, "POST", "/api/run", {"investigation_id": inv}, tok)
    st, full2 = call(base, "GET", f"/api/investigation?investigation_id={inv}", token=tok)
    check(len(full2["evidence"]) == len(full1["evidence"]), "address run idempotent", i)
    expected = 499 + 199 * (len(chosen) - 1)
    import investigation_controller as ctl
    check(ctl.address_report_price_cents(len(chosen)) == expected, "wallet pricing math", i)
    return s

def main():
    tmp = Path(tempfile.mkdtemp())
    port = rng.randint(20000, 40000)
    env = {"PATH": "/usr/bin:/bin", "LOST_BITCOIN_DB": str(tmp / "e2e.db"),
           "LOST_BITCOIN_SECRET": "e2e-secret", "PORT": str(port),
           "LOST_BITCOIN_TEST_PROVIDER": "1", "LOST_BITCOIN_RATE_LIMIT": "100000"}
    proc = subprocess.Popen([sys.executable, str(ROOT / "app.py")],
                            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(50):
            try:
                st, _ = call(base, "GET", "/api/health")
                if st == 200: break
            except Exception: time.sleep(0.2)
        st, home = call(base, "GET", "/")
        check(st == 200 and "I THINK I'VE LOST BITCOIN" in home and "I HAVE A BITCOIN ADDRESS" in home,
              "homepage has both starting points", 0)
        customers = []
        for i in range(1, JOURNEYS + 1):
            s = journey_address(base, i) if rng.random() < 0.4 else journey_lost(base, i)
            if s: customers.append(s)
        # cross-customer access attempts
        if len(customers) >= 2:
            a, b = customers[0], customers[1]
            st, _ = call(base, "GET", f"/api/investigation?investigation_id={a['investigation_id']}", token=b["token"])
            check(st == 403, "cross-customer blocked", 999)
            st, _ = call(base, "GET", f"/api/investigation?investigation_id={a['investigation_id']}", token="forged.token.here")
            check(st == 401, "forged token blocked", 999)
    finally:
        proc.terminate()
    result = {"journeys": JOURNEYS, "seed": SEED, "checks": checks,
              "failures": failures, "passed": checks - len(failures)}
    (ROOT / "tests" / "e2e_results.json").write_text(json.dumps(result, indent=2))
    print(f"journeys={JOURNEYS} checks={checks} passed={result['passed']} failed={len(failures)}")
    for f in failures[:25]:
        print("FAIL", f)
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
