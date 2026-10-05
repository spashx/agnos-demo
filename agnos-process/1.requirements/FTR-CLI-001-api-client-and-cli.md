# FTR-CLI-001: Remote booking access

## Overview
People and scripts use Roombook from outside the service. The service exposes its operations over HTTP/JSON,
and a TypeScript client and a command-line tool built on it make them easy to call.

## Stakeholders
- **Owner**: Product owner of Roombook
- **Consumers**: Developers integrating Roombook, office staff using the command line

---

## Functional Requirements

### RQ-CLI-001: Typed client operations
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The client SHALL provide typed functions to list rooms, create a reservation and cancel a
  reservation.
- **Rationale**: Typed calls catch mistakes before the service is reached.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a client pointed at a service
  - **When** the three functions are called with valid arguments
  - **Then** each returns the typed result of the corresponding HTTP call
- **Dependencies**: RQ-CLI-005

### RQ-CLI-002: Typed service errors
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the service answers with an error status, the client SHALL throw a service error
  carrying the error code, the message and the HTTP status.
- **Rationale**: Callers must tell a conflict from a capacity error without parsing text.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a service answering 409 with code CONFLICT
  - **When** a reservation is created
  - **Then** a service error with code CONFLICT and status 409 is thrown
- **Dependencies**: RQ-CLI-001

### RQ-CLI-003: Command-line booking
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The command-line tool SHALL provide the commands `rooms`, `book` and `cancel`, and SHALL
  exit with code 0 on success and a non-zero code on error.
- **Rationale**: Scripts rely on exit codes.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a service that accepts the request
  - **When** `book` is run
  - **Then** the reservation identifier is printed and the exit code is 0
  - **And** a rejected request prints the error code and exits with a non-zero code
- **Dependencies**: RQ-CLI-001, RQ-CLI-002

### RQ-CLI-004: Unreachable service report
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the service does not answer within 10 seconds, THEN the client SHALL abort the call and
  throw a network error.
- **Rationale**: A command must not hang.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a service that never answers
  - **When** any client function is called
  - **Then** the call is aborted after the timeout and a network error is thrown
- **Dependencies**: RQ-CLI-001

### RQ-CLI-005: Service access over HTTP
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The booking service SHALL expose room listing, reservation creation and reservation
  cancellation over HTTP with JSON bodies, and SHALL answer errors with a status and a body carrying a code
  and a message.
- **Rationale**: Clients in other languages need a stable contract.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the running service
  - **When** `GET /rooms`, `POST /reservations` and `DELETE /reservations/{id}` are called
  - **Then** they answer 200, 201 and 204, and a conflict answers 409 with code CONFLICT
- **Dependencies**: RQ-BKG-002, RQ-BKG-003, RQ-BKG-005

### RQ-CLI-006: Service start command
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN `python -m roombook` is run in `service/`, the booking service SHALL load the rooms of
  `rooms.json`, choose its reservation storage from the configuration, and answer HTTP on 127.0.0.1, port 8080.
- **Rationale**: The client, the command-line tool and the web interface need a running service to call.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a rooms file holding two rooms
  - **When** the service is started
  - **Then** `GET /rooms` answers the two rooms
  - **And** the service listens on 127.0.0.1, port 8080
- **Dependencies**: RQ-CLI-005, RQ-BKG-001, RQ-BKG-007

---

## Non-Functional Requirements

None in this feature.
