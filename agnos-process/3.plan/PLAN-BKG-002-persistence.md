# PLAN-BKG-002: Durable reservations

## Overview
Replaces the in-memory storage by a JSON file written atomically, selectable by configuration, as decided in
ADR-BKG-003.

## References
- **Requirements**: RQ-BKG-007
- **ADRs**: ADR-BKG-003 (DEC-BKG-004)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-BKG-007: Implement JSON file repository
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the atomic file writer and the file-backed repository implementing the repository
  port, with a dedicated error for a corrupted data file.
- **Requirement refs**: RQ-BKG-007
- **ADR refs**: ADR-BKG-003 (DEC-BKG-004)
- **Acceptance Criteria** (Gherkin):
  - **Given** a repository with 3 Confirmed and 1 Cancelled reservations
  - **When** a new repository is opened on the same file
  - **Then** the same 4 reservations are returned
  - **And** a save interrupted before the rename leaves the previous file intact
  - **And** a corrupted file raises the storage-corrupted error
- **Dependencies**: TASK-BKG-002, TASK-BKG-005
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: Timestamps are stored as ISO 8601 text with their UTC offset.

### TASK-BKG-008: Implement repository factory
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the factory that returns the file repository when the data-file setting is present
  and the in-memory repository otherwise.
- **Requirement refs**: RQ-BKG-007
- **ADR refs**: ADR-BKG-003 (DEC-BKG-004)
- **Acceptance Criteria** (Gherkin):
  - **Given** the data-file setting
  - **When** the factory is called
  - **Then** a file repository on that path is returned
  - **And** without the setting an in-memory repository is returned
- **Dependencies**: TASK-BKG-007
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: The setting is the environment variable `ROOMBOOK_DATA_FILE`.
