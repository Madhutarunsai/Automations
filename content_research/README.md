# content_research

Tools for syncing content-research data into external systems.

## push_to_airtable.py

Syncs `content_scripts/MASTER_CONTENT_SHEET.csv` into the **Content Scripts**
table of the **Content automation** Airtable base
(`apphCNLdIntwUnirW`).

The sync is idempotent — it clears the table and re-inserts the current CSV
rows, so re-running never creates duplicates.

### Setup

1. Create a personal access token at https://airtable.com/create/tokens with
   scopes `data.records:read` + `data.records:write` on the *Content
   automation* base.
2. Export it:

   ```bash
   export AIRTABLE_API_KEY=patXXXXXXXXXXXXXX.xxxxxxxx...
   pip install requests   # if not already installed
   python3 content_research/push_to_airtable.py
   ```

### Optional overrides

| Env var            | Default              | Purpose                     |
| ------------------ | -------------------- | --------------------------- |
| `AIRTABLE_BASE_ID` | `apphCNLdIntwUnirW`  | Target a different base     |
| `AIRTABLE_TABLE`   | `Content Scripts`    | Target a different table    |

The table schema matches the CSV columns: `SECTION`, `Script #`, `Type`,
`Topic`, `Week`, `Day`, `Lead Magnet Keyword`, `Status`.
