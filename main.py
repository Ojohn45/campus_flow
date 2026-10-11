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
===== CampusFlow =====
1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change ticket status
6. Reopen ticket
7. Work queue
8. Report
9. Save
0. Exit
"""


def prompt(msg):
    return input(msg).strip()


def pause():
    input("\nPress Enter to continue...")


# ---------------- View helpers (F2 co-owned) ----------------

def view_one_ticket(tickets):
    tid = prompt("Ticket ID: ")
    ticket = find_ticket(tickets, tid)
    if ticket is None:
        print(f"Unknown ticket ID: {tid}")
        return
    print("\n--- Ticket ---")
    for key, value in ticket.items():
        print(f"{key:>15}: {value}")


# ---------------- F3 — Assign ----------------

def menu_assign(tickets):
    tid = prompt("Ticket ID to assign: ")
    name = prompt("Staff name: ")
    ok, msg = assign_ticket(tickets, tid, name)
    print(("✔ " if ok else "✘ ") + msg)


# ---------------- F4 — Workflow ----------------

def menu_change_status(tickets):
    tid = prompt("Ticket ID: ")
    print("New status: open | in_progress | resolved")
    new_status = prompt("Status: ").lower()
    ok, msg = change_status(tickets, tid, new_status)
    print(("✔ " if ok else "✘ ") + msg)


def menu_reopen(tickets):
    tid = prompt("Ticket ID to reopen: ")
    ok, msg = reopen_ticket(tickets, tid)
    print(("✔ " if ok else "✘ ") + msg)


# ---------------- F5 — Work queue ----------------

def menu_queue(tickets):
    queue = get_work_queue(tickets)
    if not queue:
        print("Work queue is empty. 🎉")
        return
    print(f"\n--- Work Queue ({len(queue)} open) ---")
    print(f"{'ID':<6}{'PRIORITY':<10}{'TITLE'}")
    for t in queue:
        print(f"{t['id']:<6}{t['priority']:<10}{t['title']}")


# ---------------- F6 — Reports ----------------

def menu_report(tickets):
    report = build_report(tickets)
    print()
    print(format_report(report))


# ---------------- Main loop ----------------

def main():
    tickets = storage.load_tickets()  # Engineer A's loader
    print(f"Loaded {len(tickets)} ticket(s).")

    actions = {
        "1": lambda: create_ticket(tickets),
        "2": lambda: list_tickets(tickets),
        "3": lambda: view_one_ticket(tickets),
        "4": lambda: menu_assign(tickets),
        "5": lambda: menu_change_status(tickets),
        "6": lambda: menu_reopen(tickets),
        "7": lambda: menu_queue(tickets),
        "8": lambda: menu_report(tickets),
        "9": lambda: (storage.save_tickets(tickets), print("✔ Saved.")),
    }

    while True:
        print(MENU)
        choice = prompt("Choose: ")

        if choice == "0":
            print("Goodbye.")
            break

        action = actions.get(choice)
        if action is None:
            print("Invalid choice. Try again.")
            continue

        try:
            action()
        except Exception as exc:
            # Never let a bug crash the menu loop.
            print(f"✘ Unexpected error: {exc}")

        pause()


if __name__ == "__main__":
    main()