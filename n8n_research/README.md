# n8n Research — Learning Notes

Deep technical reference on n8n workflow automation and reverse-engineering, compiled from the official docs, the `n8n-io/n8n` monorepo, and community sources.

## Contents

- **[01_fundamentals.md](01_fundamentals.md)** — What n8n is, architecture, execution modes, core concepts (workflows, nodes, items, expressions), node categories, self-hosting, REST API, extensibility, LangChain/AI integration, common automation patterns.
- **[02_reverse_engineering.md](02_reverse_engineering.md)** — Workflow JSON schema deep-dive, reading a shared workflow (triggers, execution order, expressions, credentials, endpoints), node internals (`INodeType`, declarative vs programmatic, `typeVersion`), credential encryption, execution data format, import/export CLI, cloning community templates, security considerations before sharing.
- **[n8n_analyze.py](n8n_analyze.py)** — Static analyzer: given a workflow JSON it extracts the graph, triggers, credential requirements, outbound URLs, inbound webhooks, expression dependencies, Code-node bodies, and a secret-smell test.
- **[examples/minimal_workflow.json](examples/minimal_workflow.json)** — Reference Webhook → Edit Fields → Slack workflow for analyzer testing.

## Quick-start: analyzing a workflow

```bash
python n8n_research/n8n_analyze.py n8n_research/examples/minimal_workflow.json
```

Outputs a JSON report with the graph, creds, endpoints, expression dependencies, and flagged secret candidates.

## Key takeaways

1. A workflow is a **pure JSON document**: `nodes[]` + `connections{}` keyed by **source node name** (not id).
2. Expression strings are prefixed with `=` and wrap JS in `{{ }}`. `$json`, `$('NodeName')`, `$now`, `$workflow`, `$execution`, `$env` are the common proxies.
3. **Credentials are never inlined** in workflow exports — only `{id, name}` references. Secrets live AES-256 encrypted in the DB under `N8N_ENCRYPTION_KEY`.
4. AI/LangChain nodes use the **cluster-node pattern**: sub-nodes (LLM, memory, tools, vector stores) connect *into* a root Agent via typed ports (`ai_languageModel`, `ai_memory`, `ai_tool`, …).
5. Three production risks in shared JSON: hard-coded secrets in `parameters`, real PII in `pinData`, internal hostnames in URLs. Sanitize before committing.
6. `typeVersion` pins node schema — exporting from a newer instance to an older one can fail to load.

## Sources

Full citations at the end of each document. Primary references:

- [n8n repository](https://github.com/n8n-io/n8n)
- [n8n documentation](https://docs.n8n.io/)
- [Workflow JSON reference](https://docs.n8n.io/workflows/export-import/)
- [Expressions](https://docs.n8n.io/code/expressions/)
- [Creating nodes](https://docs.n8n.io/integrations/creating-nodes/)
- [LangChain in n8n](https://docs.n8n.io/advanced-ai/langchain/overview/)
