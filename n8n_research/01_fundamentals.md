# n8n Fundamentals — Deep Reference

## 1. What n8n Is

**n8n** (short for "nodemation") is a fair-code workflow automation platform built on Node.js/TypeScript. Founded 2019 by Jan Oberhauser (Berlin). Tagline: "Secure Workflow Automation for Technical Teams."

### License — Fair-Code (not OSI open source)

- **Sustainable Use License** — source-available, self-hostable, extensible, but restricts reselling n8n as a competing hosted service.
- **n8n Enterprise License** — covers SSO, LDAP, external secrets, advanced RBAC, audit logs.

### Positioning vs Competitors

| Dimension | n8n | Zapier | Make | Activepieces |
|---|---|---|---|---|
| License | Fair-code | Closed SaaS | Closed SaaS | MIT (true OSS) |
| Self-host | Yes (first-class) | No | No | Yes |
| Pricing | Per-execution | Per-task | Per-operation | Free self-host |
| Code nodes | JS + Python, npm | Limited | Limited JS | Limited |
| AI/LangChain | First-class built-in | Limited | Limited | Growing |
| Target user | Technical teams | Non-technical | Power ops | Mid-range |

---

## 2. Architecture

### Tech Stack

- **Backend:** Node.js + TypeScript
- **Frontend:** Vue 3 + Pinia + Element Plus
- **Monorepo:** pnpm workspaces + Turborepo
- **Database:** SQLite (dev), PostgreSQL (production)
- **Queue:** Redis (BullMQ) for queue execution mode

### Monorepo Package Layout

| Package | Role |
|---|---|
| `packages/cli` | Server, API, webhook receiver, DB migrations |
| `packages/core` | Execution engine, credential decryption, binary-data stores |
| `packages/workflow` | Types, Workflow class, expression evaluator |
| `packages/editor-ui` | Vue frontend (canvas, panels, expression editor) |
| `packages/nodes-base` | All built-in integration nodes + credentials |
| `packages/@n8n/nodes-langchain` | AI/LangChain cluster nodes |

### Execution Modes

**Regular (default):** Single process handles everything — API, UI, webhooks, execution.

**Queue mode (production):**
- Main instance(s): receive webhooks, run triggers, serve UI/API
- Workers (`n8n worker`): pull jobs from Redis, execute workflows
- Redis: BullMQ job queue
- PostgreSQL required (SQLite not safe for concurrent access)

Set via `EXECUTIONS_MODE=queue`.

### Execution Lifecycle

1. Trigger fires (webhook, schedule, poll)
2. Main creates execution record in DB
3. In queue mode, execution ID pushed to Redis
4. Worker claims job, runs nodes in topological order
5. Each node returns `INodeExecutionData[][]`
6. Results streamed back via Redis pub/sub for live UI
7. Final status persisted (success/error/canceled)

---

## 3. Core Concepts

### Workflow

A directed graph of Nodes + Connections. Key fields:
- `name`, `id`, `active` (triggers armed)
- `nodes[]`, `connections{}`
- `settings` (timezone, error workflow, timeout)
- `staticData` (persistent mutable scratchpad)
- `pinData` (editor-only test fixtures)

### Items & Data Structure

Data between nodes = **array of items**:

```json
[
  { "json": { "name": "Ada", "email": "ada@example.com" }, "binary": {}, "pairedItem": 0 },
  { "json": { "name": "Grace", "email": "grace@example.com" } }
]
```

- **`json`** — required, the item's data. Expressions read from here via `$json.field`
- **`binary`** — optional, map of binary attachments (base64 + mimeType)
- **`pairedItem`** — lineage marker for upstream item tracking

### Connections

Stored keyed by **source node name** (not ID):

```json
"connections": {
  "Webhook": {
    "main": [[{ "node": "Set", "type": "main", "index": 0 }]]
  }
}
```

Shape: `connections[sourceName][outputType][outputIndex] = [targets]`

- `IF` node: output 0 = true, output 1 = false
- Multiple targets per output = fan-out (items copied)
- AI nodes use `ai_languageModel`, `ai_memory`, `ai_tool`, etc.

### Credentials

- Separate objects from workflows, referenced by `{id, name}`
- Stored AES-256 encrypted using `N8N_ENCRYPTION_KEY`
- Never inlined in workflow exports
- Types: apiKey, Basic Auth, OAuth2, JWT, SSH, custom

### Static Data

- `getWorkflowStaticData('global' | 'node')` — persistent mutable blob
- Common use: "last-processed timestamp" for polling, dedup state
- Only persisted during production runs (not manual testing)

### Pinning

- Freeze a node's output in the editor for testing
- Ignored in production executions
- Stored in `pinData{}` keyed by node name

### Sub-Workflows

- Invoked via Execute Sub-workflow node
- Target by ID, file, URL, or inline JSON
- Sub-workflow starts with Execute Sub-workflow Trigger node
- Returns last node's output to parent

---

## 4. Node Types

### Trigger Nodes

