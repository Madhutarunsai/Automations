"""Tests for the autoresearch integration module."""

import tempfile
from pathlib import Path

import pytest

from content_engine.research import (
    ExperimentResult,
    ResultsLog,
    build_experiment_result,
    parse_run_output,
    check_autoresearch_ready,
    format_readiness_report,
)


SAMPLE_OUTPUT = """\
step 00953 (100.0%) | loss: 2.345678 | lrm: 0.00 | dt: 315ms | tok/sec: 1,234,567 | mfu: 39.8% | epoch: 1 | remaining: 0s
---
val_bpb:          0.997900
training_seconds: 300.1
total_seconds:    325.9
peak_vram_mb:     45060.2
mfu_percent:      39.80
total_tokens_M:   499.6
num_steps:        953
num_params_M:     50.3
depth:            8
"""

CRASH_OUTPUT = """\
Traceback (most recent call last):
  File "train.py", line 500, in <module>
    model = GPT(config)
RuntimeError: CUDA out of memory
"""


class TestParseRunOutput:
    def test_parses_all_metrics(self):
        metrics = parse_run_output(SAMPLE_OUTPUT)
        assert metrics["val_bpb"] == pytest.approx(0.997900)
        assert metrics["training_seconds"] == pytest.approx(300.1)
        assert metrics["total_seconds"] == pytest.approx(325.9)
        assert metrics["peak_vram_mb"] == pytest.approx(45060.2)
        assert metrics["mfu_percent"] == pytest.approx(39.80)
        assert metrics["total_tokens_M"] == pytest.approx(499.6)
        assert metrics["num_steps"] == 953
        assert metrics["num_params_M"] == pytest.approx(50.3)
        assert metrics["depth"] == 8

    def test_empty_on_crash(self):
        metrics = parse_run_output(CRASH_OUTPUT)
        assert metrics == {}

    def test_empty_string(self):
        metrics = parse_run_output("")
        assert metrics == {}


class TestBuildExperimentResult:
    def test_successful_run(self):
        result = build_experiment_result(SAMPLE_OUTPUT, commit="abc1234", description="baseline")
        assert result.val_bpb == pytest.approx(0.997900)
        assert result.peak_vram_mb == pytest.approx(45060.2)
        assert result.memory_gb == pytest.approx(44.0, abs=0.1)
        assert result.num_steps == 953
        assert result.status == "keep"
        assert result.description == "baseline"

    def test_crash_run(self):
        result = build_experiment_result(CRASH_OUTPUT, commit="def5678", description="double width")
        assert result.status == "crash"
        assert result.val_bpb == 0.0

    def test_tsv_row_format(self):
        result = build_experiment_result(SAMPLE_OUTPUT, commit="abc1234def", description="baseline")
        row = result.tsv_row()
        parts = row.split("\t")
        assert len(parts) == 5
        assert parts[0] == "abc1234"  # truncated to 7 chars
        assert parts[3] == "keep"
        assert parts[4] == "baseline"


class TestResultsLog:
    def test_add_and_summary(self):
        log = ResultsLog(path=Path("/tmp/test.tsv"))
        log.add(ExperimentResult(commit="aaa", val_bpb=0.998, status="keep", description="baseline"))
        log.add(ExperimentResult(commit="bbb", val_bpb=0.993, status="keep", description="increase LR"))
        log.add(ExperimentResult(commit="ccc", val_bpb=1.005, status="discard", description="try GeLU"))
        log.add(ExperimentResult(commit="ddd", status="crash", description="OOM"))

        summary = log.summary()
        assert summary["total_experiments"] == 4
        assert summary["kept"] == 2
        assert summary["discarded"] == 1
        assert summary["crashed"] == 1
        assert summary["best_bpb"] == pytest.approx(0.993)

    def test_best_bpb_none_when_empty(self):
        log = ResultsLog(path=Path("/tmp/test.tsv"))
        assert log.best_bpb is None

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "results.tsv"
            log = ResultsLog(path=path)
            log.add(ExperimentResult(
                commit="abc1234", val_bpb=0.998, peak_vram_mb=45000,
                status="keep", description="baseline",
            ))
            log.add(ExperimentResult(
                commit="def5678", val_bpb=0.993, peak_vram_mb=45200,
                status="keep", description="increase LR",
            ))
            log.save()

            loaded = ResultsLog.load(path)
            assert len(loaded.entries) == 2
            assert loaded.entries[0].commit == "abc1234"
            assert loaded.entries[0].status == "keep"
            assert loaded.entries[1].description == "increase LR"

    def test_load_nonexistent(self):
        log = ResultsLog.load(Path("/tmp/nonexistent_test_file.tsv"))
        assert len(log.entries) == 0


class TestReadinessCheck:
    def test_check_returns_dict(self):
        checks = check_autoresearch_ready()
        assert isinstance(checks, dict)
        assert "autoresearch_dir_exists" in checks
        assert "train_py_exists" in checks
        assert "prepare_py_exists" in checks
        assert "program_md_exists" in checks
        assert "gpu_available" in checks

    def test_autoresearch_files_exist(self):
        checks = check_autoresearch_ready()
        # These should be True since we cloned the repo
        assert checks["autoresearch_dir_exists"] is True
        assert checks["train_py_exists"] is True
        assert checks["prepare_py_exists"] is True
        assert checks["program_md_exists"] is True

    def test_format_report(self):
        checks = {"gpu_available": False, "data_prepared": True}
        report = format_readiness_report(checks)
        assert "Autoresearch Readiness Check" in report
        assert "[!]" in report  # gpu_available is False
        assert "[+]" in report  # data_prepared is True
