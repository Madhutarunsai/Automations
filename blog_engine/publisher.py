"""Blog post publisher — handles scheduling and batch publishing."""

from __future__ import annotations

import csv
import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path

from blog_engine.generator import BlogPost, BlogEngine, SEOConfig


TOPICS_PATH = Path(__file__).resolve().parent / "topics.json"


@dataclass
class TopicEntry:
    """A planned or published topic."""

    keyword: str
    title: str
    pillar: str
    status: str = "planned"  # planned | drafted | published | rejected
    slug: str = ""
    date_planned: str = ""
    date_published: str = ""
    seo_score: float = 0.0
    overall_score: float = 0.0


class PostPublisher:
    """Manages topic planning, scheduling, and publishing pipeline."""

    def __init__(self, engine: BlogEngine | None = None):
        self.engine = engine or BlogEngine()
        self.topics: list[TopicEntry] = []
        self._load_topics()

    def _load_topics(self):
        if TOPICS_PATH.exists():
            data = json.loads(TOPICS_PATH.read_text())
            self.topics = [TopicEntry(**t) for t in data]

    def save_topics(self):
        TOPICS_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = [t.__dict__ for t in self.topics]
        TOPICS_PATH.write_text(json.dumps(data, indent=2))

    def plan_topic(self, keyword: str, title: str, pillar: str, date: str = "") -> TopicEntry:
        slug = title.lower().replace(" ", "-").replace("?", "").replace(":", "")[:80]
        entry = TopicEntry(
            keyword=keyword,
            title=title,
            pillar=pillar,
            slug=slug,
            date_planned=date or dt.date.today().isoformat(),
        )
        self.topics.append(entry)
        self.save_topics()
        return entry

    def publish_post(self, post: BlogPost) -> Path:
        """Score, save, and mark a post as published."""
        self.engine.score_post(post)

        # Only publish if quality threshold met
        if post.overall_score < 50.0:
            for t in self.topics:
                if t.slug == post.slug:
                    t.status = "rejected"
            self.save_topics()
            raise ValueError(
                f"Post '{post.title}' scored {post.overall_score}/100 — "
                f"below minimum threshold of 50. Rejected."
            )

        path = self.engine.save_post(post)

        # Update topic status
        for t in self.topics:
            if t.slug == post.slug:
                t.status = "published"
                t.date_published = dt.date.today().isoformat()
                t.seo_score = post.seo_score
                t.overall_score = post.overall_score
        self.save_topics()
        return path

    def pending_topics(self) -> list[TopicEntry]:
        return [t for t in self.topics if t.status == "planned"]

    def published_topics(self) -> list[TopicEntry]:
        return [t for t in self.topics if t.status == "published"]

    def topics_by_pillar(self, pillar: str) -> list[TopicEntry]:
        return [t for t in self.topics if t.pillar == pillar]

    def publishing_stats(self) -> dict:
        total = len(self.topics)
        published = len(self.published_topics())
        planned = len(self.pending_topics())
        rejected = sum(1 for t in self.topics if t.status == "rejected")
        avg_score = 0.0
        pub = self.published_topics()
        if pub:
            avg_score = round(sum(t.overall_score for t in pub) / len(pub), 1)
        return {
            "total_topics": total,
            "published": published,
            "planned": planned,
            "rejected": rejected,
            "avg_overall_score": avg_score,
        }
