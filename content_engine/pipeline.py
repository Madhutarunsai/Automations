"""Multi-stage content pipeline with pluggable processors."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Stage:
    """A single processing stage in the pipeline.

    Args:
        name: Human-readable stage name.
        processor: Callable that receives context dict and returns updated context.
        required: If True, pipeline halts on failure. Otherwise the stage is skipped.
    """

    name: str
    processor: Callable[[dict[str, Any]], dict[str, Any]]
    required: bool = True
    status: Status = Status.PENDING
    started_at: dt.datetime | None = None
    finished_at: dt.datetime | None = None
    error: str | None = None

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        self.status = Status.IN_PROGRESS
        self.started_at = dt.datetime.now(dt.timezone.utc)
        try:
            result = self.processor(context)
            self.status = Status.COMPLETED
            return result
        except Exception as exc:
            self.error = str(exc)
            self.status = Status.FAILED
            if self.required:
                raise
            return context
        finally:
            self.finished_at = dt.datetime.now(dt.timezone.utc)

    @property
    def duration(self) -> dt.timedelta | None:
        if self.started_at and self.finished_at:
            return self.finished_at - self.started_at
        return None


@dataclass
class Pipeline:
    """Ordered sequence of stages that transform a content context dict.

    Usage:
        pipeline = Pipeline(name="blog-post")
        pipeline.add_stage(Stage("research", research_fn))
        pipeline.add_stage(Stage("draft", draft_fn))
        pipeline.add_stage(Stage("review", review_fn, required=False))
        pipeline.add_stage(Stage("publish", publish_fn))
        result = pipeline.run({"topic": "AI Agents"})
    """

    name: str
    stages: list[Stage] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def add_stage(self, stage: Stage) -> "Pipeline":
        self.stages.append(stage)
        return self

    def run(self, initial_context: dict[str, Any] | None = None) -> dict[str, Any]:
        self.context = dict(initial_context or {})
        self.context["_pipeline"] = self.name
        self.context["_started_at"] = dt.datetime.now(dt.timezone.utc).isoformat()

        for stage in self.stages:
            try:
                self.context = stage.run(self.context)
            except Exception:
                pass  # stage.run already set status to FAILED
            if stage.status == Status.FAILED and stage.required:
                self.context["_failed_stage"] = stage.name
                break

        self.context["_finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        self.context["_stages"] = {s.name: s.status.value for s in self.stages}
        return self.context

    def report(self) -> str:
        lines = [f"Pipeline: {self.name}", ""]
        for s in self.stages:
            icon = {"completed": "+", "failed": "!", "skipped": "-", "pending": " "}.get(
                s.status.value, "?"
            )
            dur = f" ({s.duration.total_seconds():.2f}s)" if s.duration else ""
            err = f"  error: {s.error}" if s.error else ""
            lines.append(f"  [{icon}] {s.name}{dur}{err}")
        return "\n".join(lines)
