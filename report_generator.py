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
