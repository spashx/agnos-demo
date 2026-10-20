// RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-006, DEC-WEB-001 (ADR-WEB-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import { CLASS } from "../src/ui/classes.ts";
import { LABEL } from "../src/ui/labels.ts";
import { FORM_FIELD, ROUTE } from "../src/ui/routes.ts";
import { EMPTY_VALUES, escapeHtml, renderBanner, renderBookingForm, renderCancelForm, renderNotFound, renderPage, renderRoomsTable } from "../src/ui/views.ts";
import type { Room } from "../src/types.ts";

const OPEN_ROOM: Room = { id: "room-a", name: "Atlas", capacity: 6, open: true };
const CLOSED_ROOM: Room = { id: "room-b", name: "Boreal", capacity: 2, open: false };
const SCRIPT_TEXT = "<script>alert('x')</script>";
const AMPERSAND_TEXT = "R&D \"lab\"";
const RESERVATION_ID = "res-42";
const BANNER_TEXT = "Something happened";
const TYPED_ORGANIZER = "ada";
const FOUND_NONE = 0;
const CONTROL_PATTERN = /<(?:input|select)\b[^>]*\bid="([^"]+)"/g;

test("given text with markup characters, when it is escaped, then no tag or quote survives", () => {
  // Given a script tag and an ampersand with quotes
  // When they are escaped
  const escaped = escapeHtml(SCRIPT_TEXT) + escapeHtml(AMPERSAND_TEXT);
  // Then no angle bracket or raw quote is left
  assert.ok(!escaped.includes("<"));
  assert.ok(!escaped.includes(">"));
  assert.ok(!escaped.includes('"'));
  assert.ok(escaped.includes("&amp;"));
});

// RQ-WEB-003
test("given open and closed rooms, when the table is rendered, then each room shows its name, capacity and a status word", () => {
  // Given an open and a closed room
  // When the table is rendered
  const html = renderRoomsTable([OPEN_ROOM, CLOSED_ROOM]);
  // Then names and capacities appear, with a status in words and the matching badge class
  assert.ok(html.includes(OPEN_ROOM.name) && html.includes(String(OPEN_ROOM.capacity)));
  assert.ok(html.includes(LABEL.statusOpen) && html.includes(CLASS.badgeOpen));
  assert.ok(html.includes(LABEL.statusClosed) && html.includes(CLASS.badgeClosed));
});

// RQ-WEB-001
test("given no room, when the table is rendered, then the empty message replaces it", () => {
  // Given an empty room list
  // When the table is rendered
  const html = renderRoomsTable([]);
  // Then the message is shown and there is no table
  assert.ok(html.includes(LABEL.noRooms));
  assert.ok(!html.includes("<table"));
});

// RQ-WEB-001
test("given a room name with markup, when the table is rendered, then the name is escaped", () => {
  // Given a room whose name is a script tag
  // When the table is rendered
  const html = renderRoomsTable([{ ...OPEN_ROOM, name: SCRIPT_TEXT }]);
  // Then the markup does not reach the page
  assert.ok(!html.includes(SCRIPT_TEXT));
});

// RQ-WEB-002
test("given rooms and typed values, when the booking form is rendered, then it posts to the book route and keeps the values", () => {
  // Given two rooms and values typed before a refusal
  const values = { ...EMPTY_VALUES, roomId: OPEN_ROOM.id, organizer: TYPED_ORGANIZER };
  // When the form is rendered
  const html = renderBookingForm([OPEN_ROOM, CLOSED_ROOM], values);
  // Then it posts to the route, selects the room and keeps the organizer
  assert.ok(html.includes(`action="${ROUTE.book}"`));
  assert.ok(html.includes(`value="${OPEN_ROOM.id}" selected`));
  assert.ok(html.includes(`value="${TYPED_ORGANIZER}"`));
  assert.ok(html.includes(LABEL.bookButton) && html.includes(CLASS.buttonPrimary));
});

