# FTR-WEB-001: Booking web interface

## Overview
Office staff who do not use the command line need to see the rooms and book or cancel a meeting from a
browser. A small web interface, built on the typed client of FTR-CLI-001, lists the rooms, books a room,
cancels a reservation and explains every refusal in plain words. Every colour, size and spacing of its
screens comes from the design system of FTR-DSN-001, never from a literal.

## Stakeholders
- **Owner**: Product owner of Roombook
- **Consumers**: Office staff booking meeting rooms, the UX designer reviewing the screens

---

## Functional Requirements

### RQ-WEB-001: Room overview display
- **Category**: Functional
- **EARS Type**: Ubiquitous
- **Statement**: The web interface SHALL display the rooms known to the booking service with their name,
  capacity and an open or closed status, styled only with design-system tokens.
- **Rationale**: Choosing a room starts with seeing which ones exist and which are closed.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a service with an open room and a closed room
  - **When** the home page is requested
  - **Then** both rooms are listed with name, capacity and status
  - **And** the page links the stylesheet generated from the design-system tokens
- **Dependencies**: RQ-CLI-001, RQ-DSN-001, RQ-DSN-003, RQ-DSN-005, ADR-DSN-001

### RQ-WEB-002: Room booking
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a visitor submits the booking form with a room, an organizer, a start, an end and a
  number of attendees, the web interface SHALL create the reservation through the service and show its
  identifier in a confirmation.
- **Rationale**: The identifier is what a visitor needs later to cancel.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** an open room that is free at the requested time
  - **When** the booking form is submitted with valid values
  - **Then** a confirmation shows the reservation identifier
  - **And** an incomplete form is refused without calling the service
- **Dependencies**: RQ-CLI-001, RQ-BKG-002, RQ-DSN-003

### RQ-WEB-003: Refusal explanation
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN the service refuses a request, the web interface SHALL show an error message worded
  for the error code, in an error banner whose colours come from design-system tokens, and SHALL keep the
  values typed in the form.
- **Rationale**: A visitor must understand a conflict or a capacity error without retyping everything.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a service answering 409 with code CONFLICT
  - **When** the booking form is submitted
  - **Then** an error banner explains that the room is already booked
  - **And** the organizer typed in the form is still in the form
- **Dependencies**: RQ-CLI-002, RQ-DSN-003

### RQ-WEB-004: In-page reservation cancellation
- **Category**: Functional
- **EARS Type**: Event-driven
- **Statement**: WHEN a visitor submits a reservation identifier, or uses the cancel button of a booking
  confirmation, the web interface SHALL cancel the reservation through the service and confirm it.
- **Rationale**: A mistaken booking must be undone in one click.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a reservation that can be cancelled
  - **When** its identifier is submitted in the cancel form
  - **Then** a confirmation names the cancelled reservation
  - **And** an unknown identifier shows the not-found wording
- **Dependencies**: RQ-CLI-001, RQ-BKG-005, RQ-DSN-003

### RQ-WEB-005: Unavailable service notice
- **Category**: Functional
- **EARS Type**: Unwanted-behavior
- **Statement**: IF the booking service does not answer, THEN the web interface SHALL show a warning banner
  that the service is unavailable and SHALL NOT show the forms.
- **Rationale**: A form that cannot succeed only frustrates the visitor.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a service that does not answer
  - **When** the home page is requested
  - **Then** the answer is a 503 page with a warning banner and no form
- **Dependencies**: RQ-CLI-004, RQ-DSN-003

---

## Non-Functional Requirements

### RQ-WEB-006: Accessible control labelling
- **Category**: Non-Functional
- **NFR Type**: Accessibility
- **EARS Type**: Ubiquitous
- **Statement**: The web interface SHALL bind a text label to every form control and SHALL write every
  status in words and a symbol in addition to its colour, so that no meaning relies on colour alone.
- **Metric**: 100% of form controls have a label bound to them; 100% of room statuses contain a word.
- **Measurement Method**: Unit test reading the rendered HTML of the booking and cancel forms and of the table.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** the rendered booking and cancel forms
  - **When** the identifier of each input and select is read
  - **Then** a label points to every one of them
  - **And** the open and closed badges contain the words Open and Closed
- **Dependencies**: RQ-DSN-001, RQ-DSN-004
