// RQ-WEB-001, RQ-WEB-002, RQ-WEB-003, RQ-WEB-005, DEC-WEB-002 (ADR-WEB-001)
import { RoombookClient } from "../src/client.ts";
import { HTTP_DELETE, HTTP_GET, HTTP_POST, HTTP_STATUS_CREATED, HTTP_STATUS_NO_CONTENT, HTTP_STATUS_OK, RESERVATIONS_PATH, ROOMS_PATH } from "../src/constants.ts";
import { NetworkError } from "../src/errors.ts";
import type { HttpResponse, Transport } from "../src/transport.ts";
import type { Reservation, Room } from "../src/types.ts";

export const ROOM_OPEN: Room = { id: "room-a", name: "Atlas", capacity: 6, open: true };
export const ROOM_CLOSED: Room = { id: "room-b", name: "Boreal", capacity: 2, open: false };
export const RESERVATION_ID = "res-1";

/** One scripted answer of the fake service: a reply, or a network failure. */
export type Reply = HttpResponse | "network-failure";

/** Fake transport: answers each `METHOD path` from a table and records every call it receives. */
export class FakeService implements Transport {
  readonly calls: { method: string; path: string; body: unknown }[] = [];
  private readonly replies = new Map<string, Reply>();

  constructor(rooms: readonly Room[] = [ROOM_OPEN, ROOM_CLOSED]) {
    this.replyTo(HTTP_GET, ROOMS_PATH, { status: HTTP_STATUS_OK, body: rooms });
    this.replyTo(HTTP_POST, RESERVATIONS_PATH, { status: HTTP_STATUS_CREATED, body: reservation(RESERVATION_ID) });
    this.replyTo(HTTP_DELETE, RESERVATIONS_PATH + "/" + RESERVATION_ID, { status: HTTP_STATUS_NO_CONTENT, body: null });
  }

  /** Scripts the answer to `method path`. */
  // RQ-WEB-001
  replyTo(method: string, path: string, reply: Reply): void {
    this.replies.set(method + " " + path, reply);
  }

  /** Counts the recorded calls to `method` on any path. */
  // RQ-WEB-001
  count(method: string): number {
    return this.calls.filter((call) => call.method === method).length;
  }

  // RQ-WEB-001
  async send(method: string, path: string, body?: unknown): Promise<HttpResponse> {
    this.calls.push({ method, path, body });
    const reply = this.replies.get(method + " " + path);
    if (reply === undefined || reply === "network-failure") {
      throw new NetworkError("fake service unreachable");
    }
    return reply;
  }
}

/** A Confirmed reservation with this identifier, as the service answers a creation. */
// RQ-WEB-001
export function reservation(id: string): Reservation {
  return { id, roomId: ROOM_OPEN.id, organizer: "ada", start: "2030-01-01T10:00:00+00:00", end: "2030-01-01T11:00:00+00:00", attendees: 4, status: "CONFIRMED" };
}

/** A typed client over a fake service. */
// RQ-WEB-001
export function clientOver(service: FakeService): RoombookClient {
  return new RoombookClient(service);
}
