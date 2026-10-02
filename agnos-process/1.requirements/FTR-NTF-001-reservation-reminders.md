# FTR-NTF-001: Reservation reminders

## Overview
Organizers forget their meetings. The booking service publishes an event when a reservation is created and
sends a reminder to the organizer shortly before the meeting starts, without ever failing a reservation
because a notification failed.

## Stakeholders
- **Owner**: Product owner of Roombook
- **Consumers**: Organizers of meetings, the booking service (FTR-BKG-001)

---

## Functional Requirements

### RQ-NTF-001: Creation event publication
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a reservation is created, the booking service SHALL publish a reservation-created
  event carrying the reservation.
- **Rationale**: Other features react to creations without the booking code knowing them.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a subscriber registered on the event bus
  - **When** a reservation is created
  - **Then** the subscriber receives one reservation-created event with that reservation
- **Dependencies**: RQ-BKG-002

### RQ-NTF-002: Reminder dispatch before meetings
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE a reservation is Confirmed, the booking service SHALL send a reminder to its
  organizer 15 minutes before its start.
- **Rationale**: A reminder reduces missed meetings; a cancelled meeting needs none.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a Confirmed reservation starting at 10:00
  - **When** the clock reaches 09:45
  - **Then** one reminder is sent to the organizer
  - **And** a Cancelled reservation never produces a reminder
- **Dependencies**: RQ-NTF-001, RQ-BKG-005

### RQ-NTF-003: Failed notification retry
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF a notification attempt fails, THEN the booking service SHALL retry until 3 attempts have
  been made in total, SHALL log the failure, and SHALL leave the reservation unchanged.
- **Rationale**: A mail server outage must not break bookings.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a notifier that fails every time
  - **When** a reminder is sent
  - **Then** 3 attempts are made and one failure is logged
  - **And** the reservation is unchanged
- **Dependencies**: RQ-NTF-002

---

## Non-Functional Requirements

### RQ-NTF-004: Reminder dispatch speed
- **Category**: Non-Functional
- **NFR Type**: Performance
- **EARS Type**: Ubiquitous
- **Statement**: The booking service SHALL dispatch 1000 due reminders in less than 1 second.
- **Metric**: Dispatch time of 1000 reminders < 1 s at P95 over 20 runs.
- **Measurement Method**: Automated timing test with an in-memory notifier.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** 1000 Confirmed reservations whose reminder is due
  - **When** the scheduler dispatches them
  - **Then** the dispatch takes less than 1 second
- **Dependencies**: RQ-NTF-002
