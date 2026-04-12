# Learning Notes: n8n Automations, Reverse Engineering & The Karpathy Method

A consolidated study guide covering three intertwined topics:
1. n8n automation fundamentals
2. Reverse engineering n8n workflows
3. Andrej Karpathy's "build from scratch" learning method

The connecting idea: **you learn a system best by tearing it apart, rebuilding it from first principles, and iterating until it works end-to-end.**

---

## Part 1 — n8n Automations

### What n8n Is
n8n (pronounced "nodemation") is an **open-source, self-hostable workflow automation platform**. It is a developer-friendly alternative to Zapier / Make / Power Automate, but you own the data, workflows, and infrastructure.

Key differentiators:
- **Visual node-based canvas** + ability to inject JavaScript / Python inside Code nodes
- **400+ built-in integrations** (Gmail, Slack, OpenAI, Postgres, HTTP Request, webhooks, etc.)
- **Self-hostable** (Docker, npm, Kubernetes) — useful for compliance and cost control
- **Fair-code license** (n8n Sustainable Use License)
- **AI-native in 2026**: first-class LangChain/Agent nodes, vector stores, chat triggers

### Core Concepts

| Concept | Description |
|---|---|
| **Workflow** | A DAG of nodes that processes data left-to-right |
| **Node** | A single unit of work (HTTP request, DB query, transform, send message) |
| **Trigger Node** | The entry point. Exactly **one per workflow** (Cron, Webhook, Manual, App events) |
| **Connection** | Edge between nodes; data flows as an array of JSON items |
| **Item** | The fundamental data unit — each node runs once per incoming item |
| **Expression** | `{{ $json.field }}` templating referencing upstream data |
| **Credential** | Stored auth (OAuth2, API keys) — kept separate from workflow JSON |
| **Sub-workflow** | A workflow invoked by another via `Execute Workflow` node |

### The Data Model
Every node outputs an array:
```json
[
  { "json": { "name": "Ada" }, "binary": {} },
  { "json": { "name": "Linus" }, "binary": {} }
]
```
Nodes iterate over items by default. This simple contract is what makes n8n composable — **any node can feed any node** as long as you reshape data in between.

### Trigger Types
- **Manual** — you click "Execute"
- **Schedule (Cron)** — recurring time-based
- **Webhook** — external HTTP call into n8n
- **App Trigger** — listens to service events (new Gmail, Stripe charge, etc.)
- **Chat Trigger** — conversational AI entry point
- **Execute Workflow Trigger** — called by another workflow

### Typical Workflow Archetypes
1. **ETL**: source → transform → sink (e.g., Airtable → normalize → Postgres)
2. **Notify**: event → filter → Slack/Email
3. **AI Pipeline**: webhook → LLM → post-process → reply
4. **RAG Agent**: chat → retrieve from vector store → LLM → answer
5. **Scheduled Job**: cron → fetch → score → write report
6. **Multi-step Agent**: tool-using LLM that invokes sub-workflows

---

## Part 2 — Reverse Engineering n8n Workflows

This is the practical skill: take an unknown workflow JSON and understand it well enough to modify, extend, or port it.

### Why Reverse Engineer?
- Community shares **9,000+ free templates** on n8n.io/workflows, plus GitHub collections like `enescingoz/awesome-n8n-templates` (280+)
- Quickest way to learn patterns is to read working examples
- Required whenever you inherit a workflow from someone else
- The best way to build **your own internal pattern library**

### The Workflow JSON Anatomy
When you export a workflow you get a JSON with roughly this shape:
```json
{
  "name": "My Workflow",
  "nodes": [
    {
      "id": "uuid",
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300],
      "parameters": { ... },
      "credentials": { "httpHeaderAuth": { "id": "1", "name": "..." } }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [ [ { "node": "Set", "type": "main", "index": 0 } ] ]
    }
  },
  "settings": {},
  "staticData": null,
  "pinData": {}
}
```

Note: **credentials are NOT included** in exports — only a reference (id + name). You must recreate them locally.

### A Reverse-Engineering Playbook

**Step 1 — Locate the trigger.**
The trigger tells you *when* and *why* the workflow runs. Search the JSON for `trigger` in `type`.

**Step 2 — Draw the graph.**
Parse the `connections` map; build an adjacency list. Identify:
- Fan-outs (one node → many)
- Fan-ins (many → one, requires Merge node)
- Loops (`SplitInBatches`, `Loop Over Items`)
- Sub-workflow calls (`Execute Workflow`)

