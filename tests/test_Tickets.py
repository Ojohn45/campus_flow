"""
Tests for CampusFlow Tickets.py
"""

import unittest

from Tickets import Ticket


class TestTicket(unittest.TestCase):

    def setUp(self):
        self.ticket = Ticket(
            title="Broken classroom projector",
            description="The projector in Room 12 is not working.",
            category="technical",
            priority="high",
        )

    def test_ticket_creation(self):
        """A ticket should be created with valid information."""

        self.assertEqual(
            self.ticket.title,
            "Broken classroom projector",
        )
        self.assertEqual(self.ticket.category, "technical")
        self.assertEqual(self.ticket.priority, "high")
        self.assertEqual(self.ticket.status, "open")

    def test_ticket_has_unique_id(self):
        """Each newly created ticket should have its own ID."""

        first = Ticket(
            title="First issue",
            description="First description",
        )

        second = Ticket(
            title="Second issue",
            description="Second description",
        )

        self.assertNotEqual(first.ticket_id, second.ticket_id)

    def test_ticket_has_timestamps(self):
        """A ticket should have creation and update timestamps."""

        self.assertTrue(self.ticket.created_at)
        self.assertTrue(self.ticket.updated_at)

    def test_empty_title_is_rejected(self):
        """An empty title should raise ValueError."""

        with self.assertRaises(ValueError):
            Ticket(
                title="   ",
                description="A valid description.",
            )

    def test_empty_description_is_rejected(self):
        """An empty description should raise ValueError."""

        with self.assertRaises(ValueError):
            Ticket(
                title="A valid title",
                description="   ",
            )

    def test_long_title_is_rejected(self):
        """Titles longer than 200 characters should be rejected."""

        with self.assertRaises(ValueError):
            Ticket(
                title="A" * 201,
                description="A valid description.",
            )

    def test_invalid_category_is_rejected(self):
        """An unsupported category should be rejected."""

        with self.assertRaises(ValueError):
            Ticket(
                title="Test ticket",
                description="Test description.",
                category="invalid_category",
            )

    def test_invalid_priority_is_rejected(self):
        """An unsupported priority should be rejected."""

        with self.assertRaises(ValueError):
            Ticket(
                title="Test ticket",
                description="Test description.",
                priority="super_urgent",
            )

    def test_invalid_status_is_rejected(self):
        """An unsupported status should be rejected."""

        with self.assertRaises(ValueError):
            Ticket(
                title="Test ticket",
                description="Test description.",
                status="pending_unknown",
            )

    def test_fields_are_normalized(self):
        """Categories, priorities, and statuses should be lowercase."""

        ticket = Ticket(
            title="  Test ticket  ",
            description="  Test description  ",
            category="TECHNICAL",
            priority="HIGH",
            status="OPEN",
        )

        self.assertEqual(ticket.title, "Test ticket")
        self.assertEqual(ticket.description, "Test description")
        self.assertEqual(ticket.category, "technical")
        self.assertEqual(ticket.priority, "high")
        self.assertEqual(ticket.status, "open")

    def test_ticket_update(self):
        """Valid updates should change ticket information."""

        self.ticket.update(
            title="Updated classroom projector",
            priority="urgent",
        )

        self.assertEqual(
            self.ticket.title,
            "Updated classroom projector",
        )
        self.assertEqual(self.ticket.priority, "urgent")

    def test_update_changes_timestamp(self):
        """Updating a ticket should refresh its update timestamp."""

        original_timestamp = self.ticket.updated_at

        self.ticket.update(status="in_progress")

        self.assertGreaterEqual(
            self.ticket.updated_at,
            original_timestamp,
        )

    def test_invalid_update_preserves_original_values(self):
        """A failed update should not change the existing ticket."""

        original_title = self.ticket.title
        original_priority = self.ticket.priority

        with self.assertRaises(ValueError):
            self.ticket.update(
                title="A new title",
                priority="invalid_priority",
            )

        self.assertEqual(self.ticket.title, original_title)
        self.assertEqual(self.ticket.priority, original_priority)

    def test_immutable_fields_cannot_be_updated(self):
        """IDs and timestamps cannot be changed through update()."""

        original_id = self.ticket.ticket_id

        with self.assertRaises(ValueError):
            self.ticket.update(ticket_id="another-id")

        self.assertEqual(self.ticket.ticket_id, original_id)

    def test_to_dict(self):
        """A ticket should convert into a dictionary."""

        data = self.ticket.to_dict()

        self.assertEqual(data["ticket_id"], self.ticket.ticket_id)
        self.assertEqual(data["title"], self.ticket.title)
        self.assertEqual(data["category"], self.ticket.category)
        self.assertEqual(data["status"], self.ticket.status)

    def test_from_dict(self):
        """A ticket should be recreated from its dictionary."""

        data = self.ticket.to_dict()
        restored = Ticket.from_dict(data)

        self.assertEqual(restored.ticket_id, self.ticket.ticket_id)
        self.assertEqual(restored.title, self.ticket.title)
        self.assertEqual(restored.description, self.ticket.description)
        self.assertEqual(restored.category, self.ticket.category)

    def test_from_dict_rejects_missing_fields(self):
        """Incomplete ticket data should be rejected."""

        with self.assertRaises(ValueError):
            Ticket.from_dict({
                "title": "Incomplete ticket",
            })


if __name__ == "__main__":
    unittest.main()