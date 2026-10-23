// RQ-CLI-004, RQ-CLI-005, DEC-CLI-002 (ADR-CLI-001)

/** RQ-CLI-004: a call that gets no answer within this many milliseconds is aborted. */
export const REQUEST_TIMEOUT_MS = 5000;

/** RQ-CLI-005: base URL of the booking service when none is configured. */
export const DEFAULT_BASE_URL = "http://localhost:8080";

/** RQ-CLI-005: route listing the rooms. */
export const ROOMS_PATH = "/rooms";

/** RQ-CLI-005: route creating and cancelling reservations. */
export const RESERVATIONS_PATH = "/reservations";

export const HTTP_GET = "GET";
export const HTTP_POST = "POST";
export const HTTP_DELETE = "DELETE";

export const HEADER_ACCEPT = "Accept";
export const HEADER_CONTENT_TYPE = "Content-Type";
export const JSON_MEDIA_TYPE = "application/json";

export const HTTP_STATUS_OK = 200;
export const HTTP_STATUS_CREATED = 201;
export const HTTP_STATUS_NO_CONTENT = 204;
export const HTTP_STATUS_NOT_FOUND = 404;
export const HTTP_STATUS_CONFLICT = 409;
export const HTTP_STATUS_UNPROCESSABLE = 422;
export const HTTP_STATUS_INTERNAL_ERROR = 500;

/** RQ-CLI-002: statuses from this value upwards are error responses. */
export const HTTP_ERROR_STATUS_MIN = 400;

/** RQ-CLI-002: code used when an error response carries no usable error body. */
export const UNKNOWN_ERROR_CODE = "UNKNOWN";
export const UNKNOWN_ERROR_MESSAGE = "unexpected error response";
