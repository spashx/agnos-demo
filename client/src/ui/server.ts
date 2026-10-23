// RQ-WEB-001, RQ-DSN-003, DEC-WEB-001, DEC-DSN-002 (ADR-WEB-001, ADR-DSN-001)
import { createServer } from "node:http";
import type { IncomingMessage, Server, ServerResponse } from "node:http";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { RoombookClient } from "../client.ts";
import { DEFAULT_BASE_URL, HTTP_POST, HTTP_STATUS_INTERNAL_ERROR } from "../constants.ts";
import { FetchTransport } from "../transport.ts";
import { BookingApp } from "./app.ts";
import { ROUTE } from "./routes.ts";
import { buildStylesheet } from "./stylesheet.ts";
import { loadTokens } from "./tokens.ts";

const ROOMBOOK_URL_ENV = "ROOMBOOK_URL";
const UI_PORT_ENV = "ROOMBOOK_UI_PORT";
const DEFAULT_UI_PORT = 3000;
const UI_HOST = "127.0.0.1";
const MAX_BODY_BYTES = 16384;
const HTTP_STATUS_TOO_LARGE = 413;
const HEADER_CONTENT_TYPE = "Content-Type";
const CONTENT_TYPE_TEXT = "text/plain; charset=utf-8";
const REQUEST_BASE = "http://localhost";
const BODY_ENCODING = "utf-8";
const ENTRY_SCRIPT_INDEX = 1;
const NO_TEXT = "";
const STARTED_TEXT = "Roombook web interface on ";

/** RQ-WEB-002: reads a form body up to the size limit; resolves to undefined when the body is larger. */
async function readBody(request: IncomingMessage): Promise<string | undefined> {
  const chunks: Buffer[] = [];
  let size = 0;
  for await (const chunk of request) {
    size += (chunk as Buffer).length;
    if (size > MAX_BODY_BYTES) {
      return undefined;
    }
    chunks.push(chunk as Buffer);
  }
  return Buffer.concat(chunks).toString(BODY_ENCODING);
}

/** RQ-WEB-001: translates one HTTP exchange to a UiRequest and writes the UiResponse back. */
async function respond(app: BookingApp, request: IncomingMessage, response: ServerResponse): Promise<void> {
  const method = request.method ?? NO_TEXT;
  const body = method === HTTP_POST ? await readBody(request) : NO_TEXT;
  if (body === undefined) {
    response.writeHead(HTTP_STATUS_TOO_LARGE, { [HEADER_CONTENT_TYPE]: CONTENT_TYPE_TEXT }).end();
    return;
  }
  const path = new URL(request.url ?? ROUTE.home, REQUEST_BASE).pathname;
  const form = Object.fromEntries(new URLSearchParams(body));
  const answer = await app.handle({ method, path, form });
  response.writeHead(answer.status, { [HEADER_CONTENT_TYPE]: answer.contentType }).end(answer.body);
}

/** RQ-WEB-001: the HTTP server of the interface; it only translates HTTP to the app (DEC-WEB-001). */
export function createUiServer(app: BookingApp): Server {
  return createServer((request, response) => {
    respond(app, request, response).catch(() => {
      response.writeHead(HTTP_STATUS_INTERNAL_ERROR, { [HEADER_CONTENT_TYPE]: CONTENT_TYPE_TEXT }).end();
    });
  });
}

/** RQ-WEB-001, RQ-DSN-003: entry point when the file is run directly; builds the stylesheet from the tokens and listens. */
function main(): void {
  const client = new RoombookClient(new FetchTransport(process.env[ROOMBOOK_URL_ENV] || DEFAULT_BASE_URL));
  const app = new BookingApp(client, buildStylesheet(loadTokens()));
  const port = Number(process.env[UI_PORT_ENV] || DEFAULT_UI_PORT);
  createUiServer(app).listen(port, UI_HOST, () => console.log(STARTED_TEXT + `http://${UI_HOST}:${port}`));
}

function isEntryPoint(): boolean {
  const script = process.argv[ENTRY_SCRIPT_INDEX];
  return script !== undefined && resolve(script) === fileURLToPath(import.meta.url);
}

if (isEntryPoint()) {
  main();
}
