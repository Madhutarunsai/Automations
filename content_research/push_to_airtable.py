#!/usr/bin/env python3
"""Push the content script sheet into Airtable.

Reads ``content_scripts/MASTER_CONTENT_SHEET.csv`` and syncs every row into the
"Content Scripts" table of the "Content automation" Airtable base.

The sync is idempotent: existing rows in the table are deleted and replaced with
the current contents of the CSV, so re-running never creates duplicates.

Configuration (environment variables):
    AIRTABLE_API_KEY   Personal access token with data.records:write +
                       data.records:read scope on the base. (required)
    AIRTABLE_BASE_ID   Override the target base (default below).
    AIRTABLE_TABLE     Override the target table name (default below).

Usage:
    export AIRTABLE_API_KEY=patXXXXXXXXXXXXXX.xxxxxxxx...
    python3 content_research/push_to_airtable.py
"""

from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

import requests

# --- Defaults (the table created for this repo) -----------------------------
DEFAULT_BASE_ID = "apphCNLdIntwUnirW"      # "Content automation" base
DEFAULT_TABLE = "Content Scripts"

# CSV column header -> Airtable field name (they match 1:1 here).
FIELDS = [
    "SECTION",
    "Script #",
    "Type",
    "Topic",
    "Week",
    "Day",
    "Lead Magnet Keyword",
    "Status",
]

API_ROOT = "https://api.airtable.com/v0"
BATCH_SIZE = 10  # Airtable allows up to 10 records per write request.

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "content_scripts" / "MASTER_CONTENT_SHEET.csv"


def _session(api_key: str) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    )
    return s


def _request(session: requests.Session, method: str, url: str, **kwargs) -> requests.Response:
    """Call the Airtable API with basic rate-limit retry handling."""
    for attempt in range(5):
        resp = session.request(method, url, timeout=30, **kwargs)
        if resp.status_code == 429:  # rate limited
            wait = 2 ** attempt
            print(f"  rate limited, retrying in {wait}s...", file=sys.stderr)
            time.sleep(wait)
            continue
        if not resp.ok:
            raise SystemExit(
                f"Airtable API error {resp.status_code} on {method} {url}:\n{resp.text}"
            )
        return resp
    raise SystemExit("Airtable API: exceeded retry budget (still rate limited).")


def read_rows() -> list[dict]:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = []
        for raw in reader:
            fields = {col: (raw.get(col) or "").strip() for col in FIELDS}
            # Skip fully empty separator rows.
            if any(fields.values()):
                rows.append(fields)
    return rows


def fetch_existing_ids(session: requests.Session, base_id: str, table: str) -> list[str]:
    ids: list[str] = []
    url = f"{API_ROOT}/{base_id}/{requests.utils.quote(table)}"
    params: dict = {"fields[]": ["SECTION"], "pageSize": 100}
    while True:
        resp = _request(session, "GET", url, params=params)
        data = resp.json()
        ids.extend(rec["id"] for rec in data.get("records", []))
        offset = data.get("offset")
        if not offset:
            break
        params["offset"] = offset
    return ids


def delete_records(session: requests.Session, base_id: str, table: str, ids: list[str]) -> None:
    url = f"{API_ROOT}/{base_id}/{requests.utils.quote(table)}"
    for i in range(0, len(ids), BATCH_SIZE):
        chunk = ids[i : i + BATCH_SIZE]
        _request(session, "DELETE", url, params=[("records[]", rid) for rid in chunk])
        print(f"  deleted {min(i + BATCH_SIZE, len(ids))}/{len(ids)} old records")


def create_records(session: requests.Session, base_id: str, table: str, rows: list[dict]) -> int:
    url = f"{API_ROOT}/{base_id}/{requests.utils.quote(table)}"
    created = 0
    for i in range(0, len(rows), BATCH_SIZE):
        chunk = rows[i : i + BATCH_SIZE]
        payload = {"records": [{"fields": r} for r in chunk], "typecast": True}
        resp = _request(session, "POST", url, json=payload)
        created += len(resp.json().get("records", []))
        print(f"  pushed {created}/{len(rows)} records")
    return created


def main() -> None:
    api_key = os.environ.get("AIRTABLE_API_KEY")
    if not api_key:
        raise SystemExit(
            "AIRTABLE_API_KEY is not set.\n"
            "Create a personal access token at https://airtable.com/create/tokens\n"
            "with scopes data.records:read + data.records:write on the "
            "'Content automation' base, then:\n"
            "    export AIRTABLE_API_KEY=patXXXX...\n"
        )

    base_id = os.environ.get("AIRTABLE_BASE_ID", DEFAULT_BASE_ID)
    table = os.environ.get("AIRTABLE_TABLE", DEFAULT_TABLE)

    rows = read_rows()
    print(f"Read {len(rows)} rows from {CSV_PATH.relative_to(REPO_ROOT)}")

    session = _session(api_key)

    print(f"Syncing to base {base_id}, table '{table}'...")
    existing = fetch_existing_ids(session, base_id, table)
    if existing:
        print(f"Clearing {len(existing)} existing records...")
        delete_records(session, base_id, table, existing)

    created = create_records(session, base_id, table, rows)
    print(f"Done. {created} records now in '{table}'.")


if __name__ == "__main__":
    main()
