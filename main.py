"""CampusFlow CLI — menu loop.

Engineer A owns: create, list/view, priority engine, storage load/save.
Engineer B owns: assign (F3), workflow (F4), queue (F5), reports (F6).
"""

from campusflow import storage
from campusflow.reports import get_work_queue, build_report, format_report
from campusflow.workflow import assign_ticket, change_status, reopen_ticket, find_ticket

try:
    from campusflow.tickets import create_ticket, list_tickets
except ImportError:
    def create_ticket(tickets):
        print("[A's feature not merged yet]")
    def list_tickets(tickets):
        print("[A's feature not merged yet]")


MENU = """
╔══════════════════════╗
║    CampusFlow CLI    ║
╠══════════════════════╣
║  1. Create ticket    ║
║  2. List all tickets ║
║  3. View one ticket  ║
║  4. Assign ticket    ║
║  5. Change status    ║
║  6. Reopen ticket    ║
║  7. Work queue       ║
║  8. Report           ║
║  9. Save             ║
║  0. Exit             ║
╚══════════════════════╝
"""

VALID_STATUSES = ["open", "in_progress", "resolved", "closed"]


def prompt(msg):
    """Get stripped input from the user."""
    return input(msg).strip()


def pause():
    """Wait for the user to press Enter."""
    input("\nPress Enter to continue...")


def divider(title=""):
    """Print a section divider with optional title."""
    if title:
        print(f"\n{'─' * 6} {title} {'─' * 6}")
    else:
        print("─" * 30)


# ---------------- View helpers ----------------

def view_one_ticket(tickets):
    tid = prompt("Ticket ID: ").upper()
    ticket = find_ticket(tickets, tid)
    if ticket is None:
        print(f"✘ Unknown ticket ID: {tid}")
        return
    divider("Ticket Details")
    for key, value in ticket.items():
        display_val = value if value is not None else "—"
        print(f"  {key:>15}: {display_val}")
    divider()


# ---------------- F3 — Assign ----------------

def menu_assign(tickets):
    divider("Assign Ticket")
    tid = prompt("Ticket ID: ").upper()
    name = prompt("Staff name : ")
    if not name:
        print("✘ Staff name cannot be empty.")
        return
    ok, msg = assign_ticket(tickets, tid, name)
    print(("✔ " if ok else "✘ ") + msg)


# ---------------- F4 — Workflow ----------------

def menu_change_status(tickets):
    divider("Change Status")
    tid = prompt("Ticket ID: ").upper()
    print(f"  Valid statuses: {' | '.join(VALID_STATUSES)}")
    new_status = prompt("New status : ").lower()
    if new_status not in VALID_STATUSES:
        print(f"✘ '{new_status}' is not a valid status.")
        return
    ok, msg = change_status(tickets, tid, new_status)
    print(("✔ " if ok else "✘ ") + msg)


def menu_reopen(tickets):
    divider("Reopen Ticket")
    tid = prompt("Ticket ID to reopen: ").upper()
    ok, msg = reopen_ticket(tickets, tid)
    print(("✔ " if ok else "✘ ") + msg)


# ---------------- F5 — Work queue ----------------

def menu_queue(tickets):
    queue = get_work_queue(tickets)
    divider("Work Queue")
    if not queue:
        print("  Work queue is empty! 🎉")
        return
    print(f"  {len(queue)} ticket(s) pending\n")
    print(f"  {'ID':<8}{'PRIORITY':<12}{'STATUS':<14}{'TITLE'}")
    print(f"  {'─'*8}{'─'*12}{'─'*14}{'─'*20}")
    for t in queue:
        assigned = f"[{t.get('assigned_to', '—')}]"
        print(f"  {t['id']:<8}{t['priority']:<12}{t['status']:<14}{t['title']}")
    divider()


# ---------------- F6 — Reports ----------------

def menu_report(tickets):
    divider("Report")
    if not tickets:
        print("  No tickets found.")
        return
    report = build_report(tickets)
    print()
    print(format_report(report))
    divider()


# ---------------- Save ----------------

def menu_save(tickets):
    try:
        storage.save_tickets(tickets)
        print("✔ Tickets saved successfully.")
    except Exception as e:
        print(f"✘ Save failed: {e}")


# ---------------- Main loop ----------------

def main():
    print("\n  Welcome to CampusFlow!")
    tickets = storage.load_tickets()
    print(f"  ✔ Loaded {len(tickets)} ticket(s).\n")

    actions = {
        "1": lambda: create_ticket(tickets),
        "2": lambda: list_tickets(tickets),
        "3": lambda: view_one_ticket(tickets),
        "4": lambda: menu_assign(tickets),
        "5": lambda: menu_change_status(tickets),
        "6": lambda: menu_reopen(tickets),
        "7": lambda: menu_queue(tickets),
        "8": lambda: menu_report(tickets),
        "9": lambda: menu_save(tickets),
    }

    while True:
        print(MENU)
        choice = prompt("Choose an option: ")

        if choice == "0":
            menu_save(tickets)
            print("\n  Goodbye! 👋")
            break

        action = actions.get(choice)
        if action is None:
            print("  ✘ Invalid choice. Please enter a number from the menu.")
            continue

        try:
            action()
        except Exception as exc:
            print(f"\n  ✘ Unexpected error: {exc}")

        pause()


if __name__ == "__main__":
    main()