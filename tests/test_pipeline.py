"""Tests for the content pipeline engine."""

import pytest

from content_engine.pipeline import Pipeline, Stage, Status


def _echo(ctx):
    ctx["visited"] = ctx.get("visited", []) + ["echo"]
    return ctx


def _double(ctx):
    ctx["value"] = ctx.get("value", 1) * 2
    return ctx


def _boom(ctx):
    raise ValueError("kaboom")


class TestStage:
    def test_run_updates_status(self):
        stage = Stage("test", _echo)
        result = stage.run({})
        assert stage.status == Status.COMPLETED
        assert result["visited"] == ["echo"]

    def test_run_records_timestamps(self):
        stage = Stage("test", _echo)
        stage.run({})
        assert stage.started_at is not None
        assert stage.finished_at is not None
        assert stage.finished_at >= stage.started_at

    def test_duration(self):
        stage = Stage("test", _echo)
        stage.run({})
        assert stage.duration is not None
        assert stage.duration.total_seconds() >= 0

    def test_required_stage_raises(self):
        stage = Stage("test", _boom, required=True)
        with pytest.raises(ValueError, match="kaboom"):
            stage.run({})
        assert stage.status == Status.FAILED
        assert stage.error == "kaboom"

    def test_optional_stage_skips(self):
        stage = Stage("test", _boom, required=False)
        result = stage.run({"keep": "me"})
        assert stage.status == Status.FAILED
        assert result["keep"] == "me"


class TestPipeline:
    def test_empty_pipeline(self):
        p = Pipeline(name="empty")
        result = p.run({})
        assert "_pipeline" in result
        assert result["_stages"] == {}

    def test_stages_run_in_order(self):
        def add_a(ctx):
            ctx["order"] = ctx.get("order", []) + ["a"]
            return ctx

        def add_b(ctx):
            ctx["order"] = ctx.get("order", []) + ["b"]
            return ctx

        p = Pipeline(name="ordered")
        p.add_stage(Stage("first", add_a))
        p.add_stage(Stage("second", add_b))
        result = p.run({})
        assert result["order"] == ["a", "b"]

    def test_context_flows_between_stages(self):
        p = Pipeline(name="flow")
        p.add_stage(Stage("init", lambda ctx: {**ctx, "value": 1}))
        p.add_stage(Stage("double", _double))
        p.add_stage(Stage("double2", _double))
        result = p.run({})
        assert result["value"] == 4

    def test_required_failure_stops_pipeline(self):
        p = Pipeline(name="halt")
        p.add_stage(Stage("ok", _echo))
        p.add_stage(Stage("fail", _boom, required=True))
        p.add_stage(Stage("never", _echo))
        result = p.run({})
        assert result["_failed_stage"] == "fail"
        assert result["_stages"]["never"] == "pending"

    def test_optional_failure_continues(self):
        p = Pipeline(name="continue")
        p.add_stage(Stage("ok", _echo))
        p.add_stage(Stage("soft-fail", _boom, required=False))
        p.add_stage(Stage("still-runs", _echo))
        result = p.run({})
        assert result["_stages"]["soft-fail"] == "failed"
        assert result["_stages"]["still-runs"] == "completed"

    def test_report(self):
        p = Pipeline(name="report-test")
        p.add_stage(Stage("one", _echo))
        p.run({})
        report = p.report()
        assert "report-test" in report
        assert "[+] one" in report

    def test_add_stage_returns_self(self):
        p = Pipeline(name="chain")
        result = p.add_stage(Stage("a", _echo)).add_stage(Stage("b", _echo))
        assert result is p
        assert len(p.stages) == 2
