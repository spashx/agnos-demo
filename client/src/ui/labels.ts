// RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-005, RQ-WEB-006, DEC-WEB-002 (ADR-WEB-001)

/** RQ-WEB-006: every visible text of the interface, in one place so the wording is reviewed and changed once. */
export const LABEL = {
  pageTitle: "Roombook",
  pageSubtitle: "Meeting-room booking",
  roomsHeading: "Rooms",
  columnName: "Room",
  columnCapacity: "Capacity",
  columnStatus: "Status",
  statusOpen: "✓ Open",
  statusClosed: "✕ Closed",
  closedSuffix: " (closed)",
  noRooms: "No room is available yet.",
  bookHeading: "Book a room",
  fieldRoom: "Room",
  fieldOrganizer: "Organizer",
  fieldStart: "Start",
  fieldEnd: "End",
  fieldAttendees: "Attendees",
  bookButton: "Book this room",
  cancelHeading: "Cancel a reservation",
  fieldReservationId: "Reservation identifier",
  cancelButton: "Cancel reservation",
  cancelThisButton: "Cancel this reservation",
  notFoundText: "This page does not exist.",
} as const;

/** RQ-WEB-003: the error codes of the service contract (DEC-CLI-001) that the interface words for people. */
export const SERVICE_CODE = {
  conflict: "CONFLICT",
  capacityExceeded: "CAPACITY_EXCEEDED",
  roomClosed: "ROOM_CLOSED",
  roomNotFound: "ROOM_NOT_FOUND",
  reservationNotFound: "RESERVATION_NOT_FOUND",
  alreadyStarted: "ALREADY_STARTED",
  badRequest: "BAD_REQUEST",
} as const;

/** RQ-WEB-003: the wording shown for each service error code. */
export const ERROR_TEXT: Readonly<Record<string, string>> = {
  [SERVICE_CODE.conflict]: "This room is already booked for that time. Pick another slot or another room.",
  [SERVICE_CODE.capacityExceeded]: "This room is too small for that many attendees.",
  [SERVICE_CODE.roomClosed]: "This room is closed and cannot be booked.",
  [SERVICE_CODE.roomNotFound]: "This room does not exist.",
  [SERVICE_CODE.reservationNotFound]: "No reservation has this identifier.",
  [SERVICE_CODE.alreadyStarted]: "This reservation has already started and cannot be cancelled.",
  [SERVICE_CODE.badRequest]: "The service could not read the request. Check every field.",
};

/** RQ-WEB-003: the wording of an error code the interface has no text for. */
export function fallbackErrorText(code: string): string {
  return `The service refused the request (${code}).`;
}

/** RQ-WEB-005: shown instead of the forms when the service does not answer. */
export const UNAVAILABLE_TEXT = "The booking service does not answer. Try again in a moment.";

/** RQ-WEB-002: shown when the form is incomplete or a value cannot be understood. */
export const INVALID_FORM_TEXT = "Fill in every field; attendees must be a whole number of at least 1.";

/** RQ-WEB-002: the confirmation of a booking, naming the reservation. */
export function bookedText(id: string): string {
  return `Reservation ${id} is confirmed.`;
}

/** RQ-WEB-004: the confirmation of a cancellation, naming the reservation. */
export function cancelledText(id: string): string {
  return `Reservation ${id} is cancelled.`;
}
