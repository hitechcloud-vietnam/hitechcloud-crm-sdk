/** Low-level HTTP transport with OAuth2 client_credentials token management. */

import { CRMError, RateLimitError, mapError, ErrorBody } from "./errors";

export const PRODUCTION_URL = "https://crm-gateways.hitechcloud.vn";
export const SANDBOX_URL = "https://crm-gateways-sandbox.hitechcloud.vn";
const TOKEN_PATH = "/v1/oauth/token";
const VERSION = "1.0.0";

export interface HttpClientOptions {
  clientId?: string;
  clientSecret?: string;
  scope?: string;
  token?: string;
  baseUrl?: string;
  timeout?: number;
  maxRetries?: number;
}

export type QueryParams = Record<string, string | number | boolean | undefined>;

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export class HttpClient {
  readonly baseUrl: string;
  private clientId?: string;
  private clientSecret?: string;
  private scope?: string;
  private token?: string;
  private tokenExpiry = 0;
  private timeout: number;
  private maxRetries: number;

  constructor(opts: HttpClientOptions = {}) {
    this.baseUrl = (opts.baseUrl || PRODUCTION_URL).replace(/\/+$/, "");
    this.clientId = opts.clientId;
    this.clientSecret = opts.clientSecret;
    this.scope = opts.scope;
    this.token = opts.token;
    this.tokenExpiry = opts.token ? Number.POSITIVE_INFINITY : 0;
    this.timeout = opts.timeout ?? 30000;
    this.maxRetries = opts.maxRetries ?? 3;
  }

  setToken(token: string): void {
    this.token = token;
    this.tokenExpiry = Number.POSITIVE_INFINITY;
  }

  async fetchToken(): Promise<Record<string, any>> {
    if (!this.clientId || !this.clientSecret) {
      throw new CRMError("No client credentials configured");
    }
    const payload: Record<string, string> = {
      grant_type: "client_credentials",
      client_id: this.clientId,
      client_secret: this.clientSecret,
    };
    if (this.scope) payload.scope = this.scope;

    const res = await this.rawFetch("POST", this.baseUrl + TOKEN_PATH, {
      "Content-Type": "application/json",
    }, JSON.stringify(payload));
    const body = await this.parse(res);
    if (res.status >= 400) {
      throw mapError(res.status, body as ErrorBody);
    }
    const data = (body as any).data || {};
    this.token = data.access_token;
    const expiresIn = Number(data.expires_in ?? 3600);
    this.tokenExpiry = Date.now() + Math.max(expiresIn - 60, 30) * 1000;
    return data;
  }

  private async ensureToken(): Promise<void> {
    if (this.token && Date.now() < this.tokenExpiry) return;
    if (!this.clientId || !this.clientSecret) {
      if (this.token) return;
      throw new CRMError("No access token and no client credentials configured");
    }
    await this.fetchToken();
  }

  private async rawFetch(method: string, url: string, headers: Record<string, string>, body?: string | FormData): Promise<Response> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeout);
    try {
      return await fetch(url, { method, headers, body, signal: controller.signal });
    } finally {
      clearTimeout(timer);
    }
  }

  private async parse(res: Response): Promise<unknown> {
    const text = await res.text();
    if (!text) return null;
    try {
      return JSON.parse(text);
    } catch {
      return { message: text.slice(0, 200) };
    }
  }

  async request<T = any>(
    method: string,
    path: string,
    options: { params?: QueryParams; json?: unknown; form?: FormData; retryAuth?: boolean } = {}
  ): Promise<T> {
    await this.ensureToken();
    let retryAuth = options.retryAuth ?? true;

    let url = this.baseUrl + "/" + path.replace(/^\/+/, "");
    if (options.params) {
      const qs = new URLSearchParams();
      for (const [k, v] of Object.entries(options.params)) {
        if (v !== undefined && v !== null) qs.append(k, String(v));
      }
      const str = qs.toString();
      if (str) url += "?" + str;
    }

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      const headers: Record<string, string> = {
        Authorization: `Bearer ${this.token}`,
        "User-Agent": `hitechcloud-crm-node/${VERSION}`,
        Accept: "application/json",
      };
      let body: string | FormData | undefined;
      if (options.form) {
        body = options.form; // fetch sets the multipart boundary
      } else if (options.json !== undefined) {
        headers["Content-Type"] = "application/json";
        body = JSON.stringify(options.json);
      }

      let res: Response;
      try {
        res = await this.rawFetch(method, url, headers, body);
      } catch (err) {
        if (attempt < this.maxRetries) {
          await sleep(Math.pow(2, attempt) * 1000);
          continue;
        }
        throw new CRMError(`Request failed: ${(err as Error).message}`);
      }

      if (res.status === 401 && retryAuth && this.clientId) {
        await this.fetchToken();
        retryAuth = false;
        attempt--; // does not count against retries
        continue;
      }

      if (res.status === 429) {
        const retryAfter = parseInt(res.headers.get("retry-after") || "60", 10);
        if (attempt < this.maxRetries) {
          await sleep(retryAfter * 1000);
          continue;
        }
        const errBody = (await this.parse(res)) as ErrorBody;
        throw new RateLimitError(errBody?.message || "Rate limit exceeded", retryAfter, errBody?.code);
      }

      if (res.status >= 500 && attempt < this.maxRetries) {
        await sleep(Math.pow(2, attempt) * 1000);
        continue;
      }

      const parsed = await this.parse(res);
      if (res.status >= 400) {
        throw mapError(res.status, (parsed || {}) as ErrorBody, parseInt(res.headers.get("retry-after") || "0", 10) || undefined);
      }
      return parsed as T;
    }
    throw new CRMError("Request failed after retries");
  }

  get<T = any>(path: string, params?: QueryParams): Promise<T> {
    return this.request<T>("GET", path, { params });
  }
  post<T = any>(path: string, json?: unknown): Promise<T> {
    return this.request<T>("POST", path, { json });
  }
  postForm<T = any>(path: string, form: FormData): Promise<T> {
    return this.request<T>("POST", path, { form });
  }
  patch<T = any>(path: string, json?: unknown): Promise<T> {
    return this.request<T>("PATCH", path, { json });
  }
  delete<T = any>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }
}
