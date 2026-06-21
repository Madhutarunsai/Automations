# GoHighLevel CLI

Agent-accessible command-line access to a GoHighLevel (GHL) account: contacts,
opportunities, calendars, workflows, conversations, payments, and locations.

This is a from-scratch, dependency-free implementation (standard library only)
modelled on the public Lead Gen Jay `gohighlevel-cli` skill specification. The
engine lives in this repo at `gohighlevel_cli/`.

## When to use

Use this skill whenever the user wants to read or modify their GoHighLevel CRM
from an agent — listing/creating contacts, managing pipeline opportunities,
checking calendar slots, enrolling contacts in workflows, reading
conversations, or pulling payment/location data.

## Prerequisites

- **Python 3.10+** (no third-party packages required).
- `GHL_API_KEY` — a **Private Integration Token** (starts with `pit-`).
  Create it in GHL: *Settings → Private Integrations → Create new integration*,
  grant the scopes you need, copy the key.
- `GHL_LOCATION_ID` — the sub-account/location id, found in your GHL URL:
  `app.../location/<LOCATION_ID>/...`. Can also be passed per-call with
  `--location-id`.

Experimental (internal-API) commands additionally need **your own** GHL web
session token:

- `GHL_FIREBASE_REFRESH_TOKEN` — your logged-in session's Firebase refresh token.
- `GHL_FIREBASE_API_KEY` — the Firebase Web API key the GHL web app uses.
- `GHL_INTERNAL_API_BASE` — optional override for the internal host/path.

> ⚠️ The internal-API path calls **undocumented** endpoints with your own
> session token. It is intended only for operating on your own account and may
> violate GoHighLevel's Terms of Service. Endpoints are not published and can
> change without notice. Prefer the public API whenever it covers the task.

## Running

```bash
# Module form (works from the repo root):
python -m gohighlevel_cli contacts list --limit 50

# Or, after `pip install -e .`, the console script:
ghl contacts list --limit 50
```

Global flags: `--json` (compact output for piping), `--location-id ID`,
`--experimental` (unlock internal-API commands). Agents should pass `--json`.

## Command reference

| Group | Actions |
| --- | --- |
| `contacts` | `list [--limit --query]`, `get <id>`, `search --query [--limit]`, `create --set k=v...`, `update <id> --set k=v...`, `delete <id>`, `add-tag <id> <tag...>`, `remove-tag <id> <tag...>` |
| `opportunities` | `list [--limit]`, `pipelines`, `get <id>`, `create --set k=v...`, `update <id> --set k=v...`, `delete <id>` |
| `calendars` | `list`, `get <id>`, `slots <id> --start <ms> --end <ms>` |
| `workflows` | `list`, `enroll --contact-id --workflow-id`, `remove --contact-id --workflow-id`, `create --from-json <file>` *(experimental, internal API)* |
| `conversations` | `list [--limit]`, `messages <id>`, `send --set k=v...` |
| `payments` | `transactions`, `orders`, `invoices` |
| `locations` | `get`, `custom-fields`, `custom-values` |

`--set key=value` adds a **string** field (sent verbatim, so numeric-looking
ids like `externalId=12345` stay strings). Use `--set-json key=value` for
**typed** fields whose value is JSON: numbers, booleans, arrays, objects
(e.g. `--set-json monetaryValue=5000`, `--set-json tags='["a","b"]'`). The
resolved location id always wins over a `--set locationId=...`.

> Endpoint caveats to verify against a live account: `contacts search` sends a
> simple `{query, pageLimit}` body and `payments invoices` sends
> `altId/altType` only — GHL's v2 search/invoice contracts may want richer
> filters or pagination. Reads elsewhere are straightforward.

## Examples

```bash
# Find a contact and tag them
ghl --json contacts search --query "jane@acme.com"
ghl --json contacts add-tag <CONTACT_ID> "demo-booked"

# Pipeline ops
ghl --json opportunities pipelines
ghl --json opportunities create --set pipelineId=P1 --set name="Acme deal" \
    --set pipelineStageId=S1 --set status=open --set monetaryValue=5000

# Enroll into a workflow (public API)
ghl --json workflows enroll --contact-id <C> --workflow-id <W>

# Build a workflow via the internal API (your own account only)
ghl --experimental --json workflows create --from-json ./welcome-workflow.json
```

## Workflow design rules (when creating sequences)

1. **Trigger** — every workflow needs a defined entry trigger.
2. **Goal/exit** — include a goal event as the final step so contacts exit
   cleanly instead of looping.
3. **Validate links** — confirm every URL/merge tag in workflow emails resolves
   before turning the workflow on.

## Notes for agents

- Always pass `--json`; parse stdout as JSON. Errors are printed to **stderr**
  as JSON (`{"error", "status", "body"}`) with a non-zero exit code.
- Never invent ids, offers, or discounts — read them first (`list`/`get`).
- Do not enable `--experimental` unless the user has explicitly provided their
  own Firebase session credentials and accepts the ToS caveat above.
