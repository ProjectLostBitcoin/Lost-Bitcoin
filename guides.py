"""
Lost Bitcoin — Guides (public SEO content).

Plain-English guides for the exact situations the investigation
service handles, written from the phrases real people search and
post. Each guide is public, linked, and in the sitemap — no hidden
pages. Every guide ends with the same honest funnel: free
assessment first; a paid report only when a credible lead exists;
recovery is never guaranteed.
"""

import html
import json

BASE = "https://lostbitcoin.org"

_CSS = """body{margin:0;font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;background:linear-gradient(180deg,#0a1526 0%,#060b16 55%);background-color:#060b16;color:#eaecef;min-height:100vh}
main{max-width:760px;margin:40px auto;padding:0 22px}.card{background:#0d1830;border:1px solid #1c2c4e;border-radius:16px;padding:42px;box-shadow:0 18px 50px rgba(0,0,0,.45)}
h1{font-size:32px;color:#ffffff;line-height:1.25}p,li{line-height:1.7;color:#9aa7bd}a{color:#f0b90b}h2{color:#ffffff;margin-top:34px}
.dek{font-size:18px;color:#c7d2e4}.warn{background:rgba(240,185,11,.10);border:1px solid #f0b90b;border-radius:10px;padding:16px 18px;margin:22px 0}.warn p{margin:6px 0;color:#e8dfc0}
.cta{background:#12233f;border:1px solid #f0b90b;border-radius:12px;padding:20px 22px;margin:30px 0}.cta p{color:#c7d2e4;margin:6px 0}
.guide-link{display:block;background:#0d1830;border:1px solid #1c2c4e;border-radius:14px;padding:22px 24px;margin:16px 0;text-decoration:none}.guide-link b{color:#ffffff;font-size:19px}.guide-link span{display:block;color:#9aa7bd;margin-top:6px;line-height:1.6}
.crumb{font-size:14px}"""


