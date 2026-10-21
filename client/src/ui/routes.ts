// RQ-WEB-001, RQ-WEB-002, RQ-WEB-004, DEC-WEB-001 (ADR-WEB-001)

/** RQ-WEB-001: the routes of the interface; the views write them in forms and links, the app dispatches on them. */
export const ROUTE = {
  home: "/",
  book: "/book",
  cancel: "/cancel",
  styles: "/styles.css",
} as const;

/** RQ-WEB-002, RQ-WEB-004: the names of the form fields, shared by the views that write them and the app that reads them. */
export const FORM_FIELD = {
  roomId: "roomId",
  organizer: "organizer",
  start: "start",
  end: "end",
  attendees: "attendees",
  reservationId: "reservationId",
} as const;