| Node | Behavior |
|---|---|
| Manual Trigger | "Click to test" in editor |
| Webhook | Registers URL, starts workflow on HTTP request |
| Schedule Trigger | Cron or human-friendly interval |
| Chat Trigger | Opens chat widget for AI agent interaction |
| Error Trigger | Fires when another workflow errors |
| App triggers | Gmail, Slack, GitHub, Stripe, etc. |

### Core / Logic Nodes

| Node | Purpose |
|---|---|
| HTTP Request | Universal REST client with auth, pagination, retry |
| Code | JS or Python; "Run Once for All" vs "Each Item" |
| IF | Two-branch boolean (true/false outputs) |
| Switch | Multi-branch by rules or expression |
| Merge | Combine inputs (Append, Combine, Choose Branch) |
| Set / Edit Fields | Add, remove, rename fields |
| Filter | Drop items not matching conditions |
| SplitInBatches | Rate-limit-safe batch iteration |
| Wait | Pause by duration, datetime, or webhook resume |
| Execute Sub-workflow | Call another workflow |

### AI / LangChain Nodes

Use cluster-node connection model — root node + typed sub-connections:

**Root nodes:** AI Agent (Tools/ReAct/SQL), Basic LLM Chain, Retrieval QA Chain, Summarization Chain

**Sub-nodes:**

| Type | Examples |
|---|---|
| `ai_languageModel` | OpenAI, Anthropic, Gemini, Groq, Ollama |
| `ai_memory` | Window Buffer, Redis, Postgres Chat Memory |
| `ai_tool` | Calculator, SerpAPI, HTTP Request Tool, Workflow Tool, Code Tool |
| `ai_embedding` | OpenAI Embeddings, Cohere, HuggingFace |
| `ai_vectorStore` | Pinecone, Qdrant, Supabase, PGVector |
| `ai_outputParser` | Structured Output Parser (Zod schema) |

Cluster connections example:
```json
"connections": {
  "OpenAI Chat Model":    { "ai_languageModel": [[{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]] },
  "Window Buffer Memory": { "ai_memory":        [[{ "node": "AI Agent", "type": "ai_memory",        "index": 0 }]] },
  "Calculator":           { "ai_tool":          [[{ "node": "AI Agent", "type": "ai_tool",          "index": 0 }]] },
  "Chat Trigger":         { "main":             [[{ "node": "AI Agent", "type": "main",             "index": 0 }]] }
}
```

---

## 5. Expression Language

### Syntax

Any field wrapped in `{{ }}` is evaluated as JavaScript. Parameter strings starting with `=` are expression-mode.

### Built-In Variables

| Variable | What it is |
|---|---|
| `$json` | Current item's `.json` payload |
| `$binary` | Current item's binary attachments |
| `$input` | Proxy: `.all()`, `.first()`, `.last()`, `.item` |
| `$('Node Name')` | Access output of named node |
| `$workflow` | `.id`, `.name`, `.active` |
| `$execution` | `.id`, `.mode`, `.resumeUrl` |
| `$env` | Process environment (gated by config) |
| `$now` / `$today` | Luxon DateTime objects |
| `$itemIndex` / `$runIndex` | Loop indices |

### Examples

```js
{{ $json.email }}
{{ $json.age > 18 ? 'adult' : 'minor' }}
{{ $now.minus({ days: 7 }).toISO() }}
{{ $('HTTP Request').item.json.data[0].id }}
{{ $input.all().reduce((s, i) => s + i.json.amount, 0) }}
```

---

## 6. Workflow JSON Structure

### Top-Level Schema

```json
{
  "name": "My Workflow",
  "active": true,
  "nodes": [],
  "connections": {},
  "settings": { "executionOrder": "v1", "timezone": "Europe/Berlin" },
  "pinData": {},
  "staticData": null,
  "versionId": "uuid",
  "id": "xV2p9ZkL1aM3qN8b",
  "tags": [],
  "meta": {}
}
```

### Node Object

```json
{
  "id": "uuid",
  "name": "Webhook",
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 2,
  "position": [240, 300],
  "parameters": { "httpMethod": "POST", "path": "lead-intake" },
  "credentials": { "httpHeaderAuth": { "id": "7", "name": "My Key" } },
  "disabled": false,
  "continueOnFail": false
}
```

- `type` — namespaced: `n8n-nodes-base.*`, `@n8n/n8n-nodes-langchain.*`, community `n8n-nodes-*.*`
- `typeVersion` — pins node schema version
- Expression-mode params stored as `"={{ $json.email }}"`

---

## 7. Self-Hosting

### Installation

```bash
# Quick try
npx n8n

# Docker (recommended)
docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n

# npm global
npm install -g n8n && n8n start
```

### Critical Environment Variables

