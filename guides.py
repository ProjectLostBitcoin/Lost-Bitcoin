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
    {
        "slug": "old-laptop-lost-bitcoin",
        "title": "Lost Bitcoin on an Old Laptop? Don't Wipe It — Do This Instead",
        "description": "An old laptop might hold a wallet file, a wallet app, or the signed-in browser and email that unlock everything. Before you wipe, sell, or recycle it — read this.",
        "dek": "It's in a closet, a drawer, the corner of the office: a laptop from 2013 that takes ten minutes to boot. If you bought Bitcoin back then, that machine may be the single most valuable object in your house right now — not because of what's on the screen, but because of the files, sessions, and email it quietly kept.",
        "body": """
<h2>Why an old laptop matters so much</h2>
<p>Early Bitcoin lived on computers, not phones. An old laptop can hold a wallet program (Bitcoin Core, Electrum, Multibit) with its wallet file, a browser still signed in to an exchange, or the email account that every password reset in the world points to. Any one of those can be the thread that unravels the whole story. People rarely lose Bitcoin all at once — they lose it in the moment they wipe, reset, sell, or recycle the machine that held the only copy of the keys.</p>
<h2>What NOT to do</h2>
<ul>
<li><b>Don't wipe it, reset it, or reinstall the operating system.</b> A factory reset is designed to destroy exactly what you're looking for.</li>
<li><b>Don't run cleaners, updaters, or "helpful" recovery tools on it</b> before it's been looked at. Work should happen on copies, never on the only original.</li>
<li><b>Don't sell it, gift it, or take it to e-waste recycling yet.</b> There is no undo.</li>
<li><b>Don't let anyone remote into it.</b> No legitimate helper needs to drive your computer — and the ones who insist on it are after what's on it.</li>
<li><b>Don't guess wallet passwords on the original files.</b> Write guesses down on paper instead.</li>
</ul>
<h2>What to do instead</h2>
<ul>
<li><b>Charge it and turn it on — that's all.</b> Note what you see: wallet programs, browser bookmarks, email accounts. Take photos of the screen for your records (never of any 12–24 word seed phrase, if one appears — that stays off every camera and cloud).</li>
<li><b>Look for the landmarks:</b> a file called wallet.dat; folders named Bitcoin, Electrum, or Multibit; a browser with saved logins; an email app with old purchase confirmations.</li>
<li><b>Write down any Bitcoin address you find</b> — in an email, a text file, a wallet program's "receiving addresses." An address can be checked against the public blockchain immediately, safely, and without touching the laptop again.</li>
<li><b>Keep the laptop somewhere safe and unplugged from daily use.</b> Treat it the way you'd treat a safe deposit box key.</li>
</ul>
<h2>What a check can tell you</h2>
<p>If you find an address, a Wallet Report ($4.99) documents its full public history in plain English: whether it was ever used, what it received and sent, and what it holds now. If the laptop holds a wallet file but the password is gone, an investigation can identify the wallet type and era, inventory your records and password clues, and classify honestly what's confirmed and what's unknown. What nobody can honestly do is promise the laptop's Bitcoin can be recovered — that depends entirely on what survived on it.</p>
""",
        "faq": [
            ("The laptop won't turn on. Is it over?",
             "Usually not. A dead laptop's hard drive can often be read by a computer technician, and the wallet files copied off it. Never hand over passwords or seed phrases to anyone in the process — files can be copied without them."),
            ("I already wiped or reset the laptop. Hopeless?",
             "The wallet files are likely gone, but the trail may not be: exchange accounts, purchase emails, and bank records often survive elsewhere. That's what the free assessment checks."),
            ("Is the Bitcoin actually 'on' the laptop?",
             "The coins live on the public blockchain. The laptop holds the keys and records that control and prove them — which is why preserving it matters so much."),
        ],
    },
    {
        "slug": "bitcoin-address-balance-access",
        "title": "Your Bitcoin Address Shows a Balance — Can You Actually Access It?",
        "description": "Anyone can look up any Bitcoin address and see its balance — that part is free, public, and proves nothing about ownership. Here's the difference between seeing Bitcoin and being able to spend it.",
        "dek": "You found an address — in an old email, a screenshot, a notebook — and a website shows it holding Bitcoin. Real Bitcoin, right there on the screen. So is it yours? Can you get it? This is the exact moment where honest information matters most, because it's also the moment scammers wait for.",
        "body": """
<h2>Seeing is free. Seeing proves almost nothing.</h2>
<p>Bitcoin's blockchain is a public record. Every address, every transaction, every balance is visible to anyone, forever — no account, no permission, no fee. So when a website shows "your" address holding 0.5 BTC, it has shown you something anyone on Earth can see. It has <b>not</b> shown that the Bitcoin is yours, and it has not moved you one inch closer to spending it. Balance proves existence. It never proves ownership, and it never proves access.</p>
<h2>Access is a completely separate question</h2>
<p>Spending Bitcoin requires the private key for that address, and keys live in specific places. Which of these is true decides everything:</p>
<ul>
<li><b>The address belongs to a wallet you still have</b> — a wallet app, a wallet file, a hardware wallet, or a written seed phrase backup. Then access may be straightforward, and the wallet itself is the tool. (Never type a seed phrase into any website to "check" — that's how wallets get emptied.)</li>
<li><b>The address was yours, but the wallet is lost.</b> Then the question becomes what survived: a file, a device, a backup, password clues. That's an investigation, and the honest answer can range from "very promising" to "unknown."</li>
<li><b>The address belongs to an exchange.</b> Exchanges hold Bitcoin in their own addresses. If the address is an exchange's, your route is the exchange account itself — sign-in and account recovery with the exchange — not the address.</li>
<li><b>The address was never yours.</b> People save addresses for many reasons — a payment they made, a donation, an example from a forum. An address in your notes with a balance is a lead, not a conclusion.</li>
</ul>
<h2>What a Wallet Report actually does</h2>
<p>A Wallet Report ($4.99) documents the address's complete public story in plain English: when it was first and last used, how much it received and sent in total, what it holds now, and whether the activity pattern fits your story — bought in 2014 and untouched since, say. It's evidence you can act on and share with family or an executor. What it can't do is give you the keys: no report can, and anyone who says otherwise is selling the next step of a scam.</p>
<div class="warn"><p><b>The classic trap:</b> a "recovery service" shows you an address with a balance — free information — then charges a "release fee" to unlock it. There is nothing to release. Locating was never the hard part.</p></div>
""",
        "faq": [
            ("Someone showed me an address and said it's my recovered Bitcoin. Is it?",
             "They showed you a public web page. Until Bitcoin moves using keys you control, nothing has been recovered — and any 'release fee' they request is the actual product being sold."),
            ("The balance hasn't moved in years. Does that mean it's mine and waiting?",
             "It means the keys haven't been used. Millions of addresses sit untouched because their keys are lost, saved, or simply patient. Stillness tells you nothing about whose keys they are."),
            ("What do I need to actually spend Bitcoin from an address?",
             "The wallet or backup that holds its private keys — a wallet file and its password, a hardware wallet and its PIN, or a seed phrase kept offline. Those never get shared with anyone, including us: we investigate records and public evidence only."),
        ],
    },
    {
        "slug": "quadrigacx-lost-bitcoin",
        "title": "QuadrigaCX Took Your Bitcoin? What Happened — and What's Still Possible",
        "description": "QuadrigaCX collapsed in 2019 and Canadians lost millions. If you had Bitcoin there, here's what happened, what the bankruptcy process did, and what your own records can still do for you.",
        "dek": "If you bought Bitcoin in Canada in the 2010s, there's a good chance you used QuadrigaCX — for years it was the country's biggest exchange. Then, in early 2019, it vanished into one of the strangest collapses in finance. Here's the honest version of what happened to the money, and what may still be worth doing.",
        "body": """
<h2>What happened, briefly</h2>
<p>QuadrigaCX stopped withdrawals, its founder was reported dead, and the exchange entered court-supervised bankruptcy in 2019 with roughly 76,000 users owed money. The court-appointed trustee (EY) investigated, recovered what could be recovered, ran a claims process for users, and made partial distributions to creditors whose claims were accepted. For most users who filed claims, that process — not the full balance — was the recovery. This is general information, not legal advice; the trustee's published materials are the authority on the claims process itself.</p>
<h2>What your own records can still prove</h2>
<ul>
<li><b>QuadrigaCX emails</b> — account confirmations, deposit and withdrawal notices. Withdrawal emails matter most: they may contain the address your Bitcoin was sent to.</li>
<li><b>Bank records</b> — Interac e-transfers and wires to QuadrigaCX/Fortress establish amounts and dates.</li>
<li><b>Tax filings</b> — purchases or losses you declared create a dated paper trail.</li>
</ul>
<h2>What may still be possible</h2>
<ul>
<li><b>Bitcoin you withdrew before the collapse.</b> If you ever moved coins off QuadrigaCX to your own wallet, that Bitcoin was never the exchange's — it sits at the address you withdrew to, on the public blockchain, to this day. Finding that address (in a withdrawal email, an old wallet, a notebook) turns a QuadrigaCX story into a checkable one: a Wallet Report ($4.99) documents exactly what that address holds and what happened to it.</li>
<li><b>Other accounts from the same era.</b> Many QuadrigaCX users also bought or held elsewhere — another exchange, a wallet app. An investigation inventories the whole trail, not just the famous collapse.</li>
<li><b>A documented loss.</b> For tax and estate purposes, a written record of what was held, what was claimed, and what was received can matter. Your accountant is the right call on how to use it.</li>
</ul>
<div class="warn"><p><b>Beware the second wave:</b> "Quadriga recovery agents" charging fees to reopen claims or release funds are a known scam pattern. The only real process was the trustee's. Nobody legitimate charges you to recover QuadrigaCX money today.</p></div>
""",
        "faq": [
            ("Did QuadrigaCX users get anything back?",
             "Creditors with accepted claims received partial distributions through the bankruptcy — a portion of what was owed, not the whole amount. The trustee's process is the complete and only official channel."),
            ("I never filed a claim. Can someone reopen it for a fee?",
             "Claims deadlines passed years ago, and no third party can reopen them. Anyone charging a fee to do so is running a scam — keep your records, and don't pay."),
            ("I withdrew Bitcoin from QuadrigaCX to my own wallet before it collapsed. Where is it?",
             "At the address you withdrew to — withdrawals are permanent public records. Find the address in your withdrawal email or old wallet and it can be checked today. That's one of the most promising QuadrigaCX-era leads there is."),
        ],
    },
    {
        "slug": "when-we-refuse-your-money",
        "title": "When We Will Refuse Your Money",
        "description": "Lost Bitcoin will not sell you a report when there is nothing to report. Here is the full list of the situations where we refuse payment — and what you get instead, for free.",
        "dek": "Most businesses in this space take your money first and explain later. We do the opposite: the free assessment comes first, and a paid report is only offered when the assessment finds something real to report.",
        "body": """
<p>Here is the list, in plain English, so you can hold us to it.</p>
<h2>We will not sell you an Investigation Report when there is no credible lead</h2>
<p>A credible lead is something specific enough to investigate: an address with activity, a purchase record, a wallet file, an exchange account, a device that has not been searched. If the free assessment finds none of those, no $9.99 offer appears at all — and checkout will refuse one if it is attempted. You are not charged, and you are not left guessing: the assessment tells you what was checked and what would change the answer.</p>
<h2>We will not sell you the guided walkthrough when there is nothing to walk through</h2>
<p>The $6.99 AI-guided walkthrough is a guided tour of the next steps for a real lead. With no lead, there are no next steps to guide, so it is gated the same way as the report. The one exception is the Wallet Report path: there, an address you provide counts as the lead, so Wallet Report customers are unaffected.</p>
<h2>We will not charge you for an address that was never used — as an investigation</h2>
<p>If the only address you have has never had a single transaction, there is no investigation to sell you on it: the blockchain record is empty, and we will say so in the free assessment. A Wallet Report ($4.99 for the first address, $1.99 for each additional address) can still document that empty record in writing if you want a dated record of it — for example, for an estate file — but we will not dress it up as a discovery, and we will never offer you the $9.99 Investigation Report on an address with nothing to investigate.</p>
<h2>We will not take your money for a report that says "nothing found"</h2>
<p>That is the situation the rule above exists to prevent. A paid report should contain findings — confirmed, strong possibility, or possible lead — and the next steps that follow from them. If the honest finding is "unknown," that finding comes from the free assessment, not from a $9.99 purchase.</p>
<h2>We will refuse your seed phrase, private key, and wallet password — even if you offer them</h2>
<p>Our system actively rejects seed phrases typed into the address box, and we never ask for or store them anywhere else. No legitimate service needs the thing that can spend your money in order to investigate what happened to it. Anyone who asks for it — including anyone using our name — is trying to steal your Bitcoin.</p>
<h2>We will not guarantee recovery, and we will not take a fee that pretends we can</h2>
<p>Recovery is never guaranteed, and no report we sell says otherwise. If the coins moved years ago to an address nobody can identify, or the only copy of the keys is provably destroyed, we will tell you that instead of selling you hope. The recovery industry's standard deal is 10–20% of the wallet, payable only if they succeed — and only if you hand them a wallet file. We do not crack passwords and we do not take a percentage of anything. Our flat prices are on the homepage, and they are the whole price.</p>
<h2>We will not contact you first, and we will not take payment anywhere but the site</h2>
<p>We will never DM you on Telegram, WhatsApp, Reddit, or anywhere else. We will never ask you to pay in Bitcoin, or to send money to a wallet address, or to pay a "release fee" or "tax" to unlock anything. The only way to start is the free assessment on lostbitcoin.org, and the only payment route is Stripe checkout on the site. If someone contacts you claiming to be us and asking for any of the above, it is not us.</p>
<h2>What you get instead, for free</h2>
<ul>
<li><b>The assessment itself.</b> What was checked, what was found, and what was not — classified honestly as confirmed, strong possibility, possible lead, or unknown.</li>
<li><b>What would change the answer.</b> For example: "if you find any email from an exchange dated 2015–2018, or a file named wallet.dat, this case reopens." A dead end with a door left open is worth more than a dead end dressed up as a report.</li>
<li><b>Nothing to buy, nothing to chase.</b> If there is no lead, there is no offer to decline. You can walk away knowing you checked, for free.</li>
</ul>
""",
        "faq": [
            ("Is this just marketing? How do I know you actually refuse payment?",
             "The rule is enforced by the site, not by a promise: the checkout step checks for a credible lead before it will take payment for the Investigation Report or the walkthrough. And the free assessment is genuinely free — no card is asked for before it."),
            ("I was told my Bitcoin is gone forever. Will you still charge me to check?",
             "No. The assessment is free, and if it confirms there is nothing to chase, that is the answer — free, in writing, with what would change it."),
            ("My address shows a balance. Does that mean you will sell me a report?",
             "A balance is a lead, so a Wallet Report ($4.99) can document exactly what that address shows. A balance alone does not prove the Bitcoin is yours or that you can access it — a report will say that plainly, and the Investigation Report is only offered when the assessment finds a credible lead to investigate further."),
            ("What if I disagree with a \"no lead\" finding?",
             "Bring the evidence: an old email, a statement, a device, a second address. New evidence reopens the case, and the assessment can be run again."),
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
    for i, g in enumerate(GUIDES):
        if g["slug"] == slug:
            related = [GUIDES[(i + k) % len(GUIDES)] for k in (1, 2, 3)]
            rel = ('<h2>Keep reading</h2><ul>' + "".join(
                f'<li><a href="/guides/{r["slug"]}">{html.escape(r["title"])}</a></li>'
                for r in related) + '</ul>')
            body = (f"<h1>{html.escape(g['title'])}</h1>\n"
                    f'<p class="dek">{html.escape(g["dek"])}</p>\n'
                    + g["body"] + _faq_html(g["faq"]) + rel + _CTA
                    + '<p><a href="/guides">← All guides</a></p>')
            return _page(g["title"], g["description"],
                         f"/guides/{slug}", body,
                         extra_head=_faq_ld(g["faq"]))
    return None
