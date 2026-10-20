# PLAN-WEB-001: Booking web interface

## Overview
Delivers the views and labels of the booking page, the application logic on top of the typed client, and the
HTTP server that serves the page and the generated stylesheet, as decided in ADR-WEB-001 on top of the design
system of ADR-DSN-001.

## References
- **Requirements**: RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-005, RQ-WEB-006, RQ-DSN-003, RQ-DSN-005
- **ADRs**: ADR-WEB-001 (DEC-WEB-001, DEC-WEB-002), ADR-DSN-001 (DEC-DSN-002)

This plan implements the tasks in the format specified below.
---

## Tasks

### TASK-WEB-001: Implement page views
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the wording of the interface in one module, the routes and form field names, and the view
  functions that render the rooms table, the booking and cancel forms, the banners and the page, using only the
  class names of the design system.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-006, RQ-DSN-003, RQ-DSN-005
- **ADR refs**: ADR-WEB-001 (DEC-WEB-001), ADR-DSN-001 (DEC-DSN-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** an open room and a closed room
  - **When** the page is rendered
  - **Then** each room shows its status in words and a symbol, and the page links the generated stylesheet
  - **And** every input and select of the forms has a label bound to it
  - **And** service data containing markup is escaped
- **Dependencies**: TASK-DSN-002
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: The status symbols are the Unicode check mark and cross, as section 2.5 of FTR-DSN-001 decides.

### TASK-WEB-002: Implement booking application
- **Tier**: M
- **Status**: Not Started
- **Description**: Add the application that routes a request to the page, the booking or the cancellation
  through the typed client, words each service error code, keeps the typed values after a refusal and shows
  the unavailable page when the service does not answer.
- **Requirement refs**: RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-005
- **ADR refs**: ADR-WEB-001 (DEC-WEB-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** a service answering 409 with code CONFLICT
  - **When** the booking form is submitted
  - **Then** the error banner words the conflict and the typed values are kept
  - **And** a service that does not answer gives a 503 page without forms
- **Dependencies**: TASK-WEB-001, TASK-CLI-003
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: Local times typed in the form are booked in UTC (+00:00) until time zones are required.

### TASK-WEB-003: Implement web server
- **Tier**: L
- **Status**: Not Started
- **Description**: Add the Node HTTP server that translates requests to the application, serves the page and the
  stylesheet generated from the tokens, limits the size of a posted body, and starts when the file is run.
- **Requirement refs**: RQ-WEB-001, RQ-WEB-002, RQ-DSN-003
- **ADR refs**: ADR-WEB-001 (DEC-WEB-001), ADR-DSN-001 (DEC-DSN-002)
- **Acceptance Criteria** (Gherkin):
  - **Given** a started server over a fake service
  - **When** the home page, the stylesheet and a booking form are requested
  - **Then** they answer 200, with the stylesheet exposing the tokens as custom properties
  - **And** a body larger than the limit answers 413
- **Dependencies**: TASK-WEB-002, TASK-DSN-002
- **Assignee**: AI
- **Verification**: Pending.
- **Assumptions**: The server listens on 127.0.0.1, port 3000 unless `ROOMBOOK_UI_PORT` is set.

### TASK-WEB-004: Correct booking button wording
- **Tier**: S
- **Status**: Not Started
- **Description**: After the UX review, rename the booking button from Submit to Book this room.
- **Requirement refs**: RQ-WEB-002
- **ADR refs**: None
- **Acceptance Criteria** (Gherkin):
  - **Given** the booking form
  - **When** it is rendered
  - **Then** its button reads Book this room
- **Dependencies**: TASK-WEB-001
- **Assignee**: Human
- **Verification**: Pending.
- **Assumptions**: None
