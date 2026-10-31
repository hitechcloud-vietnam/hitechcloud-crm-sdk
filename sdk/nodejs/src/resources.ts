/** CRM resource classes. */

import { HttpClient, QueryParams } from "./httpClient";
import { readFile } from "fs/promises";
import { basename } from "path";

export interface Envelope<T = any> {
  status: string;
  data: T;
  meta?: { pagination?: Record<string, number | boolean> };
}

export interface BulkOperation {
  op: "create" | "update" | "delete";
  data: Record<string, any>;
}

const BULK_RESOURCES = new Set(["contacts", "deals"]);

/** Generic CRUD resource bound to a collection path. */
export class CrudResource {
  constructor(protected http: HttpClient, protected path: string) {}

  list<T = any>(params: QueryParams = {}): Promise<Envelope<T[]>> {
    return this.http.get(`/v1/${this.path}`, params);
  }

  get<T = any>(id: string): Promise<Envelope<T>> {
    return this.http.get(`/v1/${this.path}/${encodeURIComponent(id)}`);
  }

  create<T = any>(data: Record<string, any>): Promise<Envelope<T>> {
    return this.http.post(`/v1/${this.path}`, data);
  }

  update<T = any>(id: string, data: Record<string, any>): Promise<Envelope<T>> {
    return this.http.patch(`/v1/${this.path}/${encodeURIComponent(id)}`, data);
  }

  delete<T = any>(id: string): Promise<Envelope<T>> {
    return this.http.delete(`/v1/${this.path}/${encodeURIComponent(id)}`);
  }

  bulk<T = any>(operations: BulkOperation[]): Promise<Envelope<T>> {
    if (!BULK_RESOURCES.has(this.path)) {
      throw new Error(`Bulk operations are not supported for ${this.path}`);
    }
    return this.http.post(`/v1/${this.path}/bulk`, { operations });
  }
}

/** Files: multipart upload, metadata and binary download URL. */
export class FilesResource extends CrudResource {
  constructor(http: HttpClient) {
    super(http, "files");
  }

  /** Upload a file (by path or Blob) and attach it to a resource. */
  async upload<T = any>(
    file: string | Blob,
    resourceType: "contact" | "company" | "deal",
    resourceId: string,
    filename?: string
  ): Promise<Envelope<T>> {
    const form = new FormData();
    if (typeof file === "string") {
      const buf = await readFile(file);
      form.append("file", new Blob([buf]), filename || basename(file));
    } else {
      form.append("file", file, filename || "upload.bin");
    }
    form.append("resource_type", resourceType);
    form.append("resource_id", resourceId);
    return this.http.postForm(`/v1/files`, form);
  }

  downloadUrl(id: string): string {
    return `${this.http.baseUrl}/v1/files/${encodeURIComponent(id)}/download`;
  }

  create(): Promise<never> {
    return Promise.reject(new Error("Use FilesResource.upload() to create files"));
  }
}

/** Webhook registration management. */
export class WebhooksResource {
  constructor(private http: HttpClient) {}

  list<T = any>(): Promise<Envelope<T[]>> {
    return this.http.get(`/v1/webhooks`);
  }

  register<T = any>(url: string, events: string[], secret?: string): Promise<Envelope<T>> {
    const body: Record<string, any> = { url, events };
    if (secret) body.secret = secret;
    return this.http.post(`/v1/webhooks`, body);
  }

  delete<T = any>(id: string): Promise<Envelope<T>> {
    return this.http.delete(`/v1/webhooks/${encodeURIComponent(id)}`);
  }
}

/** Asynchronous CSV import jobs. */
export class ImportsResource {
  constructor(private http: HttpClient) {}

  async create<T = any>(file: string | Blob, entity: "contact" | "company", filename?: string): Promise<Envelope<T>> {
    const form = new FormData();
    if (typeof file === "string") {
      const buf = await readFile(file);
      form.append("file", new Blob([buf]), filename || basename(file));
    } else {
      form.append("file", file, filename || "import.csv");
    }
    form.append("entity", entity);
    return this.http.postForm(`/v1/imports`, form);
  }

  get<T = any>(id: string): Promise<Envelope<T>> {
    return this.http.get(`/v1/imports/${encodeURIComponent(id)}`);
  }
}

/** Asynchronous CSV export jobs. */
export class ExportsResource {
  constructor(private http: HttpClient) {}

  create<T = any>(entity: "contact" | "deal" | "activity", filter?: Record<string, any>): Promise<Envelope<T>> {
    const body: Record<string, any> = { entity };
    if (filter) body.filter = filter;
    return this.http.post(`/v1/exports`, body);
  }

  get<T = any>(id: string): Promise<Envelope<T>> {
    return this.http.get(`/v1/exports/${encodeURIComponent(id)}`);
  }
}
