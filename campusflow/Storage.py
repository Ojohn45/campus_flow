"""
CampusFlow - Ticket Storage

This module provides JSON-based persistence for CampusFlow tickets.

It supports creating, retrieving, listing, updating, and deleting
tickets while keeping stored data between application runs.
"""

import json
import os
import tempfile
from pathlib import Path
from threading import RLock
from typing import Any

try:
    from .Tickets import Ticket, VALID_STATUSES
except ImportError:
    from Tickets import Ticket, VALID_STATUSES


class StorageError(Exception):
    """Base exception for ticket storage errors."""


class TicketNotFoundError(StorageError):
    """Raised when a requested ticket does not exist."""


class DuplicateTicketError(StorageError):
    """Raised when a ticket ID already exists."""


class Storage:
    """
    Store and manage CampusFlow tickets in a JSON file.

    Args:
        file_path: Location of the JSON file used for persistence.

    Example:
        storage = Storage("tickets.json")

        ticket = Ticket(
            title="Broken classroom projector",
            description="The projector in Room 12 is not working.",
            category="technical",
            priority="high",
        )

        storage.add_ticket(ticket)
    """

    def __init__(
        self,
        file_path: str | Path = "tickets.json",
    ) -> None:
        self.file_path = Path(file_path)
        self._lock = RLock()

        # Load existing data or initialize an empty store.
        self._tickets: dict[str, Ticket] = self._load_tickets()

    def _load_tickets(self) -> dict[str, Ticket]:
        """Load and validate tickets from the JSON file."""

        if not self.file_path.exists():
            return {}

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

        except json.JSONDecodeError as exc:
            raise StorageError(
                f"Invalid JSON in storage file: {self.file_path}"
            ) from exc

        except OSError as exc:
            raise StorageError(
                f"Could not read storage file: {self.file_path}"
            ) from exc

        if not isinstance(data, list):
            raise StorageError(
                "Storage file must contain a JSON list of tickets."
            )

        tickets: dict[str, Ticket] = {}

        try:
            for item in data:
                ticket = Ticket.from_dict(item)

                if ticket.ticket_id in tickets:
                    raise StorageError(
                        f"Duplicate ticket ID in storage: "
                        f"{ticket.ticket_id}"
                    )

                tickets[ticket.ticket_id] = ticket

        except (ValueError, TypeError, KeyError) as exc:
            raise StorageError(
                f"Invalid ticket data in storage file: {exc}"
            ) from exc

        return tickets

    def _save_tickets(self) -> None:
        """
        Persist tickets using an atomic file replacement.

        A temporary file is written first. The final file is replaced
        only after the temporary file has been written successfully.
        """

        parent = self.file_path.parent
        temporary_path = None

        try:
            parent.mkdir(parents=True, exist_ok=True)

            data = [
                ticket.to_dict()
                for ticket in self._tickets.values()
            ]

            file_descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{self.file_path.name}.",
                suffix=".tmp",
                dir=str(parent),
            )

            temporary_path = Path(temporary_name)

            with os.fdopen(
                file_descriptor,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())

            os.replace(temporary_path, self.file_path)

        except (OSError, TypeError, ValueError) as exc:
            raise StorageError(
                f"Could not save tickets to {self.file_path}: {exc}"
            ) from exc

        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def add_ticket(self, ticket: Ticket) -> Ticket:
        """
        Add a new ticket to storage.

        Returns:
            The saved ticket.

        Raises:
            TypeError: If the argument is not a Ticket.
            DuplicateTicketError: If its ID already exists.
        """

        if not isinstance(ticket, Ticket):
            raise TypeError("Only Ticket objects can be stored.")

        with self._lock:
            if ticket.ticket_id in self._tickets:
                raise DuplicateTicketError(
                    f"Ticket {ticket.ticket_id} already exists."
                )

            self._tickets[ticket.ticket_id] = ticket

            try:
                self._save_tickets()
            except StorageError:
                del self._tickets[ticket.ticket_id]
                raise

            return ticket

    def get_ticket(self, ticket_id: str) -> Ticket:
        """
        Retrieve a ticket by its unique ID.

        Raises:
            TicketNotFoundError: If the ticket does not exist.
        """

        with self._lock:
            try:
                return self._tickets[ticket_id]
            except KeyError as exc:
                raise TicketNotFoundError(
                    f"Ticket {ticket_id!r} was not found."
                ) from exc

    def list_tickets(
        self,
        status: str | None = None,
        category: str | None = None,
        priority: str | None = None,
    ) -> list[Ticket]:
        """
        Return tickets, optionally filtered by status, category,
        and priority.

        Filters can be combined.

        Example:
            storage.list_tickets(status="open")
            storage.list_tickets(category="technical")
            storage.list_tickets(
                status="open",
                priority="high",
            )
        """

        if status is not None:
            if not isinstance(status, str):
                raise ValueError("Status must be a string.")

            status = status.strip().lower()

            if status not in VALID_STATUSES:
                raise ValueError(
                    f"Invalid status: {status!r}."
                )

        if category is not None:
            if not isinstance(category, str) or not category.strip():
                raise ValueError("Category must be a non-empty string.")

            category = category.strip().lower()

        if priority is not None:
            if not isinstance(priority, str) or not priority.strip():
                raise ValueError("Priority must be a non-empty string.")

            priority = priority.strip().lower()

        with self._lock:
            result = list(self._tickets.values())

            if status is not None:
                result = [
                    ticket for ticket in result
                    if ticket.status == status
                ]

            if category is not None:
                result = [
                    ticket for ticket in result
                    if ticket.category == category
                ]

            if priority is not None:
                result = [
                    ticket for ticket in result
                    if ticket.priority == priority
                ]

            return sorted(
                result,
                key=lambda ticket: ticket.created_at,
            )

    def update_ticket(
        self,
        ticket_id: str,
        **changes: Any,
    ) -> Ticket:
        """
        Update a ticket and persist the changes.

        Editable fields are title, description, category,
        priority, and status.

        Returns:
            The updated ticket.
        """

        with self._lock:
            ticket = self.get_ticket(ticket_id)

            # Keep a copy so failed persistence can be rolled back.
            original_data = ticket.to_dict()

            ticket.update(**changes)

            try:
                self._save_tickets()

            except StorageError:
                restored = Ticket.from_dict(original_data)
                self._tickets[ticket_id] = restored
                raise

            return ticket

    def delete_ticket(self, ticket_id: str) -> bool:
        """
        Delete a ticket by its ID.

        Returns:
            True when the ticket is deleted.

        Raises:
            TicketNotFoundError: If the ticket does not exist.
        """

        with self._lock:
            ticket = self.get_ticket(ticket_id)

            del self._tickets[ticket_id]

            try:
                self._save_tickets()

            except StorageError:
                self._tickets[ticket_id] = ticket
                raise

            return True

    def count_tickets(self) -> int:
        """Return the total number of stored tickets."""

        with self._lock:
            return len(self._tickets)

    def clear(self) -> None:
        """
        Remove all tickets from storage.

        Use with care: this operation deletes every stored ticket.
        """

        with self._lock:
            original_tickets = self._tickets.copy()
            self._tickets = {}

            try:
                self._save_tickets()

            except StorageError:
                self._tickets = original_tickets
                raise


                