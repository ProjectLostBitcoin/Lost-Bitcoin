"""
Lost Bitcoin — AI Guided Next Steps (the $6.99 walkthrough).

Option B rules apply to chat too: every factual statement in a reply
comes from the customer's own Master Investigation Record
(recommendations, evidence, discoveries) or from the approved pricing.
The assistant never invents blockchain data, never claims ownership,
never guarantees recovery, and refuses to receive seed phrases or
private keys. This deterministic core can later be rephrased by an
LLM, but the facts it may state are fixed here.
"""

import re

import master_investigation_record as record
import investigation_controller as controller

_DISCLAIMER = ("I can only go on what's in your investigation record so far — "
               "I won't guess beyond it.")


def _money(cents):
    return f"${cents / 100:.2f}"


def reply(investigation_id, message):
    """Return a grounded reply string for one customer message."""
    if record.contains_sensitive_secret(message or ""):
        return ("Please don't send that here. A seed phrase or private key gives "
                "complete control of a wallet — never share it with anyone, "
                "including us. We will never ask for one. If you've shared it "
                "anywhere else, move your Bitcoin to a new wallet as soon as you can.")

    full = record.get_complete_investigation(investigation_id)
    if full is None:
        raise ValueError("Investigation not found.")

    text = (message or "").lower()
    recs = [r for r in full["recommendations"] if r["status"] == "pending"]
    confirmed = [e for e in full["evidence"] if e["confidence"] == "confirmed"]

    if any(w in text for w in ("seed", "private key", "password")):
        return ("We never need your seed phrase, private key or wallet password, "
                "and you should never enter them here. Your next steps only ever "
                "involve locating devices, records and accounts — not revealing secrets.")

    if any(w in text for w in ("guarantee", "definitely", "will i get", "can you recover")):
        return ("Honestly: no one can guarantee recovery, and we don't promise it. "
                "What we sell is investigation — evidence and the strongest next "
                "steps based on it. " + _DISCLAIMER)

    if any(w in text for w in ("price", "cost", "how much", "pay")):
        return (f"Our prices: Investigation Report {_money(controller.INVESTIGATION_REPORT_PRICE_CENTS)}, "
                f"AI Guided Next Steps {_money(controller.AI_WALKTHROUGH_PRICE_CENTS)}, "
                f"Wallet Report {_money(controller.ADDRESS_REPORT_FIRST_CENTS)} for the first "
                f"address and {_money(controller.ADDRESS_REPORT_EXTRA_CENTS)} for each additional "
                "address. The initial assessment is free.")

    if any(w in text for w in ("own", "prove", "proof", "mine")):
        return ("A blockchain balance or transaction shows activity for an address — "
                "it doesn't prove who owns it or that the Bitcoin can be accessed. "
                "That's exactly why your report separates confirmed findings from leads.")

    if any(w in text for w in ("balance", "address", "found", "discover", "evidence", "result")):
        if confirmed:
            lines = "\n".join(f"• {e['description']}" for e in confirmed[:5])
            return f"Here is what is CONFIRMED in your record:\n{lines}"
        return ("Nothing is confirmed in your record yet — your findings so far are "
                "leads based on your answers, not verified evidence. " + _DISCLAIMER)

    if any(w in text for w in ("all", "list", "steps", "everything")) and recs:
        lines = "\n".join(f"{i}. {r['title']} — {r['details']}" for i, r in enumerate(recs, 1))
        return f"Your proposed next steps:\n{lines}\nSay 'next' and we'll take them one at a time."

    if any(w in text for w in ("next", "first", "start", "begin", "step")) or not text.strip():
        if recs:
            r = recs[0]
            return (f"Let's start with step 1 of {len(recs)}: **{r['title']}**.\n"
                    f"{r['details']}\nTake your time — when you're done, tell me what you found "
                    "in your own words and we'll record it in your investigation.")
        return ("Your record doesn't have any recommended steps yet. That usually means "
                "we need a little more information — check that you've answered the "
                "questionnaire or added any Bitcoin addresses you remember.")

    if any(w in text for w in ("found", "done", "yes", "managed", "got it", "finished")):
        record.save_discovery(investigation_id,
                              f"Customer update via guided walkthrough: {message[:500]}",
                              source_type="customer_statement")
        return ("Thank you — I've saved that to your investigation record as a new "
                "discovery (it's recorded as your statement, not as confirmed evidence). "
                "Say 'next' whenever you're ready for the following step.")

    return ("I can walk you through your proposed next steps one at a time, list them all, "
            "explain what's confirmed in your record, or explain our pricing. "
            "Try 'next step', 'list my steps', or 'what's confirmed?'. " + _DISCLAIMER)
