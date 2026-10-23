// RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-005, DEC-WEB-001, DEC-WEB-002 (ADR-WEB-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import { HTTP_DELETE, HTTP_GET, HTTP_POST, HTTP_STATUS_CONFLICT, HTTP_STATUS_NOT_FOUND, HTTP_STATUS_OK, HTTP_STATUS_UNPROCESSABLE, RESERVATIONS_PATH, ROOMS_PATH } from "../src/constants.ts";
import { BOOKING_UTC_OFFSET, BookingApp, SECONDS_SUFFIX, readValues, toIsoWithOffset, toReservationRequest } from "../src/ui/app.ts";
import { ERROR_TEXT, INVALID_FORM_TEXT, SERVICE_CODE, UNAVAILABLE_TEXT, bookedText, cancelledText, fallbackErrorText } from "../src/ui/labels.ts";
import { FORM_FIELD, ROUTE } from "../src/ui/routes.ts";
import { EMPTY_VALUES } from "../src/ui/views.ts";
import { FakeService, ROOM_OPEN, RESERVATION_ID, clientOver } from "./fake-service.ts";

const STYLESHEET = "body { margin: 0; }";
const HTTP_STATUS_BAD_REQUEST = 400;
const HTTP_STATUS_UNAVAILABLE = 503;
const LOCAL_START = "2030-01-01T10:00";
const LOCAL_END = "2030-01-01T11:00";
const LOCAL_WITH_SECONDS = "2030-01-01T10:00:30";
const ORGANIZER = "ada";
const UNKNOWN_CODE = "TEAPOT";
const UNKNOWN_ID = "res-unknown";
const NOT_A_DATE = "tomorrow";

/** A complete booking form, as the browser would post it. */
const BOOKING_FORM: Record<string, string> = {
  [FORM_FIELD.roomId]: ROOM_OPEN.id,
  [FORM_FIELD.organizer]: ORGANIZER,
  [FORM_FIELD.start]: LOCAL_START,
  [FORM_FIELD.end]: LOCAL_END,
  [FORM_FIELD.attendees]: "4",
};

function appOver(service: FakeService): BookingApp {
  return new BookingApp(clientOver(service), STYLESHEET);
}

function post(path: string, form: Record<string, string>) {
  return { method: HTTP_POST, path, form };
}

// RQ-WEB-001
test("given a service with rooms, when the home page is requested, then the rooms are listed with status 200", async () => {
  // Given a service with an open and a closed room
  const service = new FakeService();
  // When the home page is requested
  const response = await appOver(service).handle({ method: HTTP_GET, path: ROUTE.home, form: {} });
  // Then the page lists the open room
  assert.equal(response.status, HTTP_STATUS_OK);
  assert.ok(response.body.includes(ROOM_OPEN.name));
});

// RQ-WEB-001
test("given the stylesheet route, when it is requested, then the generated stylesheet is returned as CSS", async () => {
  // Given an app holding a stylesheet
  // When the stylesheet route is requested
  const response = await appOver(new FakeService()).handle({ method: HTTP_GET, path: ROUTE.styles, form: {} });
  // Then the text is returned with a CSS content type
  assert.equal(response.body, STYLESHEET);
  assert.ok(response.contentType.startsWith("text/css"));
});

// RQ-WEB-001
test("given an unknown route, when it is requested, then the answer is 404", async () => {
  // Given an app
  // When an unknown path is requested
  const response = await appOver(new FakeService()).handle({ method: HTTP_GET, path: "/nowhere", form: {} });
  // Then the status is 404
  assert.equal(response.status, HTTP_STATUS_NOT_FOUND);
});

