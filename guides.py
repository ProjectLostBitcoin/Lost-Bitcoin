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
<div class="notice"><p><b>Got a message you're unsure about right now?</b> Paste it into our <a href="/scam-check">free scam checker</a> — it scans for the patterns on this page automatically, in your browser, and nothing you paste is sent or stored.</p></div>
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
    {
        "slug": "restored-bitcoin-wallet-shows-zero",
        "title": "Restored Your Bitcoin Wallet and It Shows Zero? Read This Before You Panic",
        "description": "You restored your wallet from its seed phrase and the balance says zero. That usually means the wallet is looking in the wrong place — not that the Bitcoin is gone. The four causes, in order.",
        "dek": "You found your seed phrase, restored the wallet, it opened — and the balance is zero. This is one of the most common sights in Bitcoin, and one of the most misleading: a zero on screen usually means the wallet is looking at the wrong set of addresses, not that your coins are gone.",
        "body": """
<h2>First, check the address — not the app</h2>
<p>The blockchain is the ground truth, and the app is only a window. If you know any address you actually used back then (from an exchange withdrawal email, a statement, or a notebook), look it up on a public block explorer, or have it checked. If that address shows your balance, your Bitcoin exists — and everything below is about making a wallet look at the right place. If you have no address at all, that check is what an investigation starts with.</p>
<h2>Cause 1: the passphrase (the "25th word")</h2>
<p>Many wallets offer an optional passphrase on top of the 12 or 24 words. It is not a password for the same wallet — it creates a completely different wallet. Restore without it (or with a slightly different one — it is case-sensitive, and a typo counts) and you get a perfectly valid, perfectly empty wallet. If your original setup used a passphrase, the words alone will never show the balance. Think hard about whether you set one, and try the exact spellings you would have used — on the device or app itself, never on a website.</p>
<h2>Cause 2: the address type</h2>
<p>Bitcoin addresses come in generations: Legacy (starting with 1), SegWit (3), and Native SegWit (bc1). A wallet restored in an app that defaults to a newer type may show only new-style addresses — an empty set — while your coins sit on the older type from the same seed. Look in the app's restore or advanced settings for the address type or "script type," and check each type before concluding anything.</p>
<h2>Cause 3: the derivation path and accounts</h2>
<p>Under the hood, wallets find addresses by following a "derivation path," and different apps and eras used different ones (you may see numbers like m/44', m/49', m/84' — each points at a different address family). Some apps let you choose the path during restore. Also check for additional accounts: many wallets support Account 2, 3, and so on under the same seed, and an empty Account 1 says nothing about the others.</p>
<h2>Cause 4: the restore itself</h2>
<p>A wallet that is still syncing can show zero until it catches up — give it time on a good connection. And confirm you restored into the same kind of wallet you had: a seed restored into a different coin's wallet (Bitcoin Cash, for example) shows that coin's empty addresses, not your Bitcoin.</p>
<h2>What not to do at this moment</h2>
<ul>
<li><b>Never type your seed phrase into a website</b> — not a "validator," not a "sync tool," not a chat window. That is the exact moment scammers design for, and it is how restored wallets get emptied.</li>
<li><b>Don't pay anyone to "fix the sync" or "restore the balance."</b> There is no such service; the fix is a setting, not a payment.</li>
<li><b>Don't keep creating new wallets or moving files around.</b> Write down what you tried, in order. Methodical beats frantic, and your notes are evidence if you ask for help.</li>
</ul>
<h2>How an investigation helps here</h2>
<p>Before wrestling settings blindly, it helps to know the target: which of your addresses actually hold Bitcoin, and how much. If you have any address from the period, a Wallet Report ($4.99) documents exactly what the blockchain shows for it — so instead of guessing whether the coins exist, you know what the restored wallet needs to find. And the free assessment will say plainly if there is nothing on-chain to aim at.</p>
""",
        "faq": [
            ("My seed phrase is definitely correct. How can the balance be zero?",
             "Because the words are only part of the address calculation. A passphrase (25th word), a different address type, or a different derivation path all produce a different, empty set of addresses from the same correct words. Correct words plus the wrong settings equals a convincing zero."),
            ("Can I check whether my Bitcoin exists without fixing the wallet first?",
             "Yes — the blockchain record is public. Any address you used can be checked directly: if it shows a balance, the Bitcoin exists and the problem is the wallet's view, not the coins. That is exactly what a Wallet Report ($4.99) documents in plain English."),
            ("Someone offered to restore my balance if I share my screen or my seed phrase. Is that legitimate?",
             "No. Nobody legitimate needs your seed phrase or a screen share to help you, and no fee can 'restore' a balance. The real fixes are settings in your own wallet app. Anyone asking for the phrase is trying to take the Bitcoin, not recover it."),
        ],
    },
    {
        "slug": "shakepay-find-your-bitcoin-address",
        "title": "Bought Bitcoin on Shakepay? How to Find an Address That's Actually Yours",
        "description": "The address in Shakepay's 'Add Funds' screen belongs to Shakepay, not you — checking it shows their activity, not yours. Where your own address actually is: in a past send.",
        "dek": "You bought and sold Bitcoin on Shakepay over the years, and now you want to see your history. So you open the app, find a Bitcoin address, and check it — and it shows millions moving, or nothing at all. Neither result is about you. Here is why, and where your address really is.",
        "body": """
<h2>The trap: the deposit address is not yours</h2>
<p>The address Shakepay shows you for adding funds is a <b>deposit address</b>. It belongs to Shakepay. They issue addresses to receive customer deposits, they rotate them, and the Bitcoin that arrives is pooled with everyone else's. An old one still works — which makes it look like "your" address — but checking it on the blockchain shows Shakepay's treasury activity: enormous sums that have nothing to do with your account, or a long-drained address that shows nothing. Either way, it cannot tell you what you held. This is not a Shakepay trick; every exchange works this way, including Newton, Coinsquare, Kraken, and Coinbase.</p>
<h2>Where your address actually is: in a past send</h2>
<p>An address becomes personally yours the moment Bitcoin moves to a wallet you control. So the address worth checking is the <b>destination of a past send out of the exchange</b> — a withdrawal to your own wallet. That address received your coins, and its blockchain record is your history: what arrived, what later moved, what is still there.</p>
<h2>How to find it in Shakepay</h2>
<ol>
<li>Open the Shakepay <b>mobile app</b> — the desktop site shows less transaction detail.</li>
<li>Tap your Bitcoin balance to open the BTC transaction history.</li>
<li>Look for a past <b>send</b> to an external wallet (not a buy or a sell — those happened inside Shakepay and never touched the blockchain in your name).</li>
<li>Open that transaction and follow its transaction ID, or its "view on the blockchain" link. On the blockchain record, the <b>destination address</b> is the one your coins actually moved through.</li>
</ol>
<p>That address is safe to share and safe to check — it is public information by design. It is also the only thing you ever need: never a seed phrase, never a password.</p>
<h2>If you never sent Bitcoin out</h2>
<p>Plenty of people only ever bought and sold inside the exchange. If that is you, there is no personal address to find — your history lives in Shakepay's own records, and the honest move is to download your transaction history or statements from the app. No blockchain report can show activity that never left the exchange, and anyone who says otherwise is guessing. Those records still matter: purchase confirmations and statements are exactly the kind of evidence an investigation works from.</p>
<h2>What to do with the address once you have it</h2>
<p>Look it up on any public block explorer, or bring it to our free assessment. A Wallet Report ($4.99) then documents the address in plain English: everything it received and sent, what it holds now, and what that does and does not prove. People are often surprised in both directions — an address they forgot turns out to have a real history, or one they worried about turns out never to have been used at all. Either way, you end up knowing, instead of wondering.</p>
""",
        "faq": [
            ("Why does my Shakepay deposit address show millions of dollars?",
             "Because it is Shakepay's address, not yours. Deposit addresses receive funds from thousands of customers into the exchange's pooled wallets. The activity is real — it just isn't your activity."),
            ("I only bought and sold inside Shakepay. Is there an address with my history?",
             "No — buys and sells inside an exchange are bookkeeping entries on the exchange's own ledger, not blockchain transactions in your name. Your record is Shakepay's transaction history and statements, which you can download from the app."),
            ("Is it safe to paste my address into a checker or a report?",
             "Yes. A Bitcoin address is public — anyone can look it up, and looking changes nothing and risks nothing. What is never safe to share is a seed phrase, a private key, or a wallet password. We will never ask for those."),
        ],
    },
    {
        "slug": "bought-bitcoin-years-ago-where-to-start",
        "title": "Bought Bitcoin Years Ago and Don't Know Where to Start? Start Here",
        "description": "Bought Bitcoin years ago and don't know where to start? Nothing is urgent — and you don't need to know how Bitcoin works. The calm, plain-English first steps: old email, statements, and devices.",
        "dek": "You bought some Bitcoin years ago — on a computer that's long retired, or through a company you can barely remember — and now you're not sure where it went, or even whether you still have it. That lost feeling is completely normal, and nothing about this is urgent today. Here is the calm way to start.",
        "body": """
<h2>First: nothing is urgent today</h2>
<p>If you bought Bitcoin years ago and now feel lost, you are in good company — and you are not behind. Bitcoin has no expiry date, no deadline, and no account that closes because you took your time. Nothing on this page needs to happen today, and nothing needs to happen in a hurry. In fact, hurrying is the one thing to avoid: the people who want you to act fast are almost never trying to help you. Anyone who says "act now or it's gone forever" is trying to frighten you into a mistake. Take your time. A slow, careful search beats a fast, panicked one every time.</p>
<h2>The three evidence piles</h2>
<p>Almost every old Bitcoin purchase left a trail, and that trail lives in one of three places. You don't need to know how Bitcoin works to search them — you're just looking for paperwork.</p>
<ul>
<li><b>Your old email.</b> Search every mailbox you've ever had — including ones you rarely open — for the names of exchanges (Coinbase, Kraken, QuadrigaCX, Coinsquare, Newton, Shakepay) and for words like "purchase confirmation" and "withdrawal." One confirmation email can carry the date, the amount, and sometimes even the address.</li>
<li><b>Bank and credit card statements.</b> A transfer to an exchange names the company and the exact date, even years later. Even a small amount — $50 or $100 — is a confirmed starting point.</li>
<li><b>Old devices.</b> A retired laptop, an old phone, a drawer with a USB stick. A wallet app, a browser still signed in, or a file called wallet.dat may be sitting there. Look — but don't change anything yet.</li>
</ul>
<h2>Preserve everything before you tidy anything</h2>
<p>This is the rule that matters most: <b>don't wipe, reset, or throw away anything before it's been checked.</b> Don't delete old email, don't run a cleanup on an old laptop, and don't recycle a device that might hold a wallet. Tidying up is how trails get destroyed — and there is no undo. Family can absolutely help you search the records: a son, daughter, or grandchild can go through email and statements with you, and that's a fine way to start. But your seed phrase and your passwords are different — those stay private, even from family. Never photograph them, never email them, never type them into any website, and never read them out to anyone who calls or messages you. No legitimate helper will ever need them.</p>
<h2>What the free assessment does</h2>
<p>Think of our free assessment as the structured version of this very search: you tell us what you found — an old email, a statement, a device, an address — and we check it against the public blockchain record and tell you, in plain English, what is confirmed, what is a strong possibility, what is a possible lead, and what is honestly unknown. A full Investigation Report ($9.99) is only offered when a credible lead is found. A Wallet Report ($4.99 for the first address, $1.99 for each additional address) documents what a single address shows. The $6.99 AI-guided walkthrough is a guided tour of your next steps — again, only when there is a real lead to walk through. Nothing here is guaranteed, and if the honest answer is "we can't find anything," that answer comes from the free assessment, not from a purchase.</p>
""",
        "faq": [
            ("I don't remember if I actually bought Bitcoin or only thought about it. Can anyone check?",
             "No one can look you up by name — there is no registry of Bitcoin owners. But a purchase almost always left a trail: an old email, a bank transfer, a tax record. The free assessment follows that trail, and if nothing turns up, it says so plainly. 'We checked, and there's nothing here' is a real answer."),
            ("My family wants to help me look. Is that safe?",
             "Yes — for records. A family member searching old email and statements with you is a good start, and two pairs of eyes find more than one. Just keep your seed phrase and passwords private, even from family. Those are never shared, photographed, or typed into a website — by anyone, for any reason."),
            ("I found an old laptop. Should I turn it on?",
             "Yes — just turn it on and look. Note what you see: wallet programs, email accounts, saved logins. Don't wipe it, update it, or run any cleanup first, and don't let anyone remote into it. If you find a Bitcoin address anywhere, write it down — it can be checked safely against the public blockchain without touching the laptop again."),
        ],
    },
    {
        "slug": "bitcoin-purchase-confirmation-email",
        "title": "That Old Purchase Confirmation Email Is Evidence — Keep It",
        "description": "An old Bitcoin purchase confirmation email can carry the exchange, the date, the amount — sometimes even the address your coins went to. How to search for it, save it, and use it as evidence.",
        "dek": "That email from years ago you never deleted — the one confirming you bought Bitcoin — is worth more than you think. It is not just a memory. It is dated, written evidence of what happened, and it is often the single piece of paper that gets an investigation started.",
        "body": """
<h2>What a purchase confirmation actually contains</h2>
<p>When you bought Bitcoin through an exchange, the exchange emailed you a receipt. That receipt usually names the <b>exchange</b>, the <b>date</b> and the <b>amount</b> you bought — and sometimes more: a transaction ID, an order number, or the address the coins were withdrawn to. Each of those details is a fact an investigation can check against the public blockchain record, instead of relying on memory. Even a small purchase matters: a $50 buy in 2017 is a confirmed starting point, and the date alone can narrow a search from "sometime years ago" to a single week.</p>
<h2>How to search your old mailboxes</h2>
<p>Search every mailbox you have ever had — including ones you rarely open, old work accounts, and the inbox you used before your current one. Try the exchange names first: <b>Coinbase, Kraken, QuadrigaCX, Coinsquare, Mt. Gox</b>. Then try the phrases exchanges used in their subject lines: <b>"purchase confirmation"</b>, <b>"withdrawal"</b>, <b>"deposit"</b>, and <b>"order complete"</b>. Search your bank statements for the same company names too — a transfer to an exchange confirms the date and the amount even when the email is gone. Go slowly, and check the spam and trash folders as well; old receipts often ended up there.</p>
<h2>Save it before you share it</h2>
<p>When you find one, <b>save or print a copy right away</b> — a PDF, a screenshot, a printout in a folder. Then leave the original where it is. Do not forward the original email to strangers, and never send it to anyone who messages you offering to "recover" your Bitcoin. Genuine helpers never need your email forwarded to them, and "recovery" accounts that slide into your DMs are almost always scams. An email is safe to show to a service you have chosen yourself, on a website you typed in yourself — and nothing more.</p>
<h2>What one email can — and can't — do</h2>
<p>One confirmation email anchors an investigation: it fixes the date, the exchange, and the amount, and sometimes it points straight at the address your coins moved to. From there, the public blockchain record can be checked — what arrived, what later moved, what is still there — and each finding is classified honestly: <b>CONFIRMED</b>, <b>STRONG POSSIBILITY</b>, <b>POSSIBLE LEAD</b>, or <b>UNKNOWN</b>. What an email cannot do is give you access. It proves the story; it is not the keys, and it does not open a wallet. That is exactly why it is the starting point, not the ending — and why it is worth keeping. Bring what you found to our free assessment, and we will tell you, in plain English, what it proves and what the next step is. A full Investigation Report ($9.99) is only offered when a credible lead is found; a Wallet Report ($4.99 for the first address, $1.99 for each additional address) documents what a single address shows; and the $6.99 AI-guided walkthrough talks you through the next steps. Nothing here is guaranteed — but an email you already have is a better place to start than most people realise.</p>
""",
        "faq": [
            ("I deleted my old email account. Is the trail gone?",
             "Not necessarily. Your bank or credit card statements still show transfers to exchanges, and those confirm the date and the amount. The exchange itself may also still hold your account records — try logging in, or use its account-recovery process. And check any other mailbox you ever had: the confirmation may be sitting in an inbox you forgot about."),
            ("The email has a transaction ID. Does that mean I can get the Bitcoin back?",
             "No — a transaction ID proves the purchase happened and lets anyone check the public blockchain record to see where the coins went. But it is not a password and it does not unlock a wallet. It is evidence, and good evidence, but access still depends on having the wallet, the login, or the recovery words."),
            ("Someone messaged me saying they found my purchase and can recover it. Is that real?",
             "Almost certainly not. Nobody can find your purchase for you — there is no registry of Bitcoin owners — and no legitimate service contacts you out of the blue. Anyone who messages you first, asks you to forward the email, or asks for a seed phrase, a private key, or a wallet password is trying to take what you have left. Do not reply, and do not send them anything."),
        ],
    },
    {
        "slug": "found-hardware-wallet-pin",
        "title": "Found a Hardware Wallet? Don't Guess the PIN",
        "description": "Found a Ledger or Trezor in a drawer? Don't guess the PIN — a few wrong tries wipes the device. What to do instead, where the real backup is, and the scams to avoid.",
        "dek": "You found a small USB-like device in a drawer — probably a Ledger or a Trezor — and it might hold the keys to a Bitcoin wallet. The most important thing you can do right now is nothing: don't guess the PIN, don't plug it in anywhere, and don't let anyone 'help' you with it until you know what you're holding.",
        "body": """
<h2>What that small device actually is</h2>
<p>A Ledger or Trezor is a hardware wallet: a small device that holds the private keys to a Bitcoin wallet offline. The Bitcoin itself is not inside it — coins live on the blockchain. What the device holds, locked away, are the keys that control the wallet. If the keys are still inside and the backup words still exist, the Bitcoin is still reachable. If either is gone, the device is just a piece of plastic.</p>
<h2>Why guessing the PIN is the fastest way to lose it</h2>
<p>Do not guess the PIN. A hardware wallet is built to defend itself: after a few wrong attempts, the device wipes itself — keys and all — on purpose, so a thief cannot keep guessing. There is no safe number of tries and no way to undo a wipe. The most common way people turn a recoverable wallet into a lost one is an afternoon of guessing birthdays and old PINs. If you do not know the PIN, stop. Do not try another one.</p>
<h2>The paper recovery sheet is the real backup</h2>
<p>When a hardware wallet is first set up, it shows 12 or 24 words — the recovery phrase — to be written down on paper. That sheet is the real backup, and it matters more than the device. Look for it where the device was kept: the same drawer, the same safe, the same folder of important papers. It may be on the small card that came in the box, or any piece of paper with a numbered list of ordinary words. Keep it private and off screens: never photograph it, never type it into any website or app, and never read it out to anyone. The only place those words ever belong is the device manufacturer's own recovery flow, entered on the device itself.</p>
<h2>Preserve what you found, and don't plug it in anywhere</h2>
<p>Until you know what you have, leave it untouched. Do not plug the device into a random computer — unfamiliar software can try to talk to it the moment it is connected. Write down what you found: the device model, anything written on it, any papers or cards that came with it, and where it was kept. That record is evidence, and it is what an investigation starts from. If the device belonged to a family member who has died, the same rules apply — and only the executor should act.</p>
<h2>What an investigation can — and cannot — do</h2>
<p>An investigation can document what you found, identify the device and the wallet it likely controlled, check any addresses you can find against the public blockchain, and guide you through the safe next steps — each finding classified honestly as CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN. What it cannot do is bypass a PIN, and nobody can: the device is designed so that is impossible. Anyone who claims they can — for a fee, by remote access, or with a special tool — is a scammer. Bring what you found to our free assessment, and we will tell you, in plain English, what is known and what the next step is. A full Investigation Report ($9.99) is only offered when a credible lead is found; a Wallet Report ($4.99 for the first address, $1.99 for each additional address) documents what a single address shows; and the $6.99 AI-guided walkthrough talks you through the next steps. Nothing here is guaranteed — but a device left untouched is a far better starting point than a device that has been guessed at.</p>
""",
        "faq": [
            ("I already tried a few PIN guesses. Is it too late?",
             "Not necessarily — but stop now. Each wrong guess brings the device closer to wiping itself, and you cannot see how many tries are left. Write down the guesses you already tried so you don't repeat them, put the device away, and get guidance before you touch it again. The recovery words, if they exist, are what matter now — not the PIN."),
            ("I found the recovery words. Can I type them into a website to get the Bitcoin back?",
             "No — never type your recovery words into any website or app. The only safe place for them is the device manufacturer's own recovery flow, entered on the device itself (or on a brand-new device bought from the manufacturer). Any website, app, or person asking for the words is trying to steal the wallet. If you have the words, you have the key — protect them like cash."),
            ("Someone says they can unlock the device for a fee. Is that real?",
             "No. Nobody can bypass a hardware wallet PIN — the device is built so that after a few wrong attempts it erases itself, and there is no back door. Anyone who offers to unlock it for a fee, by remote access, or with special software is a scammer. The only real routes are the correct PIN or the recovery words, entered on the device itself."),
        ],
    },
    {
        "slug": "why-bitcoin-assessment-is-free",
        "title": "Why Our Bitcoin Assessment Is Free (and What It Actually Does)",
        "description": "Our Bitcoin investigation assessment is free because many people have no credible lead — and charging them to learn that would be wrong. Here's what the free step checks, and when the $9.99 report is offered.",
        "dek": "Most people who think they lost Bitcoin honestly don't know whether anything is recoverable. The free assessment exists to answer that first question — do you have a credible lead at all? — before anyone is asked to pay anything.",
        "body": """
<h2>What the free assessment actually does</h2>
<p>The assessment takes the details you remember — an old exchange, a device, a wallet file, an address, a date — and organizes them into one investigation record. If you have a Bitcoin address, it is checked against the public blockchain: has it ever been used, what moved through it, and does it hold a balance today? Everything found is classified honestly, in plain language: CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN. A balance, on its own, never proves the Bitcoin is yours or that it can be recovered — the assessment says so when that's the case.</p>
<h2>Why it costs nothing</h2>
<p>Because in a great many cases, the honest answer is that there is no credible lead: the address was never used, the exchange is gone with no records, the trail simply ends. Charging someone $9.99 to hear "there's nothing here" would be wrong — and it's exactly what the scam services do in reverse, taking money first and inventing hope later. The free step is the filter that protects you: we only offer the paid Investigation Report ($9.99) when the assessment finds a credible lead worth documenting. If there's no lead, you pay nothing, and you still leave knowing where you stand.</p>
<h2>What the assessment never does</h2>
<p>It never asks for seed phrases, private keys, or wallet passwords — not in the form, not by email, not ever. Anyone who asks for those is trying to steal a wallet, full stop. It also never promises recovery. Lost Bitcoin sells investigation, evidence, and guidance: a written record of what the evidence shows and the clearest next step from where you are. Sometimes that next step leads to access; sometimes it honestly doesn't, and the report says that too.</p>
<h2>How the business makes money, in the open</h2>
<p>Small flat fees for documented work — that's the whole model. The Investigation Report is $9.99 when a credible lead exists. The AI Guided Next Steps walkthrough is $6.99. A Wallet Report — the public record of one address, written up plainly — is $4.99 for the first address and $1.99 for each additional one. No percentages of your Bitcoin, no "release fees," no payment in crypto, no charges you weren't shown up front. If we can't help, we tell you for free; if we can, the price is the price.</p>
""",
        "faq": [
            ("If the assessment is free, what's the catch?",
             "There isn't one. The free step costs us a little automated checking and organization; what it earns us is that the people who do pay are people we can genuinely help. If your assessment finds no credible lead, we'll tell you plainly and you owe nothing — that's published policy on our 'when we will refuse your money' page."),
            ("What counts as a credible lead?",
             "Evidence that something specific is worth investigating: an address that was actually used, records from an exchange you had an account with, a wallet file, a device, or documents tying you to a purchase. Hope alone isn't a lead, and neither is a balance on an address that was never yours — the assessment classifies what it finds as CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN."),
            ("Why not just charge everyone a small fee for the assessment itself?",
             "Because most assessments end with 'no credible lead,' and charging for that answer would punish exactly the people who most need a straight one. Free also keeps us honest: our income depends on finding real leads and documenting them well, not on collecting fees from everyone who walks in worried."),
        ],
    },
    {
        "slug": "remember-exchange-try-logging-in",
        "title": "You Remember the Exchange — Have You Actually Tried Logging In?",
        "description": "Remember the exchange you bought Bitcoin on? The coins may still be sitting in that account. How to try logging in safely, fix a 2FA lockout, and what to do once you're in.",
        "dek": "You remember the exchange. Coinbase, Kraken, Shakepay, QuadrigaCX — the name is right there in your memory. So here's the question almost nobody asks first: have you actually tried logging in? A surprising share of 'lost' Bitcoin is sitting in an account its owner simply never tried to re-enter.",
        "body": """
<h2>The most overlooked step in the whole search</h2>
<p>When people say they "lost" their Bitcoin, they usually picture a missing wallet, a forgotten password, or a computer that's long gone. But often it's simpler: the Bitcoin is sitting in an exchange account the owner never tried to open again. The account still exists, the coins are still there — nobody has been back in years. Before digging through old devices, try the front door. It costs nothing, and it is the fastest answer in this whole space.</p>
<h2>Go to the real site — type the address yourself</h2>
<p>Never reach an exchange through a link in an email, a DM, a text, or an ad. That's where fake exchange sites live, and a fake login page will happily take your password and hand it to a thief. Type the exchange's address into your browser yourself — coinbase.com, kraken.com, shakepay.com — or open the official app from your phone's app store. If you're not sure of the address, search the exchange's name and check the result before clicking.</p>
<h2>Try the original email, then the password reset</h2>
<p>Sign in with the email you used when you bought — the one from that year, not necessarily your current one. If the password is gone, use the exchange's own "forgot password" link on the sign-in page. The reset goes to that original inbox, so if you no longer have access to it, recover the email account first. Write down what you try instead of hammering the same guesses over and over — most exchanges lock an account after repeated failures.</p>
<h2>Locked out by two-factor authentication? That's normal — and fixable</h2>
<p>Two-factor authentication (2FA) is the most common reason people give up: you changed phones, the authenticator app is gone, the backup codes are in a drawer you can't find. Every real exchange has a process for exactly this: identity-verification recovery, usually a photo ID and a selfie, sometimes with a waiting period. It is slow on purpose — that slowness is what stops a thief doing the same thing. Start it through the exchange's official support page, never through a person who messages you offering to "fix" it. The exchange's own process is free — anyone charging a fee to unlock your account is running a scam.</p>
<h2>If the exchange no longer exists</h2>
<p>Sometimes the front door is gone: exchanges shut down — QuadrigaCX is the famous Canadian example — and logging in is no longer an option. That is a different road: your own records — purchase emails, bank statements, tax filings — become the evidence, and the exchange's bankruptcy or claims process, if one exists, is the only official route. Our QuadrigaCX guide explains what happened there and what your records can still do: <a href="/guides/quadrigacx-lost-bitcoin">QuadrigaCX Took Your Bitcoin? What Happened — and What's Still Possible</a>.</p>
<h2>Once you're in: don't move anything yet</h2>
<p>If the login works and there is a balance, congratulations — and stop. Don't move anything in a panic. First, document what you see: write down the balances, transaction history, and dates, and download your statements. That record is evidence — for your taxes, your family, and any investigation that follows. Then decide what to do next, slowly — leaving it where it is while you think is almost always the safe choice. If the account shows nothing, that is also an answer: it tells the free assessment where the trail does not go, and the assessment classifies what you found — CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN — before any paid report is offered.</p>
""",
        "faq": [
            ("I tried logging in and the exchange says my account doesn't exist. What now?",
             "First, check the email — try every address you used around the time you bought, and check you're on the right exchange; similar names and old rebrands trip people up. If the exchange genuinely has no record of you, that is still useful information: it tells the free assessment to look elsewhere — old devices, wallet files, and bank statements — instead of chasing an account that was never there."),
            ("The exchange wants a photo ID and a selfie to restore my account. Is that safe?",
             "Yes — when you started the process yourself, on the exchange's real site or official app, and the request comes from the exchange's own support flow. Real exchanges verify identity this way because it is the only way to be sure the person asking is the account holder. Never send ID to a person who messages you, and never upload it through a link someone sent you — that is how identity theft starts."),
            ("I got in and there's a balance. Should I move it right away?",
             "No — document it first. Write down the balances, the transaction history, and the dates, and download your statements. That record is evidence for your taxes and your family, and it is what an investigation works from. Leaving the Bitcoin where it is while you think is almost always the safe choice; if you do move it, use the exchange's own withdrawal process, slowly, to a wallet you control. If you want the address's history documented in writing, a Wallet Report ($4.99 for the first address, $1.99 for each additional address) does exactly that — and the $6.99 AI Guided Next Steps walkthrough talks you through what to do next, only when a real lead exists."),
        ],
    },
    {
        "slug": "bought-bitcoin-canada-2016-2017",
        "title": "Bought Bitcoin in Canada in 2016–2017? Where It Likely Went",
        "description": "If you bought Bitcoin in Canada in 2016–2017, a short list of exchanges, ATMs, and marketplaces handled almost everyone. Which still exist, which are gone, and the records that can still tell you where yours went.",
        "dek": "Canadians who bought Bitcoin in 2016 or 2017 almost all used the same handful of places. Which one you used decides everything about what to do next — and your bank records from that year can usually still tell you.",
        "body": """
<h2>The short list of where Canadians bought</h2>
<p>In 2016–2017, most Canadians bought Bitcoin in one of a few places. <b>QuadrigaCX</b> was the biggest Canadian exchange of the era. <b>Coinsquare</b> also operated then. <b>Einstein Exchange</b> served a lot of buyers in British Columbia. Beyond exchanges, <b>Bitcoin ATMs</b> were common in cities, and <b>LocalBitcoins</b> matched buyers with individual sellers. Some Canadians also used international platforms, but for most people the answer is one of those names.</p>
<h2>Why the name matters: still open, or gone</h2>
<p>If the place you used still operates, your road is account recovery: go to its real site by typing the address yourself, try your original email, and use its own password-reset and identity-verification process. If it no longer exists, that road is closed and the work changes completely: the investigation runs on records — and on whether you ever withdrew the Bitcoin to a wallet of your own. QuadrigaCX is the famous Canadian case: it collapsed in 2019, and there is a specific, honest picture of what that means for former customers — see <a href="https://lostbitcoin.org/guides/quadrigacx-lost-bitcoin">our QuadrigaCX guide</a>. Einstein Exchange is also gone. LocalBitcoins shut down in 2023. A Bitcoin ATM purchase usually sent coins straight to a wallet address you provided, which makes that address the whole trail.</p>
<h2>The records from that era that still survive</h2>
<p>You don't have to rely on memory. Your bank can usually show Interac e-transfer history and card charges from 2016–2017 — the recipient name on the transfer often <i>is</i> the exchange name. Old email accounts hold welcome messages, purchase confirmations, and withdrawal notices. Tax filings from those years sometimes name the platform. Even a rough date plus a dollar amount is a strong starting point, because it narrows the list to one or two names.</p>
<h2>The strongest lead from that era</h2>
<p>If you ever withdrew Bitcoin from an exchange to your own wallet — a paper wallet, a phone app, a desktop wallet — that withdrawal is the best news an investigation can get. The destination address is visible on the public blockchain today: whether it was used, what it holds, and where the coins moved. An investigation can classify that trail honestly — CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN — and a Wallet Report ($4.99 for the first address) documents an address's public record in plain English. What no one can do is recreate keys that are gone, so be wary of anyone who promises otherwise.</p>
""",
        "faq": [
            ("I think I used QuadrigaCX. Is there anything left to do?",
             "There is an honest, limited picture — not nothing, and not a promise. QuadrigaCX collapsed in 2019 and its court-supervised process has largely run its course for customer claims. What still matters is whether you ever withdrew Bitcoin to your own wallet: that wallet is outside the collapse entirely. Our QuadrigaCX guide lays out the full picture, and the free assessment sorts out which branch your case is in."),
            ("I bought from a Bitcoin ATM and only kept a paper receipt. Is that enough?",
             "Often, yes — a receipt usually shows the date, the amount, and sometimes the wallet address the Bitcoin was sent to. That address can be checked on the public blockchain today. Even without the address, the date and amount help pin down which wallet you were using at the time."),
            ("I can't remember if I ever withdrew anything. How would I know?",
             "Look for a withdrawal confirmation email from the exchange, or check whether you still have a wallet app, a paper wallet, or a hardware wallet from that time. If an address turns up anywhere in your records, the public blockchain shows whether coins ever arrived at it. That's exactly what the free assessment is built to sort out — and it never asks for seed phrases, private keys, or passwords."),
        ],
    },
    {
        "slug": "how-much-bitcoin-is-lost-forever",
        "title": "How Much Bitcoin Is Lost Forever? What the Estimates Actually Say",
        "description": "Estimates say millions of Bitcoin may be lost forever — but nobody can count them. What 'lost' really means, how the numbers are built, the famous cases, and why some 'lost' Bitcoin turns up.",
        "dek": "You've probably heard the number: millions of Bitcoin, gone forever. It's one of the most searched questions in crypto — and one of the most misunderstood. Here's what the estimates actually say, and what they can't.",
        "body": """
<h2>The headline number</h2>
<p>The most cited estimate comes from blockchain analysis firm Chainalysis, which has estimated that roughly <b>3.7 million Bitcoin</b> — somewhere around 17–20% of all the Bitcoin that will ever exist — may be lost or stranded. Other analysts land lower or higher depending on their assumptions. Every one of those numbers is an <i>estimate</i>, not a count, and the gap between them is the honest part of the story: nobody can know the true figure, because nobody can tell a lost key from a patient holder just by looking at the blockchain.</p>
<h2>How anyone estimates this at all</h2>
<p>The methods are indirect. Analysts look at coins that have not moved in many years — a decade of silence usually means the owner either lost access or is extraordinarily patient. They look at the earliest era of Bitcoin, when coins were worth almost nothing and were mined on home computers that were later wiped, sold, or thrown away. Roughly a million early coins attributed to Bitcoin's first miners have never moved at all. Layer statistical models of lost keys and dead hard drives on top of that, and you get a range — millions of coins, give or take a lot. Treat any single precise-sounding figure with suspicion.</p>
<h2>What "lost" actually means</h2>
<p>Here is the part that surprises people: lost Bitcoin never disappears. The coins sit on the public blockchain, visible to anyone, exactly where they were left. What is lost is the <b>private key</b> — the secret that proves ownership and allows the coins to move. Without it, no one can move them: not the owner, not a bank, not a court, not the person who wrote Bitcoin's code. That is not a bug or an oversight; it is the design. It also means every "lost Bitcoin" headline is really a story about a lost key, a lost password, or a lost device.</p>
<h2>The famous cases</h2>
<p>A Welsh man says a hard drive holding about 8,000 Bitcoin was thrown into a landfill in 2013, when the coins were worth far less; his efforts to excavate the site have been refused, and the drive — if it is there — has never been recovered. An engineer has described forgetting the password to an encrypted drive holding thousands of Bitcoin, with only a couple of guesses left before the device locks forever. Early miners wiped laptops that held coins worth cents at the time. These stories are real, and they are also the extreme end: most lost Bitcoin was lost quietly, in small amounts, by ordinary people who didn't keep records because there was no reason to.</p>
<h2>Why some "lost" Bitcoin isn't</h2>
<p>Not every dormant coin is lost, and not every lost wallet stays lost. Old devices surface in drawers. Exchange accounts get re-entered years later. Paper backups turn up in estate files. That is why an investigation starts with evidence — records, devices, addresses — and classifies what it finds honestly: CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN. Some cases really are over, and an honest investigation says so. Others have a trail nobody had followed. The headline estimates can't tell you which kind yours is; only looking can. If you think you may have lost Bitcoin, start with <a href="https://lostbitcoin.org/guides/bought-bitcoin-years-ago-where-to-start">where to start</a> — and whatever you do, never share a seed phrase or password with anyone who offers to help.</p>
""",
        "faq": [
            ("Can lost Bitcoin ever be recovered?",
             "Only if a path to the keys survived: the wallet file, the backup words, the device itself, or an exchange account that can be re-entered. If the private key is truly gone, the coins are unreachable by anyone — that is how Bitcoin is designed. An investigation looks for what survived, and classifies what it finds as CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN. Anyone who guarantees recovery is not telling you the truth."),
            ("If millions of Bitcoin are lost, does that make the rest worth more?",
             "It reduces the number of coins actually available to trade, which is part of why these estimates get so much attention. Bitcoin's total supply is capped at 21 million either way; lost coins simply sit outside the market, possibly forever. Whether that matters for price is a market question — what matters here is that 'lost' is an estimate, and some of those coins may not be lost at all."),
            ("I think I lost Bitcoin years ago. Where do I start?",
             "With records, not guesses: bank statements, old emails, any device from that era, any address you wrote down. Our free assessment organizes what you remember and checks any address against the public blockchain, then tells you plainly whether there is a credible lead. It never asks for seed phrases, private keys, or wallet passwords — and neither should anyone else."),
        ],
    },
    {
        "slug": "bitcoin-recovery-guarantee-scam",
        "title": "Any Bitcoin 'Recovery' Service That Guarantees Results Is Lying to You",
        "description": "No one can guarantee Bitcoin recovery — access depends entirely on what survived, which nobody knows until they investigate. Why the guarantee is always a lie, what honest services say instead, and how it pairs with release-fee scams.",
        "dek": "If someone is promising you your Bitcoin back — guaranteed — they are lying to you. Not exaggerating. Not being optimistic. Lying. Here is why that promise can never be honest, and what an honest service says instead.",
        "body": """
<h2>Why a guarantee is impossible in principle</h2>
<p>Bitcoin has no reset button, no head office, and no support desk that can hand your coins back. Access depends entirely on what survived: a wallet file on an old laptop, an exchange account that can still be re-entered, a paper backup in a drawer, a device nobody wiped. If the keys survived, access may be straightforward. If the only copy is gone, the coins are unreachable by anyone — permanently, by design. And here is the point: nobody knows which of those is true until someone actually investigates. Not you, not an investigator, not the person who wrote Bitcoin's code. A guarantee offered before that work is done is a promise about facts the promiser does not have. It cannot be an honest promise, because the outcome is decided by evidence nobody has seen yet.</p>
<h2>What honest services say instead</h2>
<p>An honest service talks about evidence, not outcomes. It classifies what it finds, in writing, as <b>CONFIRMED</b>, <b>STRONG POSSIBILITY</b>, <b>POSSIBLE LEAD</b>, or <b>UNKNOWN</b> — and it does that classifying before asking for money. That is why our assessment is free: it checks your records, your devices, and any address against the public blockchain, and tells you plainly whether a credible lead exists. A full Investigation Report ($9.99) is only offered when one does. A Wallet Report ($4.99 for the first address, $1.99 for each additional address) documents what a single address shows. The AI Guided Next Steps walkthrough ($6.99) talks you through next steps — again, only when there is a real lead. Investigation, evidence, and guidance. Recovery is never guaranteed, and we never ask for seed phrases, private keys, or wallet passwords.</p>
<h2>Why the guarantee works — and what it pairs with</h2>
<p>The guarantee is not information. It is a sales weapon, aimed at hope and at grief — at the person who just lost money, or just lost a spouse, and wants one clear "yes." Once you believe the yes, the next step arrives: an upfront "release," "unlock," or "tax" fee to free the Bitcoin they claim to have found. Often they show you an address with a balance as proof. That proves nothing — balances are public, and anyone can display one. The full pattern, and how to test any service against it, is in our checklist: <a href="https://lostbitcoin.org/guides/bitcoin-recovery-service-scams">Bitcoin Recovery Service Scams: 9 Red Flags Before You Pay Anyone</a>. If they contacted you first, guarantee results, ask for your seed phrase, or want remote access to your computer, you do not need a second opinion. Walk away.</p>
<h2>Our standard, as a worked example</h2>
<p>Hold us to the same test. We will refuse your money when there is no credible lead: no report is offered, and checkout refuses one if it is attempted. That rule is published, in full, on our <a href="/guides/when-we-refuse-your-money">when we will refuse your money</a> page — and it is enforced by the site, not just promised in words. Prices are public before signup, payment goes through a real card checkout, and every finding separates what is confirmed from what is honestly unknown. If a service will not show you that much, in writing, before you pay, its guarantee is worth exactly what it costs to make: nothing.</p>
""",
        "faq": [
            ("A service says it has a 100% success rate. Could that be true?",
             "No. Success depends entirely on what survived in each case — a file, an account, a backup — and no service controls that. A 100% claim means they are cherry-picking easy cases, defining 'success' creatively, or lying. An honest service shows you the evidence classification for your case, in writing, before you pay anything."),
            ("They only charge after recovery, so doesn't that make the guarantee safe?",
             "No. A percentage-on-success deal is the model some legitimate wallet-file specialists use, but even they cannot promise an outcome before examining what survived — and the deal usually requires handing over your wallet file, which is its own risk. And watch the switch: 'pay after' scammers routinely invent a release, tax, or verification fee you must pay first. Any upfront fee to unlock your own money is a scam, and any request for a seed phrase, private key, or wallet password is theft."),
            ("How do I find out whether my Bitcoin is reachable at all?",
             "Start with evidence: old emails, bank statements, devices from that era, and any Bitcoin address you can find. Our free assessment organizes what you remember, checks any address against the public blockchain, and classifies the result as CONFIRMED, STRONG POSSIBILITY, POSSIBLE LEAD, or UNKNOWN. If there is no credible lead, you pay nothing — and new evidence, if it turns up later, reopens the case."),
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


_SCAM_CHECK_BODY = """
<h1>Is This a Bitcoin Recovery Scam? Free Checker</h1>
<p class="dek">Someone offering to get your Bitcoin back? Paste their message below. This checker scans it for the patterns that appear in almost every recovery scam — it runs entirely in your browser, and what you paste is never sent or stored anywhere.</p>
<textarea id="scamText" rows="9" style="width:100%;box-sizing:border-box" placeholder="Paste the message, email, or chat you received here..."></textarea>
<p><button class="button" onclick="checkScam()">CHECK THIS MESSAGE →</button></p>
<div id="scamResult"></div>
<h2>How to read the result</h2>
<p>One critical flag — a seed-phrase ask, a private-key ask, a "release fee" — is enough on its own: stop, do not pay, do not reply. Several smaller flags together paint the same picture. And no flags is <b>not</b> proof a service is honest — new scripts appear constantly. Whoever you deal with, these never change: never share a seed phrase, private key, or wallet password; never pay a fee to "unlock" your own money; type the website address yourself instead of following a link you were sent.</p>
<p>Read the full breakdown: <a href="/guides/bitcoin-recovery-service-scams">Bitcoin Recovery Service Scams: 9 Red Flags Before You Pay Anyone</a> — and here is <a href="/guides/when-we-refuse-your-money">when we will refuse your money</a>, so you can hold us to the same standard.</p>
<script>
var RULES = [
 {re:/seed phrase|recovery phrase|mnemonic|12[- ]word|24[- ]word/i, sev:3, t:"Asks for your seed / recovery phrase", w:"No legitimate service ever needs it. Whoever holds it can take everything, instantly and irreversibly. This alone settles it."},
 {re:/private key/i, sev:3, t:"Asks for your private key", w:"A private key is the money itself. Never share it with anyone, for any reason."},
 {re:/release fee|unlock(ing)? fee|clearance fee|liberation fee/i, sev:3, t:"Wants a 'release' or 'unlock' fee", w:"There is no such thing. Bitcoin has no gate and no gatekeeper. This is the classic second theft, aimed at people who have already lost money once."},
 {re:/(pay|send|deposit)[^.\\n]{0,60}(tax|verification|validation|processing fee)|(tax|verification|validation) (fee|payment|deposit)/i, sev:3, t:"Wants an upfront 'tax' or 'verification' payment", w:"Taxes are paid to a government — never to a recovery agent, and never as a condition of getting your own money back."},
 {re:/guarantee[ds]?[^.\\n]{0,40}(recover|success|return)|100\\s?%[^.\\n]{0,30}(recover|success|guaranteed)/i, sev:2, t:"Guarantees recovery", w:"Nobody can. Whether Bitcoin is reachable depends entirely on what survived — a file, an account, a backup. A guarantee is a sales weapon, not a fact."},
 {re:/wallet\\.dat|upload your wallet|send (us )?your wallet file|share your screen|anydesk|teamviewer|remote access/i, sev:2, t:"Wants your wallet file or screen access", w:"Handing over a wallet file or your screen gives a stranger everything they need. Legitimate help never starts this way."},
 {re:/telegram|whatsapp|signal app|dm me|message me on/i, sev:1, t:"Operates through chat apps and DMs", w:"Legitimate firms have a real website, a business identity, and paperwork. Recovery scammers live in DMs because the accounts are disposable."},
 {re:/act now|urgent(ly)?|immediately|within (24|48) hours|offer expires|last chance/i, sev:1, t:"Pressure and urgency", w:"Urgency exists to stop you checking. A real investigation takes the same steps next week as today."},
 {re:/\\b(1|3|bc1)[a-zA-HJ-NP-Za-km-z0-9]{25,39}\\b/, sev:1, t:"Includes a raw Bitcoin address to pay", w:"Payment to a raw address has no refunds and no way back. Our only payment route is card checkout on lostbitcoin.org — anyone asking you to pay in Bitcoin is not us."},
 {re:/fbi|interpol|europol|police|government (agent|agency)|official recovery (team|unit)/i, sev:1, t:"Claims official authority", w:"Law enforcement does not message people offering recovery, and never charges a fee to return property."},
 {re:/double your|guaranteed profit|investment opportunit|returns of \\d+\\s?%/i, sev:1, t:"Promises investment returns", w:"That is not recovery at all — it is an investment scam wearing a recovery costume."}
];
function checkScam(){
  var text = document.getElementById('scamText').value || '';
  var out = document.getElementById('scamResult');
  if(text.trim().length < 10){ out.innerHTML = '<div class="warn"><p>Paste the full message first — a few words is not enough to check.</p></div>'; return; }
  var hits = [], score = 0, critical = false;
  for(var i=0;i<RULES.length;i++){ if(RULES[i].re.test(text)){ hits.push(RULES[i]); score += RULES[i].sev; if(RULES[i].sev>=3) critical = true; } }
  var html = '';
  if(critical || score >= 4){
    html = '<div class="warn"><p><b>This carries the marks of a recovery scam.</b> Do not pay anything, do not share any keys or phrases, and do not reply — engagement only invites the next script. If you already paid, our <a href="/guides/bitcoin-recovery-service-scams">red-flags guide</a> has a section on what to do next.</p></div>';
  } else if(score >= 1){
    html = '<div class="warn"><p><b>Caution — patterns worth a hard second look.</b> None of these alone proves a scam, but together they are how the scripts usually start. Verify the business independently before sending anything.</p></div>';
  } else {
    html = '<div class="notice"><p><b>None of the classic patterns found.</b> That is not proof a service is honest — new scripts appear constantly. Still verify them independently, and never share a seed phrase, private key, or wallet password with anyone, whatever this checker says.</p></div>';
  }
  if(hits.length){
    html += '<h2>What was flagged</h2><ul>';
    for(var j=0;j<hits.length;j++){ html += '<li><b>' + hits[j].t + '.</b> ' + hits[j].w + '</li>'; }
    html += '</ul>';
  }
  out.innerHTML = html;
}
</script>
"""


def render_scam_check():
    return _page(
        "Is This a Bitcoin Recovery Scam? Free Checker",
        "Paste a message from anyone offering to recover your Bitcoin. Free checker scans for the classic recovery-scam patterns — seed-phrase asks, release fees, guaranteed recovery. Runs in your browser; nothing is sent or stored.",
        "/scam-check", _SCAM_CHECK_BODY + _CTA)
