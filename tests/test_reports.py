import unittest
from campusflow.reports import get_work_queue, build_report


def make_ticket(tid, priority, status="open"):
    return {
        "id": tid, "title": "t", "category": "Network",
        "urgency": "high", "affected_users": 5,
        "priority": priority, "status": status, "assigned_to": None,
    }


class TestQueue(unittest.TestCase):
    def test_queue_order(self):
        tickets = [
            make_ticket("T003", "low"),
            make_ticket("T001", "critical"),
            make_ticket("T002", "critical"),
            make_ticket("T004", "resolved", status="resolved"),
        ]
        queue = get_work_queue(tickets)
        ids = [t["id"] for t in queue]
        self.assertEqual(ids, ["T001", "T002", "T003"])  # T004 excluded

    def test_queue_priority_then_id(self):
        tickets = [
            make_ticket("T010", "high"),
            make_ticket("T002", "high"),
            make_ticket("T001", "critical"),
        ]
        ids = [t["id"] for t in get_work_queue(tickets)]
        self.assertEqual(ids, ["T001", "T002", "T010"])


class TestReport(unittest.TestCase):
    def test_empty_report(self):
        r = build_report([])
        self.assertEqual(r["total"], 0)
        self.assertEqual(sum(r["by_status"].values()), 0)

    def test_counts(self):
        tickets = [
            make_ticket("T001", "critical", "open"),
            make_ticket("T002", "high", "resolved"),
            make_ticket("T003", "high", "open"),
        ]
        r = build_report(tickets)
        self.assertEqual(r["total"], 3)
        self.assertEqual(r["by_status"]["open"], 2)
        self.assertEqual(r["by_priority"]["high"], 2)


if __name__ == "__main__":
    unittest.main()