# FTR-BKG-002: Reservation persistence

## Overview
The first demonstration of Roombook lost every reservation when the service restarted. This feature makes
reservations durable.

## Stakeholders
- **Owner**: Product owner of Roombook
- **Consumers**: Office staff, operations

---

## Functional Requirements

None in this feature; the behavior of reservations is defined by FTR-BKG-001.

---

## Non-Functional Requirements

### RQ-BKG-007: Reservation retention across restarts
- **Category**: Non-Functional
- **NFR Type**: Reliability
- **EARS Type**: Ubiquitous
- **Statement**: The booking service SHALL keep every Confirmed and Cancelled reservation across a restart
  and SHALL never leave a partially written data file.
- **Metric**: 100% of reservations present after a restart; 0 partially written file after an interrupted
  save.
- **Measurement Method**: Automated test that saves, reopens the repository and compares; automated test
  that interrupts a save before its final rename.
- **Priority**: Must
- **Acceptance Criteria** (Gherkin):
  - **Given** a service with 3 Confirmed and 1 Cancelled reservations
  - **When** it is restarted
  - **Then** the same 4 reservations are returned
  - **And** an interrupted save leaves the previous data file intact
- **Dependencies**: RQ-BKG-002, RQ-BKG-005
