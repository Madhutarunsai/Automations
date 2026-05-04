"""Telegram bot client. Pure stdlib (urllib).

Why no ``requests``? Keeps the project zero-dep, matches the rest of the
repo, and avoids supply-chain surface area for a 5-line API call.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


class TelegramError(RuntimeError):
    """Raised when the Telegram API returns an error or is unreachable."""


def send_message(bot_token: str, chat_id: str, text: str,
                 parse_mode: str = "Markdown") -> dict[str, Any]:
    """POST to /sendMessage. Returns the parsed JSON response.

    Telegram caps message length at 4096 chars. Longer messages are split.
    """
    if not bot_token or not chat_id:
        raise TelegramError("bot_token and chat_id are required")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    if len(text) > 4000:
        chunks = _split_text(text, 4000)
        last_response: dict[str, Any] = {}
        for chunk in chunks:
            last_response = _post(url, chat_id, chunk, parse_mode)
        return last_response

    return _post(url, chat_id, text, parse_mode)


def _post(url: str, chat_id: str, text: str, parse_mode: str) -> dict[str, Any]:
    payload = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": "true",
    }).encode()
    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode())
    except Exception as exc:
        raise TelegramError(f"Telegram request failed: {exc}") from exc

    if not body.get("ok"):
        raise TelegramError(f"Telegram API error: {body.get('description')}")
    return body


def _split_text(text: str, max_len: int) -> list[str]:
    """Split on paragraph boundaries first, then hard-break if a paragraph
    is itself too long. Preserves Markdown structure across chunks."""
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""
    for p in paragraphs:
        candidate = f"{current}\n\n{p}" if current else p
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(p) <= max_len:
                current = p
            else:
                # paragraph itself too long - hard-break
                for i in range(0, len(p), max_len):
                    chunks.append(p[i:i + max_len])
                current = ""
    if current:
        chunks.append(current)
    return chunks


def get_chat_id_hint(bot_token: str) -> str:
    """Helper: tells you the chat_id of whoever last DM'd the bot.

    Useful during setup. Send your bot a message, then run this.
    """
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = json.loads(resp.read().decode())
    except Exception as exc:
        raise TelegramError(f"getUpdates failed: {exc}") from exc

    if not body.get("ok"):
        raise TelegramError(f"Telegram API error: {body.get('description')}")
    updates = body.get("result", [])
    if not updates:
        return "No messages received yet. DM your bot first, then re-run."
    last = updates[-1]
    chat = last.get("message", {}).get("chat", {})
    return f"chat_id = {chat.get('id')} (from {chat.get('username') or chat.get('first_name')})"
