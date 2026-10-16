// RQ-CLI-003, RQ-CLI-001, RQ-CLI-002, RQ-CLI-004, DEC-CLI-002 (ADR-CLI-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import { HTTP_DELETE, HTTP_GET, HTTP_POST, HTTP_STATUS_CONFLICT, HTTP_STATUS_CREATED, HTTP_STATUS_NO_CONTENT, HTTP_STATUS_OK, RESERVATIONS_PATH, ROOMS_PATH } from "../src/constants.ts";
import { RoombookClient } from "../src/client.ts";
import { CLI_USAGE, run } from "../src/cli.ts";
import type { Output } from "../src/cli.ts";
import { NetworkError } from "../src/errors.ts";
import type { HttpResponse, Transport } from "../src/transport.ts";

const COMMAND_ROOMS = "rooms";
const COMMAND_BOOK = "book";
const COMMAND_CANCEL = "cancel";
const UNKNOWN_COMMAND = "teleport";
const ROOM_ID = "room-1";
const ROOM_NAME = "Atlas";
const ROOM_CAPACITY = "6";
const ORGANIZER = "ada";
const START = "2030-01-01T10:00:00+00:00";
const END = "2030-01-01T11:00:00+00:00";
const ATTENDEES = "4";
const NOT_A_NUMBER = "four";
const RESERVATION_ID = "res-1";
const CONFLICT_CODE = "CONFLICT";
const CONFLICT_MESSAGE = "room already booked";
const EXPECTED_ROOM_LINE = `${ROOM_ID} ${ROOM_NAME} ${ROOM_CAPACITY} true`;
const ROOM_FIELD_COUNT = 4;
const NETWORK_FAILURE_MESSAGE = "the service could not be reached";

/** Fake output that records every line written. */
class MemoryOutput implements Output {
  readonly lines: string[] = [];
  readonly errors: string[] = [];

  // RQ-CLI-003
  log(text: string): void {
    this.lines.push(text);
  }

  // RQ-CLI-003
  error(text: string): void {
    this.errors.push(text);
  }
}

/** Fake transport: records each call and answers with a fixed reply or throws. */
class FakeTransport implements Transport {
  readonly calls: string[] = [];
  private readonly reply: () => Promise<HttpResponse>;

  constructor(reply: () => Promise<HttpResponse>) {
    this.reply = reply;
  }

  // RQ-CLI-003
  send(method: string, path: string): Promise<HttpResponse> {
    this.calls.push(method + " " + path);
    return this.reply();
  }
}

function clientAnswering(status: number, body: unknown): { client: RoombookClient; transport: FakeTransport } {
  const transport = new FakeTransport(async () => ({ status, body }));
  return { client: new RoombookClient(transport), transport };
}

// RQ-CLI-003
test("given a service that accepts the booking, when book is run, then the reservation identifier is printed and the exit code is 0", async () => {
  // Given
  const { client, transport } = clientAnswering(HTTP_STATUS_CREATED, { id: RESERVATION_ID, roomId: ROOM_ID, organizer: ORGANIZER, start: START, end: END, attendees: Number(ATTENDEES), status: "CONFIRMED" });
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_BOOK, ROOM_ID, ORGANIZER, START, END, ATTENDEES], client, output);
  // Then
  assert.equal(exitCode, 0);
  assert.deepEqual(output.lines, [RESERVATION_ID]);
  assert.deepEqual(transport.calls, [HTTP_POST + " " + RESERVATIONS_PATH]);
});

// RQ-CLI-003
test("given a service rejecting the booking with CONFLICT, when book is run, then the error code is printed and the exit code is non-zero", async () => {
  // Given
  const { client } = clientAnswering(HTTP_STATUS_CONFLICT, { code: CONFLICT_CODE, message: CONFLICT_MESSAGE });
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_BOOK, ROOM_ID, ORGANIZER, START, END, ATTENDEES], client, output);
  // Then
  assert.notEqual(exitCode, 0);
  assert.ok(output.errors.join("\n").includes(CONFLICT_CODE));
});

// RQ-CLI-003
test("given a service listing rooms, when rooms is run, then one line per room is printed and the exit code is 0", async () => {
  // Given
  const { client, transport } = clientAnswering(HTTP_STATUS_OK, [{ id: ROOM_ID, name: ROOM_NAME, capacity: Number(ROOM_CAPACITY), open: true }]);
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_ROOMS], client, output);
  // Then
  assert.equal(exitCode, 0);
  assert.deepEqual(output.lines, [EXPECTED_ROOM_LINE]);
  assert.equal(output.lines[0]?.split(" ").length, ROOM_FIELD_COUNT);
  assert.deepEqual(transport.calls, [HTTP_GET + " " + ROOMS_PATH]);
});

// RQ-CLI-003
test("given a service accepting the cancellation, when cancel is run, then the exit code is 0 and DELETE is sent", async () => {
  // Given
  const { client, transport } = clientAnswering(HTTP_STATUS_NO_CONTENT, null);
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_CANCEL, RESERVATION_ID], client, output);
  // Then
  assert.equal(exitCode, 0);
  assert.deepEqual(transport.calls, [HTTP_DELETE + " " + RESERVATIONS_PATH + "/" + RESERVATION_ID]);
});

// RQ-CLI-003
test("given a service that cannot be reached, when rooms is run, then the exit code is non-zero and a message is printed", async () => {
  // Given
  const client = new RoombookClient(new FakeTransport(async () => {
    throw new NetworkError(NETWORK_FAILURE_MESSAGE);
  }));
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_ROOMS], client, output);
  // Then
  assert.notEqual(exitCode, 0);
  assert.equal(output.errors.length, 1);
});

// RQ-CLI-003
test("given book without all its arguments, when run, then the usage text is printed and the exit code is non-zero", async () => {
  // Given
  const { client } = clientAnswering(HTTP_STATUS_CREATED, {});
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_BOOK, ROOM_ID], client, output);
  // Then
  assert.notEqual(exitCode, 0);
  assert.deepEqual(output.errors, [CLI_USAGE]);
});

// RQ-CLI-003
test("given book with a non-numeric attendee count, when run, then the usage text is printed and the exit code is non-zero", async () => {
  // Given
  const { client } = clientAnswering(HTTP_STATUS_CREATED, {});
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_BOOK, ROOM_ID, ORGANIZER, START, END, NOT_A_NUMBER], client, output);
  // Then
  assert.notEqual(exitCode, 0);
  assert.deepEqual(output.errors, [CLI_USAGE]);
});

// RQ-CLI-003
test("given cancel without a reservation identifier, when run, then the usage text is printed and the exit code is non-zero", async () => {
  // Given
  const { client } = clientAnswering(HTTP_STATUS_NO_CONTENT, null);
  const output = new MemoryOutput();
  // When
  const exitCode = await run([COMMAND_CANCEL], client, output);
  // Then
  assert.notEqual(exitCode, 0);
  assert.deepEqual(output.errors, [CLI_USAGE]);
});

// RQ-CLI-003
test("given an unknown command, when run, then the usage text is printed and the exit code is non-zero", async () => {
  // Given
  const { client } = clientAnswering(HTTP_STATUS_OK, []);
  const output = new MemoryOutput();
  // When
  const exitCode = await run([UNKNOWN_COMMAND], client, output);
  // Then
  assert.notEqual(exitCode, 0);
  assert.deepEqual(output.errors, [CLI_USAGE]);
});
