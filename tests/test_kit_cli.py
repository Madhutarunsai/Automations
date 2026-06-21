"""Tests for the Kit CLI (no network calls)."""

from __future__ import annotations

import json

import pytest

from kit_cli.cli import _kv_body, build_parser, main
from kit_cli.client import KitClient, KitError
from kit_cli.config import ConfigError, KitConfig


def test_from_env_requires_api_key(monkeypatch):
    monkeypatch.delenv("KIT_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        KitConfig.from_env()


def test_kv_body_decodes():
    assert _kv_body(["a=1", "b=hi"]) == {"a": 1, "b": "hi"}
    with pytest.raises(ConfigError):
        _kv_body(["bad"])


class FakeClient:
    def __init__(self):
        self.config = KitConfig(api_key="k")
        self.calls: list[tuple] = []

    def request(self, method, path, *, params=None, body=None):
        self.calls.append((method, path, params, body))
        return {"ok": True}


def run(argv, client):
    return main(argv, client=client)


def test_broadcasts_list():
    fc = FakeClient()
    assert run(["broadcasts", "list"], fc) == 0
    assert fc.calls[0][:2] == ("GET", "/broadcasts")


def test_broadcast_create_with_body_file(tmp_path, capsys):
    body_file = tmp_path / "b.html"
    body_file.write_text("<p>hello</p>")
    fc = FakeClient()
    run(["broadcasts", "create", "--subject", "Hi", "--body-file", str(body_file), "--send-at", "2026-07-01T10:00:00Z"], fc)
    method, path, _, body = fc.calls[0]
    assert (method, path) == ("POST", "/broadcasts")
    assert body == {"subject": "Hi", "content": "<p>hello</p>", "send_at": "2026-07-01T10:00:00Z"}
    assert json.loads(capsys.readouterr().out) == {"ok": True}


def test_broadcast_create_requires_body():
    fc = FakeClient()
    assert run(["broadcasts", "create", "--subject", "Hi"], fc) == 2
    assert fc.calls == []


def test_sequence_email_create_path():
    fc = FakeClient()
    run(["sequence-emails", "create", "--sequence-id", "9", "--subject", "S", "--content", "x", "--delay-days", "2"], fc)
    method, path, _, body = fc.calls[0]
    assert (method, path) == ("POST", "/sequences/9/emails")
    assert body == {"subject": "S", "content": "x", "delay_days": 2}


def test_subscriber_create():
    fc = FakeClient()
    run(["subscribers", "create", "--email", "a@b.com", "--set", "first_name=Jay"], fc)
    method, path, _, body = fc.calls[0]
    assert (method, path) == ("POST", "/subscribers")
    assert body == {"email_address": "a@b.com", "first_name": "Jay"}


def test_api_error_reported(capsys):
    class Boom(FakeClient):
        def request(self, *a, **k):
            raise KitError(422, "bad", {"errors": ["bad"]})

    assert run(["tags", "list"], Boom()) == 1
    assert json.loads(capsys.readouterr().err)["status"] == 422


def test_parser_groups():
    parser = build_parser()
    for argv in (
        ["broadcasts", "stats", "1"],
        ["sequences", "create", "--name", "n"],
        ["tags", "list"],
        ["custom-fields", "list"],
        ["segments", "list"],
    ):
        ns = parser.parse_args(argv)
        assert ns.group and ns.action


def test_client_constructible():
    assert KitClient(KitConfig(api_key="x")).config.api_key == "x"
