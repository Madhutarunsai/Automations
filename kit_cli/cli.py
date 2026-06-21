"""Command-line interface for the Kit (ConvertKit) v4 API.

Usage:
    kit [--json] <group> <action> [options]

Groups: broadcasts, sequences, sequence-emails, tags, custom-fields,
subscribers, segments. Run ``kit <group> --help`` for per-group options.
"""

from __future__ import annotations

import argparse
import json
import sys

from .client import KitClient, KitError
from .config import ConfigError, KitConfig


# ── helpers ─────────────────────────────────────────────────────────────

def _emit(result, *, compact: bool) -> None:
    if compact:
        print(json.dumps(result, separators=(",", ":")))
    else:
        print(json.dumps(result, indent=2))


def _kv_body(pairs: list[str] | None) -> dict:
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


def _read_body_file(path: str | None) -> str | None:
    if not path:
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# ── parser ──────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kit", description="Kit (ConvertKit) v4 CLI")
    parser.add_argument("--json", action="store_true", help="compact JSON output (for piping)")
    groups = parser.add_subparsers(dest="group", required=True)

    # broadcasts ---------------------------------------------------------
    b = groups.add_parser("broadcasts").add_subparsers(dest="action", required=True)
    b.add_parser("list")
    p = b.add_parser("get"); p.add_argument("id")
    p = b.add_parser("stats"); p.add_argument("id")
    p = b.add_parser("create")
    p.add_argument("--subject", required=True)
    p.add_argument("--content", help="HTML/text body (or use --body-file)")
    p.add_argument("--body-file", help="path to a body file")
    p.add_argument("--send-at", help="ISO timestamp to schedule; omit to leave as draft")
    p.add_argument("--set", action="append", metavar="key=value")

    # sequences ----------------------------------------------------------
    s = groups.add_parser("sequences").add_subparsers(dest="action", required=True)
    s.add_parser("list")
    p = s.add_parser("create"); p.add_argument("--name", required=True)

    # sequence-emails ----------------------------------------------------
    se = groups.add_parser("sequence-emails").add_subparsers(dest="action", required=True)
    p = se.add_parser("list"); p.add_argument("--sequence-id", required=True)
    p = se.add_parser("create")
    p.add_argument("--sequence-id", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--content", help="HTML/text body (or use --body-file)")
    p.add_argument("--body-file")
    p.add_argument("--delay-days", type=int, default=0)

    # tags ---------------------------------------------------------------
    t = groups.add_parser("tags").add_subparsers(dest="action", required=True)
    t.add_parser("list")
    p = t.add_parser("create"); p.add_argument("--name", required=True)

    # custom-fields ------------------------------------------------------
    groups.add_parser("custom-fields").add_subparsers(dest="action", required=True).add_parser("list")

    # subscribers --------------------------------------------------------
    sub = groups.add_parser("subscribers").add_subparsers(dest="action", required=True)
    p = sub.add_parser("list"); p.add_argument("--limit", type=int, default=50)
    p = sub.add_parser("create"); p.add_argument("--email", required=True); p.add_argument("--set", action="append", metavar="key=value")

    # segments -----------------------------------------------------------
    groups.add_parser("segments").add_subparsers(dest="action", required=True).add_parser("list")

    return parser


# ── dispatch ────────────────────────────────────────────────────────────

def _dispatch(args, client: KitClient) -> object:
    group, action = args.group, args.action

    if group == "broadcasts":
        if action == "list":
            return client.request("GET", "/broadcasts")
        if action == "get":
            return client.request("GET", f"/broadcasts/{args.id}")
        if action == "stats":
            return client.request("GET", f"/broadcasts/{args.id}/stats")
        if action == "create":
            content = args.content or _read_body_file(args.body_file)
            if not content:
                raise ConfigError("provide --content or --body-file for the broadcast body")
            body = {"subject": args.subject, "content": content, **_kv_body(args.set)}
            if args.send_at:
                body["send_at"] = args.send_at
            return client.request("POST", "/broadcasts", body=body)

    if group == "sequences":
        if action == "list":
            return client.request("GET", "/sequences")
        if action == "create":
            return client.request("POST", "/sequences", body={"name": args.name})

    if group == "sequence-emails":
        if action == "list":
            return client.request("GET", f"/sequences/{args.sequence_id}/emails")
        if action == "create":
            content = args.content or _read_body_file(args.body_file)
            if not content:
                raise ConfigError("provide --content or --body-file for the email body")
            body = {"subject": args.subject, "content": content, "delay_days": args.delay_days}
            return client.request("POST", f"/sequences/{args.sequence_id}/emails", body=body)

    if group == "tags":
        if action == "list":
            return client.request("GET", "/tags")
        if action == "create":
            return client.request("POST", "/tags", body={"name": args.name})

    if group == "custom-fields":
        if action == "list":
            return client.request("GET", "/custom_fields")

    if group == "subscribers":
        if action == "list":
            return client.request("GET", "/subscribers", params={"per_page": args.limit})
        if action == "create":
            return client.request("POST", "/subscribers", body={"email_address": args.email, **_kv_body(args.set)})

    if group == "segments":
        if action == "list":
            return client.request("GET", "/segments")

    raise ConfigError(f"unknown command: {group} {action}")


def main(argv: list[str] | None = None, *, client: KitClient | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if client is None:
            client = KitClient(KitConfig.from_env())
        result = _dispatch(args, client)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KitError as exc:
        payload = {"error": str(exc), "status": exc.status, "body": exc.body}
        print(json.dumps(payload, indent=2), file=sys.stderr)
        return 1
    _emit(result, compact=args.json)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
