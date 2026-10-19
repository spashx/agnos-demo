// RQ-CLI-003, RQ-CLI-001, RQ-CLI-002, RQ-CLI-004, DEC-CLI-002 (ADR-CLI-001)
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { RoombookClient } from "./client.ts";
import { DEFAULT_BASE_URL } from "./constants.ts";
import { NetworkError, ServiceError } from "./errors.ts";
import { FetchTransport } from "./transport.ts";
import type { Reservation, Room } from "./types.ts";

export const CLI_USAGE = "usage: roombok <rooms|book|cancel> [options]";

const COMMAND_ROOMS = "rooms";
const COMMAND_BOOK = "book";
const COMMAND_CANCEL = "cancel";
const BOOK_ARG_COUNT = 5;
const CANCEL_ARG_COUNT = 1;
const ROOM_FIELD_SEPARATOR = " ";
const ERROR_SEPARATOR = ": ";
const NETWORK_FAILURE_TEXT = "network error: the service did not answer";
const ROOMBOOK_URL_ENV = "ROOMBOOK_URL";
const ARGV_OFFSET = 2;
const ENTRY_SCRIPT_INDEX = 1;

const EXIT_SUCCESS = 0;
const EXIT_SERVICE_ERROR = 1;
const EXIT_USAGE = 2;
const EXIT_NETWORK_ERROR = 3;

/** RQ-CLI-003: where the command-line tool writes its lines. */
export interface Output {
  log(text: string): void;
  error(text: string): void;
}

/** RQ-CLI-003: runs one command and returns the exit code. */
export async function run(argv: readonly string[], client: RoombookClient, output: Output): Promise<number> {
  const [command, ...args] = argv;
  try {
    switch (command) {
      case COMMAND_ROOMS:
        return await listRooms(client, output);
      case COMMAND_BOOK:
        return await book(args, client, output);
      case COMMAND_CANCEL:
        return await cancel(args, client, output);
      default:
        return usage(output);
    }
  } catch (error) {
    return reportFailure(error, output);
  }
}

/** RQ-CLI-003: prints one line per room. */
async function listRooms(client: RoombookClient, output: Output): Promise<number> {
  const rooms = await client.listRooms();
  rooms.forEach((room) => output.log(formatRoom(room)));
  return EXIT_SUCCESS;
}

/** RQ-CLI-003: books a room and prints the new reservation identifier. */
async function book(args: readonly string[], client: RoombookClient, output: Output): Promise<number> {
  if (args.length !== BOOK_ARG_COUNT) {
    return usage(output);
  }
  const [roomId, organizer, start, end, attendeesText] = args;
  const attendees = Number(attendeesText);
  if (!Number.isInteger(attendees)) {
    return usage(output);
  }
  const reservation: Reservation = await client.createReservation({ roomId, organizer, start, end, attendees });
  output.log(reservation.id);
  return EXIT_SUCCESS;
}

/** RQ-CLI-003: cancels a reservation by identifier. */
async function cancel(args: readonly string[], client: RoombookClient, output: Output): Promise<number> {
  if (args.length !== CANCEL_ARG_COUNT) {
    return usage(output);
  }
  const [id] = args;
  await client.cancelReservation(id);
  output.log(id);
  return EXIT_SUCCESS;
}

/** RQ-CLI-003: prints the usage text and returns the usage exit code. */
function usage(output: Output): number {
  output.error(CLI_USAGE);
  return EXIT_USAGE;
}

/** RQ-CLI-003, RQ-CLI-002, RQ-CLI-004: prints a service or network failure and returns its exit code. */
function reportFailure(error: unknown, output: Output): number {
  if (error instanceof ServiceError) {
    output.error(error.code + ERROR_SEPARATOR + error.message);
    return EXIT_SERVICE_ERROR;
  }
  if (error instanceof NetworkError) {
    output.error(NETWORK_FAILURE_TEXT);
    return EXIT_NETWORK_ERROR;
  }
  throw error;
}

function formatRoom(room: Room): string {
  return [room.id, room.name, String(room.capacity), String(room.open)].join(ROOM_FIELD_SEPARATOR);
}

/** RQ-CLI-003: entry point when the file is run directly; reads ROOMBOOK_URL and sets the exit code. */
async function main(): Promise<void> {
  const baseUrl = process.env[ROOMBOOK_URL_ENV] || DEFAULT_BASE_URL;
  const client = new RoombookClient(new FetchTransport(baseUrl));
  const output: Output = {
    log: (text) => console.log(text),
    error: (text) => console.error(text),
  };
  process.exitCode = await run(process.argv.slice(ARGV_OFFSET), client, output);
}

function isEntryPoint(): boolean {
  const script = process.argv[ENTRY_SCRIPT_INDEX];
  return script !== undefined && resolve(script) === fileURLToPath(import.meta.url);
}

if (isEntryPoint()) {
  void main();
}