// RQ-WEB-002
test("given a valid booking form, when it is submitted, then the reservation is created and its identifier is confirmed", async () => {
  // Given a service that accepts the booking
  const service = new FakeService();
  // When the form is submitted
  const response = await appOver(service).handle(post(ROUTE.book, BOOKING_FORM));
  // Then the confirmation names the reservation and the service received a UTC request
  assert.equal(response.status, HTTP_STATUS_OK);
  assert.ok(response.body.includes(bookedText(RESERVATION_ID)));
  const sent = service.calls.find((call) => call.method === HTTP_POST)?.body as Record<string, unknown>;
  assert.equal(sent.start, toIsoWithOffset(LOCAL_START));
});

// RQ-WEB-003
test("given a service answering a conflict, when a booking is submitted, then the conflict wording is shown and the values are kept", async () => {
  // Given a service that answers 409 with code CONFLICT
  const service = new FakeService();
  service.replyTo(HTTP_POST, RESERVATIONS_PATH, { status: HTTP_STATUS_CONFLICT, body: { code: SERVICE_CODE.conflict, message: "room already booked" } });
  // When the form is submitted
  const response = await appOver(service).handle(post(ROUTE.book, BOOKING_FORM));
  // Then the wording of the code is shown with the status of the service and what was typed
  assert.equal(response.status, HTTP_STATUS_CONFLICT);
  assert.ok(response.body.includes(ERROR_TEXT[SERVICE_CODE.conflict]));
  assert.ok(response.body.includes(`value="${ORGANIZER}"`));
});

// RQ-WEB-002
test("given a service answering a code without wording, when a booking is submitted, then the fallback wording names the code", async () => {
  // Given a service that answers 422 with an unknown code
  const service = new FakeService();
  service.replyTo(HTTP_POST, RESERVATIONS_PATH, { status: HTTP_STATUS_UNPROCESSABLE, body: { code: UNKNOWN_CODE, message: "teapot" } });
  // When the form is submitted
  const response = await appOver(service).handle(post(ROUTE.book, BOOKING_FORM));
  // Then the fallback text with the code is shown
  assert.ok(response.body.includes(fallbackErrorText(UNKNOWN_CODE)));
});

// RQ-WEB-003
test("given an incomplete booking form, when it is submitted, then the service is not called and the form is refused", async () => {
  // Given a form without organizer
  const service = new FakeService();
  const form = { ...BOOKING_FORM, [FORM_FIELD.organizer]: "" };
  // When the form is submitted
  const response = await appOver(service).handle(post(ROUTE.book, form));
  // Then the answer is 400 with the invalid-form text and no reservation was requested
  assert.equal(response.status, HTTP_STATUS_BAD_REQUEST);
  assert.ok(response.body.includes(INVALID_FORM_TEXT));
  assert.equal(service.count(HTTP_POST), 0);
});

// RQ-WEB-005
test("given a service that does not answer, when the home page is requested, then the unavailable page is shown without forms", async () => {
  // Given a service that fails every call
  const service = new FakeService();
  service.replyTo(HTTP_GET, ROOMS_PATH, "network-failure");
  // When the home page is requested
  const response = await appOver(service).handle({ method: HTTP_GET, path: ROUTE.home, form: {} });
  // Then the answer is 503 with the warning and no form
  assert.equal(response.status, HTTP_STATUS_UNAVAILABLE);
  assert.ok(response.body.includes(UNAVAILABLE_TEXT));
  assert.ok(!response.body.includes("<form"));
});

// RQ-WEB-005
test("given a service that fails while booking, when the form is submitted, then the unavailable page is shown", async () => {
  // Given a service whose creation call fails
  const service = new FakeService();
  service.replyTo(HTTP_POST, RESERVATIONS_PATH, "network-failure");
  // When the form is submitted
  const response = await appOver(service).handle(post(ROUTE.book, BOOKING_FORM));
  // Then the unavailable page is shown
  assert.equal(response.status, HTTP_STATUS_UNAVAILABLE);
  assert.ok(response.body.includes(UNAVAILABLE_TEXT));
});

