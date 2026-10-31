/** Typed error hierarchy for the HiTechCloud CRM SDK. */

export interface ErrorBody {
  status?: string;
  code?: string;
  message?: string;
  errors?: Record<string, string[]>;
}

export class CRMError extends Error {
  statusCode?: number;
  code?: string;
  errors: Record<string, string[]>;

  constructor(message: string, statusCode?: number, code?: string, errors?: Record<string, string[]>) {
    super(message);
    this.name = "CRMError";
    this.statusCode = statusCode;
    this.code = code;
    this.errors = errors || {};
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class AuthenticationError extends CRMError {
  constructor(message = "Authentication failed", code?: string, errors?: Record<string, string[]>) {
    super(message, 401, code, errors);
    this.name = "AuthenticationError";
  }
}

export class AuthorizationError extends CRMError {
  constructor(message = "Access denied", code?: string, errors?: Record<string, string[]>) {
    super(message, 403, code, errors);
    this.name = "AuthorizationError";
  }
}

export class NotFoundError extends CRMError {
  constructor(message = "Resource not found", code?: string, errors?: Record<string, string[]>) {
    super(message, 404, code, errors);
    this.name = "NotFoundError";
  }
}

export class ConflictError extends CRMError {
  constructor(message = "Conflict", code?: string, errors?: Record<string, string[]>) {
    super(message, 409, code, errors);
    this.name = "ConflictError";
  }
}

export class ValidationError extends CRMError {
  constructor(message = "Validation error", statusCode = 422, code?: string, errors?: Record<string, string[]>) {
    super(message, statusCode, code, errors);
    this.name = "ValidationError";
  }
}

export class RateLimitError extends CRMError {
  retryAfter: number;
  constructor(message = "Rate limit exceeded", retryAfter = 60, code?: string, errors?: Record<string, string[]>) {
    super(message, 429, code, errors);
    this.name = "RateLimitError";
    this.retryAfter = retryAfter;
  }
}

export class ServerError extends CRMError {
  constructor(message = "Server error", statusCode = 500, code?: string, errors?: Record<string, string[]>) {
    super(message, statusCode, code, errors);
    this.name = "ServerError";
  }
}

export function mapError(status: number, body: ErrorBody, retryAfter?: number): CRMError {
  const message = body?.message || `HTTP ${status}`;
  const code = body?.code;
  const errors = body?.errors;
  switch (status) {
    case 400:
      return new ValidationError(message, 400, code, errors);
    case 401:
      return new AuthenticationError(message, code, errors);
    case 403:
      return new AuthorizationError(message, code, errors);
    case 404:
      return new NotFoundError(message, code, errors);
    case 409:
      return new ConflictError(message, code, errors);
    case 422:
      return new ValidationError(message, 422, code, errors);
    case 429:
      return new RateLimitError(message, retryAfter ?? 60, code, errors);
    default:
      if (status >= 500) return new ServerError(message, status, code, errors);
      return new CRMError(message, status, code, errors);
  }
}
