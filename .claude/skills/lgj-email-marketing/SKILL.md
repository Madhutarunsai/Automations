# Email Marketing (Kit + GoHighLevel)

Author and deploy email campaigns: deliverability-grade **broadcasts** and
**nurture sequences** via Kit (formerly ConvertKit), and workflow emails via
GoHighLevel. Companion to the `gohighlevel-cli` skill.

Engine: `kit_cli/` (this repo, stdlib only). GHL workflow enrollment uses the
`gohighlevel_cli` package.

## Why two tools

- **GoHighLevel** — CRM, forms, calendars, automations/workflows. Great for
  triggered, behavior-based sequences while a contact is hot.
- **Kit** — newsletters/broadcasts and linear nurture sequences to large lists,
  where deliverability matters. Use Kit for cold/large sends, re-engagement,
  and broadcasts; avoid blasting big lists from GHL.

## Prerequisites

- Python 3.10+ (no third-party packages).
- `KIT_API_KEY` — a Kit **v4** API key (Kit → Settings → Advanced → API).
- For GHL enrollment: `GHL_API_KEY` + `GHL_LOCATION_ID` (see the
  `gohighlevel-cli` skill).

## Running

```bash
python -m kit_cli broadcasts list           # or: kit broadcasts list
```

Global flag: `--json` (compact output for piping). Agents should pass `--json`.

## Command reference (`kit`)

| Group | Actions |
| --- | --- |
| `broadcasts` | `list`, `get <id>`, `stats <id>`, `create --subject --content/--body-file [--send-at <iso>] [--set k=v]` |
| `sequences` | `list`, `create --name` |
| `sequence-emails` | `list --sequence-id`, `create --sequence-id --subject --content/--body-file [--delay-days N]` |
| `tags` | `list`, `create --name` |
| `custom-fields` | `list` |
| `subscribers` | `list [--limit]`, `create --email [--set k=v]` |
| `segments` | `list` |

Enrolling a contact into a GHL workflow:

```bash
ghl --json workflows enroll --contact-id <C> --workflow-id <W>
```

## Copywriting rules (apply when writing emails)

- Before writing, establish the **trigger** (what starts the sequence) and the
  **goal/exit** (what ends it).
- One CTA per email. Roughly an 80:20 value-to-sales ratio across a sequence.
- Provide A/B subject-line variants where the user wants to test.
- Add UTM tracking to links (`?utm_source=email&utm_content=<id>`).
- Verify every URL/offer is real before sending — never invent discounts.
- Kit merge tags use Liquid: `{{ subscriber.first_name }}`. GHL uses
  `{{contact.first_name}}` (no fallback operators).

## Notes for agents

- Always pass `--json`; parse stdout. Errors print to **stderr** as JSON with a
  non-zero exit code.
- `broadcasts create` without `--send-at` leaves the broadcast as a **draft** —
  safe to create and review before scheduling.
- Some Kit sequence-authoring endpoints vary by plan; if a `sequence-emails`
  call errors, fall back to building the sequence in the Kit UI and use the CLI
  for broadcasts/tags/subscribers.
