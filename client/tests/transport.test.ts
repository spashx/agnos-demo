// RQ-CLI-004, RQ-CLI-005, DEC-CLI-002 (ADR-CLI-001)
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  DEFAULT_BASE_URL,
  HTTP_DELETE,
  HTTP_GET,
  HTTP_POST,
  HTTP_STATUS_CREATED,
  HTTP_STATUS_NO_CONTENT,
  HTTP_STATUS_OK,
  REQUEST_TIMEOUT_MS,
  RESERVATIONS_PATH,
  ROOMS_PATH,
} from "../src/constants.ts";
import { NetworkError } from "../src/errors.ts";
import { FetchTransport } from "../src/transport.ts";
import type { FetchLike } from "../src/transport.ts";

const TEST_TIMEOUT_MS = 20;
const ABORT_REASON = "aborted by the test";
const ROOM_ID = "room-1";
const ROOM_BODY = [{ id: ROOM_ID, name: "Atlas", capacity: 6, open: true }];
const NEW_RESERVATION_BODY = { roomId: ROOM_ID, organizer: "ada", start: "2030-01-01T10:00:00+00:00", end: "2030-01-01T11:00:00+00:00", attendees: 4 };
const NETWORK_FAILURE_REASON = "socket hang up";

interface RecordedRequest {
  readonly url: string;
  readonly init: RequestInit;
}

/** Fake fetch that never answers and rejects only when the transport aborts the signal. */
function neverAnsweringFetch(signals: AbortSignal[]): FetchLike {
  return (_url, init) =>
    new Promise<Response>((_resolve, reject) => {
      if (init.signal) {
        signals.push(init.signal);
        init.signal.addEventListener("abort", () => reject(new Error(ABORT_REASON)));
      }
    });
}

/** Fake fetch that answers with a fixed status and body text, and records each request. */
function answeringFetch(status: number, bodyText: string | null, recorded: RecordedRequest[]): FetchLike {
  return async (url, init) => {
    recorded.push({ url, init });
    return new Response(bodyText, { status });
  };
}

// RQ-CLI-004
test("given a server that never answers, when a call is made through the transport, then it is aborted after the timeout and a network error is thrown", async () => {
  // Given
  const signals: AbortSignal[] = [];
  const transport = new FetchTransport(DEFAULT_BASE_URL, TEST_TIMEOUT_MS, neverAnsweringFetch(signals));
  // When
  const call = transport.send(HTTP_GET, ROOMS_PATH);
  // Then
  await assert.rejects(call, NetworkError);
  assert.equal(signals[0]?.aborted, true);
});

// RQ-CLI-004
test("given a fetch that ignores the abort signal, when a call is made, then the timeout still ends the call with a network error", async () => {
  // Given
  const transport = new FetchTransport(DEFAULT_BASE_URL, TEST_TIMEOUT_MS, () => new Promise<Response>(() => undefined));
  // When
  const call = transport.send(HTTP_GET, ROOMS_PATH);
  // Then
  await assert.rejects(call, NetworkError);
});

// RQ-CLI-004
test("given a network failure, when a call is made, then a network error is thrown", async () => {
  // Given
  const failingFetch: FetchLike = () => Promise.reject(new Error(NETWORK_FAILURE_REASON));
  const transport = new FetchTransport(DEFAULT_BASE_URL, TEST_TIMEOUT_MS, failingFetch);
  // When
  const call = transport.send(HTTP_GET, ROOMS_PATH);
  // Then
  await assert.rejects(call, NetworkError);
});

// RQ-CLI-004
test("given a server answering 200 with a JSON body, when a GET is sent, then the status and the parsed body are returned", async () => {
  // Given
  const recorded: RecordedRequest[] = [];
  const transport = new FetchTransport(DEFAULT_BASE_URL, REQUEST_TIMEOUT_MS, answeringFetch(HTTP_STATUS_OK, JSON.stringify(ROOM_BODY), recorded));
  // When
  const response = await transport.send(HTTP_GET, ROOMS_PATH);
  // Then
  assert.equal(response.status, HTTP_STATUS_OK);
  assert.deepEqual(response.body, ROOM_BODY);
  assert.equal(recorded[0]?.url, DEFAULT_BASE_URL + ROOMS_PATH);
});

// RQ-CLI-004
test("given a server answering 204 with no body, when a DELETE is sent, then the body is null", async () => {
  // Given
  const recorded: RecordedRequest[] = [];
  const transport = new FetchTransport(DEFAULT_BASE_URL, REQUEST_TIMEOUT_MS, answeringFetch(HTTP_STATUS_NO_CONTENT, null, recorded));
  // When
  const response = await transport.send(HTTP_DELETE, RESERVATIONS_PATH + "/" + ROOM_ID);
  // Then
  assert.equal(response.status, HTTP_STATUS_NO_CONTENT);
  assert.equal(response.body, null);
  assert.equal(recorded[0]?.init.method, HTTP_DELETE);
});

// RQ-CLI-004
test("given a body to send, when a POST is sent, then the request carries the method and the JSON body", async () => {
  // Given
  const recorded: RecordedRequest[] = [];
  const transport = new FetchTransport(DEFAULT_BASE_URL, REQUEST_TIMEOUT_MS, answeringFetch(HTTP_STATUS_CREATED, "{}", recorded));
  // When
  await transport.send(HTTP_POST, RESERVATIONS_PATH, NEW_RESERVATION_BODY);
  // Then
  const sent = recorded[0];
  assert.equal(sent?.init.method, HTTP_POST);
  assert.deepEqual(JSON.parse(String(sent?.init.body)), NEW_RESERVATION_BODY);
});

// RQ-CLI-004
test("given no timeout argument, when a transport is created, then the timeout is REQUEST_TIMEOUT_MS", () => {
  // Given
  const transport = new FetchTransport(DEFAULT_BASE_URL);
  // When
  const timeoutMs = transport.timeoutMs;
  // Then
  assert.equal(timeoutMs, REQUEST_TIMEOUT_MS);
});
