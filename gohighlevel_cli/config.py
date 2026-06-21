"""Environment-driven configuration for the GoHighLevel CLI."""

from __future__ import annotations

import os
from dataclasses import dataclass

# Public GHL API v2.
PUBLIC_API_BASE = "https://services.leadconnectorhq.com"
API_VERSION = "2021-07-28"

# Internal (undocumented) API. Overridable because the real host/paths are not
# published and may change. Used only with the operator's own session token.
DEFAULT_INTERNAL_API_BASE = "https://backend.leadconnectorhq.com"

# Firebase secure-token endpoint used to exchange a refresh token for an id token.
FIREBASE_TOKEN_URL = "https://securetoken.googleapis.com/v1/token"


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass
class Config:
    """Resolved runtime configuration.

    Everything is sourced from environment variables so the CLI can run
    unattended inside an agent loop with no secrets on the command line.
    """

    api_key: str
    location_id: str | None = None
    firebase_refresh_token: str | None = None
    firebase_api_key: str | None = None
    internal_api_base: str = DEFAULT_INTERNAL_API_BASE

    @classmethod
    def from_env(cls, *, require_api_key: bool = True) -> "Config":
        api_key = os.environ.get("GHL_API_KEY", "").strip()
        if require_api_key and not api_key:
            raise ConfigError(
                "GHL_API_KEY is not set. Create a Private Integration Token in "
                "GHL (Settings → Private Integrations) and export it as GHL_API_KEY."
            )
        return cls(
            api_key=api_key,
            location_id=os.environ.get("GHL_LOCATION_ID") or None,
            firebase_refresh_token=os.environ.get("GHL_FIREBASE_REFRESH_TOKEN") or None,
            firebase_api_key=os.environ.get("GHL_FIREBASE_API_KEY") or None,
            internal_api_base=os.environ.get(
                "GHL_INTERNAL_API_BASE", DEFAULT_INTERNAL_API_BASE
            ),
        )

    def require_location(self, override: str | None = None) -> str:
        """Return the location id, preferring an explicit override."""
        loc = override or self.location_id
        if not loc:
            raise ConfigError(
                "No location id. Pass --location-id or set GHL_LOCATION_ID "
                "(found in your GHL URL: app.../location/<LOCATION_ID>/...)."
            )
        return loc
