### Engineer A — Creation, validation, priority, storage
# campus_flow

---

## 6. File: `Campusflow/Readme`

This is the project's main documentation file. It explains what CampusFlow does, how to install or run it, how to use the code, and how to execute the tests.

Copy this into the file named `Readme` (without adding a `.txt` extension):

```markdown
# CampusFlow — Engineer A

## 1. Project Overview

CampusFlow is a campus-related software project.

This part of the project implements the ticket management and
storage components.

It provides functionality for creating tickets, validating ticket
information, storing tickets, retrieving tickets, updating tickets,
and deleting tickets.

The implementation is written in Python and uses JSON files
for persistent storage.

## 2. Features

The current implementation supports:

- Creating tickets.
- Generating unique ticket IDs.
- Validating ticket information.
- Assigning ticket categories.
- Assigning ticket priorities.
- Tracking ticket status.
- Recording creation and update timestamps.
- Saving tickets to a JSON file.
- Loading saved tickets.
- Retrieving tickets by ID.
- Listing all tickets.
- Filtering tickets by status, category, and priority.
- Updating tickets.
- Deleting tickets.
- Clearing stored tickets.
- Automated unit testing.

## 3. Project Structure

### Engineer B — Assignment, workflow, queue, reports

- **F3 — Assign**: assigns a ticket to a non-empty staff member name; rejects
  unknown ticket IDs and blank/whitespace-only names.
- **F4 — Workflow**: enforces the state machine `open → in_progress → resolved`.
  - An **unassigned** ticket cannot move to `in_progress`.
  - `open → resolved` (skipping `in_progress`) is rejected.
  - A `resolved` ticket can only be modified after an explicit **reopen**
    (`resolved → open`).
- **F5 — Work queue**: lists open, unresolved tickets ordered
  `critical → high → medium → low`, with ties broken by the **numeric** ticket
  ID (so `T002` comes before `T010`).
- **F6 — Reports**: total ticket count plus breakdowns by status and priority.
  Handles zero tickets correctly.
- **CLI menu**: wires all seven features into a looping menu with friendly
  `✔` / `✘` feedback and a top-level error guard so one bug cannot crash the app.

### Shared

- **F2 — List / view**: list all tickets and display the full details of one.

---

## Requirements

- Python 3.10 or newer (developed on 3.12)
- No third-party packages — standard library only (`json`, `unittest`)

---

## Setup

Clone the repository:

```bash
git clone <repository-url>
cd campus_flow


```text
Campusflow/
│
├── Tickets.py
├── Storage.py
│
├── tests/
│   ├── test_Tickets.py
│   └── test_Storage.py
│
├── doc/
│   └── design-decisions.md
│
└── Readme