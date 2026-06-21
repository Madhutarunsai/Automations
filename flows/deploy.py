"""Provision a lead-gen flow from a JSON spec, using the GHL + Kit clients.

Dry-run by default (prints the ordered plan, no network). ``--apply`` executes
it against the live APIs using env credentials (``KIT_API_KEY`` for the Kit
steps; ``GHL_*`` for the optional GoHighLevel workflow step).

    python -m flows.deploy flows/ai_automation_leadgen/flow.json          # plan
    python -m flows.deploy flows/ai_automation_leadgen/flow.json --apply  # run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gohighlevel_cli.client import GHLClient
from gohighlevel_cli.config import Config as GHLConfig
from kit_cli.client import KitClient
from kit_cli.config import KitConfig


def load_flow(path: str | Path) -> dict:
    path = Path(path)
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_id(resp, *wrappers):
    """Pull an id out of a response that may wrap the object."""
    if not isinstance(resp, dict):
        return None
    for w in wrappers:
        inner = resp.get(w)
        if isinstance(inner, dict) and "id" in inner:
            return inner["id"]
    return resp.get("id")


class FlowDeployer:
    """Turns a flow spec into ordered provisioning steps."""

    def __init__(self, flow: dict, base_dir: str | Path, *, experimental: bool = False,
                 kit_client: KitClient | None = None, ghl_client: GHLClient | None = None):
        self.flow = flow
        self.base_dir = Path(base_dir)
        self.experimental = experimental
        self._kit = kit_client
        self._ghl = ghl_client

    # ── planning (pure, no network) ───────────────────────────────────
    def plan(self) -> list[dict]:
        steps: list[dict] = []
        kit = self.flow.get("kit", {})
        if tag := kit.get("tag"):
            steps.append({"tool": "kit", "op": "ensure-tag",
                          "summary": f"ensure Kit tag '{tag}' exists"})
        if seq := kit.get("sequence_name"):
            steps.append({"tool": "kit", "op": "create-sequence",
                          "summary": f"create Kit nurture sequence '{seq}'"})
            for i, email in enumerate(kit.get("emails", []), 1):
                steps.append({"tool": "kit", "op": "add-sequence-email",
                              "summary": f"  email {i} (day {email.get('delay_days', 0)}): "
                                         f"{email.get('subject', '(no subject)')}"})
        if reeng := kit.get("reengagement_sequence"):
            steps.append({"tool": "kit", "op": "create-sequence",
                          "summary": f"create Kit re-engagement sequence "
                                     f"'{reeng.get('sequence_name')}'"})
            for i, email in enumerate(reeng.get("emails", []), 1):
                steps.append({"tool": "kit", "op": "add-sequence-email",
                              "summary": f"  re-engage email {i} (day {email.get('delay_days', 0)}): "
                                         f"{email.get('subject', '(no subject)')}"})
        ghl = self.flow.get("ghl", {})
        if wf := ghl.get("workflow_file"):
            gate = "" if self.experimental else "  (SKIPPED — needs --experimental + Firebase creds)"
            steps.append({"tool": "ghl", "op": "create-workflow",
                          "summary": f"create GHL workflow from '{wf}'{gate}"})
        return steps

    # ── execution (live) ──────────────────────────────────────────────
    @property
    def kit(self) -> KitClient:
        if self._kit is None:
            self._kit = KitClient(KitConfig.from_env())
        return self._kit

    @property
    def ghl(self) -> GHLClient:
        if self._ghl is None:
            self._ghl = GHLClient(GHLConfig.from_env(require_api_key=False))
        return self._ghl

    def _read_email_body(self, email: dict) -> str:
        if "body_file" in email:
            return (self.base_dir / email["body_file"]).read_text(encoding="utf-8")
        return email.get("body", "")

    def _apply_sequence(self, spec: dict, results: list[dict]) -> None:
        created = self.kit.request("POST", "/sequences", body={"name": spec["sequence_name"]})
        seq_id = _extract_id(created, "sequence")
        results.append({"op": "create-sequence", "name": spec["sequence_name"], "id": seq_id})
        for email in spec.get("emails", []):
            body = {"subject": email["subject"], "content": self._read_email_body(email),
                    "delay_days": email.get("delay_days", 0)}
            res = self.kit.request("POST", f"/sequences/{seq_id}/emails", body=body)
            results.append({"op": "add-sequence-email", "sequence_id": seq_id,
                            "subject": email["subject"], "result": res})

    def apply(self) -> list[dict]:
        results: list[dict] = []
        kit = self.flow.get("kit", {})

        if tag := kit.get("tag"):
            existing = self.kit.request("GET", "/tags")
            names = {t.get("name"): t.get("id") for t in (existing.get("tags") or [])}
            if tag in names:
                results.append({"op": "ensure-tag", "name": tag, "id": names[tag], "existed": True})
            else:
                res = self.kit.request("POST", "/tags", body={"name": tag})
                results.append({"op": "ensure-tag", "name": tag, "id": _extract_id(res, "tag"),
                                "existed": False})

        if kit.get("sequence_name"):
            self._apply_sequence(kit, results)
        if reeng := kit.get("reengagement_sequence"):
            self._apply_sequence(reeng, results)

        ghl = self.flow.get("ghl", {})
        if wf := ghl.get("workflow_file"):
            if not self.experimental:
                results.append({"op": "create-workflow", "skipped": "needs --experimental"})
            else:
                definition = json.loads((self.base_dir / wf).read_text(encoding="utf-8"))
                res = self.ghl.internal_request("POST", "/workflows/", body=definition)
                results.append({"op": "create-workflow", "result": res})
        return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="leadflow", description="Provision a lead-gen flow")
    parser.add_argument("flow", help="path to a flow.json spec")
    parser.add_argument("--apply", action="store_true", help="execute against live APIs (default: dry-run)")
    parser.add_argument("--experimental", action="store_true", help="also create the GHL workflow (internal API)")
    args = parser.parse_args(argv)

    flow_path = Path(args.flow)
    flow = load_flow(flow_path)
    dep = FlowDeployer(flow, base_dir=flow_path.parent, experimental=args.experimental)

    print(f"Flow: {flow.get('name', flow_path.stem)}  (site: {flow.get('site', 'n/a')})")
    print(f"Lead magnet: {flow.get('lead_magnet', 'n/a')}")
    print(f"Trigger: {flow.get('trigger', 'n/a')}  →  Goal: {flow.get('goal', 'n/a')}\n")

    plan = dep.plan()
    print("Plan:")
    for i, step in enumerate(plan, 1):
        print(f"  {i:2}. [{step['tool']}] {step['summary']}")

    if not args.apply:
        print("\n(dry-run — pass --apply to execute. Kit steps need KIT_API_KEY; "
              "the GHL workflow step needs --experimental + Firebase creds.)")
        return 0

    print("\nApplying...")
    try:
        results = dep.apply()
    except Exception as exc:  # surface a clean message instead of a traceback
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
