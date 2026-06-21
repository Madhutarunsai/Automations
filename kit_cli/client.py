"""Minimal HTTP client for the Kit v4 API (standard library only)."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .config import KitConfig


class KitError(RuntimeError):
    def __init__(self, status: int, message: str, body: Any = None):
        super().__init__(f"Kit error {status}: {message}" if status else f"Kit error: {message}")
        self.status = status
        self.body = body


class KitClient:
    def __init__(self, config: KitConfig, *, timeout: int = 30):
        self.config = config
        self.timeout = timeout

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        body: dict | None = None,
    ) -> Any:
        url = self.config.api_base + path
        if params:
            clean = {k: v for k, v in params.items() if v is not None}
            if clean:
                url += "?" + urllib.parse.urlencode(clean, doseq=True)
        headers = {
            # Kit v4 authenticates with this header.
            "X-Kit-Api-Key": self.config.api_key,
            "Accept": "application/json",
        }
        data = None
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=data, method=method.upper(), headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode()
        except urllib.error.HTTPError as exc:
            parsed = _read_error(exc)
            message = ""
            if isinstance(parsed, dict):
                errs = parsed.get("errors")
                if isinstance(errs, list) and errs:
                    message = "; ".join(str(e) for e in errs)
                message = message or parsed.get("message") or parsed.get("error") or ""
            raise KitError(exc.code, message or exc.reason, parsed)
        except urllib.error.URLError as exc:  # pragma: no cover - network
            raise KitError(0, f"network error: {exc.reason}")
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}


def _read_error(exc: urllib.error.HTTPError) -> Any:
    try:
        raw = exc.read().decode()
    except Exception:  # pragma: no cover - defensive
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}
