"""Engineer B — Assignment and lifecycle (F3 + F4)."""

VALID_STATUSES = ["open", "in_progress", "resolved"]

# Legal transitions only. Anything not listed is rejected.
ALLOWED_TRANSITIONS = {
    ("open", "in_progress"),
    ("in_progress", "resolved"),
    ("resolved", "open"),   # explicit reopen only
}


def find_ticket(tickets, ticket_id):
    """Return the ticket dict with this id, or None."""
    for t in tickets:
        if t["id"] == ticket_id:
            return t
    return None


def assign_ticket(tickets, ticket_id, staff_name):
    """
    F3 — Assign a ticket to a staff member.
    Returns (True, message) on success, (False, message) on failure.
    """
    if staff_name is None or not str(staff_name).strip():
        return False, "Staff name cannot be empty."

    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        return False, f"Unknown ticket ID: {ticket_id}"

    ticket["assigned_to"] = str(staff_name).strip()
    return True, f"Ticket {ticket_id} assigned to {ticket['assigned_to']}."


def change_status(tickets, ticket_id, new_status):
    """
    F4 — Move a ticket through its lifecycle.
    Rules:
      - new_status must be a known status
      - the (current -> new) pair must be an allowed transition
      - a ticket must be assigned before entering in_progress
    Returns (True, message) or (False, message).
    """
    ticket = find_ticket(tickets, ticket_id)
    if ticket is None:
        return False, f"Unknown ticket ID: {ticket_id}"

    if new_status not in VALID_STATUSES:
        return False, f"Invalid status: {new_status}"

    current = ticket["status"]

    if (current, new_status) not in ALLOWED_TRANSITIONS:
        return False, f"Cannot move from '{current}' to '{new_status}'."

    if new_status == "in_progress" and not ticket.get("assigned_to"):
        return False, "Unassigned ticket cannot move to in_progress."

    ticket["status"] = new_status
    return True, f"Ticket {ticket_id} is now '{new_status}'."


def reopen_ticket(tickets, ticket_id):
    """Explicit reopen: resolved -> open."""
    return change_status(tickets, ticket_id, "open")