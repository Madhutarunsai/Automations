"""Tests for the GoHighLevel CLI (no network calls)."""

from __future__ import annotations

import json

import pytest

from gohighlevel_cli.cli import _kv_body, build_parser, main
from gohighlevel_cli.client import GHLClient, GHLError, _with_params
from gohighlevel_cli.config import Config, ConfigError


# ── config ──────────────────────────────────────────────────────────────

def test_from_env_requires_api_key(monkeypatch):
    monkeypatch.delenv("GHL_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        Config.from_env()


def test_from_env_reads_values(monkeypatch):
    monkeypatch.setenv("GHL_API_KEY", "pit-123")
    monkeypatch.setenv("GHL_LOCATION_ID", "loc-9")
    cfg = Config.from_env()
    assert cfg.api_key == "pit-123"
    assert cfg.location_id == "loc-9"


def test_require_location_prefers_override():
    cfg = Config(api_key="x", location_id="env-loc")
    assert cfg.require_location("cli-loc") == "cli-loc"
    assert cfg.require_location(None) == "env-loc"
    with pytest.raises(ConfigError):
        Config(api_key="x").require_location(None)


# ── helpers ──────────────────────────────────────────────────────────────

def test_with_params_drops_none():
    url = _with_params("http://h/x", {"a": 1, "b": None, "c": "z"})
    assert url in ("http://h/x?a=1&c=z", "http://h/x?c=z&a=1")
    assert _with_params("http://h/x", None) == "http://h/x"
    assert _with_params("http://h/x", {"a": None}) == "http://h/x"


def test_kv_body_json_decodes_values():
    body = _kv_body(["firstName=Jay", "tags=[\"a\",\"b\"]", "value=10"])
    assert body == {"firstName": "Jay", "tags": ["a", "b"], "value": 10}


def test_kv_body_rejects_bad_pair():
    with pytest.raises(ConfigError):
        _kv_body(["nope"])


# ── dispatch (fake client records the calls) ──────────────────────────────

class FakeClient:
    def __init__(self, location_id="loc-1", experimental_ready=True):
        self.config = Config(
            api_key="pit",
            location_id=location_id,
            firebase_refresh_token="r" if experimental_ready else None,
            firebase_api_key="k" if experimental_ready else None,
        )
        self.calls: list[tuple] = []

    def request(self, method, path, *, params=None, body=None):
        self.calls.append(("public", method, path, params, body))
        return {"ok": True}

    def internal_request(self, method, path, *, params=None, body=None):
        self.calls.append(("internal", method, path, params, body))
        return {"ok": True}


def run(argv, client):
    return main(argv, client=client)


def test_contacts_list_builds_request(capsys):
    fc = FakeClient()
    assert run(["contacts", "list", "--limit", "5"], fc) == 0
    kind, method, path, params, _ = fc.calls[0]
    assert (kind, method, path) == ("public", "GET", "/contacts/")
    assert params == {"locationId": "loc-1", "limit": 5, "query": None}
    assert json.loads(capsys.readouterr().out) == {"ok": True}


def test_contacts_create_merges_location_and_set():
    fc = FakeClient()
    run(["contacts", "create", "--set", "email=a@b.com"], fc)
    _, method, path, _, body = fc.calls[0]
    assert method == "POST" and path == "/contacts/"
    assert body == {"locationId": "loc-1", "email": "a@b.com"}


def test_add_tag_posts_tags():
    fc = FakeClient()
    run(["contacts", "add-tag", "c1", "vip", "lead"], fc)
    _, method, path, _, body = fc.calls[0]
    assert (method, path, body) == ("POST", "/contacts/c1/tags", {"tags": ["vip", "lead"]})


def test_workflow_enroll_path():
    fc = FakeClient()
    run(["workflows", "enroll", "--contact-id", "c1", "--workflow-id", "w1"], fc)
    _, method, path, _, _ = fc.calls[0]
    assert (method, path) == ("POST", "/contacts/c1/workflow/w1")


def test_workflow_create_requires_experimental_flag():
    fc = FakeClient()
    # Without --experimental the command is refused (returns error exit code).
    assert run(["workflows", "create", "--from-json", "x.json"], fc) == 2
    assert fc.calls == []


def test_workflow_create_uses_internal_api(tmp_path):
    fc = FakeClient()
    definition = tmp_path / "wf.json"
    definition.write_text(json.dumps({"name": "Welcome"}))
    rc = run(["--experimental", "workflows", "create", "--from-json", str(definition)], fc)
    assert rc == 0
    kind, method, path, _, body = fc.calls[0]
    assert kind == "internal" and method == "POST" and path == "/workflows/"
    assert body == {"name": "Welcome", "locationId": "loc-1"}


def test_payments_transactions_alt_params():
    fc = FakeClient()
    run(["payments", "transactions"], fc)
    _, _, path, params, _ = fc.calls[0]
    assert path == "/payments/transactions"
    assert params == {"altId": "loc-1", "altType": "location"}


def test_missing_location_is_an_error():
    fc = FakeClient(location_id=None)
    assert run(["contacts", "list"], fc) == 2


def test_api_error_is_reported(capsys):
    class Boom(FakeClient):
        def request(self, *a, **k):
            raise GHLError(404, "not found", {"message": "not found"})

    rc = run(["contacts", "get", "missing"], Boom())
    assert rc == 1
    err = json.loads(capsys.readouterr().err)
    assert err["status"] == 404


# ── parser smoke test ─────────────────────────────────────────────────────

def test_parser_accepts_all_groups():
    parser = build_parser()
    for argv in (
        ["contacts", "list"],
        ["opportunities", "pipelines"],
        ["calendars", "slots", "cal1", "--start", "1", "--end", "2"],
        ["conversations", "send", "--set", "type=Email"],
        ["locations", "custom-fields"],
    ):
        ns = parser.parse_args(argv)
        assert ns.group and ns.action


def test_client_is_constructible():
    # Ensures the real client wiring imports cleanly.
    client = GHLClient(Config(api_key="x", location_id="l"))
    assert client.config.api_key == "x"
