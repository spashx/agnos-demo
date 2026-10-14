// RQ-CLI-001, RQ-CLI-002, DEC-CLI-002 (ADR-CLI-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import { HTTP_DELETE, HTTP_GET, HTTP_POST, HTTP_STATUS_CONFLICT, HTTP_STATUS_CREATED, HTTP_STATUS_INTERNAL_ERROR, HTTP_STATUS_NO_CONTENT, HTTP_STATUS_NOT_FOUND, HTTP_STATUS_OK, RESERVATIONS_PATH, ROOMS_PATH, UNKNOWN_ERROR_CODE } from "../src/constants.ts";
import { NetworkError, ServiceError } from "../src/errors.ts";
import { RoombookClient } from "../src/client.ts";
import type { HttpResponse, Transport } from "../src/transport.ts";
import type { ReservationRequest } from "../src/types.ts";

const ROOM_ID = "room-1";
const ROOM_NAME = "Atlas";
const ROOM_CAPACITY = 6;
const RESERVATION_ID = "res-1";
const ORGANIZER = "ada";
const START = "2030-01-01T10:00:00+00:00";
const END = "2030-01-01T11:00:00+00:00";
const ATTENDEES = 4;
const CONFLICT_CODE = "CONFLICT";
const NOT_FOUND_CODE = "ROOM_NOT_FOUND";
const CONFLICT_MESSAGE = "room already booked";
const NETWORK_FAILURE_MESSAGE = "the service could not be reached";
const SERVICE_ERROR_MESSAGE = "a service error";

const NEW_RESERVATION: ReservationRequest = { roomId: ROOM_ID, organizer: ORGANIZER, start: START, end: END, attendees: ATTENDEES };
const CREATED_RESERVATION = { id: RESERVATION_ID, ...NEW_RESERVATION, status: "CONFIRMED" };

interface SentCall {
  readonly method: string;
  readonly path: string;
  readonly body: unknown;
}

/** Fake transport: records each call and answers with a fixed reply or throws. */
class FakeTransport implements Transport {
  readonly calls: SentCall[] = [];
  private readonly reply: () => Promise<HttpResponse>;

  constructor(reply: () => Promise<HttpResponse>) {
    this.reply = reply;
  }

  // RQ-CLI-001
  send(method: string, path: string, body?: unknown): Promise<HttpResponse> {
    this.calls.push({ method, path, body });
    return this.reply();
  }
}

function answering(status: number, body: unknown): FakeTransport {
  return new FakeTransport(async () => ({ status, body }));
}

// RQ-CLI-001
test("given a service listing one room, when listRooms is called, then the typed rooms are returned from GET /rooms", async () => {
  // Given
  const transport = answering(HTTP_STATUS_OK, [{ id: ROOM_ID, name: ROOM_NAME, capacity: ROOM_CAPACITY, open: true }]);
  const client = new RoombookClient(transport);
  // When
  const rooms = await client.listRooms();
  // Then
  assert.deepEqual(rooms, [{ id: ROOM_ID, name: ROOM_NAME, capacity: ROOM_CAPACITY, open: true }]);
  assert.equal(transport.calls[0]?.method, HTTP_GET);
  assert.equal(transport.calls[0]?.path, ROOMS_PATH);
});

// RQ-CLI-001
test("given a service accepting a reservation, when createReservation is called, then the typed reservation is returned from POST /reservations", async () => {
  // Given
  const transport = answering(HTTP_STATUS_CREATED, CREATED_RESERVATION);
  const client = new RoombookClient(transport);
  // When
  const reservation = await client.createReservation(NEW_RESERVATION);
  // Then
  assert.deepEqual(reservation, CREATED_RESERVATION);
  assert.equal(transport.calls[0]?.method, HTTP_POST);
  assert.equal(transport.calls[0]?.path, RESERVATIONS_PATH);
  assert.deepEqual(transport.calls[0]?.body, NEW_RESERVATION);
});

// RQ-CLI-001
test("given a service answering 204, when cancelReservation is called, then the call resolves and sends DELETE on the reservation", async () => {
  // Given
  const transport = answering(HTTP_STATUS_NO_CONTENT, null);
  const client = new RoombookClient(transport);
  // When
  await client.cancelReservation(RESERVATION_ID);
  // Then
  assert.equal(transport.calls[0]?.method, HTTP_DELETE);
  assert.equal(transport.calls[0]?.path, RESERVATIONS_PATH + "/" + RESERVATION_ID);
});

// RQ-CLI-002
test("given a service answering 409 with code CONFLICT, when a reservation is created, then a service error with code CONFLICT and status 409 is thrown", async () => {
  // Given
  const client = new RoombookClient(answering(HTTP_STATUS_CONFLICT, { code: CONFLICT_CODE, message: CONFLICT_MESSAGE }));
  // When
  const call = client.createReservation(NEW_RESERVATION);
  // Then
  await assert.rejects(call, (error: unknown) => error instanceof ServiceError && error.code === CONFLICT_CODE && error.status === HTTP_STATUS_CONFLICT);
});

// RQ-CLI-002
test("given a service answering 404 with a code, when rooms are listed, then a service error carries that code and status", async () => {
  // Given
  const client = new RoombookClient(answering(HTTP_STATUS_NOT_FOUND, { code: NOT_FOUND_CODE, message: SERVICE_ERROR_MESSAGE }));
  // When
  const call = client.listRooms();
  // Then
  await assert.rejects(call, (error: unknown) => error instanceof ServiceError && error.code === NOT_FOUND_CODE && error.status === HTTP_STATUS_NOT_FOUND);
});

// RQ-CLI-002
test("given an error status with no error body, when a call is made, then a service error with the unknown code is thrown", async () => {
  // Given
  const client = new RoombookClient(answering(HTTP_STATUS_INTERNAL_ERROR, null));
  // When
  const call = client.listRooms();
  // Then
  await assert.rejects(call, (error: unknown) => error instanceof ServiceError && error.code === UNKNOWN_ERROR_CODE && error.status === HTTP_STATUS_INTERNAL_ERROR);
});

// RQ-CLI-002
test("given a transport that throws a network error, when a call is made, then the network error propagates", async () => {
  // Given
  const transport = new FakeTransport(async () => {
    throw new NetworkError(NETWORK_FAILURE_MESSAGE);
  });
  const client = new RoombookClient(transport);
  // When
  const call = client.cancelReservation(RESERVATION_ID);
  // Then
  await assert.rejects(call, NetworkError);
});

// RQ-CLI-002
test("given a service error, when it is built, then it exposes the code, the status and is an Error", () => {
  // Given
  const error = new ServiceError(CONFLICT_CODE, SERVICE_ERROR_MESSAGE, HTTP_STATUS_CONFLICT);
  // When
  const isError = error instanceof Error;
  // Then
  assert.equal(isError, true);
  assert.equal(error.code, CONFLICT_CODE);
  assert.equal(error.status, HTTP_STATUS_CONFLICT);
});
