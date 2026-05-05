# n8n Reverse Engineering — Deep Technical Brief

Educational/defensive reference for understanding how n8n workflows are constructed, exported, shared, and analyzed.

---

## 1. Workflow JSON Schema (Deep Dive)

### Top-Level Object

```json
{
  "id": "aBcD1234EfGh5678",
  "name": "Weekly Lead Enrichment",
  "active": false,
  "nodes": [],
  "connections": {},
  "settings": {
    "executionOrder": "v1",
    "errorWorkflow": "wf_error_handler_id",
    "timezone": "Europe/Berlin",
    "executionTimeout": -1
  },
  "staticData": null,
  "pinData": {},
  "versionId": "7c2a9a5d-2f4e-4a3d-8f21-0f1c9a0b7e55",
  "meta": { "instanceId": "c1a2b3...", "templateCredsSetupCompleted": true },
  "tags": [{ "id": "1", "name": "prod" }]
}
```

| Key | Notes |
|---|---|
| `id` | DB primary key. **Overwrites same-ID on import** — strip before importing. |
| `active` | Whether triggers are armed. Import never auto-activates. |
| `nodes` | Graph vertices. Order is not semantically meaningful. |
| `connections` | Edges keyed by source node **name** (not id). |
| `staticData` | Persistent state across executions (cursors, tokens). |
| `pinData` | Editor-only test fixtures. Can leak real payloads. |
| `versionId` | Optimistic concurrency token, bumps on every save. |
| `meta.instanceId` | Identifies originating n8n instance. |

### Per-Node Object

```json
{
  "id": "b5a1f2e3-4c5d-6e7f-8a9b-0c1d2e3f4a5b",
  "name": "HTTP Request",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.2,
  "position": [820, 300],
  "parameters": {
    "method": "POST",
    "url": "https://api.example.com/v1/leads",
    "jsonBody": "={{ { email: $json.email } }}"
  },
  "credentials": {
    "httpHeaderAuth": { "id": "17", "name": "Example API" }
  },
  "disabled": false,
  "continueOnFail": false,
  "retryOnFail": true,
  "maxTries": 3,
  "waitBetweenTries": 2000,
  "webhookId": "f3c4b5a6-..."
}
```

Key points:
- **`type`** — fully-qualified: `n8n-nodes-base.*`, `@n8n/n8n-nodes-langchain.*`, `n8n-nodes-<community>.*`
- **`typeVersion`** — can be decimal (4.2). Pins schema version. Importing to older instance may fail.
- **`parameters`** — strings starting with `=` are expressions
- **`credentials`** — reference only (`{id, name}`), no secrets inlined
- **`webhookId`** — defines webhook URL path. Preserving it means same URL on new instance.

### Connections Object

```json
"connections": {
  "Webhook": {
    "main": [[{ "node": "Set", "type": "main", "index": 0 }]]
  },
  "IF": {
    "main": [
      [{ "node": "True Branch", "type": "main", "index": 0 }],
      [{ "node": "False Branch", "type": "main", "index": 0 }]
    ]
  }
}
```

Shape: `connections[sourceName][outputType][outputIndex] = [{node, type, index}]`

- IF/Switch: multiple output indices (true=0, false=1)
- Fan-out: multiple targets in inner array
- Fan-in: same target appears under multiple source keys

### AI Sub-Node Connections

Sub-nodes are **sources** feeding into the root Agent:

```json
"OpenAI Chat Model": {
  "ai_languageModel": [[{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]]
},
"SerpAPI": {
  "ai_tool": [[{ "node": "AI Agent", "type": "ai_tool", "index": 0 }]]
}
```

Connection types: `ai_languageModel`, `ai_memory`, `ai_tool`, `ai_embedding`, `ai_vectorStore`, `ai_outputParser`, `ai_textSplitter`, `ai_document`, `ai_retriever`

---

## 2. Reading a Workflow Export

### Find the Triggers

Identify by type suffix: `*trigger`, `*webhook`, `*cron`, `*scheduleTrigger`, `*chatTrigger`, `*manualTrigger`

Also: any node with no inbound edges in connections.

A workflow can have **multiple triggers** — each is an independent entry point.

### Trace Execution Order

n8n uses depth-first traversal from trigger (`executionOrder: "v1"`):

1. Build `indegree[nodeName]` from connections
2. BFS/DFS from triggers along `main` edges
3. Skip `ai_*` edges (dependency injection, not data flow)
4. Branching: IF/Switch emit on separate output indices
5. Merge: joins two upstream branches
6. SplitInBatches: output 0 = loop body, output 1 = done

### Expressions

Any parameter starting with `=` is evaluated. Inside `{{ }}`:

| Variable | Meaning |
|---|---|
| `$json` | Current item's JSON |
| `$("Node Name").item.json.x` | Upstream node's output |
| `$input.all()` | All input items |
| `$workflow.id` / `$execution.id` | Metadata |
| `$now` | Luxon DateTime |
| `$env.VAR` | Environment variable |

### Fan-out / Fan-in / Loops

