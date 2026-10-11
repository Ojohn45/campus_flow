import unittest
from campusflow.workflow import assign_ticket, change_status, reopen_ticket


def make_ticket(tid="T001", status="open", assigned_to=None, priority="high"):
    return {
        "id": tid,
        "title": "Test ticket",
        "category": "Network",
        "urgency": "high",
        "affected_users": 5,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestAssign(unittest.TestCase):
    def test_assign_success(self):
        tickets = [make_ticket()]
        ok, _ = assign_ticket(tickets, "T001", "Ada")
        self.assertTrue(ok)
        self.assertEqual(tickets[0]["assigned_to"], "Ada")

    def test_assign_unknown_id(self):
        tickets = [make_ticket()]
        ok, msg = assign_ticket(tickets, "T999", "Ada")
        self.assertFalse(ok)
        self.assertIn("Unknown", msg)

    def test_assign_empty_name(self):
        tickets = [make_ticket()]
        ok, _ = assign_ticket(tickets, "T001", "   ")
        self.assertFalse(ok)


class TestWorkflow(unittest.TestCase):
    def test_unassigned_cannot_start(self):
        tickets = [make_ticket()]
        ok, msg = change_status(tickets, "T001", "in_progress")
        self.assertFalse(ok)
        self.assertEqual(tickets[0]["status"], "open")

    def test_full_lifecycle(self):
        tickets = [make_ticket()]
        assign_ticket(tickets, "T001", "Ada")
        self.assertTrue(change_status(tickets, "T001", "in_progress")[0])
        self.assertTrue(change_status(tickets, "T001", "resolved")[0])
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_invalid_transition(self):
        tickets = [make_ticket()]
        assign_ticket(tickets, "T001", "Ada")
        ok, _ = change_status(tickets, "T001", "resolved")  # open -> resolved
        self.assertFalse(ok)

    def test_reopen(self):
        tickets = [make_ticket(status="resolved", assigned_to="Ada")]
        self.assertTrue(reopen_ticket(tickets, "T001")[0])
        self.assertEqual(tickets[0]["status"], "open")


if __name__ == "__main__":
    unittest.main()