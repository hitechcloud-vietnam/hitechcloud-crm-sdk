/** Main HiTechCloud CRM client. */

import { HttpClient, HttpClientOptions, PRODUCTION_URL, SANDBOX_URL } from "./httpClient";
import {
  CrudResource,
  FilesResource,
  WebhooksResource,
  ImportsResource,
  ExportsResource,
} from "./resources";

export interface CRMClientOptions extends HttpClientOptions {
  /** Shortcut to target the sandbox environment. */
  sandbox?: boolean;
}

export class CRMClient {
  static readonly PRODUCTION_URL = PRODUCTION_URL;
  static readonly SANDBOX_URL = SANDBOX_URL;

  private http: HttpClient;

  // Standard CRUD resources
  readonly contacts: CrudResource;
  readonly companies: CrudResource;
  readonly deals: CrudResource;
  readonly pipelines: CrudResource;
  readonly stages: CrudResource;
  readonly activities: CrudResource;
  readonly tasks: CrudResource;
  readonly calls: CrudResource;
  readonly emails: CrudResource;
  readonly meetings: CrudResource;
  readonly notes: CrudResource;
  readonly tags: CrudResource;
  readonly segments: CrudResource;
  readonly customFields: CrudResource;
  readonly leadSources: CrudResource;
  readonly products: CrudResource;
  readonly quotes: CrudResource;
  readonly users: CrudResource;
  readonly teams: CrudResource;

  // Special resources
  readonly files: FilesResource;
  readonly webhooks: WebhooksResource;
  readonly imports: ImportsResource;
  readonly exports: ExportsResource;

  constructor(options: CRMClientOptions = {}) {
    const baseUrl = options.sandbox ? SANDBOX_URL : options.baseUrl || PRODUCTION_URL;
    this.http = new HttpClient({ ...options, baseUrl });

    this.contacts = new CrudResource(this.http, "contacts");
    this.companies = new CrudResource(this.http, "companies");
    this.deals = new CrudResource(this.http, "deals");
    this.pipelines = new CrudResource(this.http, "pipelines");
    this.stages = new CrudResource(this.http, "stages");
    this.activities = new CrudResource(this.http, "activities");
    this.tasks = new CrudResource(this.http, "tasks");
    this.calls = new CrudResource(this.http, "calls");
    this.emails = new CrudResource(this.http, "emails");
    this.meetings = new CrudResource(this.http, "meetings");
    this.notes = new CrudResource(this.http, "notes");
    this.tags = new CrudResource(this.http, "tags");
    this.segments = new CrudResource(this.http, "segments");
    this.customFields = new CrudResource(this.http, "custom-fields");
    this.leadSources = new CrudResource(this.http, "lead-sources");
    this.products = new CrudResource(this.http, "products");
    this.quotes = new CrudResource(this.http, "quotes");
    this.users = new CrudResource(this.http, "users");
    this.teams = new CrudResource(this.http, "teams");

    this.files = new FilesResource(this.http);
    this.webhooks = new WebhooksResource(this.http);
    this.imports = new ImportsResource(this.http);
    this.exports = new ExportsResource(this.http);
  }

  /** Force an OAuth2 token exchange and return the token data. */
  fetchToken(): Promise<Record<string, any>> {
    return this.http.fetchToken();
  }

  /** Use a pre-issued access token. */
  setToken(token: string): void {
    this.http.setToken(token);
  }
}