def _page(title, description, path, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:type" content="article">
<style>{_CSS}</style>{extra_head}</head>
<body><main><div class="card">
<p class="crumb"><a href="/">Lost Bitcoin</a> · <a href="/guides">Guides</a></p>
{body}
</div></main></body></html>"""


def _faq_ld(faq):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq
        ],
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data) + "</script>")


def _faq_html(faq):
    parts = ["<h2>Questions people ask</h2>"]
    for q, a in faq:
        parts.append(f"<p><b>{html.escape(q)}</b><br>{html.escape(a)}</p>")
    return "\n".join(parts)


_CTA = """<div class="cta"><p><b>Start with a free assessment.</b></p>
<p>Lost Bitcoin investigates what actually happened to your Bitcoin —
records, old devices, and public blockchain evidence — and classifies
what is confirmed, what is a possible lead, and what is honestly
unknown. A full Investigation Report is $9.99 and is only offered
when a credible lead exists. <b>We never ask for seed phrases,
private keys, or wallet passwords.</b> Recovery is never guaranteed.</p>
<p><a href="/">Start the free assessment →</a></p></div>"""


GUIDES = [
    {
        "slug": "wallet-dat-forgot-password",
        "title": "Found a wallet.dat File but Forgot the Password? Read This First",
        "description": "You found your old Bitcoin wallet file (wallet.dat) but can't remember the password. Don't experiment on the only copy. Here's what to do — and what never to do.",
        "dek": "You found it — on an old laptop, a backup drive, or buried in a folder from 2013: a file called wallet.dat (or an Electrum wallet file). The file surviving is half the battle. The password is gone. Here's how to handle it without making it worse.",
        "body": """
<h2>What NOT to do</h2>
<ul>
<li><b>Don't experiment on the only copy.</b> Every random "recovery tool" or forum script you run against the original file risks corrupting the one thing you can't replace.</li>
<li><b>Don't keep guessing passwords into the original wallet.</b> Write your guesses down instead.</li>
<li><b>Don't send the file — or your password guesses — to anyone who messages you.</b> The moment you post about a found wallet anywhere, "recovery experts" appear in your DMs. Every one of them is a thief.</li>
<li><b>Don't update or reinstall wallet software over the old installation</b> before the file is safely copied. Work on copies, never the original.</li>
</ul>
<h2>What to do first</h2>
<ul>
<li><b>Copy the file, twice.</b> One copy on a USB stick, one in a second safe place. From now on, anything anyone does happens to a copy.</li>
<li><b>Note exactly where it was found</b> — which computer, which folder, what else was in it. Context is evidence.</li>
<li><b>Write down every password fragment you remember</b> — patterns you used back then, old email passwords, anything close. Partial memories are real leads; they belong on paper, not typed into the wallet.</li>
<li><b>Check the file before assuming riches.</b> A found wallet.dat is sometimes empty — many people spent or moved their coins in 2013 and forgot. A balance check against the public blockchain comes before any conclusions.</li>
</ul>
<h2>Where an investigation fits</h2>
<p>An investigation doesn't crack passwords and doesn't promise recovery. It does the unglamorous work that decides whether the file is worth anything at all: identifying the wallet type and era, checking the addresses it likely controlled against the blockchain, inventorying your password clues and records, and giving you an honest classification — confirmed, strong possibility, possible lead, or unknown.</p>
""",
        "faq": [
            ("Is my Bitcoin \"in\" the wallet.dat file?",
             "Not exactly — coins live on the blockchain; the file holds the keys that control them. That's why preserving the file matters so much."),
            ("Can the password be reset?",
             "No. Self-custody wallets have no company and no reset button. Anyone who says otherwise is selling something."),
            ("The file shows a zero balance. Is it hopeless?",
             "Zero usually means the Bitcoin moved at some point. A Wallet Report ($4.99) can document where it went and when."),
        ],
    },
    {
        "slug": "spouse-parent-passed-away-bitcoin",
        "title": "Your Spouse or Parent Passed Away and Had Bitcoin: First Steps for Families and Executors",
        "description": "If your spouse or parent died and owned Bitcoin, don't delete emails or wipe computers. A calm, step-by-step guide for executors and families — and the scams to avoid.",
        "dek": "First: we're sorry for your loss. This guide can wait until you're ready — nothing here is urgent this week, and the worst mistakes happen when grieving families rush. When you are ready, here's the calm version.",
        "body": """
<h2>The three rules that protect everything else</h2>
<ul>
<li><b>Don't delete their email, and don't wipe their computer.</b> Purchase confirmations, exchange accounts, wallet backups and password-reset paths all run through the deceased's email and devices. Tidying up too early is the #1 way families accidentally destroy the trail.</li>
<li><b>Only the executor should act.</b> A will grants authority — it never grants access — and the lawful route to exchange accounts is the exchange's own deceased-account process (death certificate + proof of authority), not logging in as the deceased.</li>
<li><b>Expect scam messages, and ignore all of them.</b> Bereaved families who post anywhere about inherited crypto get targeted by fake "recovery services" within minutes — the FBI has warned about exactly this. No legitimate service DMs you first, charges an upfront "release fee," or asks for a seed phrase.</li>
</ul>
<div class="warn"><p><b>We never ask for seed phrases, private keys, or wallet passwords</b> — from anyone, ever. If a "service" needs those, it isn't a service.</p></div>
<h2>Where Bitcoin hides in an estate</h2>
<ul>
<li><b>Tax returns and the accountant's file</b> — crypto purchases and disposals are often declared; this is frequently how families first learn it existed at all.</li>
<li><b>Email</b> — purchase confirmations, withdrawal notices, hardware wallet order emails, exchange statements.</li>
<li><b>Bank and card statements</b> — transfers to exchanges name the company and the dates.</li>
<li><b>Devices</b> — an old laptop or phone with a wallet app; a small USB-like hardware wallet (Ledger/Trezor) in a desk or safe. <b>Do not guess a hardware wallet's PIN</b> — a few wrong tries can wipe it.</li>
<li><b>Paper</b> — a folder of printouts, a notebook with 12–24 words written in it. If you find words: don't photograph them, don't send them to anyone, don't type them into any website. Store the paper securely and treat it like cash.</li>
</ul>
<h2>What an executor actually needs</h2>
<p>An estate needs a documented inventory: what accounts, wallets and addresses are known; what's confirmed on the public blockchain; what's a lead; and what's honestly unknown. That documentation is exactly what an investigation produces — evidence the estate file, the accountant, and the beneficiaries can rely on, without anyone promising the Bitcoin can be recovered. A single address found in the papers can be checked with a Wallet Report ($4.99). This guide is general information, not legal advice — for the estate's legal questions, your estate lawyer is the right call.</p>
""",
        "faq": [
            ("The will mentions Bitcoin but there are no passwords. Is it gone?",
             "Not automatically. The trail is usually in email, statements, tax records and devices — that's the investigation."),
            ("Can we just use their password to log in?",
             "Use the exchange's deceased-account/estate process instead. It's the lawful route and it protects the executor."),
            ("We found a hardware wallet but no PIN and no words. Now what?",
             "Preserve it untouched. An investigation can document what exists and what the realistic options are — including, sometimes, that access may not be possible. Honest answers beat false hope."),
        ],
    },
    {
        "slug": "bitcoin-recovery-service-scams",
        "title": "Bitcoin Recovery Service Scams: 9 Red Flags Before You Pay Anyone",
        "description": "Searching 'bitcoin recovery service scam' before you pay? Good instinct. The 9 red flags every fake recovery service shows — and a checklist you can use on any service, including us.",
        "dek": "If you're reading this, there's a decent chance you're mid-conversation with someone who says they can get your Bitcoin back. Pause. Pausing is free, and it's the one move the scammers can't counter — everything on this page can be checked in ten minutes, before any money moves.",
        "body": """
<h2>Why this scam works so well</h2>
<p>Losing Bitcoin hurts, and the fake-recovery industry knows it. The FBI has warned about crypto recovery scams that charge upfront fees for recoveries that never happen — and the cruellest version targets people <i>who were already scammed once</i>, promising to recover the stolen funds for one more "fee." Real help exists. It just never looks like this:</p>
<h2>The 9 red flags</h2>
<ul>
<li><b>They contacted you first.</b> A DM, a comment reply, an email out of nowhere. Legitimate services wait to be found; hunters go looking for the already-hurt.</li>
<li><b>They guarantee recovery.</b> Nobody can. Access depends on what survived — a file, an account, a record. A guarantee is a lie told to close a sale.</li>
<li><b>They ask for your seed phrase, private keys, or wallet password.</b> This is the whole scam in one step. With those, they don't recover your Bitcoin — they take it. No exceptions, no "we need it to verify."</li>
<li><b>There's an upfront "release," "activation," or "tax" fee</b> before funds you've never seen can be "unlocked." Classic advance-fee fraud. Real recovered money never needs a toll booth.</li>
<li><b>They want remote access to your computer</b> (AnyDesk, TeamViewer, "let me just do it for you"). That's not support; that's hands in your pockets.</li>
<li><b>They show you a "recovered balance."</b> A screenshot, a dashboard login they gave you, an address with money in it. Balances are <i>public</i> — anyone can show you an address. Showing isn't recovering.</li>
<li><b>Pressure and secrecy.</b> "Act today," "don't tell your bank," "your family won't understand." Urgency is the tool; isolation is the setup.</li>
<li><b>Payment only in crypto, gift cards, or wire to a person</b> — no real checkout, no receipt, no business you can look up. Money sent that way is gone by design.</li>
<li><b>They impersonate.</b> Fake exchange support, fake wallet companies, lookalike websites, "official" emails. Type addresses yourself; never arrive from a link someone sent you.</li>
</ul>
<h2>The verify-us checklist</h2>
<p>Don't trust a service's claims — run its tests. Here's ours, and you should apply it to anyone, <b>including us</b>:</p>
<ul>
<li><b>Type the address yourself</b> (lostbitcoin.org) instead of clicking links.</li>
<li><b>Prices in public, before signup:</b> free assessment; Investigation Report $9.99, only offered when a credible lead exists; Wallet Report $4.99.</li>
<li><b>Payment through a real card checkout</b> (Stripe) with receipts — never crypto-first, never person-to-person.</li>
<li><b>A written report</b> that separates what's <i>confirmed</i> from what's a <i>possible lead</i> from what's honestly <i>unknown</i>.</li>
<li><b>We refuse your seed phrase even if you offer it.</b> Our system actively rejects them. That's what a real service's "no" sounds like.</li>
</ul>
<h2>If you've already paid — or shared</h2>
<ul>
<li><b>Stop contact, and don't pay the second fee.</b> The "we found it, just one release payment" message is the second scam arriving.</li>
<li><b>If you shared a seed phrase:</b> treat that wallet as public. From a clean device, move anything remaining to a brand-new wallet.</li>
<li><b>Save everything</b> — chats, addresses, receipts — and report it: in Canada, the Canadian Anti-Fraud Centre; in the US, the FBI's IC3 and the FTC. Reporting rarely returns money, but it's how these operations get shut down.</li>
</ul>
""",
        "faq": [
            ("Is any Bitcoin recovery legitimate?",
             "Investigation is; magic isn't. A legitimate service documents what happened, checks evidence against the public blockchain, and guides your next steps. Whether access is possible depends on what survived — and honest services say so, in writing, before you pay."),
            ("A service says my Bitcoin is \"located\" and I owe a fee to release it. Real?",
             "No. Locating a public balance is free and instant — it proves nothing about access. The fee is the product they're selling."),
            ("Can a real service ever need my password?",
             "Your exchange account recovery goes through the exchange itself. Your wallet password is yours alone. Anyone asking for either is red flag #3 — walk away."),
        ],
    },
    {
        "slug": "did-i-ever-have-bitcoin",
        "title": "Did I Ever Have Bitcoin? How to Find Out for Sure",
        "description": "Wondering if you ever actually bought Bitcoin years ago? There's no registry to look you up in — but buying almost always left a trail. Here's how to check, step by step.",
        "dek": "Maybe you bought a little Bitcoin in 2015 and life moved on. Maybe a family member mentioned it, or you found something odd in old paperwork. The honest starting point: there is no list of Bitcoin owners anywhere, and nobody can look you up by name. But almost nobody bought Bitcoin without leaving evidence — and evidence can be checked.",
        "body": """
<h2>The short answer</h2>
<p>Bitcoin has no registry, no head office, and no account with your name on it. Coins are controlled by whoever holds the keys to an address — and addresses are public strings of characters, not names. So the question "did I ever have Bitcoin?" is never answered by a lookup. It's answered by a trail: the records of buying it, and the public blockchain record of where it went. Both can still exist years later — blockchain records are permanent, and email and bank records often outlast our memories.</p>
<h2>The five places the trail hides</h2>
<ul>
<li><b>Your old email.</b> Search every mailbox you've ever had for the names of exchanges (Coinbase, Kraken, QuadrigaCX, Coinsquare, Newton, Shakepay, Mt. Gox) and for words like "purchase confirmation," "withdrawal," and "deposit." A single confirmation email can date and place the whole story.</li>
<li><b>Bank and credit card statements.</b> Transfers to an exchange name the company and the exact dates. Even a small $50 or $100 transfer from years ago is a confirmed starting point.</li>
<li><b>Tax records.</b> If you (or your accountant) ever declared a purchase or a sale, it's written down. For executors, this is often the very first sign Bitcoin existed in an estate at all.</li>
<li><b>Old devices.</b> A retired laptop or phone may hold a wallet app, a browser still signed in somewhere, or backup files. Don't wipe, update, or "clean up" old devices before they're checked — tidying up is how trails get destroyed.</li>
<li><b>Paper and hardware.</b> A notebook, a printed page, a small USB-like device (a Ledger or Trezor). If you find 12–24 handwritten words, that's a seed phrase: never photograph it, never type it into a website, never send it to anyone. Store it like cash.</li>
</ul>
<h2>What the evidence can actually prove</h2>
<ul>
<li><b>An address tells its whole public story.</b> If you find a Bitcoin address anywhere in the trail, its complete history is public and checkable: when it was first and last used, how much it received and sent in total, and what it holds now. That's what a Wallet Report ($4.99) documents in plain English. One warning that matters: a balance proves the address holds Bitcoin — it never, by itself, proves the Bitcoin is yours or that you can still access it.</li>
<li><b>An exchange account is often recoverable</b> through the exchange's own sign-in and account-recovery process, using the original email. Exchanges that shut down are harder — some, like QuadrigaCX, went through court-supervised processes — but records of what you held can still matter.</li>
<li><b>Sometimes the honest answer is "unknown."</b> If every record is gone, a good investigation says so plainly instead of inventing hope. Knowing for sure — one way or the other — is worth something by itself, especially for taxes and estates.</li>
</ul>
<h2>Two traps to avoid while you check</h2>
<ul>
<li><b>Anyone claiming a name-based lookup is lying.</b> There is no database of Bitcoin owners to search — a service that says "we found your Bitcoin, pay a fee to release it" is running the oldest scam in this space. Locating a public balance is free and proves nothing.</li>
<li><b>Never "check" by entering secrets.</b> No website, app, or person needs your seed phrase or wallet password to tell you whether you had Bitcoin. The moment one asks, you're not being helped — you're being robbed.</li>
</ul>
<h2>A simple order of operations</h2>
<ul>
<li><b>First,</b> search old email and statements — an hour of searching beats a week of guessing.</li>
<li><b>Second,</b> preserve any old device or paper exactly as you found it.</li>
<li><b>Third,</b> if you find an address, check it before concluding anything — addresses that look empty sometimes aren't the whole story, and busy ones settle the question immediately.</li>
<li><b>Fourth,</b> if the trail points somewhere real, that's a credible lead — and that's the only point where a paid Investigation Report ($9.99) makes sense. If there's no lead, you shouldn't be charged, and we won't offer one.</li>
</ul>
""",
        "faq": [
            ("Can you look me up by name or email and tell me if I had Bitcoin?",
             "No — and neither can anyone else. No such registry exists. What an investigation does is follow your evidence: emails, statements, tax records, devices, and any addresses, and check them against the public blockchain."),
            ("I bought on an exchange that shut down years ago. Is there any point checking?",
             "Yes. Your own records (emails, statements) can still prove what you bought and when, and some defunct exchanges have claims or distribution processes where documentation matters. What can be recovered varies — an honest assessment separates what's confirmed from what's unknown."),
            ("What if the answer turns out to be that I never had any, or it's gone?",
             "Then that's the answer, and it comes from the free assessment — the paid report is only offered when a credible lead exists. For many people, especially executors settling an estate, a documented 'no' is genuinely valuable."),
        ],
    },
]


def render_index():
    cards = "\n".join(
        f'<a class="guide-link" href="/guides/{g["slug"]}"><b>{html.escape(g["title"])}</b>'
        f'<span>{html.escape(g["dek"])}</span></a>'
        for g in GUIDES
    )
    body = f"""<h1>Guides: finding lost Bitcoin, step by step</h1>
<p class="dek">Calm, plain-English guides for the situations we investigate —
written from the questions real people ask. No hype, no recovery
promises, and one rule that never changes: <b>never share your seed
phrase with anyone.</b></p>
{cards}
{_CTA}"""
    return _page("Guides | Lost Bitcoin",
                 "Plain-English guides for finding lost Bitcoin: old wallets, forgotten passwords, defunct exchanges, and Bitcoin in estates.",
                 "/guides", body)


def render_post(slug):
    for g in GUIDES:
        if g["slug"] == slug:
            body = (f"<h1>{html.escape(g['title'])}</h1>\n"
                    f'<p class="dek">{html.escape(g["dek"])}</p>\n'
                    + g["body"] + _faq_html(g["faq"]) + _CTA
                    + '<p><a href="/guides">← All guides</a></p>')
            return _page(g["title"], g["description"],
                         f"/guides/{slug}", body,
                         extra_head=_faq_ld(g["faq"]))
    return None
