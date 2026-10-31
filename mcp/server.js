#!/usr/bin/env node
/**
 * HiTechCloud CRM MCP Server
 *
 * A Model Context Protocol server exposing core HiTechCloud CRM operations as
 * tools. Authenticates with the OAuth2 client_credentials flow and caches the
 * access token.
 *
 * Environment:
 *   CRM_BASE_URL       (default https://crm-gateways.hitechcloud.vn)
 *   CRM_CLIENT_ID      OAuth2 client id       (required)
 *   CRM_CLIENT_SECRET  OAuth2 client secret   (required)
 *   CRM_SCOPE          space-separated scopes (optional)
 *   CRM_TOKEN          pre-issued token, skips the OAuth exchange (optional)
 */
"use strict";

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require("@modelcontextprotocol/sdk/types.js");

const BASE_URL = (process.env.CRM_BASE_URL || "https://crm-gateways.hitechcloud.vn").replace(/\/+$/, "");
const CLIENT_ID = process.env.CRM_CLIENT_ID;
const CLIENT_SECRET = process.env.CRM_CLIENT_SECRET;
const SCOPE = process.env.CRM_SCOPE;

let token = process.env.CRM_TOKEN || null;
let tokenExpiry = token ? Number.POSITIVE_INFINITY : 0;

async function ensureToken() {
  if (token && Date.now() < tokenExpiry) return token;
  if (!CLIENT_ID || !CLIENT_SECRET) {
    if (token) return token;
    throw new Error("Set CRM_CLIENT_ID and CRM_CLIENT_SECRET (or CRM_TOKEN)");
  }
  const payload = {
    grant_type: "client_credentials",
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
  };
  if (SCOPE) payload.scope = SCOPE;
  const res = await fetch(`${BASE_URL}/v1/oauth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await res.json();
  if (res.status >= 400) {
    throw new Error(`Token exchange failed: ${body.message || res.status}`);
  }
  token = body.data.access_token;
  const expiresIn = Number(body.data.expires_in || 3600);
  tokenExpiry = Date.now() + Math.max(expiresIn - 60, 30) * 1000;
  return token;
}

async function apiCall(method, path, { params, json } = {}) {
  const t = await ensureToken();
  let url = `${BASE_URL}${path}`;
  if (params) {
    const qs = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null) qs.append(k, String(v));
    }
    const str = qs.toString();
    if (str) url += `?${str}`;
  }
  const opts = {
    method,
    headers: { Authorization: `Bearer ${t}`, Accept: "application/json" },
  };
  if (json !== undefined) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(json);
  }
  const res = await fetch(url, opts);
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

const TOOLS = [
  {
    name: "list_contacts",
    description: "List CRM contacts, optionally filtered by lifecycle_stage, company_id, tag or a search query q.",
    inputSchema: {
      type: "object",
      properties: {
        q: { type: "string" },
        lifecycle_stage: { type: "string" },
        company_id: { type: "string" },
        tag: { type: "string" },
        page: { type: "integer" },
        per_page: { type: "integer" },
      },
    },
  },
  {
    name: "get_contact",
    description: "Get a single contact by ID (e.g. con_8f2a1c9d).",
    inputSchema: { type: "object", properties: { id: { type: "string" } }, required: ["id"] },
  },
  {
    name: "create_contact",
    description: "Create a contact. Provide first_name and optionally last_name, email, phone, company_id, lifecycle_stage.",
    inputSchema: {
      type: "object",
      properties: {
        first_name: { type: "string" },
        last_name: { type: "string" },
        email: { type: "string" },
        phone: { type: "string" },
        company_id: { type: "string" },
        lifecycle_stage: { type: "string" },
      },
      required: ["first_name"],
    },
  },
  {
    name: "list_deals",
    description: "List CRM deals, optionally filtered by pipeline_id, stage_id or status (open|won|lost).",
    inputSchema: {
      type: "object",
      properties: {
        pipeline_id: { type: "string" },
        stage_id: { type: "string" },
        status: { type: "string" },
        page: { type: "integer" },
        per_page: { type: "integer" },
      },
    },
  },
  {
    name: "create_deal",
    description: "Create a deal. Requires title, pipeline_id and stage_id; optional amount, contact_id, expected_close_date.",
    inputSchema: {
      type: "object",
      properties: {
        title: { type: "string" },
        pipeline_id: { type: "string" },
        stage_id: { type: "string" },
        amount: { type: "number" },
        contact_id: { type: "string" },
        expected_close_date: { type: "string" },
      },
      required: ["title", "pipeline_id", "stage_id"],
    },
  },
  {
    name: "list_companies",
    description: "List CRM companies, optionally filtered by industry or a search query q.",
    inputSchema: {
      type: "object",
      properties: { q: { type: "string" }, industry: { type: "string" }, page: { type: "integer" }, per_page: { type: "integer" } },
    },
  },
  {
    name: "list_pipelines",
    description: "List sales pipelines and their stage counts.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "create_note",
    description: "Attach a note to a contact, company or deal.",
    inputSchema: {
      type: "object",
      properties: {
        body: { type: "string" },
        resource_type: { type: "string", enum: ["contact", "company", "deal"] },
        resource_id: { type: "string" },
      },
      required: ["body", "resource_type", "resource_id"],
    },
  },
];

const HANDLERS = {
  list_contacts: (a) => apiCall("GET", "/v1/contacts", { params: a }),
  get_contact: (a) => apiCall("GET", `/v1/contacts/${encodeURIComponent(a.id)}`),
  create_contact: (a) => apiCall("POST", "/v1/contacts", { json: a }),
  list_deals: (a) => apiCall("GET", "/v1/deals", { params: a }),
  create_deal: (a) => apiCall("POST", "/v1/deals", { json: a }),
  list_companies: (a) => apiCall("GET", "/v1/companies", { params: a }),
  list_pipelines: () => apiCall("GET", "/v1/pipelines"),
  create_note: (a) => apiCall("POST", "/v1/notes", { json: a }),
};

async function main() {
  const server = new Server(
    { name: "hitechcloud-crm", version: "1.0.0" },
    { capabilities: { tools: {} } }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    const handler = HANDLERS[name];
    if (!handler) throw new Error(`Unknown tool: ${name}`);
    try {
      const result = await handler(args || {});
      return { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] };
    } catch (err) {
      return {
        isError: true,
        content: [{ type: "text", text: `Error: ${err.message}` }],
      };
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("HiTechCloud CRM MCP server running on stdio");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
