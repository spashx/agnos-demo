// RQ-CLI-002, RQ-CLI-004, DEC-CLI-002 (ADR-CLI-001)

const NETWORK_ERROR_NAME = "NetworkError";
const SERVICE_ERROR_NAME = "ServiceError";

/** RQ-CLI-004: the service could not be reached or did not answer in time. */
export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = NETWORK_ERROR_NAME;
  }
}

/** RQ-CLI-002: the service answered with an error status; carries the code, message and status. */
export class ServiceError extends Error {
  readonly code: string;
  readonly status: number;

  constructor(code: string, message: string, status: number) {
    super(message);
    this.name = SERVICE_ERROR_NAME;
    this.code = code;
    this.status = status;
  }
}
