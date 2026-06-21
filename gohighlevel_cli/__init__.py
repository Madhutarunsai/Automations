"""GoHighLevel CLI — agent-accessible command-line access to the GHL CRM.

Built as a reference implementation modelled on Lead Gen Jay's `gohighlevel-cli`
skill, but reworked to fit this repo's conventions: standard-library only
(``urllib`` + ``argparse``), no third-party dependencies.

Two API surfaces are supported:

* **Public API** (stable) — GoHighLevel API v2 via a Private Integration Token.
* **Internal API** (experimental) — undocumented endpoints reached with the
  caller's own Firebase session token. Gated behind ``--experimental`` and the
  user's own credentials. This mirrors the video's "internal API" path; it is
  only ever pointed at the operator's own account/data.
"""

from .client import GHLClient, GHLError
from .config import Config, ConfigError

__all__ = ["GHLClient", "GHLError", "Config", "ConfigError"]
__version__ = "0.1.0"
