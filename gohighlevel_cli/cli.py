"""Command-line interface for the GoHighLevel CLI.

Usage:
    ghl [--json] [--location-id ID] [--experimental] <group> <action> [options]

Command groups: contacts, opportunities, calendars, workflows, conversations,
payments, locations. Run ``ghl <group> --help`` for per-group options.
"""

from __future__ import annotations

import argparse
import json
import sys

from .client import GHLClient, GHLError
from .config import Config, ConfigError


# ── output helpers ─────────────────────────────────────────────────────

def _emit(result, *, compact: bool) -> None:
    if compact:
        print(json.dumps(result, separators=(",", ":")))
    else:
        print(json.dumps(result, indent=2, sort_keys=False))


def _kv_body(pairs: list[str] | None) -> dict:
    """Parse repeated ``key=value`` flags into a dict (values JSON-decoded)."""
    body: dict = {}
    for item in pairs or []:
        if "=" not in item:
            raise ConfigError(f"--set expects key=value, got: {item!r}")
        key, _, value = item.partition("=")
        try:
            body[key] = json.loads(value)
        except json.JSONDecodeError:
            body[key] = value
    return body


def _load_json_file(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# ── argument parser ────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ghl", description="GoHighLevel CLI")
    parser.add_argument("--json", action="store_true", help="compact JSON output (for piping)")
    parser.add_argument("--location-id", help="override GHL_LOCATION_ID for this call")
    parser.add_argument(
        "--experimental",
        action="store_true",
        help="enable internal-API commands (uses your own Firebase session token)",
    )
    groups = parser.add_subparsers(dest="group", required=True)

    # contacts -----------------------------------------------------------
    c = groups.add_parser("contacts").add_subparsers(dest="action", required=True)
    p = c.add_parser("list"); p.add_argument("--limit", type=int, default=20); p.add_argument("--query")
    p = c.add_parser("get"); p.add_argument("id")
    p = c.add_parser("search"); p.add_argument("--query", required=True); p.add_argument("--limit", type=int, default=20)
    p = c.add_parser("create"); p.add_argument("--set", action="append", metavar="key=value")
    p = c.add_parser("update"); p.add_argument("id"); p.add_argument("--set", action="append", metavar="key=value")
    p = c.add_parser("delete"); p.add_argument("id")
    p = c.add_parser("add-tag"); p.add_argument("id"); p.add_argument("tags", nargs="+")
    p = c.add_parser("remove-tag"); p.add_argument("id"); p.add_argument("tags", nargs="+")

    # opportunities ------------------------------------------------------
    o = groups.add_parser("opportunities").add_subparsers(dest="action", required=True)
    p = o.add_parser("list"); p.add_argument("--limit", type=int, default=20)
    o.add_parser("pipelines")
    p = o.add_parser("get"); p.add_argument("id")
    p = o.add_parser("create"); p.add_argument("--set", action="append", metavar="key=value")
    p = o.add_parser("update"); p.add_argument("id"); p.add_argument("--set", action="append", metavar="key=value")
    p = o.add_parser("delete"); p.add_argument("id")

    # calendars ----------------------------------------------------------
    cal = groups.add_parser("calendars").add_subparsers(dest="action", required=True)
    cal.add_parser("list")
    p = cal.add_parser("get"); p.add_argument("id")
    p = cal.add_parser("slots"); p.add_argument("id"); p.add_argument("--start", required=True, help="epoch ms"); p.add_argument("--end", required=True, help="epoch ms")

    # workflows ----------------------------------------------------------
    w = groups.add_parser("workflows").add_subparsers(dest="action", required=True)
    w.add_parser("list")
    p = w.add_parser("enroll"); p.add_argument("--contact-id", required=True); p.add_argument("--workflow-id", required=True)
    p = w.add_parser("remove"); p.add_argument("--contact-id", required=True); p.add_argument("--workflow-id", required=True)
    p = w.add_parser("create"); p.add_argument("--from-json", required=True, help="path to workflow definition JSON (experimental, internal API)")

    # conversations ------------------------------------------------------
    cv = groups.add_parser("conversations").add_subparsers(dest="action", required=True)
    p = cv.add_parser("list"); p.add_argument("--limit", type=int, default=20)
    p = cv.add_parser("messages"); p.add_argument("id")
    p = cv.add_parser("send"); p.add_argument("--set", action="append", metavar="key=value", required=True)

    # payments -----------------------------------------------------------
    pay = groups.add_parser("payments").add_subparsers(dest="action", required=True)
    pay.add_parser("transactions")
    pay.add_parser("orders")
    pay.add_parser("invoices")

    # locations ----------------------------------------------------------
    loc = groups.add_parser("locations").add_subparsers(dest="action", required=True)
    loc.add_parser("get")
    loc.add_parser("custom-fields")
    loc.add_parser("custom-values")

    return parser


# ── dispatch ────────────────────────────────────────────────────────────

def _dispatch(args, client: GHLClient) -> object:
    cfg = client.config
    group, action = args.group, args.action

    if group == "contacts":
        if action == "list":
            loc = cfg.require_location(args.location_id)
            return client.request("GET", "/contacts/", params={"locationId": loc, "limit": args.limit, "query": args.query})
        if action == "get":
            return client.request("GET", f"/contacts/{args.id}")
        if action == "search":
            loc = cfg.require_location(args.location_id)
            return client.request("POST", "/contacts/search", body={"locationId": loc, "query": args.query, "pageLimit": args.limit})
        if action == "create":
            loc = cfg.require_location(args.location_id)
            return client.request("POST", "/contacts/", body={"locationId": loc, **_kv_body(args.set)})
        if action == "update":
            return client.request("PUT", f"/contacts/{args.id}", body=_kv_body(args.set))
        if action == "delete":
            return client.request("DELETE", f"/contacts/{args.id}")
        if action == "add-tag":
            return client.request("POST", f"/contacts/{args.id}/tags", body={"tags": args.tags})
        if action == "remove-tag":
            return client.request("DELETE", f"/contacts/{args.id}/tags", body={"tags": args.tags})

    if group == "opportunities":
        loc = cfg.require_location(args.location_id)
        if action == "list":
            return client.request("GET", "/opportunities/search", params={"location_id": loc, "limit": args.limit})
        if action == "pipelines":
            return client.request("GET", "/opportunities/pipelines", params={"locationId": loc})
        if action == "get":
            return client.request("GET", f"/opportunities/{args.id}")
        if action == "create":
            return client.request("POST", "/opportunities/", body={"locationId": loc, **_kv_body(args.set)})
        if action == "update":
            return client.request("PUT", f"/opportunities/{args.id}", body=_kv_body(args.set))
        if action == "delete":
            return client.request("DELETE", f"/opportunities/{args.id}")

    if group == "calendars":
        loc = cfg.require_location(args.location_id)
        if action == "list":
            return client.request("GET", "/calendars/", params={"locationId": loc})
        if action == "get":
            return client.request("GET", f"/calendars/{args.id}")
        if action == "slots":
            return client.request("GET", f"/calendars/{args.id}/free-slots", params={"startDate": args.start, "endDate": args.end})

    if group == "workflows":
        loc = cfg.require_location(args.location_id)
        if action == "list":
            return client.request("GET", "/workflows/", params={"locationId": loc})
        if action == "enroll":
            return client.request("POST", f"/contacts/{args.contact_id}/workflow/{args.workflow_id}")
        if action == "remove":
            return client.request("DELETE", f"/contacts/{args.contact_id}/workflow/{args.workflow_id}")
        if action == "create":
            if not args.experimental:
                raise ConfigError("'workflows create' uses the internal API; pass --experimental to enable it.")
            definition = _load_json_file(args.from_json)
            definition.setdefault("locationId", loc)
            return client.internal_request("POST", "/workflows/", body=definition)

    if group == "conversations":
        loc = cfg.require_location(args.location_id)
        if action == "list":
            return client.request("GET", "/conversations/search", params={"locationId": loc, "limit": args.limit})
        if action == "messages":
            return client.request("GET", f"/conversations/{args.id}/messages")
        if action == "send":
            return client.request("POST", "/conversations/messages", body=_kv_body(args.set))

    if group == "payments":
        loc = cfg.require_location(args.location_id)
        params = {"altId": loc, "altType": "location"}
        if action == "transactions":
            return client.request("GET", "/payments/transactions", params=params)
        if action == "orders":
            return client.request("GET", "/payments/orders", params=params)
        if action == "invoices":
            return client.request("GET", "/invoices/", params=params)

    if group == "locations":
        loc = cfg.require_location(args.location_id)
        if action == "get":
            return client.request("GET", f"/locations/{loc}")
        if action == "custom-fields":
            return client.request("GET", f"/locations/{loc}/customFields")
        if action == "custom-values":
            return client.request("GET", f"/locations/{loc}/customValues")

    raise ConfigError(f"unknown command: {group} {action}")


def main(argv: list[str] | None = None, *, client: GHLClient | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if client is None:
            # Experimental commands also need the public api key for config.
            client = GHLClient(Config.from_env())
        result = _dispatch(args, client)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except GHLError as exc:
        payload = {"error": str(exc), "status": exc.status, "body": exc.body}
        print(json.dumps(payload, indent=2), file=sys.stderr)
        return 1
    _emit(result, compact=args.json)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