// RQ-WEB-003
test("given a closed room, when the booking form is rendered, then the room is listed but disabled and marked closed", () => {
  // Given a closed room
  // When the form is rendered
  const html = renderBookingForm([CLOSED_ROOM], EMPTY_VALUES);
  // Then the option is disabled and carries the closed wording
  assert.ok(html.includes("disabled"));
  assert.ok(html.includes(LABEL.closedSuffix));
});

// RQ-WEB-006
test("given the booking and cancel forms, when their controls are listed, then each control has a label bound to it", () => {
  // Given both forms
  const html = renderBookingForm([OPEN_ROOM], EMPTY_VALUES) + renderCancelForm();
  // When the identifier of each input and select is read
  const controls = [...html.matchAll(CONTROL_PATTERN)].map((match) => match[1]);
  // Then a label points to every one
  assert.ok(controls.length > FOUND_NONE);
  for (const control of controls) {
    assert.ok(html.includes(`for="${control}"`), control);
  }
});

// RQ-WEB-004
test("given the cancel form, when it is rendered, then it posts to the cancel route with a secondary button", () => {
  // Given the cancel form
  // When it is rendered
  const html = renderCancelForm();
  // Then it posts to the route and asks for a reservation identifier
  assert.ok(html.includes(`action="${ROUTE.cancel}"`));
  assert.ok(html.includes(`name="${FORM_FIELD.reservationId}"`));
  assert.ok(html.includes(CLASS.buttonSecondary));
});

// RQ-WEB-006
test("given each banner kind, when it is rendered, then its modifier class and ARIA role match", () => {
  // Given the three kinds
  // When each is rendered
  // Then the error is an alert and the others are status messages, each with its class
  assert.ok(renderBanner({ kind: "error", text: BANNER_TEXT }).includes('role="alert"'));
  assert.ok(renderBanner({ kind: "success", text: BANNER_TEXT }).includes(CLASS.bannerSuccess));
  assert.ok(renderBanner({ kind: "warning", text: BANNER_TEXT }).includes(`role="status"`));
  assert.ok(renderBanner({ kind: "warning", text: BANNER_TEXT }).includes(CLASS.bannerWarning));
});

// RQ-WEB-004
test("given a success banner with a reservation, when it is rendered, then it offers a one-click cancel of that reservation", () => {
  // Given a confirmation carrying a reservation identifier
  // When the banner is rendered
  const html = renderBanner({ kind: "success", text: BANNER_TEXT, reservationId: RESERVATION_ID });
  // Then a danger button posts that identifier to the cancel route
  assert.ok(html.includes(`action="${ROUTE.cancel}"`));
  assert.ok(html.includes(`value="${RESERVATION_ID}"`));
  assert.ok(html.includes(CLASS.buttonDanger) && html.includes(LABEL.cancelThisButton));
});

// RQ-WEB-002
test("given a page model with forms enabled, when the page is rendered, then it links the stylesheet and shows the three cards", () => {
  // Given rooms and enabled forms
  // When the page is rendered
  const html = renderPage({ rooms: [OPEN_ROOM], formsEnabled: true });
  // Then the stylesheet is linked and the three headings appear
  assert.ok(html.includes(`href="${ROUTE.styles}"`));
  for (const heading of [LABEL.roomsHeading, LABEL.bookHeading, LABEL.cancelHeading]) {
    assert.ok(html.includes(heading), heading);
  }
});

// RQ-WEB-003
test("given a page model with forms disabled, when the page is rendered, then only the banner and the title remain", () => {
  // Given a service that does not answer
  // When the page is rendered with a warning
  const html = renderPage({ rooms: [], formsEnabled: false, banner: { kind: "warning", text: BANNER_TEXT } });
  // Then the title and the banner show, the forms do not
  assert.ok(html.includes(LABEL.pageTitle) && html.includes(BANNER_TEXT));
  assert.ok(!html.includes("<form"));
});

// RQ-WEB-002
test("given an unknown route, when the not-found page is rendered, then it says so without forms", () => {
  // Given the not-found page
  // When it is rendered
  const html = renderNotFound();
  // Then it carries the not-found text and no form
  assert.ok(html.includes(LABEL.notFoundText));
  assert.ok(!html.includes("<form"));
});
