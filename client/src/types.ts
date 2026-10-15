// RQ-CLI-001, RQ-CLI-002, DEC-CLI-001 (ADR-CLI-001)

/** RQ-CLI-001: a meeting room as listed by GET /rooms. */
export interface Room {
  readonly id: string;
  readonly name: string;
  readonly capacity: number;
  readonly open: boolean;
}

/** RQ-CLI-001: the body of POST /reservations. */
export interface ReservationRequest {
  readonly roomId: string;
  readonly organizer: string;
  readonly start: string;
  readonly end: string;
  readonly attendees: number;
}

/** RQ-CLI-001: a reservation as answered by POST /reservations. */
export interface Reservation extends ReservationRequest {
  readonly id: string;
  readonly status: string;
}

/** RQ-CLI-002: the error body {code, message} of every error response. */
export interface ErrorBody {
  readonly code: string;
  readonly message: string;
}
