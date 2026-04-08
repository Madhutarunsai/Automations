"""Tests for the content calendar."""

import datetime as dt
import json
import tempfile
from pathlib import Path

import pytest

from content_engine.calendar import ContentCalendar, ContentItem, ContentStatus


@pytest.fixture
def today():
    return dt.date(2026, 4, 8)


@pytest.fixture
def sample_items(today):
    return [
        ContentItem(
            title="Post A",
            topic="ai",
            status=ContentStatus.SCHEDULED,
            publish_date=today,
            tags=["ai", "tutorial"],
            channel="blog",
        ),
        ContentItem(
            title="Post B",
            topic="python",
            status=ContentStatus.DRAFTING,
            publish_date=today + dt.timedelta(days=3),
            tags=["python"],
            channel="blog",
        ),
        ContentItem(
            title="Newsletter C",
            topic="news",
            status=ContentStatus.IDEA,
            publish_date=today + dt.timedelta(days=10),
            tags=["news"],
            channel="newsletter",
        ),
        ContentItem(
            title="Tweet D",
            topic="tips",
            status=ContentStatus.PUBLISHED,
            publish_date=today - dt.timedelta(days=1),
            tags=["tips"],
            channel="social",
        ),
    ]


class TestContentItem:
    def test_is_due_when_scheduled_and_past(self, today):
        item = ContentItem(
            title="Due", topic="x", status=ContentStatus.SCHEDULED, publish_date=today
        )
        assert item.is_due(today) is True

    def test_not_due_when_published(self, today):
        item = ContentItem(
            title="Done", topic="x", status=ContentStatus.PUBLISHED, publish_date=today
        )
        assert item.is_due(today) is False

    def test_not_due_when_future(self, today):
        item = ContentItem(
            title="Future",
            topic="x",
            status=ContentStatus.SCHEDULED,
            publish_date=today + dt.timedelta(days=5),
        )
        assert item.is_due(today) is False

    def test_not_due_when_no_date(self, today):
        item = ContentItem(title="No date", topic="x")
        assert item.is_due(today) is False

    def test_advance_workflow(self):
        item = ContentItem(title="Flow", topic="x", status=ContentStatus.IDEA)
        item.advance()
        assert item.status == ContentStatus.RESEARCHING
        item.advance()
        assert item.status == ContentStatus.DRAFTING
        item.advance()
        assert item.status == ContentStatus.REVIEWING
        item.advance()
        assert item.status == ContentStatus.SCHEDULED
        item.advance()
        assert item.status == ContentStatus.PUBLISHED

    def test_advance_stops_at_published(self):
        item = ContentItem(title="Done", topic="x", status=ContentStatus.PUBLISHED)
        item.advance()
        assert item.status == ContentStatus.PUBLISHED


class TestContentCalendar:
    def test_add_and_count(self, sample_items):
        cal = ContentCalendar()
        for item in sample_items:
            cal.add(item)
        assert len(cal.items) == 4

    def test_due(self, sample_items, today):
        cal = ContentCalendar(sample_items)
        due = cal.due(today)
        assert len(due) == 1
        assert due[0].title == "Post A"

    def test_by_status(self, sample_items):
        cal = ContentCalendar(sample_items)
        drafting = cal.by_status(ContentStatus.DRAFTING)
        assert len(drafting) == 1
        assert drafting[0].title == "Post B"

    def test_by_channel(self, sample_items):
        cal = ContentCalendar(sample_items)
        blogs = cal.by_channel("blog")
        assert len(blogs) == 2

    def test_by_tag(self, sample_items):
        cal = ContentCalendar(sample_items)
        ai = cal.by_tag("ai")
        assert len(ai) == 1
        assert ai[0].title == "Post A"

    def test_upcoming(self, sample_items, today):
        cal = ContentCalendar(sample_items)
        upcoming = cal.upcoming(7, today)
        assert len(upcoming) == 2  # Post A (today) and Post B (today+3)

    def test_summary(self, sample_items):
        cal = ContentCalendar(sample_items)
        s = cal.summary()
        assert s["scheduled"] == 1
        assert s["drafting"] == 1
        assert s["idea"] == 1
        assert s["published"] == 1

    def test_save_and_load(self, sample_items):
        cal = ContentCalendar(sample_items)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "calendar.json"
            cal.save(path)

            loaded = ContentCalendar.load(path)
            assert len(loaded.items) == len(cal.items)
            assert loaded.items[0].title == "Post A"
            assert loaded.items[0].status == ContentStatus.SCHEDULED
            assert loaded.items[0].publish_date == sample_items[0].publish_date

    def test_save_creates_parent_dirs(self, sample_items):
        cal = ContentCalendar(sample_items)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "deep" / "calendar.json"
            cal.save(path)
            assert path.exists()
            data = json.loads(path.read_text())
            assert len(data) == 4
