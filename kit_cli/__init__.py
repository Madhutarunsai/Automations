"""Kit (formerly ConvertKit) CLI — agent-accessible email marketing.

Companion to ``gohighlevel_cli``; together they cover the workflow described in
Lead Gen Jay's GHL/Kit videos: CRM/automation in GHL, deliverability-grade
broadcasts and nurture sequences in Kit.

Standard-library only (``urllib`` + ``argparse``), no third-party dependencies.
Talks to the Kit v4 REST API using a ``KIT_API_KEY``.
"""

from .client import KitClient, KitError
from .config import KitConfig, ConfigError

__all__ = ["KitClient", "KitError", "KitConfig", "ConfigError"]
__version__ = "0.1.0"
