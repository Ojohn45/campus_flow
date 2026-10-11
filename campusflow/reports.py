"""Engineer B — Work queue (F5) and reports (F6)."""

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _numeric_id(ticket):
    """'T007' -> 7 so ties break by real number, not string."""
    return int(ticket["id"].lstrip("T"))


def get_work_queue(tickets):
    """
    F5 — Open, unresolved tickets, ordered critical -> high -> medium -> low,
    ties broken by earlier numeric ticket ID.
    """
    open_tickets = [t for t in tickets if t["status"] == "open"]
    return sorted(
        open_tickets,
        key=lambda t: (PRIORITY_ORDER.get(t["priority"], 99), _numeric_id(t)),
    )


def build_report(tickets):
    """
    F6 — Totals and breakdowns. Handles zero tickets.
    Returns a dict so it is easy to test and print.
    """
    report = {
        "total": len(tickets),
        "by_status": {s: 0 for s in ["open", "in_progress", "resolved"]},
        "by_priority": {p: 0 for p in ["critical", "high", "medium", "low"]},
    }
    for t in tickets:
        if t["status"] in report["by_status"]:
            report["by_status"][t["status"]] += 1
        if t["priority"] in report["by_priority"]:
            report["by_priority"][t["priority"]] += 1
    return report


def format_report(report):
    """Turn the report dict into printable text."""
    lines = [f"Total tickets: {report['total']}"]
    lines.append("By status:")
    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")
    lines.append("By priority:")
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")
    return "\n".join(lines)