// RQ-WEB-004
test("given an existing reservation, when its cancel form is submitted, then the cancellation is confirmed", async () => {
  // Given a service that accepts the cancellation
  const service = new FakeService();
  // When the cancel form is submitted
  const response = await appOver(service).handle(post(ROUTE.cancel, { [FORM_FIELD.reservationId]: RESERVATION_ID }));
  // Then the confirmation names the reservation and a DELETE was sent
  assert.equal(response.status, HTTP_STATUS_OK);
  assert.ok(response.body.includes(cancelledText(RESERVATION_ID)));
  assert.equal(service.count(HTTP_DELETE), 1);
});

// RQ-WEB-004
test("given an unknown reservation, when its cancel form is submitted, then the not-found wording is shown", async () => {
  // Given a service answering 404 for the identifier
  const service = new FakeService();
  service.replyTo(HTTP_DELETE, `${RESERVATIONS_PATH}/${UNKNOWN_ID}`, { status: HTTP_STATUS_NOT_FOUND, body: { code: SERVICE_CODE.reservationNotFound, message: "unknown" } });
  // When the cancel form is submitted
  const response = await appOver(service).handle(post(ROUTE.cancel, { [FORM_FIELD.reservationId]: UNKNOWN_ID }));
  // Then the wording of the code is shown
  assert.equal(response.status, HTTP_STATUS_NOT_FOUND);
  assert.ok(response.body.includes(ERROR_TEXT[SERVICE_CODE.reservationNotFound]));
});

// RQ-WEB-004
test("given a cancel form without identifier, when it is submitted, then the form is refused without calling the service", async () => {
  // Given an empty identifier
  const service = new FakeService();
  // When the cancel form is submitted
  const response = await appOver(service).handle(post(ROUTE.cancel, { [FORM_FIELD.reservationId]: "  " }));
  // Then the answer is 400 and no DELETE was sent
  assert.equal(response.status, HTTP_STATUS_BAD_REQUEST);
  assert.equal(service.count(HTTP_DELETE), 0);
});

// RQ-WEB-002
test("given a posted form with spaces and a missing field, when the values are read, then values are trimmed and a missing field is empty", () => {
  // Given a form with a padded organizer and no attendees
  const form = { [FORM_FIELD.organizer]: `  ${ORGANIZER} `, [FORM_FIELD.roomId]: ROOM_OPEN.id };
  // When the values are read
  const values = readValues(form);
  // Then the organizer is trimmed and the attendees are empty
  assert.equal(values.organizer, ORGANIZER);
  assert.equal(values.attendees, EMPTY_VALUES.attendees);
});

// RQ-WEB-003
test("given local date and time texts, when they are converted, then minutes get seconds and the UTC offset, and other texts are refused", () => {
  // Given a local time to the minute, one with seconds and a text that is not a date
  // When each is converted
  // Then the first gets seconds and the offset, the second only the offset and the last gives nothing
  assert.equal(toIsoWithOffset(LOCAL_START), LOCAL_START + SECONDS_SUFFIX + BOOKING_UTC_OFFSET);
  assert.equal(toIsoWithOffset(LOCAL_WITH_SECONDS), LOCAL_WITH_SECONDS + BOOKING_UTC_OFFSET);
  assert.equal(toIsoWithOffset(NOT_A_DATE), undefined);
});

// RQ-WEB-002
test("given form values, when the reservation request is built, then a valid form gives a request and an invalid one gives nothing", () => {
  // Given complete values, and the same values with zero attendees
  const complete = readValues(BOOKING_FORM);
  const zeroAttendees = { ...complete, attendees: "0" };
  const fractional = { ...complete, attendees: "2.5" };
  // When the requests are built
  // Then only the complete values give a request with a numeric attendee count
  assert.equal(toReservationRequest(complete)?.attendees, Number(complete.attendees));
  assert.equal(toReservationRequest(zeroAttendees), undefined);
  assert.equal(toReservationRequest(fractional), undefined);
  assert.equal(toReservationRequest(EMPTY_VALUES), undefined);
});
