// RQ-CLI-004, RQ-CLI-005, DEC-CLI-002 (ADR-CLI-001)
import { HEADER_ACCEPT, HEADER_CONTENT_TYPE, JSON_MEDIA_TYPE, REQUEST_TIMEOUT_MS } from "./constants.ts";
import { NetworkError } from "./errors.ts";

const TIMEOUT_MESSAGE = "the service did not answer in time";
const FAILURE_MESSAGE = "the service could not be reached";
const EMPTY_BODY_TEXT = "";
const EMPTY_BODY = null;

/** RQ-CLI-004: the status and the parsed JSON body of an answer. */
export interface HttpResponse {
  readonly status: number;
  readonly body: unknown;
}

/** RQ-CLI-004: sends one HTTP call; the port that the typed client depends on. */
export interface Transport {
  send(method: string, path: string, body?: unknown): Promise<HttpResponse>;
}

/** RQ-CLI-004: the subset of fetch used by the transport, replaceable by a fake in tests. */
export type FetchLike = (url: string, init: RequestInit) => Promise<Response>;

/** RQ-CLI-004: performs JSON calls with a timeout; any abort or failure becomes a NetworkError. */
export class FetchTransport implements Transport {
  readonly timeoutMs: number;
  private readonly baseUrl: string;
  private readonly fetchImpl: FetchLike;

  constructor(baseUrl: string, timeoutMs: number = REQUEST_TIMEOUT_MS, fetchImpl: FetchLike = fetch) {
    this.baseUrl = baseUrl;
    this.timeoutMs = timeoutMs;
    this.fetchImpl = fetchImpl;
  }

  // RQ-CLI-004
  async send(method: string, path: string, body?: unknown): Promise<HttpResponse> {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    const expired = new Promise<never>((_resolve, reject) => {
      timer = setTimeout(() => {
        controller.abort();
        reject(new NetworkError(TIMEOUT_MESSAGE));
      }, this.timeoutMs);
    });
    try {
      return await Promise.race([this.exchange(method, path, body, controller.signal), expired]);
    } catch (error) {
      if (error instanceof NetworkError) {
        throw error;
      }
      throw new NetworkError(FAILURE_MESSAGE);
    } finally {
      clearTimeout(timer);
    }
  }

  private async exchange(method: string, path: string, body: unknown, signal: AbortSignal): Promise<HttpResponse> {
    const headers: Record<string, string> = { [HEADER_ACCEPT]: JSON_MEDIA_TYPE };
    if (body !== undefined) {
      headers[HEADER_CONTENT_TYPE] = JSON_MEDIA_TYPE;
    }
    const init: RequestInit = {
      method,
      headers,
      signal,
      body: body === undefined ? undefined : JSON.stringify(body),
    };
    const response = await this.fetchImpl(this.baseUrl + path, init);
    const text = await response.text();
    return { status: response.status, body: text === EMPTY_BODY_TEXT ? EMPTY_BODY : (JSON.parse(text) as unknown) };
  }
}
