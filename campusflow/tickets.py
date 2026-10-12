"""
CampusFlow - Ticket Management

This module defines the Ticket model and provides validation
for tickets created within the CampusFlow application.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4



# Allowed ticket categories
VALID_CATEGORIES = {
    "maintenance",
    "academic",
    "technical",
    "security",
    "administration",
    "other",
}

# Allowed ticket priorities
VALID_PRIORITIES = {
    "low",
    "medium",
    "high",
    "urgent",
}

# Allowed ticket statuses
VALID_STATUSES = {
    "open",
    "in_progress",
    "resolved",
    "closed",
}


def current_timestamp() -> str:
    """Return the current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Ticket:
    """
    Represents a ticket submitted by a campus community member.

    Attributes:
        title: Short description of the issue.
        description: Detailed explanation of the issue.
        category: Type of issue being reported.
        priority: Importance of the ticket.
        ticket_id: Unique identifier for the ticket.
        status: Current state of the ticket.
        created_at: Time when the ticket was created.
        updated_at: Time when the ticket was last updated.
    """

    title: str
    description: str
    category: str = "other"
    priority: str = "medium"

    ticket_id: str = field(default_factory=lambda: str(uuid4()))
    status: str = "open"
    created_at: str = field(default_factory=current_timestamp)
    updated_at: str = field(default_factory=current_timestamp)

    def __post_init__(self) -> None:
        """Validate ticket data after initialization."""
        self.validate()

    def validate(self) -> None:
        """Raise ValueError if any ticket field is invalid."""

        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Ticket title cannot be empty.")

        if len(self.title.strip()) > 200:
            raise ValueError(
                "Ticket title cannot exceed 200 characters."
            )

        if not isinstance(self.description, str):
            raise ValueError("Ticket description must be a string.")

        if not self.description.strip():
            raise ValueError("Ticket description cannot be empty.")

        if len(self.description.strip()) > 5000:
            raise ValueError(
                "Ticket description cannot exceed 5000 characters."
            )

        if not isinstance(self.category, str):
            raise ValueError("Ticket category must be a string.")

        if self.category.strip().lower() not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category. Choose one of: "
                f"{', '.join(sorted(VALID_CATEGORIES))}."
            )

        if not isinstance(self.priority, str):
            raise ValueError("Ticket priority must be a string.")

        if self.priority.strip().lower() not in VALID_PRIORITIES:
            raise ValueError(
                f"Invalid priority. Choose one of: "
                f"{', '.join(sorted(VALID_PRIORITIES))}."
            )

        if not isinstance(self.status, str):
            raise ValueError("Ticket status must be a string.")

        if self.status.strip().lower() not in VALID_STATUSES:
            raise ValueError(
                f"Invalid status. Choose one of: "
                f"{', '.join(sorted(VALID_STATUSES))}."
            )

        if not isinstance(self.ticket_id, str) or not self.ticket_id.strip():
            raise ValueError("Ticket ID cannot be empty.")

        for field_name in ("created_at", "updated_at"):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        # Store normalized values consistently.
        self.title = self.title.strip()
        self.description = self.description.strip()
        self.category = self.category.strip().lower()
        self.priority = self.priority.strip().lower()
        self.status = self.status.strip().lower()
        self.ticket_id = self.ticket_id.strip()

    def update(self, **changes: Any) -> None:
        """
        Update editable ticket fields.

        Editable fields:
            title, description, category, priority, status.

        The update is validated before it is applied. If validation
        fails, the original ticket remains unchanged.
        """

        allowed_fields = {
            "title",
            "description",
            "category",
            "priority",
            "status",
        }

        unknown_fields = set(changes) - allowed_fields

        if unknown_fields:
            raise ValueError(
                f"Fields cannot be updated: "
                f"{', '.join(sorted(unknown_fields))}."
            )

        if not changes:
            return

        candidate = {
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
        }

        candidate.update(changes)

        # Validate a temporary ticket before changing this instance.
        Ticket(
            title=candidate["title"],
            description=candidate["description"],
            category=candidate["category"],
            priority=candidate["priority"],
            ticket_id=self.ticket_id,
            status=candidate["status"],
            created_at=self.created_at,
            updated_at=current_timestamp(),
        )

        # All fields are valid; apply the changes.
        for name, value in changes.items():
            setattr(self, name, value.strip().lower()
                    if name in {"category", "priority", "status"}
                    and isinstance(value, str)
                    else value.strip()
                    if name in {"title", "description"}
                    and isinstance(value, str)
                    else value)

        self.updated_at = current_timestamp()

    def to_dict(self) -> dict[str, Any]:
        """Convert the ticket into a dictionary."""
        return {
            "ticket_id": self.ticket_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ticket":
        """Create a Ticket instance from a dictionary."""

        if not isinstance(data, dict):
            raise ValueError("Ticket data must be a dictionary.")

        required_fields = {
            "ticket_id",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "created_at",
            "updated_at",
        }

        missing_fields = required_fields - data.keys()

        if missing_fields:
            raise ValueError(
                f"Missing ticket fields: "
                f"{', '.join(sorted(missing_fields))}."
            )

        return cls(
            ticket_id=data["ticket_id"],
            title=data["title"],
            description=data["description"],
            category=data["category"],
            priority=data["priority"],
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )

    def __str__(self) -> str:
        """Return a readable summary of the ticket."""
        return (
            f"Ticket(id={self.ticket_id}, "
            f"title={self.title!r}, "
            f"status={self.status!r}, "
            f"priority={self.priority!r})"
        )

"""Engineer A — Create and List tickets (F1 + F2)."""

VALID_PRIORITIES = ["low", "medium", "high", "critical"]
VALID_CATEGORIES = ["technical", "maintenance", "academic", "security", "administration", "other"]


def _next_id(tickets):
    """Generate the next ticket ID like T001, T002 etc."""
    if not tickets:
        return "T001"
    nums = []
    for t in tickets:
        try:
            nums.append(int(t["id"].lstrip("T")))
        except ValueError:
            pass
    return f"T{max(nums) + 1:03d}"


def create_ticket(tickets):
    """F1 — Create a new ticket interactively."""
    print("\n────── Create Ticket ──────")

    # Title
    title = input("Title: ").strip()
    if not title:
        print("✘ Title cannot be empty.")
        return

    # Category
    print(f"Categories: {' | '.join(VALID_CATEGORIES)}")
    category = input("Category: ").strip().lower()
    if category not in VALID_CATEGORIES:
        print(f"✘ Invalid category: '{category}'")
        return

    # Priority
    print(f"Priorities: {' | '.join(VALID_PRIORITIES)}")
    priority = input("Priority: ").strip().lower()
    if priority not in VALID_PRIORITIES:
        print(f"✘ Invalid priority: '{priority}'")
        return

    # Build the ticket
    ticket = {
        "id": _next_id(tickets),
        "title": title,
        "category": category,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    tickets.append(ticket)
    print(f"✔ Ticket {ticket['id']} created successfully!")


def list_tickets(tickets):
    """F2 — List all tickets."""
    print("\n────── All Tickets ──────")
    if not tickets:
        print("  No tickets found.")
        return
    print(f"  {'ID':<8}{'PRIORITY':<12}{'STATUS':<14}{'ASSIGNED':<14}{'TITLE'}")
    print(f"  {'─'*8}{'─'*12}{'─'*14}{'─'*14}{'─'*20}")
    for t in tickets:
        assigned = t.get("assigned_to") or "—"
        print(f"  {t['id']:<8}{t['priority']:<12}{t['status']:<14}{assigned:<14}{t['title']}")
    print(f"\n  Total: {len(tickets)} ticket(s)")