"""Simple list-based storage for the CampusFlow CLI."""
import json
from pathlib import Path

DATA_FILE = Path("tickets.json")


def load_tickets():
    """Load tickets from JSON file. Returns empty list if file doesn't exist."""
    if not DATA_FILE.exists():
        return []
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_tickets(tickets):
    """Save tickets list to JSON file."""
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=4)
        f.write("\n")