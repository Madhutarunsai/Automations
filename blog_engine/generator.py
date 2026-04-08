"""Blog post generator with SEO/AEO/GEO optimization scoring."""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent / "seo_rules.json"


@dataclass
class SEOConfig:
    """Loaded from seo_rules.json — the fixed evaluation standard."""

    site: dict = field(default_factory=dict)
    seo: dict = field(default_factory=dict)
    aeo: dict = field(default_factory=dict)
    geo: dict = field(default_factory=dict)
    content_pillars: list = field(default_factory=list)
    target_keywords: dict = field(default_factory=dict)
    internal_links: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None = None) -> "SEOConfig":
        path = path or RULES_PATH
        data = json.loads(path.read_text())
        return cls(**data)

    def pillar_for_date(self, date: dt.date | None = None) -> dict:
        date = date or dt.date.today()
        day_name = date.strftime("%A")
        for pillar in self.content_pillars:
            if pillar["day"] == day_name:
                return pillar
        return self.content_pillars[date.weekday() % len(self.content_pillars)]


@dataclass
class BlogPost:
    """A single blog post with SEO/AEO/GEO metadata."""

    title: str
    slug: str
    meta_description: str
    primary_keyword: str
    secondary_keywords: list[str]
    content: str  # full markdown body
    pillar: str
    faq: list[dict] = field(default_factory=list)  # [{"q": "...", "a": "..."}]
    stats_cited: list[str] = field(default_factory=list)
    tools_mentioned: list[str] = field(default_factory=list)
    internal_links_used: list[str] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat()
    )
    word_count: int = 0
    seo_score: float = 0.0
    aeo_score: float = 0.0
    geo_score: float = 0.0
    overall_score: float = 0.0

    def __post_init__(self):
        self.word_count = len(self.content.split())

    def evaluate(self, config: SEOConfig) -> dict:
        """Score the post against SEO/AEO/GEO rules. Returns breakdown."""
        seo = self._score_seo(config)
        aeo = self._score_aeo(config)
        geo = self._score_geo(config)
        self.seo_score = seo["score"]
        self.aeo_score = aeo["score"]
        self.geo_score = geo["score"]
        self.overall_score = round(
            (self.seo_score * 0.4 + self.aeo_score * 0.3 + self.geo_score * 0.3), 2
        )
        return {"seo": seo, "aeo": aeo, "geo": geo, "overall": self.overall_score}

    def _score_seo(self, config: SEOConfig) -> dict:
        rules = config.seo
        checks = {}
        # Title length
        checks["title_length"] = len(self.title) <= rules["title_max_chars"]
        # Title has keyword
        checks["title_has_keyword"] = (
            self.primary_keyword.lower() in self.title.lower()
        )
        # Meta description length
        md_len = len(self.meta_description)
        checks["meta_desc_length"] = (
            rules["meta_description_min_chars"] <= md_len <= rules["meta_description_max_chars"]
        )
        # Word count
        checks["word_count"] = (
            rules["min_word_count"] <= self.word_count <= rules["max_word_count"]
        )
        # Headings count
        headings = len(re.findall(r"^#{2,3}\s", self.content, re.MULTILINE))
        checks["enough_headings"] = headings >= rules["min_headings"]
        # Internal links
        checks["internal_links"] = (
            len(self.internal_links_used) >= rules["min_internal_links"]
        )
        # Keyword density
        kw_lower = self.primary_keyword.lower()
        content_lower = self.content.lower()
        kw_count = content_lower.count(kw_lower)
        density = kw_count / max(self.word_count, 1)
        checks["keyword_density"] = (
            rules["keyword_density_min"] <= density <= rules["keyword_density_max"]
        )
        passed = sum(checks.values())
        total = len(checks)
        return {"score": round(passed / total * 100, 1), "checks": checks}

    def _score_aeo(self, config: SEOConfig) -> dict:
        rules = config.aeo
        checks = {}
        # Direct answer in first N words
        first_words = " ".join(self.content.split()[:rules["direct_answer_within_words"]])
        checks["direct_answer_early"] = (
            self.primary_keyword.lower() in first_words.lower()
        )
        # FAQ section
        checks["has_faq"] = len(self.faq) >= rules["min_faq_questions"]
        # Question format in headings
        question_patterns = rules["question_formats"]
        heading_text = " ".join(re.findall(r"^#{2,3}\s+(.+)", self.content, re.MULTILINE))
        checks["question_headings"] = any(
            q.lower() in heading_text.lower() for q in question_patterns
        )
        # Citation tone
        citation_phrases = ["according to", "research shows", "studies indicate", "data from", "statistics show"]
        checks["citation_tone"] = any(
            p in self.content.lower() for p in citation_phrases
        )
        passed = sum(checks.values())
        total = len(checks)
        return {"score": round(passed / total * 100, 1), "checks": checks}

    def _score_geo(self, config: SEOConfig) -> dict:
        rules = config.geo
        checks = {}
        # Statistics cited
        checks["enough_stats"] = len(self.stats_cited) >= rules["min_statistics"]
        # Tool mentions
        checks["enough_tools"] = len(self.tools_mentioned) >= rules["min_tool_mentions"]
        # Step-by-step sections
        step_patterns = re.findall(
            r"(?:step\s+\d|^\d+\.\s)", self.content, re.MULTILINE | re.IGNORECASE
        )
        checks["has_steps"] = len(step_patterns) >= rules["min_step_by_step_sections"]
        # Comparisons
        comparison_words = [" vs ", " versus ", " compared to ", " better than ", " alternative"]
        checks["has_comparisons"] = any(
            w in self.content.lower() for w in comparison_words
        )
        passed = sum(checks.values())
        total = len(checks)
        return {"score": round(passed / total * 100, 1), "checks": checks}

    def to_markdown_file(self) -> str:
        """Render as a publishable markdown file with frontmatter."""
        faq_md = ""
        if self.faq:
            faq_md = "\n## Frequently Asked Questions\n\n"
            for item in self.faq:
                faq_md += f"### {item['q']}\n\n{item['a']}\n\n"

        frontmatter = f"""---
title: "{self.title}"
slug: "{self.slug}"
meta_description: "{self.meta_description}"
primary_keyword: "{self.primary_keyword}"
secondary_keywords: {json.dumps(self.secondary_keywords)}
pillar: "{self.pillar}"
word_count: {self.word_count}
seo_score: {self.seo_score}
aeo_score: {self.aeo_score}
geo_score: {self.geo_score}
overall_score: {self.overall_score}
date: "{self.created_at[:10]}"
author: "Madhu Tarun Sai"
---

"""
        return frontmatter + self.content + faq_md

    def to_dict(self) -> dict:
        return asdict(self)


