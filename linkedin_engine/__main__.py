"""CLI entry: ``python -m linkedin_engine <command>``.

Commands:
    send-daily            Send today's plan to Telegram (use --dry-run to print only)
    preview               Print today's plan to stdout
    chat-id               Print the chat_id of the latest message to your bot
    week                  Print the current week number
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

from linkedin_engine.planner import plan_day, week_number
from linkedin_engine.telegram import (
    TelegramError,
    get_chat_id_hint,
    send_message,
)


CONFIG_PATH = Path(__file__).parent / "config.json"


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        sys.exit(
            f"Config not found at {CONFIG_PATH}. "
            f"Copy config.example.json to config.json and fill it in."
        )
    with CONFIG_PATH.open() as f:
        return json.load(f)


def _build_plan(cfg: dict, override_date: str | None = None):
    today = dt.date.fromisoformat(override_date) if override_date else dt.date.today()
    start = dt.date.fromisoformat(cfg["program"]["start_date"])
    return plan_day(
        today=today,
        start_date=start,
        thesis=cfg["program"]["thesis"],
        cadence=cfg.get("cadence", {}),
    )


def cmd_send_daily(args: argparse.Namespace) -> int:
    cfg = _load_config()
    plan = _build_plan(cfg, args.date)
    msg = plan.to_telegram_markdown()

    if args.dry_run:
        print(msg)
        print("\n[dry-run] Not sent.")
        return 0

    try:
        send_message(
            bot_token=cfg["telegram"]["bot_token"],
            chat_id=cfg["telegram"]["chat_id"],
            text=msg,
        )
    except TelegramError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(f"Sent. ({len(msg)} chars)")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    cfg = _load_config()
    plan = _build_plan(cfg, args.date)
    print(plan.to_telegram_markdown())
    return 0


def cmd_chat_id(args: argparse.Namespace) -> int:
    cfg = _load_config()
    try:
        print(get_chat_id_hint(cfg["telegram"]["bot_token"]))
    except TelegramError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


def cmd_week(args: argparse.Namespace) -> int:
    cfg = _load_config()
    today = dt.date.today()
    start = dt.date.fromisoformat(cfg["program"]["start_date"])
    print(f"Week {week_number(today, start)} of the 26-week program "
          f"({today.strftime('%a %b %d')})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="linkedin_engine")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_send = sub.add_parser("send-daily", help="Send today's plan to Telegram")
    p_send.add_argument("--dry-run", action="store_true", help="Print only, don't send")
    p_send.add_argument("--date", help="Override date (YYYY-MM-DD), useful for testing")
    p_send.set_defaults(func=cmd_send_daily)

    p_prev = sub.add_parser("preview", help="Print today's plan to stdout")
    p_prev.add_argument("--date", help="Override date (YYYY-MM-DD)")
    p_prev.set_defaults(func=cmd_preview)

    p_id = sub.add_parser("chat-id", help="Print your Telegram chat_id (DM the bot first)")
    p_id.set_defaults(func=cmd_chat_id)

    p_wk = sub.add_parser("week", help="Print current week number of the program")
    p_wk.set_defaults(func=cmd_week)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
