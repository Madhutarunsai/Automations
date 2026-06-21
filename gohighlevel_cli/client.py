"""Minimal HTTP client for the GoHighLevel public and internal APIs.

Uses only the standard library (``urllib``) to stay dependency-free.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .config import API_VERSION, FIREBASE_TOKEN_URL, PUBLIC_API_BASE, Config


class GHLError(RuntimeError):
    """An API or transport error, carrying the HTTP status and parsed body."""

    def __init__(self, status: int, message: str, body: Any = None):
        super().__init__(f"GHL error {status}: {message}" if status else f"GHL error: {message}")
        self.status = status
        self.body = body


class GHLClient:
    """Thin wrapper over the GHL REST surfaces.

    ``request`` hits the documented public API. ``internal_request`` hits the
    experimental internal API after exchanging the caller's Firebase refresh
    token for a short-lived id token.
    """

    def __init__(self, config: Config, *, timeout: int = 30):
        self.config = config
        self.timeout = timeout
        self._id_token: str | None = None

    # ── public API ────────────────────────────────────────────────────
    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        body: dict | None = None,
    ) -> Any:
        url = _with_params(PUBLIC_API_BASE + path, params)
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Version": API_VERSION,
            "Accept": "application/json",
        }
        return self._send(method, url, headers, body)

    # ── internal API (experimental) ───────────────────────────────────
    def internal_request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        body: dict | None = None,
    ) -> Any:
        token = self._ensure_id_token()
        url = _with_params(self.config.internal_api_base + path, params)
        headers = {
            # Header names mirror what the GHL web app sends with its session.
            "token-id": token,
            "channel": "APP",
            "source": "WEB_USER",
            "Version": API_VERSION,
            "Accept": "application/json",
        }
        return self._send(method, url, headers, body)

    def _ensure_id_token(self) -> str:
        if self._id_token:
            return self._id_token
        cfg = self.config
        if not cfg.firebase_refresh_token or not cfg.firebase_api_key:
            raise GHLError(
                0,
                "Experimental/internal commands need GHL_FIREBASE_REFRESH_TOKEN "
                "and GHL_FIREBASE_API_KEY (your own GHL web session token).",
            )
        data = urllib.parse.urlencode(
            {"grant_type": "refresh_token", "refresh_token": cfg.firebase_refresh_token}
        ).encode()
        req = urllib.request.Request(
            f"{FIREBASE_TOKEN_URL}?key={urllib.parse.quote(cfg.firebase_api_key)}",
            data=data,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:  # pragma: no cover - network
            raise GHLError(exc.code, "Firebase token refresh failed", _read_error(exc))
        except urllib.error.URLError as exc:  # pragma: no cover - network
            raise GHLError(0, f"network error during token refresh: {exc.reason}")
        token = payload.get("id_token") or payload.get("access_token")
        if not token:
            raise GHLError(0, "Firebase response did not include an id_token")
        self._id_token = token
        return token

    # ── transport ─────────────────────────────────────────────────────
    def _send(self, method: str, url: str, headers: dict, body: dict | None) -> Any:
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
                message = parsed.get("message") or parsed.get("error") or ""
            raise GHLError(exc.code, message or exc.reason, parsed)
        except urllib.error.URLError as exc:  # pragma: no cover - network
            raise GHLError(0, f"network error: {exc.reason}")
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}


def _with_params(url: str, params: dict | None) -> str:
    if not params:
        return url
    clean = {k: v for k, v in params.items() if v is not None}
    if not clean:
        return url
    return f"{url}?{urllib.parse.urlencode(clean, doseq=True)}"


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
