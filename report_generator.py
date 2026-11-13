"""
Lost Bitcoin — Report generator.

Builds a professional Markdown investigation report from the Master
Investigation Record and registers it with save_report().

The report always separates:
  CONFIRMED findings / STRONG POSSIBILITIES / POSSIBLE LEADS / UNKNOWN,
and always states that a balance does not prove ownership and that
recovery is never guaranteed.
"""

from datetime import datetime, timezone
from pathlib import Path

import master_investigation_record as record

_SECTIONS = [
    ("confirmed", "Confirmed findings"),
    ("strong_possibility", "Strong possibilities"),
    ("possible_lead", "Possible leads"),
    ("unknown", "Unknowns and limitations"),
]


def _checklist_for(title):
    """Concrete working steps for a recommendation, in plain English."""
    steps = {
        "Preserve the original device or backup": [
            "Stop using the device or backup for everyday tasks where practical.",
            "Do not wipe, factory-reset, reinstall, format or discard it.",
            "Write down what it is, where it was found, and when it was last used.",
            "Photograph labels, ports, drive markings and any handwritten notes stored with it.",
            "Make a verified copy before searching it, and work from the copy rather than the original.",
        ],
        "Gather the records you mentioned": [
            "Search the original email account for: the exchange name, Bitcoin, BTC, "
            "order, purchase, deposit, withdrawal, confirmation and transaction ID.",
            "Focus first on the approximate acquisition period, then widen the date range if nothing appears.",
            "For bank or card statements, capture the date, amount, exchange or payment processor, and any reference number.",
            "For every useful record, note the date, amount, exchange, wallet address and transaction ID in one timeline.",
            "Keep the original files unchanged; work from copies.",
        ],
        "Try the original account first": [
            "Establish whether the service still operates, has closed, or has an official bankruptcy or claims process.",
            "Go directly to the service's official website or app yourself; do not follow sign-in links from old emails.",
            "Try signing in or resetting access with the original email address.",
            "Save screenshots, confirmation emails and support replies to the investigation timeline.",
            "Stop immediately if any site asks for a seed phrase or private key — a legitimate account-recovery process will not ask for one.",
        ],
        "Answer the remaining questions": [
            "Revisit each unknown one at a time; a small detail can change which lead is strongest.",
            "If a question cannot be answered, leave it unknown rather than guessing.",
        ],
        "Double-check this address": [
            "Compare the address character by character with the original source.",
            "Check old emails, exchange withdrawal records and wallet backups for other addresses from the same period.",
        ],
        "Work out how this address was controlled": [
            "List every wallet, device, backup and exchange account that could have controlled the address.",
            "Compare the address's first and latest activity with your records and acquisition dates.",
            "Do not move any funds while ownership and access are still being established.",
        ],
    }
    return steps.get(title, [
        "Work through this recommendation in the order shown and preserve every record you find.",
        "Record what you checked, what you found, and what remains unknown.",
    ])


def build_report_markdown(investigation_id):
    full = record.get_complete_investigation(investigation_id)
    if full is None:
        raise ValueError("Investigation not found.")

    customer = full["customer"]
    lines = [
        "# Lost Bitcoin — Investigation Report",
        "",
        f"**Customer:** {customer['name']} ({customer['email']})",
        f"**Investigation started:** {full['created_at']}",
        f"**Starting point:** {full['starting_point']}",
        f"**Report generated:** "
        f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "## Summary of information you provided",
    ]
    if full["answers"]:
        for a in full["answers"]:
            lines.append(f"- **{a['question_key']}:** {a['answer_value']}")
    else:
        lines.append("- No questionnaire answers recorded yet.")
    if full["addresses"]:
        lines += ["", "## Bitcoin addresses investigated"]
        for a in full["addresses"]:
            label = f" — {a['label']}" if a["label"] else ""
            lines.append(f"- `{a['address']}`{label}")
    if full["discoveries"]:
        lines += ["", "## Investigation steps completed"]
        for d in full["discoveries"]:
            lines.append(f"- {d['description']} _(source: {d['source_type']})_")

    lines += [
        "",
        "## How to read this report",
        "",
        "- **CONFIRMED** means the point was checked against a source "
        "independent of the customer's account, such as the public blockchain.",
        "- **STRONG POSSIBILITY** means several pieces of information point "
        "the same way, but the point has not been independently proven.",
        "- **POSSIBLE LEAD** means the customer provided a clue that is "
        "specific enough to investigate; it is not a finding.",
        "- **UNKNOWN** means there is not enough reliable information yet. "
        "An unknown is not treated as evidence that Bitcoin is lost.",
    ]

    for confidence, title in _SECTIONS:
        items = [e for e in full["evidence"] if e["confidence"] == confidence]
        lines += ["", f"## {title}"]
        if items:
            for e in items:
                lines.append(f"- {e['description']}")
        else:
            lines.append("- None recorded.")
            if confidence == "unknown":
                lines[-1] = ("- Anything not listed above remains unknown. "
                             "Absence of evidence is not evidence of loss.")

    lines += ["", "## Recommended next actions"]
    if full["recommendations"]:
        for r in full["recommendations"]:
            lines.append(f"- **{r['title']}** ({r['priority']}): {r['details']}")
    else:
        lines.append("- None recorded yet.")

    lines += ["", "## Detailed action checklists"]
    if full["recommendations"]:
        for r in full["recommendations"]:
            lines += ["", f"### {r['title']}"]
            for step in _checklist_for(r["title"]):
                lines.append(f"- {step}")
    else:
        lines.append("- No checklist can be prepared until at least one "
                     "recommendation has been recorded.")

    lines += [
        "", "## Important limitations", "",
        "- Blockchain activity confirms transactions and balances for an "
        "address. It does **not** prove who owns an address, and it does "
        "not prove Bitcoin can be accessed or recovered.",
        "- Lost Bitcoin sells investigation, evidence and guidance. "
        "Recovery is never guaranteed.",
        "- Never share a seed phrase or private key with anyone — "
        "including us. We will never ask for one.",
        "",
    ]
    return "\n".join(lines)


def generate_report(investigation_id, output_dir, report_type="investigation_report"):
    """Write the report file and register it in the investigation record."""
    markdown = build_report_markdown(investigation_id)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"report_{investigation_id[:8]}_{stamp}.md"
    path.write_text(markdown, encoding="utf-8")
    report_id = record.save_report(investigation_id, report_type, str(path))
    return {"report_id": report_id, "file_path": str(path), "markdown": markdown}
