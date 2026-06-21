# AI Automation Lead-Gen Flow

A complete opt-in funnel for **webaiautomations.com**, built on the
`gohighlevel-cli` and `lgj-email-marketing` skills.

```
Lead-magnet opt-in  ──►  tag: lead-magnet-ghl-cli
        │
        ├─►  Kit nurture sequence (deliverability-grade)
        │      day 0  welcome + deliver the CLI
        │      day 2  value: map your workflows
        │      day 4  value: launch a sequence in a day
        │      day 7  offer: free automation audit  ──► GOAL: call booked
        │
        └─►  GHL workflow (CRM side)
               trigger: tag added
               nudge → if call booked → goal (clean exit)

Inactive 180 days ──► Kit re-engagement sequence (2 emails)
```

**Why split Kit + GHL:** new opt-ins are cold, so the first emails go through
Kit where deliverability is protected. GHL handles the CRM-side automation and
the booking goal. This mirrors the approach in the reference videos.

## Files

- `flow.json` — the spec the deployer reads (tags, sequence, emails, workflow).
- `emails/` — the email bodies (Kit Liquid merge tags, UTM-tracked links, one
  CTA each, ~80:20 value-to-sales).
- `ghl-workflow.json` — workflow definition for `ghl --experimental workflows create`.

## Deploy

Dry-run (no network, prints the ordered plan):

```bash
python -m flows.deploy flows/ai_automation_leadgen/flow.json
```

Execute (provisions the Kit tag + sequences; add `--experimental` to also
create the GHL workflow):

```bash
export KIT_API_KEY=...                 # for the Kit steps
export GHL_API_KEY=... GHL_LOCATION_ID=...
export GHL_FIREBASE_REFRESH_TOKEN=... GHL_FIREBASE_API_KEY=...   # for the workflow
python -m flows.deploy flows/ai_automation_leadgen/flow.json --apply --experimental
```

> The deployer provisions the **assets** (tag, sequences, emails, workflow).
> Subscribing a specific lead and enrolling them happens at opt-in time, e.g.
> `kit subscribers create --email … --set first_name=…` then
> `ghl workflows enroll --contact-id … --workflow-id …`.

## Editing

Everything is data. Change subjects/timing in `flow.json`, edit copy in
`emails/*.md`, adjust the CRM automation in `ghl-workflow.json`. No code changes
needed.
