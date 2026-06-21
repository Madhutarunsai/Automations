"""Tests for the lead-gen flow deployer (no network)."""

from __future__ import annotations

import json
from pathlib import Path

from flows.deploy import FlowDeployer, _extract_id, load_flow, main

FLOW_DIR = Path(__file__).resolve().parent.parent / "flows" / "ai_automation_leadgen"


def test_real_flow_spec_loads_and_files_exist():
    flow = load_flow(FLOW_DIR / "flow.json")
    assert flow["kit"]["sequence_name"]
    for email in flow["kit"]["emails"]:
        assert (FLOW_DIR / email["body_file"]).exists()
    assert (FLOW_DIR / flow["ghl"]["workflow_file"]).exists()


def test_extract_id_handles_wrapped_and_flat():
    assert _extract_id({"sequence": {"id": 7}}, "sequence") == 7
    assert _extract_id({"id": 9}, "sequence") == 9
    assert _extract_id({"nope": 1}, "sequence") is None
    assert _extract_id("not a dict") is None


def test_plan_orders_steps_and_gates_ghl():
    flow = load_flow(FLOW_DIR / "flow.json")
    plan = FlowDeployer(flow, FLOW_DIR, experimental=False).plan()
    ops = [s["op"] for s in plan]
    assert ops[0] == "ensure-tag"
    assert "create-sequence" in ops
    assert ops.count("add-sequence-email") == 6  # 4 nurture + 2 re-engage
    # GHL step present but flagged skipped without --experimental
    ghl_step = [s for s in plan if s["op"] == "create-workflow"][0]
    assert "SKIPPED" in ghl_step["summary"]
    # With experimental on, the skip note is gone.
    plan2 = FlowDeployer(flow, FLOW_DIR, experimental=True).plan()
    assert "SKIPPED" not in [s for s in plan2 if s["op"] == "create-workflow"][0]["summary"]


class FakeKit:
    def __init__(self):
        self.calls = []
        self._seq = 100

    def request(self, method, path, *, params=None, body=None):
        self.calls.append((method, path, body))
        if method == "GET" and path == "/tags":
            return {"tags": [{"id": 1, "name": "existing"}]}
        if method == "POST" and path == "/tags":
            return {"tag": {"id": 2, "name": body["name"]}}
        if method == "POST" and path == "/sequences":
            self._seq += 1
            return {"sequence": {"id": self._seq, "name": body["name"]}}
        if "/emails" in path:
            return {"id": 555}
        return {}


class FakeGHL:
    def __init__(self):
        self.calls = []

    def internal_request(self, method, path, *, params=None, body=None):
        self.calls.append((method, path, body))
        return {"workflow": {"id": "wf_1"}}


def test_apply_provisions_tag_sequences_and_chains_ids():
    flow = load_flow(FLOW_DIR / "flow.json")
    kit, ghl = FakeKit(), FakeGHL()
    results = FlowDeployer(flow, FLOW_DIR, experimental=True, kit_client=kit, ghl_client=ghl).apply()

    # Tag created (not pre-existing), two sequences, each email posted to the sequence id.
    tag = [r for r in results if r["op"] == "ensure-tag"][0]
    assert tag["existed"] is False and tag["id"] == 2

    seqs = [r for r in results if r["op"] == "create-sequence"]
    assert len(seqs) == 2
    nurture_id = seqs[0]["id"]
    email_posts = [c for c in kit.calls if c[1].endswith("/emails")]
    assert email_posts[0][1] == f"/sequences/{nurture_id}/emails"
    # Bodies were read from the email files (non-empty content).
    assert all(c[2]["content"].strip() for c in email_posts)

    # GHL workflow created via the internal API when --experimental is set.
    assert ghl.calls and ghl.calls[0][1] == "/workflows/"


def test_apply_skips_ghl_without_experimental():
    flow = load_flow(FLOW_DIR / "flow.json")
    kit, ghl = FakeKit(), FakeGHL()
    results = FlowDeployer(flow, FLOW_DIR, experimental=False, kit_client=kit, ghl_client=ghl).apply()
    wf = [r for r in results if r["op"] == "create-workflow"][0]
    assert wf.get("skipped")
    assert ghl.calls == []


def test_apply_uses_existing_tag_when_present():
    flow = {"kit": {"tag": "existing"}}
    kit = FakeKit()
    results = FlowDeployer(flow, FLOW_DIR, kit_client=kit).apply()
    tag = results[0]
    assert tag["existed"] is True and tag["id"] == 1
    assert not any(c[0] == "POST" and c[1] == "/tags" for c in kit.calls)


def test_main_dry_run_prints_plan(capsys):
    rc = main([str(FLOW_DIR / "flow.json")])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Plan:" in out and "dry-run" in out
    assert "GHL CLI Nurture" in out
