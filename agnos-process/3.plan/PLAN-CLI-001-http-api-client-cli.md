# PLAN-CLI-001: Remote booking access

## Overview
Delivers the HTTP adapter of the service, then the transport, the typed client and the command-line tool
in TypeScript, as decided in ADR-CLI-001, and the command that starts the service.

## References
- **Requirements**: RQ-CLI-001, RQ-CLI-002, RQ-CLI-003, RQ-CLI-004, RQ-CLI-005, RQ-CLI-006
- **ADRs**: ADR-CLI-001 (DEC-CLI-001, DEC-CLI-002)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-CLI-001: Implement service HTTP adapter
- **Tier**: M
- **Status**: Done
- **Description**: Add the Python HTTP adapter that serves the three routes, runs the use cases and turns
  domain errors into status and error body.
- **Requirement refs**: RQ-CLI-005
- **ADR refs**: ADR-CLI-001 (DEC-CLI-001)
- **Acceptance Criteria** (Gherkin):
  - **Given** the adapter wired to the use cases
  - **When** `GET /rooms`, `POST /reservations` and `DELETE /reservations/{id}` are called
  - **Then** they answer 200, 201 and 204
  - **And** a conflict answers 409 with code CONFLICT
- **Dependencies**: TASK-BKG-005, TASK-BKG-008
- **Assignee**: AI
- **Verification**: `python -m unittest tests.test_api` (in `service/`): Ran 19 tests, OK.
- **Assumptions**: Dates travel as ISO 8601 text with a UTC offset.

### TASK-CLI-002: Implement client transport layer
- **Tier**: M
- **Status**: Done
- **Description**: Create the TypeScript project, the HTTP transport with a timeout, and the network error
  and service error classes.
- **Requirement refs**: RQ-CLI-004, RQ-CLI-002
- **ADR refs**: ADR-CLI-001 (DEC-CLI-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** a server that never answers
  - **When** a call is made through the transport
  - **Then** it is aborted after the timeout and a network error is thrown
- **Dependencies**: None
- **Assignee**: AI
- **Verification**: `node --test tests/transport.test.ts` (in `client/`): 7 passed, 0 failed.
- **Assumptions**: Node 18 or later, using its built-in `fetch`.

### TASK-CLI-003: Implement typed client
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the response types and the client with its three functions, turning error bodies into
  service errors.
- **Requirement refs**: RQ-CLI-001, RQ-CLI-002
- **ADR refs**: ADR-CLI-001 (DEC-CLI-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** a fake transport answering 409 with code CONFLICT
  - **When** a reservation is created
  - **Then** a service error with code CONFLICT and status 409 is thrown
  - **And** successful calls return typed results
- **Dependencies**: TASK-CLI-002, TASK-CLI-001
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: None

### TASK-CLI-004: Implement command-line tool
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the `rooms`, `book` and `cancel` commands on top of the client, with exit codes.
- **Requirement refs**: RQ-CLI-003
- **ADR refs**: ADR-CLI-001 (DEC-CLI-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** a client that accepts the request
  - **When** `book` is run
  - **Then** the reservation identifier is printed and the exit code is 0
  - **And** a rejected request prints the error code and exits with a non-zero code
- **Dependencies**: TASK-CLI-003
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: Arguments are positional, no option parsing library.

### TASK-CLI-005: Correct usage text
- **Tier**: S
- **Status**: Not Started
- **Description**: Correct the program name in the usage text.
- **Requirement refs**: RQ-CLI-003
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** the command-line constants
  - **When** the usage text is read
  - **Then** it names the program `roombook`
- **Dependencies**: TASK-CLI-004
- **Assignee**: Human
- **Verification**: Pending.
- **Assumptions**: None

### TASK-CLI-006: Implement service start command
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the service's entry point, which loads the rooms file, wires the use cases to the HTTP
  adapter and serves it, and the rooms file of the office.
- **Requirement refs**: RQ-CLI-006, RQ-CLI-005
- **ADR refs**: ADR-CLI-001 (DEC-CLI-001)
- **Acceptance Criteria** (Gherkin):
  - **Given** a rooms file holding two rooms
  - **When** the service is built from it
  - **Then** `GET /rooms` answers the two rooms
  - **And** the entry point serves on 127.0.0.1, port 8080
- **Dependencies**: TASK-CLI-001
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: No reminder is scheduled by the entry point: reminders need a mail adapter, not yet chosen.
