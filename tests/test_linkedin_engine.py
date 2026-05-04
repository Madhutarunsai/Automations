"""Tests for linkedin_engine planner.

Telegram client isn't tested - it's a thin urllib wrapper, and we don't
mock external HTTP. CLI is exercised manually with --dry-run.
"""

from __future__ import annotations

import datetime as dt

from linkedin_engine.planner import (
    CONTENT_BY_WEEKDAY,
    WEEK_MILESTONES,
    plan_day,
    week_number,
)


THESIS = "I automate the back office of staffing firms. 6-week hires become 1-week hires."
START = dt.date(2026, 5, 4)  # Monday


def test_week_number_counts_from_one():
    assert week_number(START, START) == 1
    assert week_number(START + dt.timedelta(days=6), START) == 1
    assert week_number(START + dt.timedelta(days=7), START) == 2
    assert week_number(START + dt.timedelta(days=14), START) == 3


def test_week_number_floor_is_one():
    """Days before start still return week 1 (defensive)."""
    assert week_number(START - dt.timedelta(days=3), START) == 1


def test_monday_is_carousel_day():
    plan = plan_day(START, START, THESIS)
    assert plan.weekday_name == "Monday"
    assert "Carousel" in plan.content_block["format"]
    assert plan.content_block["cta_keyword"] == "HIRING"
    assert plan.is_workday


def test_thursday_is_comment_only():
    thursday = START + dt.timedelta(days=3)
    plan = plan_day(thursday, START, THESIS)
    assert "NO POST" in plan.content_block["format"]
    assert plan.is_workday  # still a work day, just no post


def test_sunday_is_off():
    sunday = START + dt.timedelta(days=6)
    plan = plan_day(sunday, START, THESIS)
    assert not plan.is_workday
    assert "OFF" in plan.content_block["format"]


def test_week_one_milestones_present():
    plan = plan_day(START, START, THESIS)
    assert len(plan.week_milestones) > 0
    assert any("verification" in m.lower() for m in plan.week_milestones)


def test_week_with_no_milestones_returns_empty():
    week_5_thursday = START + dt.timedelta(days=4 * 7 + 3)
    plan = plan_day(week_5_thursday, START, THESIS)
    assert plan.week_milestones == WEEK_MILESTONES.get(5, [])


def test_distribution_tasks_present_on_workdays():
    plan = plan_day(START, START, THESIS)
    assert any("comments" in t.lower() for t in plan.distribution_tasks)
    assert any("invites" in t.lower() for t in plan.distribution_tasks)


def test_telegram_render_includes_thesis_and_week():
    plan = plan_day(START, START, THESIS)
    rendered = plan.to_telegram_markdown()
    assert "Week 1" in rendered
    assert "staffing firms" in rendered
    assert "Distribution > Content" in rendered


def test_telegram_render_for_sunday_skips_post_block():
    sunday = START + dt.timedelta(days=6)
    plan = plan_day(sunday, START, THESIS)
    rendered = plan.to_telegram_markdown()
    assert "TODAY'S POST" not in rendered
    assert "TODAY" in rendered


def test_cadence_overrides_propagate():
    plan = plan_day(START, START, THESIS, cadence={"comments_per_day": 25})
    assert any("25 thoughtful comments" in t for t in plan.distribution_tasks)


def test_all_weekdays_have_content_definitions():
    for wd in range(7):
        assert wd in CONTENT_BY_WEEKDAY
        assert CONTENT_BY_WEEKDAY[wd]["format"]
