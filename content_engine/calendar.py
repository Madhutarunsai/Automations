"""Content calendar — schedule, query, and manage content items."""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path


class ContentStatus(Enum):
    IDEA = "idea"
    RESEARCHING = "researching"
    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class ContentItem:
    title: str
    topic: str
    status: ContentStatus = ContentStatus.IDEA
    publish_date: dt.date | None = None
    tags: list[str] = field(default_factory=list)
    channel: str = "blog"
    notes: str = ""
    created_at: str = field(
        default_factory=lambda: dt.datetime.now(dt.timezone.utc).isoformat()
    )

    def is_due(self, as_of: dt.date | None = None) -> bool:
        if self.publish_date is None:
            return False
        ref = as_of or dt.date.today()
        return self.publish_date <= ref and self.status != ContentStatus.PUBLISHED

    def advance(self) -> "ContentItem":
        """Move to the next status in the workflow."""
        order = list(ContentStatus)
        idx = order.index(self.status)
        if idx < len(order) - 2:  # don't auto-advance past PUBLISHED
            self.status = order[idx + 1]
        return self


class ContentCalendar:
    """Manages a collection of content items with persistence."""

    def __init__(self, items: list[ContentItem] | None = None):
        self.items: list[ContentItem] = list(items or [])

    def add(self, item: ContentItem) -> "ContentCalendar":
        self.items.append(item)
        return self

    def due(self, as_of: dt.date | None = None) -> list[ContentItem]:
        return [i for i in self.items if i.is_due(as_of)]

    def by_status(self, status: ContentStatus) -> list[ContentItem]:
        return [i for i in self.items if i.status == status]

    def by_channel(self, channel: str) -> list[ContentItem]:
        return [i for i in self.items if i.channel == channel]

    def by_tag(self, tag: str) -> list[ContentItem]:
        return [i for i in self.items if tag in i.tags]

    def upcoming(self, days: int = 7, as_of: dt.date | None = None) -> list[ContentItem]:
        ref = as_of or dt.date.today()
        window = ref + dt.timedelta(days=days)
        return [
            i
            for i in self.items
            if i.publish_date and ref <= i.publish_date <= window
        ]

    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.status.value] = counts.get(item.status.value, 0) + 1
        return counts

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = []
        for item in self.items:
            d = asdict(item)
            d["status"] = item.status.value
            d["publish_date"] = item.publish_date.isoformat() if item.publish_date else None
            data.append(d)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "ContentCalendar":
        path = Path(path)
        data = json.loads(path.read_text())
        items = []
        for d in data:
            d["status"] = ContentStatus(d["status"])
            d["publish_date"] = (
                dt.date.fromisoformat(d["publish_date"]) if d["publish_date"] else None
            )
            items.append(ContentItem(**d))
        return cls(items)
