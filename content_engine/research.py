"""Research pipeline — wraps karpathy/autoresearch into the content engine.

Provides a ResearchExperiment runner that manages the autoresearch loop:
branch creation, experiment execution, result parsing, and TSV logging.
"""

from __future__ import annotations

import csv
import datetime as dt
import io
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


AUTORESEARCH_DIR = Path(__file__).resolve().parent.parent / "autoresearch"

RESULT_PATTERN = re.compile(
    r"^(?P<key>val_bpb|training_seconds|total_seconds|peak_vram_mb|"
    r"mfu_percent|total_tokens_M|num_steps|num_params_M|depth):\s+(?P<value>\S+)$",
    re.MULTILINE,
)


@dataclass
class ExperimentResult:
    """Parsed output from a single autoresearch training run."""

    commit: str = ""
    val_bpb: float = 0.0
    peak_vram_mb: float = 0.0
    training_seconds: float = 0.0
    total_seconds: float = 0.0
    mfu_percent: float = 0.0
    total_tokens_m: float = 0.0
    num_steps: int = 0
    num_params_m: float = 0.0
    depth: int = 0
    status: str = "crash"  # keep | discard | crash
    description: str = ""

    @property
    def memory_gb(self) -> float:
        return round(self.peak_vram_mb / 1024, 1)

    def tsv_row(self) -> str:
        return "\t".join([
            self.commit[:7] if self.commit else "0000000",
            f"{self.val_bpb:.6f}",
            f"{self.memory_gb:.1f}",
            self.status,
            self.description,
        ])


def parse_run_output(output: str) -> dict[str, float]:
    """Extract key-value metrics from autoresearch training output."""
    results: dict[str, float] = {}
    for match in RESULT_PATTERN.finditer(output):
        key = match.group("key")
        try:
            results[key] = float(match.group("value"))
        except ValueError:
            pass
    return results


def build_experiment_result(
    output: str,
    commit: str = "",
    description: str = "",
) -> ExperimentResult:
    """Parse training output into an ExperimentResult."""
    metrics = parse_run_output(output)
    if not metrics:
        return ExperimentResult(
            commit=commit, status="crash", description=description
        )
    return ExperimentResult(
        commit=commit,
        val_bpb=metrics.get("val_bpb", 0.0),
        peak_vram_mb=metrics.get("peak_vram_mb", 0.0),
        training_seconds=metrics.get("training_seconds", 0.0),
        total_seconds=metrics.get("total_seconds", 0.0),
        mfu_percent=metrics.get("mfu_percent", 0.0),
        total_tokens_m=metrics.get("total_tokens_M", 0.0),
        num_steps=int(metrics.get("num_steps", 0)),
        num_params_m=metrics.get("num_params_M", 0.0),
        depth=int(metrics.get("depth", 0)),
        status="keep",
        description=description,
    )


@dataclass
class ResultsLog:
    """Manages the results.tsv experiment log."""

    path: Path
    entries: list[ExperimentResult] = field(default_factory=list)

    TSV_HEADER = "commit\tval_bpb\tmemory_gb\tstatus\tdescription"

    def add(self, result: ExperimentResult) -> None:
        self.entries.append(result)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [self.TSV_HEADER] + [e.tsv_row() for e in self.entries]
        self.path.write_text("\n".join(lines) + "\n")

    @classmethod
    def load(cls, path: Path) -> "ResultsLog":
        log = cls(path=path)
        if not path.exists():
            return log
        text = path.read_text().strip()
        if not text:
            return log
        reader = csv.DictReader(io.StringIO(text), delimiter="\t")
        for row in reader:
            log.entries.append(ExperimentResult(
                commit=row.get("commit", ""),
                val_bpb=float(row.get("val_bpb", 0)),
                peak_vram_mb=float(row.get("memory_gb", 0)) * 1024,
                status=row.get("status", "crash"),
                description=row.get("description", ""),
            ))
        return log

    @property
    def best_bpb(self) -> float | None:
        kept = [e for e in self.entries if e.status == "keep" and e.val_bpb > 0]
        return min(e.val_bpb for e in kept) if kept else None

    def summary(self) -> dict[str, Any]:
        total = len(self.entries)
        kept = sum(1 for e in self.entries if e.status == "keep")
        discarded = sum(1 for e in self.entries if e.status == "discard")
        crashed = sum(1 for e in self.entries if e.status == "crash")
        return {
            "total_experiments": total,
            "kept": kept,
            "discarded": discarded,
            "crashed": crashed,
            "best_bpb": self.best_bpb,
        }


def check_autoresearch_ready() -> dict[str, bool]:
    """Check if autoresearch prerequisites are met."""
    checks = {
        "autoresearch_dir_exists": AUTORESEARCH_DIR.is_dir(),
        "train_py_exists": (AUTORESEARCH_DIR / "train.py").is_file(),
        "prepare_py_exists": (AUTORESEARCH_DIR / "prepare.py").is_file(),
        "program_md_exists": (AUTORESEARCH_DIR / "program.md").is_file(),
    }

    # Check for GPU
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import torch; print(torch.cuda.is_available())"],
            capture_output=True, text=True, timeout=30,
        )
        checks["gpu_available"] = result.stdout.strip() == "True"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        checks["gpu_available"] = False

    # Check for cached data
    from pathlib import Path as P
    cache_dir = P.home() / ".cache" / "autoresearch"
    checks["data_prepared"] = (cache_dir / "data").is_dir() and any(
        (cache_dir / "data").glob("*.parquet")
    ) if (cache_dir / "data").is_dir() else False
    checks["tokenizer_trained"] = (
        cache_dir / "tokenizer" / "tokenizer.pkl"
    ).is_file() if (cache_dir / "tokenizer").is_dir() else False

    return checks


def format_readiness_report(checks: dict[str, bool]) -> str:
    """Format the readiness check as a human-readable report."""
    lines = ["Autoresearch Readiness Check", "=" * 35]
    for key, ok in checks.items():
        icon = "+" if ok else "!"
        label = key.replace("_", " ").title()
        lines.append(f"  [{icon}] {label}")

    all_good = all(checks.values())
    lines.append("")
    if all_good:
        lines.append("Ready to run experiments!")
    else:
        missing = [k for k, v in checks.items() if not v]
        lines.append("Not ready yet. Missing:")
        for m in missing:
            label = m.replace("_", " ")
            if m == "gpu_available":
                lines.append(f"  - {label}: need an NVIDIA GPU with CUDA")
            elif m == "data_prepared":
                lines.append(f"  - {label}: run 'uv run prepare.py' in autoresearch/")
            elif m == "tokenizer_trained":
                lines.append(f"  - {label}: run 'uv run prepare.py' in autoresearch/")
            else:
                lines.append(f"  - {label}")
    return "\n".join(lines)