- **Fan-out**: one output → multiple downstream nodes. Items **copied**.
- **Fan-in**: multiple sources → one target. Items merged in arrival order.
- **Loops**: SplitInBatches output 0 feeds back to itself.
- **Error workflow**: `settings.errorWorkflow` references another workflow ID.

---

## 3. Reverse-Engineering a Shared Workflow

### 3.1 Identify Required Credentials

Grep every node for `credentials` blocks. Also check `parameters.authentication` and `parameters.genericAuthType` for HTTP Request nodes.

After import, each unconfigured credential shows a red indicator in the UI.

### 3.2 Find External Endpoints

- Outbound: Any `http://` or `https://` in parameters
- Inbound: `webhookId` on trigger nodes → `/webhook/<path>`
- Service nodes: `resource` + `operation` → specific vendor API calls
- Code nodes: review `jsCode`/`pythonCode` for fetch calls

### 3.3 Map Data Flow

Label each edge:
- **Transform**: Set, Edit Fields, Code, Date & Time
- **Branch**: IF, Switch
- **Aggregate**: Aggregate, Summarize, Merge
- **Side-effects**: HTTP POST, Slack, email, DB insert
- **Sinks**: nodes with no outgoing main edges

### 3.4 Extract Expressions

Walk parameters recursively, collect strings starting with `=`, pull `{{ }}` blocks. These reveal:
- Upstream node names consumed (`$("Name")`)
- Fields read (`.json.someField`)
- Embedded JS logic
- Accidentally hard-coded secrets

### 3.5 Pinned Data

`pinData` shows the author's assumed input schema and may contain:
- Real customer PII
- API response examples
- Test fixtures

Always sanitize before republishing.

---

## 4. Node Internals

### INodeType Interface

```typescript
interface INodeType {
  description: INodeTypeDescription;
  execute?(this: IExecuteFunctions): Promise<INodeExecutionData[][]>;
  poll?(this: IPollFunctions): Promise<INodeExecutionData[][] | null>;
  trigger?(this: ITriggerFunctions): Promise<ITriggerResponse | undefined>;
  webhook?(this: IWebhookFunctions): Promise<IWebhookResponseData>;
}
```

### Declarative Nodes (routing-based)

No `execute()` method. HTTP request built from `routing` metadata on properties:

```typescript
options: [{
  name: 'Get', value: 'get',
  routing: {
    request: { method: 'GET', url: '=/contacts/{{$parameter["id"]}}' },
    output: { postReceive: [{ type: 'rootProperty', properties: { property: 'data' } }] }
  }
}]
```

### Programmatic Nodes

Full `execute()` with access to:
- `this.getInputData()` — items array
- `this.getNodeParameter(name, itemIndex)` — after expression evaluation
- `this.getCredentials(name)` — decrypted at call time
- `this.helpers.httpRequest(...)` — HTTP client

Return: `INodeExecutionData[][]` — outer = output ports, inner = items.

### Source Layout

```
packages/nodes-base/nodes/
├── HttpRequest/
│   ├── HttpRequest.node.ts    (versioned router)
│   ├── V1/, V2/, V3/
├── Set/
├── Code/
├── Webhook/
└── ... (hundreds of service nodes)
```

### typeVersion Handling

A single node can serve multiple versions:

```typescript
class HttpRequest extends VersionedNodeType {
  constructor() {
    super({
      defaultVersion: 4.2,
      nodeVersions: { 1: V1, 2: V2, 3: V3, 4: V3, 4.1: V3, 4.2: V3 }
    });
  }
}
```

Workflow JSON pins the version per-node. Importing to an older instance lacking that version will fail.

---

## 5. Credentials Reverse-Engineering

### Types

- **apiKey/header/query** — static secrets injected via `authenticate.properties`
- **httpBasicAuth** — user/password → Basic header
- **oAuth2Api** — n8n handles OAuth dance; stores access_token, refresh_token, expires_at
- **custom** — node ships own `authenticate` function

### Encryption at Rest

- AES-256 symmetric using `N8N_ENCRYPTION_KEY`
- Auto-generated on first boot if unset (written to `~/.n8n/config`)
- Decrypted only at execution time, never serialized into exports
- **Losing the key = permanently unreadable credentials**

### Exported Credentials

Default (encrypted):
```json
{ "id": "17", "name": "Example API", "type": "httpHeaderAuth", "data": "U2FsdGVkX1+...base64..." }
```

With `--decrypted`:
```json
{ "id": "17", "name": "Example API", "type": "httpHeaderAuth", "data": { "name": "X-API-Key", "value": "sk_live_abc123" } }
```

---

## 6. Execution Data Format

### Structure (IRunExecutionData)

```json
{
  "resultData": {
    "runData": {
      "Webhook": [{ "startTime": 1700000000, "executionTime": 4,
        "data": { "main": [[{ "json": {...} }]] } }],
      "Set": [{ ... }]
    },
    "lastNodeExecuted": "Slack",
    "error": { "message": "...", "node": { "name": "..." } }
  }
}
```

Each entry in `runData[nodeName]` is one execution of that node (can be multiple in loops).

### Manual vs Production