| Variable | Role |
|---|---|
| `N8N_ENCRYPTION_KEY` | AES key for all credentials (generate once, never lose) |
| `WEBHOOK_URL` | Public-facing base URL (essential behind reverse proxy) |
| `N8N_HOST` / `N8N_PORT` | Bind address |
| `DB_TYPE` | `sqlite` / `postgresdb` |
| `EXECUTIONS_MODE` | `regular` / `queue` |
| `QUEUE_BULL_REDIS_*` | Redis for queue mode |
| `NODE_FUNCTION_ALLOW_EXTERNAL` | npm packages Code nodes may require() |
| `N8N_BLOCK_ENV_ACCESS_IN_NODE` | Block $env access in nodes |

### Must Back Up Together

1. Database (SQLite file or Postgres dump)
2. Data directory (`~/.n8n/`)
3. Encryption key (`N8N_ENCRYPTION_KEY`)

---

## 8. REST API

Base: `/api/v1/`. Auth: `X-N8N-API-KEY` header.

| Endpoint | Action |
|---|---|
| `GET /workflows` | List workflows |
| `POST /workflows` | Create from JSON |
| `PUT /workflows/{id}` | Update (needs versionId) |
| `POST /workflows/{id}/activate` | Arm triggers |
| `GET /executions` | List executions |
| `GET /executions/{id}` | Full run data |
| `POST /credentials` | Create credential |
| `GET /credentials/schema/{type}` | Inspect fields |

Webhook URLs:
- Test: `https://<host>/webhook-test/<path>`
- Production: `https://<host>/webhook/<path>`

---

## 9. Extensibility — Custom Nodes

### Declarative Style (JSON-driven, recommended for REST APIs)

```typescript
export class MyApi implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'MyApi',
    name: 'myApi',
    version: 1,
    credentials: [{ name: 'myApiApi', required: true }],
    requestDefaults: { baseURL: 'https://api.myservice.com/v1' },
    properties: [
      { displayName: 'Operation', name: 'operation', type: 'options',
        options: [{ name: 'Get', value: 'get',
          routing: { request: { method: 'GET', url: '=/contacts/{{$parameter["id"]}}' } }
        }], default: 'get' }
    ],
  };
}
```

### Programmatic Style (full control)

```typescript
async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
  const items = this.getInputData();
  const returnData: INodeExecutionData[] = [];
  for (let i = 0; i < items.length; i++) {
    const response = await this.helpers.request({ method: 'GET', url: '...' });
    returnData.push({ json: response, pairedItem: { item: i } });
  }
  return [returnData];
}
```

### Community Nodes

- npm packages named `n8n-nodes-*` with keyword `n8n-community-node-package`
- Install from UI: Settings > Community Nodes
- Starter template: `n8n-io/n8n-nodes-starter`

---

## 10. AI / LangChain Integration

### Tools Agent (recommended)

Uses LLM's native tool-calling API. Each connected tool sub-node becomes a callable function.

**Killer feature — Workflow Tool:** Expose any n8n workflow to the agent as a tool, giving it access to 400+ integrations.

### RAG Pattern

- **Indexing:** Loader -> Splitter -> Embeddings -> Vector Store (Insert)
- **Query:** User question -> Agent -> Vector Store Tool -> chunks -> LLM answer

### Streaming

Chat Trigger supports SSE natively. Webhook can stream for chatbot APIs.

---

## 11. Common Automation Patterns

### Lead Capture -> CRM -> Slack
```
Webhook -> HTTP Request (enrich) -> Set -> HubSpot (Upsert) -> IF (qualified?)
  true  -> Slack (#hot-leads)
  false -> Google Sheets (nurture list)
```

### RSS -> Summarize -> Social
```
Schedule (15min) -> RSS Read -> Filter (new) -> Summarization Chain -> Twitter/LinkedIn
```

### AI Chatbot with RAG
```
Chat Trigger -> AI Agent
  ├─ lm:     OpenAI (gpt-4o)
  ├─ memory: Postgres Chat Memory
  ├─ tool:   Vector Store Tool (company KB)
  ├─ tool:   Workflow Tool (CRM lookup sub-workflow)
  └─ tool:   HTTP Request Tool (pricing API)
```

### Error Handling Pattern
- Dedicated workflow with Error Trigger node
- Point any workflow's Settings -> Error Workflow to it
- Receives: execution ID, workflow info, error message, failing node

### Long-Running Async (Wait for Webhook)
```
Start -> HTTP Request (submit job) -> Wait (resume on webhook callback)
  -> Continue processing when callback arrives
```

---

## Sources

- [n8n GitHub](https://github.com/n8n-io/n8n)
- [n8n Documentation](https://docs.n8n.io/)
- [Workflow docs](https://docs.n8n.io/workflows/)
- [Expressions](https://docs.n8n.io/code/expressions/)
- [Creating nodes](https://docs.n8n.io/integrations/creating-nodes/)
- [LangChain in n8n](https://docs.n8n.io/advanced-ai/langchain/overview/)
- [Queue mode](https://docs.n8n.io/hosting/scaling/queue-mode/)
- [Docker install](https://docs.n8n.io/hosting/installation/docker/)
- [API reference](https://docs.n8n.io/api/api-reference/)
