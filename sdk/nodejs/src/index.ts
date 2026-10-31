/** HiTechCloud CRM SDK for Node.js / TypeScript. */

export { CRMClient, CRMClientOptions } from "./client";
export {
  HttpClient,
  HttpClientOptions,
  QueryParams,
  PRODUCTION_URL,
  SANDBOX_URL,
} from "./httpClient";
export {
  CrudResource,
  FilesResource,
  WebhooksResource,
  ImportsResource,
  ExportsResource,
  Envelope,
  BulkOperation,
} from "./resources";
export { verifyWebhookSignature, computeSignature } from "./webhooks";
export {
  CRMError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  ConflictError,
  ValidationError,
  RateLimitError,
  ServerError,
} from "./errors";
