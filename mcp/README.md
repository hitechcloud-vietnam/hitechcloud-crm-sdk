# HiTechCloud CRM MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes
core HiTechCloud CRM operations as tools an AI assistant can call.

## Install

```bash
cd mcp
npm install
```

## Configure

Set OAuth2 client credentials (the server fetches and caches the access token):

```bash
export CRM_CLIENT_ID="YOUR_CLIENT_ID"
export CRM_CLIENT_SECRET="YOUR_CLIENT_SECRET"
export CRM_SCOPE="contacts:read contacts:write deals:read deals:write"
# Optional:
# export CRM_BASE_URL="https://crm-gateways-sandbox.hitechcloud.vn"
# export CRM_TOKEN="crm_at_..."   # use a pre-issued token instead
```

## Run

```bash
npm start
```

### Claude Desktop / MCP client config

```json
{
  "mcpServers": {
    "hitechcloud-crm": {
      "command": "node",
      "args": ["/absolute/path/to/mcp/server.js"],
      "env": {
        "CRM_CLIENT_ID": "YOUR_CLIENT_ID",
        "CRM_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
        "CRM_SCOPE": "contacts:read contacts:write deals:read deals:write"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `list_contacts` | List contacts with filters |
| `get_contact` | Get a contact by ID |
| `create_contact` | Create a contact |
| `list_deals` | List deals with filters |
| `create_deal` | Create a deal |
| `list_companies` | List companies |
| `list_pipelines` | List sales pipelines |
| `create_note` | Attach a note to a contact/company/deal |

## License

MIT
