// RQ-CLI-001, RQ-CLI-002, DEC-CLI-002 (ADR-CLI-001)
import { HTTP_DELETE, HTTP_ERROR_STATUS_MIN, HTTP_GET, HTTP_POST, RESERVATIONS_PATH, ROOMS_PATH, UNKNOWN_ERROR_CODE, UNKNOWN_ERROR_MESSAGE } from "./constants.ts";
import { ServiceError } from "./errors.ts";
import type { HttpResponse, Transport } from "./transport.ts";
import type { ErrorBody, Reservation, ReservationRequest, Room } from "./types.ts";

const PATH_SEPARATOR = "/";

/** RQ-CLI-001, RQ-CLI-002: typed operations of the booking service on top of a transport. */
export class RoombookClient {
  private readonly transport: Transport;

  constructor(transport: Transport) {
    this.transport = transport;
  }

  /** RQ-CLI-001: lists the rooms. */
  async listRooms(): Promise<Room[]> {
    const response = await this.call(HTTP_GET, ROOMS_PATH);
    return response.body as Room[];
  }

  /** RQ-CLI-001: creates a reservation and returns it. */
  async createReservation(request: ReservationRequest): Promise<Reservation> {
    const response = await this.call(HTTP_POST, RESERVATIONS_PATH, request);
    return response.body as Reservation;
  }

  /** RQ-CLI-001: cancels a reservation by identifier. */
  async cancelReservation(id: string): Promise<void> {
    await this.call(HTTP_DELETE, RESERVATIONS_PATH + PATH_SEPARATOR + encodeURIComponent(id));
  }

  /** RQ-CLI-002: returns the answer, or throws a ServiceError for an error status. */
  private async call(method: string, path: string, body?: unknown): Promise<HttpResponse> {
    const response = await this.transport.send(method, path, body);
    if (response.status >= HTTP_ERROR_STATUS_MIN) {
      throw toServiceError(response);
    }
    return response;
  }
}

/** RQ-CLI-002: maps an error answer to a ServiceError, with a fallback when the body is not an error body. */
function toServiceError(response: HttpResponse): ServiceError {
  const body = isErrorBody(response.body)
    ? response.body
    : { code: UNKNOWN_ERROR_CODE, message: UNKNOWN_ERROR_MESSAGE };
  return new ServiceError(body.code, body.message, response.status);
}

/** RQ-CLI-002: true when the value has the {code, message} shape of an error body. */
function isErrorBody(value: unknown): value is ErrorBody {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const candidate = value as Partial<ErrorBody>;
  return typeof candidate.code === "string" && typeof candidate.message === "string";
}
