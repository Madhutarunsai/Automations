"""Environment-driven configuration for the Kit CLI."""

from __future__ import annotations

import os
from dataclasses import dataclass

KIT_API_BASE = "https://api.kit.com/v4"


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass
class KitConfig:
    api_key: str
    api_base: str = KIT_API_BASE

    @classmethod
    def from_env(cls, *, require_api_key: bool = True) -> "KitConfig":
        api_key = os.environ.get("KIT_API_KEY", "").strip()
        if require_api_key and not api_key:
            raise ConfigError(
                "KIT_API_KEY is not set. Create a v4 API key in Kit "
                "(Settings → Advanced → API) and export it as KIT_API_KEY."
            )
        return cls(
            api_key=api_key,
            api_base=os.environ.get("KIT_API_BASE", KIT_API_BASE),
        )
