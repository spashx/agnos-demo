// RQ-WEB-001, RQ-WEB-002, RQ-DSN-003, DEC-WEB-001, DEC-DSN-002 (ADR-WEB-001, ADR-DSN-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import type { AddressInfo } from "node:net";
import { HTTP_POST, HTTP_STATUS_NOT_FOUND, HTTP_STATUS_OK } from "../src/constants.ts";
import { BookingApp } from "../src/ui/app.ts";
import { FORM_FIELD, ROUTE } from "../src/ui/routes.ts";
import { createUiServer } from "../src/ui/server.ts";
import { buildStylesheet, toCustomProperty } from "../src/ui/stylesheet.ts";
import { loadTokens } from "../src/ui/tokens.ts";
import { bookedText } from "../src/ui/labels.ts";
import { FakeService, RESERVATION_ID, ROOM_OPEN, clientOver } from "./fake-service.ts";

const LOCALHOST = "127.0.0.1";
const ANY_FREE_PORT = 0;
const FORM_CONTENT_TYPE = "application/x-www-form-urlencoded";
const HEADER_CONTENT_TYPE = "content-type";
const HTTP_STATUS_TOO_LARGE = 413;
const OVERSIZE_BYTES = 20000;
const SURFACE_TOKEN = "colour.surface.base";

/** Runs one test against a started server and stops it afterwards. */
async function withServer(run: (base: string) => Promise<void>): Promise<void> {
  const app = new BookingApp(clientOver(new FakeService()), buildStylesheet(loadTokens()));
  const server = createUiServer(app);
  await new Promise<void>((resolve) => server.listen(ANY_FREE_PORT, LOCALHOST, resolve));
  try {
    await run(`http://${LOCALHOST}:${(server.address() as AddressInfo).port}`);
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
}

// RQ-WEB-001
test("given a started server, when the home page is fetched, then it answers 200 HTML listing the rooms", async () => {
  await withServer(async (base) => {
    // Given a started server over a fake service
    // When the home page is fetched
    const response = await fetch(base + ROUTE.home);
    // Then the answer is HTML with the open room
    assert.equal(response.status, HTTP_STATUS_OK);
    assert.ok((response.headers.get(HEADER_CONTENT_TYPE) ?? "").startsWith("text/html"));
    assert.ok((await response.text()).includes(ROOM_OPEN.name));
  });
});

// RQ-DSN-003
test("given a started server, when the stylesheet is fetched, then it is CSS generated from the tokens", async () => {
  await withServer(async (base) => {
    // Given a started server
    // When the stylesheet is fetched
    const response = await fetch(base + ROUTE.styles);
    // Then it is CSS exposing a token as a custom property
    assert.ok((response.headers.get(HEADER_CONTENT_TYPE) ?? "").startsWith("text/css"));
    assert.ok((await response.text()).includes(`${toCustomProperty(SURFACE_TOKEN)}:`));
  });
});

// RQ-WEB-002
test("given a started server, when a booking form is posted, then the reservation is confirmed on the page", async () => {
  await withServer(async (base) => {
    // Given a started server
    // When a booking form is posted URL-encoded
    const form = new URLSearchParams({
      [FORM_FIELD.roomId]: ROOM_OPEN.id,
      [FORM_FIELD.organizer]: "ada",
      [FORM_FIELD.start]: "2030-01-01T10:00",
      [FORM_FIELD.end]: "2030-01-01T11:00",
      [FORM_FIELD.attendees]: "4",
    });
    const response = await fetch(base + ROUTE.book, { method: HTTP_POST, headers: { [HEADER_CONTENT_TYPE]: FORM_CONTENT_TYPE }, body: form });
    // Then the page confirms the reservation
    assert.equal(response.status, HTTP_STATUS_OK);
    assert.ok((await response.text()).includes(bookedText(RESERVATION_ID)));
  });
});

// RQ-WEB-001
test("given a started server, when a body larger than the limit is posted, then the answer is 413", async () => {
  await withServer(async (base) => {
    // Given a started server
    // When an oversized body is posted
    const response = await fetch(base + ROUTE.book, { method: HTTP_POST, headers: { [HEADER_CONTENT_TYPE]: FORM_CONTENT_TYPE }, body: "x".repeat(OVERSIZE_BYTES) });
    // Then the server refuses it
    assert.equal(response.status, HTTP_STATUS_TOO_LARGE);
  });
});

// RQ-WEB-001
test("given a started server, when an unknown path is fetched, then the answer is 404", async () => {
  await withServer(async (base) => {
    // Given a started server
    // When an unknown path is fetched
    const response = await fetch(base + "/nowhere");
    // Then the answer is 404
    assert.equal(response.status, HTTP_STATUS_NOT_FOUND);
  });
});
