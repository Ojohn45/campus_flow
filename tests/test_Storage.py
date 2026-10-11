"""
Tests for CampusFlow Storage.py
"""

import json
import tempfile
import unittest
from pathlib import Path

from Tickets import Ticket
from Storage import (
    Storage,
    StorageError,
    TicketNotFoundError,
    DuplicateTicketError,
)


class TestStorage(unittest.TestCase):

    def setUp(self):
        """Create a temporary storage file for each test."""

        self.temp_directory = tempfile.TemporaryDirectory()

        self.storage_path = (
            Path(self.temp_directory.name) / "tickets.json"
        )

        self.storage = Storage(self.storage_path)

        self.ticket = Ticket(
            title="Broken classroom projector",
            description="The projector in Room 12 is not working.",
            category="technical",
            priority="high",
        )

    def tearDown(self):
        """Remove temporary files after each test."""

        self.temp_directory.cleanup()

    def test_storage_starts_empty(self):
        """New storage should contain no tickets."""

        self.assertEqual(self.storage.count_tickets(), 0)
        self.assertEqual(self.storage.list_tickets(), [])

    def test_add_ticket(self):
        """A valid ticket should be saved successfully."""

        saved_ticket = self.storage.add_ticket(self.ticket)

        self.assertEqual(saved_ticket.ticket_id, self.ticket.ticket_id)
        self.assertEqual(self.storage.count_tickets(), 1)

    def test_add_non_ticket_is_rejected(self):
        """Only Ticket objects should be accepted."""

        with self.assertRaises(TypeError):
            self.storage.add_ticket({"title": "Invalid ticket"})

    def test_add_duplicate_ticket_is_rejected(self):
        """Duplicate ticket IDs should not be accepted."""

        self.storage.add_ticket(self.ticket)

        duplicate = Ticket(
            title="Another issue",
            description="Another description.",
            ticket_id=self.ticket.ticket_id,
        )

        with self.assertRaises(DuplicateTicketError):
            self.storage.add_ticket(duplicate)

        self.assertEqual(self.storage.count_tickets(), 1)

    def test_get_ticket(self):
        """A saved ticket should be retrievable by its ID."""

        self.storage.add_ticket(self.ticket)

        retrieved = self.storage.get_ticket(self.ticket.ticket_id)

        self.assertEqual(retrieved.ticket_id, self.ticket.ticket_id)
        self.assertEqual(retrieved.title, self.ticket.title)

    def test_get_missing_ticket_raises_error(self):
        """Retrieving a nonexistent ticket should raise an error."""

        with self.assertRaises(TicketNotFoundError):
            self.storage.get_ticket("missing-ticket-id")

    def test_list_tickets(self):
        """All saved tickets should be returned."""

        second_ticket = Ticket(
            title="Library access problem",
            description="My student card cannot open the library.",
            category="administration",
            priority="medium",
        )

        self.storage.add_ticket(self.ticket)
        self.storage.add_ticket(second_ticket)

        tickets = self.storage.list_tickets()

        self.assertEqual(len(tickets), 2)

    def test_filter_tickets_by_status(self):
        """Tickets should be filterable by status."""

        self.storage.add_ticket(self.ticket)

        self.storage.update_ticket(
            self.ticket.ticket_id,
            status="resolved",
        )

        self.storage.add_ticket(
            Ticket(
                title="New network issue",
                description="The campus network is unavailable.",
                category="technical",
                priority="high",
            )
        )

        open_tickets = self.storage.list_tickets(status="open")
        resolved_tickets = self.storage.list_tickets(status="resolved")

        self.assertEqual(len(open_tickets), 1)
        self.assertEqual(len(resolved_tickets), 1)

    def test_filter_tickets_by_category(self):
        """Tickets should be filterable by category."""

        self.storage.add_ticket(self.ticket)

        self.storage.add_ticket(
            Ticket(
                title="Broken desk",
                description="A desk in the classroom is damaged.",
                category="maintenance",
            )
        )

        results = self.storage.list_tickets(category="technical")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].category, "technical")

    def test_filter_tickets_by_priority(self):
        """Tickets should be filterable by priority."""

        self.storage.add_ticket(self.ticket)

        self.storage.add_ticket(
            Ticket(
                title="Minor issue",
                description="A small issue requiring attention.",
                priority="low",
            )
        )

        results = self.storage.list_tickets(priority="high")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].priority, "high")

    def test_combined_filters(self):
        """Multiple filters should work together."""

        self.storage.add_ticket(self.ticket)

        self.storage.add_ticket(
            Ticket(
                title="Another technical issue",
                description="A separate technical problem.",
                category="technical",
                priority="low",
            )
        )

        results = self.storage.list_tickets(
            category="technical",
            priority="high",
            status="open",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].ticket_id, self.ticket.ticket_id)

    def test_update_ticket(self):
        """Ticket changes should be saved."""

        self.storage.add_ticket(self.ticket)

        updated = self.storage.update_ticket(
            self.ticket.ticket_id,
            title="Fixed classroom projector",
            status="resolved",
        )

        self.assertEqual(updated.title, "Fixed classroom projector")
        self.assertEqual(updated.status, "resolved")

        retrieved = self.storage.get_ticket(self.ticket.ticket_id)

        self.assertEqual(retrieved.title, "Fixed classroom projector")
        self.assertEqual(retrieved.status, "resolved")

    def test_update_missing_ticket_raises_error(self):
        """Updating a nonexistent ticket should fail."""

        with self.assertRaises(TicketNotFoundError):
            self.storage.update_ticket(
                "missing-ticket-id",
                status="resolved",
            )

    def test_invalid_update_is_not_saved(self):
        """Invalid changes should leave the saved ticket unchanged."""

        self.storage.add_ticket(self.ticket)

        with self.assertRaises(ValueError):
            self.storage.update_ticket(
                self.ticket.ticket_id,
                priority="invalid_priority",
            )

        retrieved = self.storage.get_ticket(self.ticket.ticket_id)

        self.assertEqual(retrieved.priority, "high")

    def test_delete_ticket(self):
        """A ticket should be removable from storage."""

        self.storage.add_ticket(self.ticket)

        result = self.storage.delete_ticket(self.ticket.ticket_id)

        self.assertTrue(result)
        self.assertEqual(self.storage.count_tickets(), 0)

        with self.assertRaises(TicketNotFoundError):
            self.storage.get_ticket(self.ticket.ticket_id)

    def test_delete_missing_ticket_raises_error(self):
        """Deleting a nonexistent ticket should fail."""

        with self.assertRaises(TicketNotFoundError):
            self.storage.delete_ticket("missing-ticket-id")

    def test_data_persists_after_reopening_storage(self):
        """Saved tickets should remain available after reopening."""

        self.storage.add_ticket(self.ticket)

        new_storage = Storage(self.storage_path)

        retrieved = new_storage.get_ticket(self.ticket.ticket_id)

        self.assertEqual(retrieved.title, self.ticket.title)
        self.assertEqual(retrieved.category, self.ticket.category)

    def test_storage_file_contains_valid_json(self):
        """The storage file should contain readable JSON."""

        self.storage.add_ticket(self.ticket)

        with self.storage_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], self.ticket.title)

    def test_clear_storage(self):
        """Clearing storage should remove all saved tickets."""

        self.storage.add_ticket(self.ticket)
        self.storage.clear()

        self.assertEqual(self.storage.count_tickets(), 0)
        self.assertEqual(self.storage.list_tickets(), [])

        reopened_storage = Storage(self.storage_path)

        self.assertEqual(reopened_storage.count_tickets(), 0)

    def test_invalid_json_raises_storage_error(self):
        """Corrupted JSON should produce a clear storage error."""

        self.storage_path.write_text(
            "{invalid json",
            encoding="utf-8",
        )

        with self.assertRaises(StorageError):
            Storage(self.storage_path)

    def test_invalid_filter_is_rejected(self):
        """Unsupported status filters should raise ValueError."""

        with self.assertRaises(ValueError):
            self.storage.list_tickets(status="unknown_status")


if __name__ == "__main__":
    unittest.main()