**Step 3 — Classify each node.**
- **IO boundary** (webhook, HTTP Request, DB, file)
- **Transform** (Set, Code, Function, Edit Fields)
- **Control flow** (If, Switch, Merge, Wait)
- **Side effect** (Send email, post to Slack, write to sheet)
- **LLM / AI** (OpenAI, Agent, Vector Store)

**Step 4 — Map the data shape at each hop.**
Skim `parameters` for expressions like `{{ $json.X }}` and `{{ $node["Y"].json.Z }}`. These tell you the implicit schema.

**Step 5 — Rebuild credentials.**
List every `credentials` reference; create local equivalents.

**Step 6 — Dry-run with pinned test data.**
Use n8n's `pinData` / "Execute Node" to test individual nodes without running the whole chain.

**Step 7 — Refactor/extract patterns.**
Pull recurring sub-graphs into sub-workflows. Rename nodes to be self-documenting.

### Useful CLI Commands
```bash
# Export all workflows to individual files
n8n export:workflow --all --separate --output=./backup/

# Import a folder of JSON workflows
n8n import:workflow --separate --input=./backup/

# Export credentials (encrypted)
n8n export:credentials --all --output=creds.json
```

### Common Gotchas
- **Version drift**: `typeVersion` mismatch between the source and your instance can silently break nodes
- **Credential names are leaked in exports** — sanitize before public sharing
- **Static data** (`staticData`) stores runtime state (e.g., last-seen ID) and can make a workflow behave differently after import
- **Pinned data** (`pinData`) may ship with the JSON and mask real behavior
- **Expressions referencing node names** break when you rename a node

### Patterns You Will See Repeatedly
1. **Webhook → Validate → Enrich → Respond** (synchronous API)
2. **Cron → Fetch → Diff → Upsert** (idempotent sync job)
3. **Trigger → LLM → Tool Router (Switch) → Sub-workflow** (agent pattern)
4. **Queue pattern**: Webhook drops item to Redis/DB; Cron worker picks it up
5. **Batching**: `SplitInBatches` + `Wait` to respect rate limits
6. **Error workflow**: a separate workflow designated in Settings that runs on any failure

---

## Part 3 — The Karpathy Method of Learning

Andrej Karpathy (ex-OpenAI, ex-Tesla, Stanford CS231n) is unusually good at teaching. His pedagogical approach is consistent across his blog, YouTube lectures, and repos (`micrograd`, `makemore`, `nanoGPT`, `llm.c`, `nanochat`). Key principles:

### 1. Build From Scratch, In Code
Don't read a paper and nod. **Type it out, in the simplest language possible, with no framework magic**.
- `micrograd` = a full autograd engine in ~150 lines of Python. Single scalar `Value` + backward pass. Once you've written it, backprop is no longer mysterious.
- `nanoGPT` = GPT-2 (124M) training loop in ~600 lines across `train.py` + `model.py`.
- `llm.c` = the same but in pure C/CUDA for a deeper mechanical understanding.

**Rule of thumb**: if you can't write it from a blank file, you don't understand it.

### 2. Bottom-Up, Incremental Complexity
His courses ("Neural Networks: Zero to Hero") go in this order:
1. Scalar autograd (micrograd)
2. Character-level bigram model
3. MLP language model (Bengio 2003)
4. BatchNorm / WaveNet style CNNs
5. Transformer / GPT
6. Training at scale / tokenization / RLHF

Each step adds **one new idea** on top of something you already built. No giant leaps.

### 3. Live Coding With Mistakes Left In
His videos show the bugs, the confusions, the off-by-ones, and the fixes. This matters because:
- Learners realize errors are normal
- You see the *process* of debugging, not just the answer
- Watching a concrete failure + fix encodes the concept better than abstract explanation

### 4. Form Hypotheses and Run Experiments
From *"A Recipe for Training Neural Networks"* (his famous blog post):
> *"Be paranoid about silent failures. At every step make a concrete hypothesis about what will happen, then validate with an experiment or investigate until you find the issue."*

The loop:
1. Predict what will happen
2. Run it
3. Reconcile prediction vs reality
4. If they differ, you just learned something — dig in

### 5. "Become One With the Data"
Before modeling, **spend hours just staring at raw data**. Look at distributions, outliers, duplicates. Understand it so well that the right architecture/approach becomes obvious.

