# FTR-BKG-001: Room reservation

## Overview
Roombook lets people book meeting rooms. This feature covers the core of the booking service: the catalog
of rooms, the creation and cancellation of reservations, and the rules that keep a reservation valid
(no double booking, capacity, closed rooms).

## Stakeholders
- **Owner**: Product owner of Roombook
- **Consumers**: The future HTTP API and reminder features, office staff

---

## Functional Requirements

### RQ-BKG-001: Room catalog listing
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The booking service SHALL keep a catalog of rooms, each with an identifier, a name, a
  capacity (integer, at least 1) and an open flag.
- **Rationale**: Reservations are made against known rooms.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** two rooms added to the catalog
  - **When** the catalog is listed
  - **Then** each room is returned with its identifier, name, capacity and open flag
- **Dependencies**: None

### RQ-BKG-002: Reservation creation
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a user requests a reservation of a room with an organizer, a start, an end and an
  attendee count, the booking service SHALL create a Confirmed reservation and return its identifier.
- **Rationale**: Creating reservations is the purpose of the product.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** an open room with no reservation
  - **When** a valid reservation is requested
  - **Then** a Confirmed reservation is stored and its identifier is returned
- **Dependencies**: RQ-BKG-001

### RQ-BKG-003: Double booking rejection
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the requested interval overlaps a Confirmed reservation of the same room, THEN the
  booking service SHALL reject the request with a conflict error that names the existing reservation;
  an interval that starts exactly when another ends SHALL NOT be a conflict.
- **Rationale**: A room cannot host two meetings at the same time.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a Confirmed reservation from 10:00 to 11:00
  - **When** a reservation from 10:30 to 11:30 is requested for the same room
  - **Then** a conflict error naming the first reservation is raised
  - **And** a reservation from 11:00 to 12:00 is accepted
- **Dependencies**: RQ-BKG-002

### RQ-BKG-004: Room capacity check
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the attendee count is greater than the capacity of the room, THEN the booking service
  SHALL reject the request with a capacity error.
- **Rationale**: A meeting must fit in the room.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a room of capacity 6
  - **When** a reservation for 7 attendees is requested
  - **Then** a capacity error is raised
  - **And** a reservation for 6 attendees is accepted
- **Dependencies**: RQ-BKG-002

### RQ-BKG-005: Reservation cancellation
- **Category**: Functional
- **EARS Type**: Complex
- **Statement**: WHEN a user cancels a Confirmed reservation, the booking service SHALL mark it Cancelled
  so that its interval can be booked again; IF the reservation has already started, THEN the service SHALL
  reject the cancellation with an already-started error.
- **Rationale**: Plans change, and a released room can be used by others.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a Confirmed reservation that has not started
  - **When** it is cancelled
  - **Then** its status is Cancelled and the same interval can be booked again
  - **And** cancelling a reservation that has started raises an already-started error
- **Dependencies**: RQ-BKG-002

### RQ-BKG-006: Closed room rejection
- **Category**: Functional
- **EARS Type**: State-driven
- **Statement**: WHILE a room is flagged closed, the booking service SHALL reject new reservations for it
  with a room-closed error.
- **Rationale**: Rooms under maintenance cannot be used.
- **Priority**: Should
- **Acceptance Criteria** (Gherkin):
  - **Given** a room flagged closed
  - **When** a reservation is requested for it
  - **Then** a room-closed error is raised
- **Dependencies**: RQ-BKG-002

---

## Non-Functional Requirements

None in this feature.