- `manual` — triggered from editor, honors `pinData`
- `trigger`/`webhook` — production, ignores `pinData`
- `webhook-test/<id>` only works during editor listen mode
- `webhook/<id>` is live when workflow is active

---

## 7. Import/Export CLI

| Command | Notes |
|---|---|
| `n8n export:workflow --all --output=./backup/` | All workflows |
| `n8n export:workflow --id=123 --output=wf.json` | Single workflow |
| `n8n export:credentials --all --decrypted` | Plain text secrets |
| `n8n import:workflow --input=wf.json` | Import (same-ID overwrites!) |
| `n8n import:credentials --input=creds.json` | Must match current encryption key |
| `n8n execute --id=123` | One-shot run |
| `n8n update:workflow --id=123 --active=true` | Activate triggers |

**Warning**: Same-ID items are overwritten silently on import. Strip `id`/`versionId` for fresh copies.

### UI Import/Export

- Download → JSON file
- Import from File or URL
- Ctrl+C/V — copies/pastes selected nodes as JSON fragment

---

## 8. Cloning Community Workflows

### Template Catalog: n8n.io/workflows/

- Rendered preview of node graph
- "Use workflow" button → copies JSON
- "Download" → raw JSON

### Adapting a Template

1. Strip `id`, `versionId`, `meta.instanceId`
2. Review `credentials` blocks — rebind after import
3. Scan parameters for hard-coded URLs, emails, channel IDs
4. Check `pinData` — remove real PII
5. Import via UI or CLI
6. Wire credentials in editor
7. Test with pinned sample before activating

### License Considerations

- n8n itself: Sustainable Use License (not OSI open source)
- User-authored workflow JSON: creator's content, not covered by n8n license
- Treat shared workflows like code snippets — ask before re-selling

---

## 9. Static Analysis Script

See `n8n_analyze.py` in this directory — given a workflow JSON, extracts:

- Node graph (adjacency + triggers)
- Credential requirements
- External API surface (outbound URLs + inbound webhooks)
- Expression dependencies (which nodes reference which upstream)
- Code node bodies
- Secret-smell detection (OpenAI keys, Slack tokens, GitHub PATs, etc.)

Usage: `python n8n_analyze.py workflow.json`

---

## 10. Security Considerations Before Sharing

Before committing workflow JSON to a public repo:

1. **Strip** `id`, `versionId`, `meta.instanceId`
2. **Remove/sanitize `pinData`** — often contains real PII
3. **Audit parameters** for:
   - Hard-coded API keys/tokens
   - Internal hostnames (`http://10.0.0.5/...`)
   - Private Slack channels, Airtable base IDs, customer emails
4. **`webhookId`** — regenerate if already whitelisted somewhere
5. **Code nodes** — review for inline credentials
6. **`credentials` names** — can reveal environments ("Prod Stripe")
7. **`$env` references** — document required env vars
8. **Error workflow IDs** — dangling refs, remove if not shipping together
9. **Tags** — may carry project/customer names
10. **Run `n8n_analyze.py`** as a pre-commit check

### Minimal Sanitization

```python
def sanitize(wf):
    for k in ("id", "versionId", "tags", "pinData"):
        wf.pop(k, None)
    if "meta" in wf:
        wf["meta"].pop("instanceId", None)
    (wf.get("settings") or {}).pop("errorWorkflow", None)
    for n in wf.get("nodes", []):
        n.pop("webhookId", None)
        if n.get("credentials"):
            n["credentials"] = {k: {"name": f"{k} credential"} for k in n["credentials"]}
    return wf
```

---

## 11. Key Source Files in the Monorepo

| File | Purpose |
|---|---|
| `packages/workflow/src/Interfaces.ts` | Canonical types: INode, INodeType, IConnections, IWorkflowBase |
| `packages/workflow/src/Workflow.ts` | Graph introspection, expression resolution |
| `packages/workflow/src/Expression.ts` | Expression evaluator (wraps Tournament/tmpl) |
| `packages/workflow/src/WorkflowDataProxy.ts` | $json, $node, $input, $workflow implementations |
| `packages/core/src/WorkflowExecute.ts` | Execution engine (node iterator, retries, waits) |
| `packages/core/src/NodeExecuteFunctions.ts` | Builds IExecuteFunctions per node call |
| `packages/core/src/Credentials.ts` | Encrypt/decrypt |
| `packages/cli/src/commands/import.ts` | CLI import |
| `packages/cli/src/commands/export.ts` | CLI export |

---

## Sources

- [n8n repository](https://github.com/n8n-io/n8n)
- [packages/workflow](https://github.com/n8n-io/n8n/tree/master/packages/workflow)
- [packages/nodes-base](https://github.com/n8n-io/n8n/tree/master/packages/nodes-base)
- [Export and import workflows](https://docs.n8n.io/workflows/export-import/)
- [CLI commands](https://docs.n8n.io/hosting/cli-commands/)
- [Expressions](https://docs.n8n.io/code/expressions/)
- [Creating nodes](https://docs.n8n.io/integrations/creating-nodes/)
- [Encryption key](https://docs.n8n.io/hosting/configuration/configuration-examples/encryption-key/)
- [n8n template catalog](https://n8n.io/workflows/)
