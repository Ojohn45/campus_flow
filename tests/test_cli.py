"""CLI wiring tests for Engineer B's menu functions.

Strategy: replace input() with a scripted list of answers, replace print()
with a capture so we can assert on what the user would have seen. This tests
the WIRING (right function called, right message shown), not the business
logic — that's already covered in test_workflow.py and test_reports.py.
"""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import main
from main import (
    menu_assign,
    menu_change_status,
    menu_reopen,
    menu_queue,
    menu_report,
    view_one_ticket,
)


def make_ticket(tid="T001", status="open", assigned_to=None,
                priority="high", title="Test ticket"):
    return {
        "id": tid,
        "title": title,
        "category": "Network",
        "urgency": "high",
        "affected_users": 5,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


def run_with_inputs(func, *args, inputs):
    """Run func with scripted input() answers, capture stdout, return it."""
    with patch("builtins.input", side_effect=inputs):
        buf = io.StringIO()
        with redirect_stdout(buf):
            func(*args)
    return buf.getvalue()


class TestMenuAssign(unittest.TestCase):
    def test_assign_success_message(self):
        tickets = [make_ticket()]
        out = run_with_inputs(menu_assign, tickets,
                              inputs=["T001", "Ada"])
        self.assertIn("✔", out)
        self.assertEqual(tickets[0]["assigned_to"], "Ada")

    def test_assign_unknown_id_shows_error(self):
        tickets = [make_ticket()]
        out = run_with_inputs(menu_assign, tickets,
                              inputs=["T999", "Ada"])
        self.assertIn("✘", out)
        self.assertIn("Unknown", out)
        self.assertIsNone(tickets[0]["assigned_to"])

    def test_assign_blank_name_shows_error(self):
        tickets = [make_ticket()]
        out = run_with_inputs(menu_assign, tickets,
                              inputs=["T001", "   "])
        self.assertIn("✘", out)


class TestMenuChangeStatus(unittest.TestCase):
    def test_status_change_success(self):
        tickets = [make_ticket(assigned_to="Ada")]
        out = run_with_inputs(menu_change_status, tickets,
                              inputs=["T001", "in_progress"])
        self.assertIn("✔", out)
        self.assertEqual(tickets[0]["status"], "in_progress")

    def test_unassigned_to_in_progress_rejected(self):
        tickets = [make_ticket()]
        out = run_with_inputs(menu_change_status, tickets,
                              inputs=["T001", "in_progress"])
        self.assertIn("✘", out)
        self.assertEqual(tickets[0]["status"], "open")

    def test_status_input_is_lowercased(self):
        """Menu lowercases the status, so 'IN_PROGRESS' should work."""
        tickets = [make_ticket(assigned_to="Ada")]
        out = run_with_inputs(menu_change_status, tickets,
                              inputs=["T001", "IN_PROGRESS"])
        self.assertIn("✔", out)
        self.assertEqual(tickets[0]["status"], "in_progress")


class TestMenuReopen(unittest.TestCase):
    def test_reopen_success(self):
        tickets = [make_ticket(status="resolved", assigned_to="Ada")]
        out = run_with_inputs(menu_reopen, tickets, inputs=["T001"])
        self.assertIn("✔", out)
        self.assertEqual(tickets[0]["status"], "open")


class TestMenuQueue(unittest.TestCase):
    def test_queue_prints_ticket_ids(self):
        tickets = [
            make_ticket("T003", priority="low"),
            make_ticket("T001", priority="critical"),
            make_ticket("T002", priority="high"),
        ]
        out = run_with_inputs(menu_queue, tickets, inputs=[])
        self.assertIn("T001", out)
        self.assertIn("T002", out)
        self.assertIn("T003", out)
        # critical should appear before low in the output
        self.assertLess(out.index("T001"), out.index("T003"))

    def test_empty_queue_prints_friendly_message(self):
        out = run_with_inputs(menu_queue, [], inputs=[])
        self.assertIn("empty", out.lower())


class TestMenuReport(unittest.TestCase):
    def test_report_prints_total(self):
        tickets = [make_ticket(), make_ticket("T002", priority="low")]
        out = run_with_inputs(menu_report, tickets, inputs=[])
        self.assertIn("Total tickets: 2", out)

    def test_empty_report_prints_zero(self):
        out = run_with_inputs(menu_report, [], inputs=[])
        self.assertIn("Total tickets: 0", out)


class TestViewOneTicket(unittest.TestCase):
    def test_view_shows_ticket_fields(self):
        tickets = [make_ticket(title="Wi-Fi down")]
        out = run_with_inputs(view_one_ticket, tickets, inputs=["T001"])
        self.assertIn("Wi-Fi down", out)
        self.assertIn("T001", out)

    def test_view_unknown_id_shows_error(self):
        tickets = [make_ticket()]
        out = run_with_inputs(view_one_ticket, tickets, inputs=["T999"])
        self.assertIn("Unknown", out)


class TestMainLoop(unittest.TestCase):
    def test_menu_exits_on_zero(self):
        """Feed '0' to the menu loop and confirm it exits cleanly."""
        with patch.object(main.storage, "load_tickets", return_value=[]):
            with patch("builtins.input", side_effect=["0"]):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    main.main()
        out = buf.getvalue()
        self.assertIn("Goodbye", out)

    def test_menu_rejects_unknown_choice_then_exits(self):
        with patch.object(main.storage, "load_tickets", return_value=[]):
            with patch("builtins.input", side_effect=["99", "", "0"]):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    main.main()
        out = buf.getvalue()
        self.assertIn("Invalid choice", out)
        self.assertIn("Goodbye", out)


if __name__ == "__main__":
    unittest.main()