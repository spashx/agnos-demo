# PLAN-NTF-001: Reservation reminders

## Overview
Delivers the creation event, the reminder scheduler with its notifier port, and retries on failure, as
decided in ADR-NTF-001.

## References
- **Requirements**: RQ-NTF-001, RQ-NTF-002, RQ-NTF-003, RQ-NTF-004
- **ADRs**: ADR-NTF-001 (DEC-NTF-001, DEC-NTF-002)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-NTF-001: Implement reservation event publishing
- **Tier**: M
- **Status**: Done
- **Description**: Add the in-process event bus, the reservation-created event and the decorator that
  publishes it after a successful creation.
- **Requirement refs**: RQ-NTF-001
- **ADR refs**: ADR-NTF-001 (DEC-NTF-001)
- **Acceptance Criteria** (Gherkin):
  - **Given** a subscriber registered on the event bus
  - **When** a reservation is created through the decorated use case
  - **Then** the subscriber receives one event with that reservation
  - **And** a rejected request publishes nothing
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `python -m unittest tests.test_events tests.test_publishing_create` (in `service/`): Ran 7 tests,
  OK.
- **Assumptions**: A subscriber that raises does not stop the other subscribers.

### TASK-NTF-002: Implement reminder scheduling
- **Tier**: L
- **Status**: Done
- **Description**: Add the notifier port with a console notifier and the scheduler that sends one reminder
  per Confirmed reservation when its lead time is reached.
- **Requirement refs**: RQ-NTF-002, RQ-NTF-004
- **ADR refs**: ADR-NTF-001 (DEC-NTF-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** a Confirmed reservation starting at 10:00
  - **When** the clock reaches the start minus the lead time
  - **Then** one reminder is sent to the organizer
  - **And** a Cancelled reservation produces none
  - **And** 1000 due reminders are dispatched in less than 1 second
- **Dependencies**: TASK-NTF-001, TASK-BKG-005
- **Assignee**: AI
- **Verification**: `python -m unittest tests.test_notifier tests.test_reminder_scheduler` (in `service/`):
  Ran 8 tests, OK, including the 1000-reminder dispatch under 1 second.
- **Assumptions**: A reminder is sent once per reservation (the scheduler remembers those sent).

### TASK-NTF-003: Implement retrying notifier
- **Tier**: M
- **Status**: Done
- **Description**: Add the decorator that retries a failing notification up to the maximum number of
  attempts, logs the last failure and never raises.
- **Requirement refs**: RQ-NTF-003
- **ADR refs**: ADR-NTF-001 (DEC-NTF-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** a notifier that fails every time
  - **When** a reminder is sent through the decorator
  - **Then** the maximum number of attempts is made and one failure is logged
  - **And** no error reaches the caller
- **Dependencies**: TASK-NTF-002
- **Assignee**: AI
- **Verification**: `python -m unittest tests.test_retrying_notifier` (in `service/`): Ran 5 tests, OK.
- **Assumptions**: No delay between attempts in this version.

### TASK-NTF-004: Correct reminder lead time
- **Tier**: S
- **Status**: Done
- **Description**: Set the reminder lead time constant to the 15 minutes required.
- **Requirement refs**: RQ-NTF-002
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** the scheduler constants
  - **When** the lead time is read
  - **Then** it is 15 minutes
- **Dependencies**: TASK-NTF-002
- **Assignee**: Human
- **Verification**: N/A (Tier S)
- **Assumptions**: None