### 6. Simplify Relentlessly
Karpathy's repos are famously small — because small is studyable. When you explain something, your first pass should be the *minimum viable version*. Add sophistication only when forced.

### 7. Patience + Attention to Detail
When asked what traits predict success in ML, he cites **patience** and **attention to detail** over raw intelligence. Long debugging sessions, reading tensor shapes, sanity-checking gradients — this is the work.

### 8. Teach What You Learn
Karpathy himself says making the videos forces him to understand things more deeply. Writing, explaining, and shipping a tutorial is a forcing function for real comprehension.

### The Karpathy Loop (Meta-Algorithm)
```
for concept in curriculum:
    read_minimal_reference(concept)       # 1 paper or 1 blog post
    implement_from_scratch(concept)       # tiny, single-file
    break_it_intentionally()              # remove a piece, see what fails
    run_small_experiments(concept)        # ablations
    explain_it_to_someone()               # blog / video / friend
    scale_up_only_if_needed()
```

---

## Part 4 — Applying Karpathy's Method to n8n

The three topics connect directly. Here is how to learn n8n the Karpathy way:

### Phase 0 — Stare at the Data
Import 10 community workflows. Just *look* at them in the UI. Don't modify. What patterns recur? What nodes show up in 80% of them?

### Phase 1 — Build the Minimum Workflow
Build, by hand, the simplest possible workflow:
- Manual trigger → Set node → nothing else

Export it. Read the JSON. Identify every field. Delete a field, re-import, see what breaks. This is your `micrograd` moment for n8n.

### Phase 2 — Add One Concept at a Time
1. Add a second node → study `connections`
2. Add an expression `{{ $json.x }}` → study the data flow
3. Add an `If` → study branching
4. Add a `Webhook` → study triggers
5. Add an `HTTP Request` + credential → study auth
6. Add a `Code` node → study the scripting escape hatch
7. Add a `Wait` + `SplitInBatches` → study control flow
8. Add an LLM node → study AI integration
9. Add a sub-workflow call → study composition
10. Add an error workflow → study failure handling

Each step = one new idea. No giant leaps.

### Phase 3 — Reverse Engineer a Real Template
Pick a complex community workflow (e.g., a RAG agent from `enescingoz/awesome-n8n-templates`). Walk the playbook from Part 2. Rewrite it from a blank canvas without copying. If you can reproduce it, you understand it.

### Phase 4 — Build Something Original
Pick a personal pain point. Automate it in n8n. Ship it. When it breaks, debug it like Karpathy debugs training runs — form a hypothesis, check the actual data at each node, find the root cause.

### Phase 5 — Teach It
Write a README, a blog post, or a short video walking through your workflow. Teaching is the final compression step.

---

## Reference Links

### n8n
- n8n Docs — https://docs.n8n.io/
- Workflows concept — https://docs.n8n.io/workflows/
- Nodes reference — https://docs.n8n.io/workflows/components/nodes/
- Export/Import guide — https://docs.n8n.io/workflows/export-import/
- Community template library — https://n8n.io/workflows/
- `enescingoz/awesome-n8n-templates` — https://github.com/enescingoz/awesome-n8n-templates
- n8n GitHub org — https://github.com/n8n-io

### Karpathy
- Blog — http://karpathy.github.io/
- Personal site — https://karpathy.ai/
- Neural Networks: Zero to Hero — https://karpathy.ai/zero-to-hero.html
- A Recipe for Training Neural Networks — http://karpathy.github.io/2019/04/25/recipe/
- Hacker's Guide to Neural Networks — http://karpathy.github.io/neuralnets/
- `karpathy/nanoGPT` — https://github.com/karpathy/nanoGPT
- `karpathy/build-nanogpt` — https://github.com/karpathy/build-nanogpt

---

## TL;DR

- **n8n** = visual, self-hostable workflow engine; every workflow is a DAG of nodes with one trigger; every workflow is exportable as JSON.
- **Reverse engineering n8n** = locate trigger → map graph → classify nodes → trace data shapes → rebuild credentials → dry-run.
- **The Karpathy method** = build from scratch, smallest possible version, one concept at a time, make predictions and run experiments, fall in love with the data, and teach what you learn.
- **Combined**: the fastest way to master n8n is to reverse-engineer real workflows the way Karpathy reverse-engineers transformers — by rebuilding them from a blank file.