class BlogEngine:
    """Manages blog post generation, scoring, and persistence."""

    def __init__(self, config: SEOConfig | None = None, posts_dir: str | Path | None = None):
        self.config = config or SEOConfig.load()
        self.posts_dir = Path(posts_dir or Path(__file__).resolve().parent / "posts")
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    def score_post(self, post: BlogPost) -> dict:
        return post.evaluate(self.config)

    def save_post(self, post: BlogPost) -> Path:
        date_str = post.created_at[:10]
        filename = f"{date_str}-{post.slug}.md"
        path = self.posts_dir / filename
        path.write_text(post.to_markdown_file())
        return path

    def list_posts(self) -> list[Path]:
        return sorted(self.posts_dir.glob("*.md"), reverse=True)

    def posts_today(self, date: dt.date | None = None) -> list[Path]:
        date = date or dt.date.today()
        prefix = date.isoformat()
        return [p for p in self.list_posts() if p.name.startswith(prefix)]

    def todays_pillar(self, date: dt.date | None = None) -> dict:
        return self.config.pillar_for_date(date)

    def daily_summary(self, date: dt.date | None = None) -> dict:
        posts = self.posts_today(date)
        return {
            "date": (date or dt.date.today()).isoformat(),
            "pillar": self.todays_pillar(date)["name"],
            "posts_published": len(posts),
            "target": 5,
            "filenames": [p.name for p in posts],
        }
