# How to review the working version (Mark) — updated 12 Nov evening

## Fastest way
Ask Muse: "start the Lost Bitcoin review server" — or run it yourself:
```
cd dev
python3 app.py
```
Then open http://127.0.0.1:8765 in a browser.

## Try both journeys (use a fake email, e.g. test@example.com)
1. **I think I've lost Bitcoin** → enter name/email → answer the questions → your answers save as you go → the results page shows the server's preliminary assessment and the $9.99 report / $6.99 AI walkthrough offers when a lead is found. Leave, come back, and use "Resume" on the homepage with the same email — everything is restored.
2. **I have a Bitcoin address** → enter name/email → paste an address (the Genesis address 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa is a good test — you'll get the unspendable warning) → results show live blockchain data and the $4.99 Wallet Report price. Try a mistyped address: it's rejected before saving. Try pasting a 12-word seed phrase as an answer anywhere: it's refused.

## Also try (added in the finish-line session)
3. **Buy something (demo money):** on a results page, use the report / walkthrough buttons. Checkout is a clearly-labelled demo — no real money — until your Stripe keys exist. After "paying", the report downloads and the AI Guided Next Steps chat opens. Ask it "next step", "what's confirmed?", and "can you guarantee recovery?" — and try pasting a seed phrase (it refuses and warns you).
4. **Privacy / Terms:** links in the footer. Drafts for your review, not legal advice.

## What is NOT in this version yet
- Real payments: needs your Stripe account (15 minutes of your time when you're ready; everything else is built, including webhook verification).
- Emails: resume currently returns a token to the browser (fine for private review); emailed magic links come with the email-provider step.
- A hosting/deployment decision for lostbitcoin.org.

## Give feedback however suits you
Just tell Muse what to change — wording, prices (your call only), flow, design — and it gets changed before launch, with tests re-run.
