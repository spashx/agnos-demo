// RQ-WEB-002, RQ-WEB-003, RQ-WEB-004, RQ-WEB-005, DEC-WEB-001, DEC-WEB-002 (ADR-WEB-001)
import type { RoombookClient } from "../client.ts";
import { HTTP_GET, HTTP_POST, HTTP_STATUS_NOT_FOUND, HTTP_STATUS_OK } from "../constants.ts";
import { NetworkError, ServiceError } from "../errors.ts";
import type { ReservationRequest } from "../types.ts";
import { ERROR_TEXT, INVALID_FORM_TEXT, UNAVAILABLE_TEXT, bookedText, cancelledText, fallbackErrorText } from "./labels.ts";
import { FORM_FIELD, ROUTE } from "./routes.ts";
import { EMPTY_VALUES, renderNotFound, renderPage } from "./views.ts";
import type { Banner, FormValues } from "./views.ts";

const HTTP_STATUS_BAD_REQUEST = 400;
const HTTP_STATUS_UNAVAILABLE = 503;
const CONTENT_TYPE_HTML = "text/html; charset=utf-8";
const CONTENT_TYPE_CSS = "text/css; charset=utf-8";
const LOCAL_DATETIME_PATTERN = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?$/;
const MINUTE_PRECISION_LENGTH = 16;
export const SECONDS_SUFFIX = ":00";
/** DEC-WEB-002: the form collects local times without a zone; the interface books them in UTC. */
export const BOOKING_UTC_OFFSET = "+00:00";
const MIN_ATTENDEES = 1;
const NO_TEXT = "";

/** RQ-WEB-001: a request as the app sees it, independent of the HTTP library. */
export interface UiRequest {
  readonly method: string;
  readonly path: string;
  readonly form: Readonly<Record<string, string>>;
}

/** RQ-WEB-001: an answer as the app produces it, written to the socket by the server. */
export interface UiResponse {
  readonly status: number;
  readonly contentType: string;
  readonly body: string;
}

/** DEC-WEB-002: the interface logic, a function of a request and of the typed client, with no HTTP server inside. */
export class BookingApp {
  private readonly client: RoombookClient;
  private readonly stylesheet: string;

  constructor(client: RoombookClient, stylesheet: string) {
    this.client = client;
    this.stylesheet = stylesheet;
  }

  /** RQ-WEB-001: routes one request to the page, the stylesheet, the booking or the cancellation. */
  async handle(request: UiRequest): Promise<UiResponse> {
    if (request.method === HTTP_GET && request.path === ROUTE.styles) {
      return { status: HTTP_STATUS_OK, contentType: CONTENT_TYPE_CSS, body: this.stylesheet };
    }
    if (request.method === HTTP_GET && request.path === ROUTE.home) {
      return this.page(HTTP_STATUS_OK);
    }
    if (request.method === HTTP_POST && request.path === ROUTE.book) {
      return this.book(request.form);
    }
    if (request.method === HTTP_POST && request.path === ROUTE.cancel) {
      return this.cancel(request.form);
    }
    return { status: HTTP_STATUS_NOT_FOUND, contentType: CONTENT_TYPE_HTML, body: renderNotFound() };
  }

  /** RQ-WEB-002, RQ-WEB-003: books the room asked for, or answers why it could not. */
  private async book(form: Readonly<Record<string, string>>): Promise<UiResponse> {
    const values = readValues(form);
    const request = toReservationRequest(values);
    if (request === undefined) {
      return this.page(HTTP_STATUS_BAD_REQUEST, { kind: "error", text: INVALID_FORM_TEXT }, values);
    }
    try {
      const reservation = await this.client.createReservation(request);
      return this.page(HTTP_STATUS_OK, { kind: "success", text: bookedText(reservation.id), reservationId: reservation.id });
    } catch (error) {
      return this.failure(error, values);
    }
  }

  /** RQ-WEB-004, RQ-WEB-003: cancels the reservation named in the form, or answers why it could not. */
  private async cancel(form: Readonly<Record<string, string>>): Promise<UiResponse> {
    const id = (form[FORM_FIELD.reservationId] ?? NO_TEXT).trim();
    if (id === NO_TEXT) {
      return this.page(HTTP_STATUS_BAD_REQUEST, { kind: "error", text: INVALID_FORM_TEXT });
    }
    try {
      await this.client.cancelReservation(id);
      return this.page(HTTP_STATUS_OK, { kind: "success", text: cancelledText(id) });
    } catch (error) {
      return this.failure(error, EMPTY_VALUES);
    }
  }

  /** RQ-WEB-003, RQ-WEB-005: turns a service error into an error banner and a network error into the unavailable page. */
  private async failure(error: unknown, values: FormValues): Promise<UiResponse> {
    if (error instanceof ServiceError) {
      const text = ERROR_TEXT[error.code] ?? fallbackErrorText(error.code);
      return this.page(error.status, { kind: "error", text }, values);
    }
    if (error instanceof NetworkError) {
      return unavailablePage();
    }
    throw error;
  }

  /** RQ-WEB-001: the page with the current rooms; when the rooms cannot be read the unavailable page is shown instead. */
  private async page(status: number, banner?: Banner, values?: FormValues): Promise<UiResponse> {
    try {
      const rooms = await this.client.listRooms();
      return { status, contentType: CONTENT_TYPE_HTML, body: renderPage({ rooms, formsEnabled: true, banner, values }) };
    } catch (error) {
      if (error instanceof NetworkError) {
        return unavailablePage();
      }
      throw error;
    }
  }
}

/** RQ-WEB-005: the page shown while the service does not answer, with no form since none could succeed. */
function unavailablePage(): UiResponse {
  const body = renderPage({ rooms: [], formsEnabled: false, banner: { kind: "warning", text: UNAVAILABLE_TEXT } });
  return { status: HTTP_STATUS_UNAVAILABLE, contentType: CONTENT_TYPE_HTML, body };
}

/** RQ-WEB-002: reads the booking fields of a submitted form; a missing field is an empty text. */
export function readValues(form: Readonly<Record<string, string>>): FormValues {
  const read = (field: string): string => (form[field] ?? NO_TEXT).trim();
  return {
    roomId: read(FORM_FIELD.roomId),
    organizer: read(FORM_FIELD.organizer),
    start: read(FORM_FIELD.start),
    end: read(FORM_FIELD.end),
    attendees: read(FORM_FIELD.attendees),
  };
}

/** RQ-WEB-002: converts a local date and time typed in the form to an ISO 8601 text with the booking offset. */
export function toIsoWithOffset(local: string): string | undefined {
  if (!LOCAL_DATETIME_PATTERN.test(local)) {
    return undefined;
  }
  const withSeconds = local.length === MINUTE_PRECISION_LENGTH ? local + SECONDS_SUFFIX : local;
  return withSeconds + BOOKING_UTC_OFFSET;
}

/** RQ-WEB-002: builds the service request from the form values, or nothing when a value is missing or invalid. */
export function toReservationRequest(values: FormValues): ReservationRequest | undefined {
  const start = toIsoWithOffset(values.start);
  const end = toIsoWithOffset(values.end);
  const attendees = Number(values.attendees);
  const complete = values.roomId !== NO_TEXT && values.organizer !== NO_TEXT && values.attendees !== NO_TEXT;
  if (!complete || start === undefined || end === undefined || !Number.isInteger(attendees) || attendees < MIN_ATTENDEES) {
    return undefined;
  }
  return { roomId: values.roomId, organizer: values.organizer, start, end, attendees };
}
