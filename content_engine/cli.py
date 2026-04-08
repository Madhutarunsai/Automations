"""CLI for the content automation engine."""

from __future__ import annotations

import argparse
import datetime as dt
import sys

from content_engine.calendar import ContentCalendar, ContentItem, ContentStatus
from content_engine.pipeline import Pipeline, Stage


# ── Built-in demo processors ────────────────────────────────────────

def _research(ctx: dict) -> dict:
    topic = ctx.get("topic", "unknown")
    ctx["research"] = {
        "topic": topic,
        "key_points": [
            f"Core concepts of {topic}",
            f"Recent developments in {topic}",
            f"Expert opinions on {topic}",
        ],
        "sources": ["web search", "academic papers", "industry reports"],
    }
    print(f"  Researched: {topic} ({len(ctx['research']['key_points'])} key points)")
    return ctx


def _draft(ctx: dict) -> dict:
    research = ctx.get("research", {})
    points = research.get("key_points", [])
    ctx["draft"] = {
        "title": f"Deep Dive: {ctx.get('topic', 'Unknown')}",
        "sections": [f"Section on: {p}" for p in points],
        "word_count": len(points) * 350,
    }
    print(f"  Drafted: {ctx['draft']['title']} (~{ctx['draft']['word_count']} words)")
    return ctx


def _review(ctx: dict) -> dict:
    draft = ctx.get("draft", {})
    ctx["review"] = {
        "approved": True,
        "suggestions": ["Add more examples", "Strengthen conclusion"],
        "score": 8.5,
    }
    print(f"  Reviewed: score {ctx['review']['score']}/10")
    return ctx


def _publish(ctx: dict) -> dict:
    ctx["published"] = {
        "url": f"https://blog.example.com/{ctx.get('topic', 'post').lower().replace(' ', '-')}",
        "published_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    print(f"  Published: {ctx['published']['url']}")
    return ctx


# ── Commands ─────────────────────────────────────────────────────────

def cmd_demo(args: argparse.Namespace) -> None:
    """Run a demo pipeline on the given topic."""
    topic = " ".join(args.topic) if args.topic else "AI Agent Teams"
    print(f"\nContent Pipeline Demo: '{topic}'\n{'=' * 40}")

    pipeline = (
        Pipeline(name="content-demo")
        .add_stage(Stage("research", _research))
        .add_stage(Stage("draft", _draft))
        .add_stage(Stage("review", _review, required=False))
        .add_stage(Stage("publish", _publish))
    )

    pipeline.run({"topic": topic})
    print(f"\n{pipeline.report()}")


def cmd_calendar(args: argparse.Namespace) -> None:
    """Show a sample content calendar."""
    today = dt.date.today()
    cal = ContentCalendar()
    cal.add(ContentItem(
        title="Getting Started with Agent Teams",
        topic="agent-teams",
        status=ContentStatus.SCHEDULED,
        publish_date=today + dt.timedelta(days=1),
        tags=["tutorial", "ai"],
        channel="blog",
    ))
    cal.add(ContentItem(
        title="Content Pipelines Explained",
        topic="pipelines",
        status=ContentStatus.DRAFTING,
        publish_date=today + dt.timedelta(days=3),
        tags=["engineering", "automation"],
        channel="blog",
    ))
    cal.add(ContentItem(
        title="Weekly AI Roundup",
        topic="ai-news",
        status=ContentStatus.IDEA,
        publish_date=today + dt.timedelta(days=5),
        tags=["news", "ai"],
        channel="newsletter",
    ))
    cal.add(ContentItem(
        title="Automation Tips Thread",
        topic="automation",
        status=ContentStatus.REVIEWING,
        publish_date=today,
        tags=["tips", "automation"],
        channel="social",
    ))

    print(f"\nContent Calendar — {today.isoformat()}\n{'=' * 40}")
    print(f"\nSummary: {cal.summary()}")
    print(f"\nDue today ({len(cal.due(today))}):")
    for item in cal.due(today):
        print(f"  ! [{item.channel}] {item.title} ({item.status.value})")
    print(f"\nUpcoming 7 days ({len(cal.upcoming(7, today))}):")
    for item in cal.upcoming(7, today):
        print(f"  - [{item.channel}] {item.title} — {item.publish_date}")

    if args.save:
        cal.save(args.save)
        print(f"\nSaved to {args.save}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="content-engine",
        description="Content Automation Engine CLI",
    )
    sub = parser.add_subparsers(dest="command")

    demo_p = sub.add_parser("demo", help="Run a demo content pipeline")
    demo_p.add_argument("topic", nargs="*", help="Topic to process (default: AI Agent Teams)")

    cal_p = sub.add_parser("calendar", help="Show a sample content calendar")
    cal_p.add_argument("--save", help="Save calendar to a JSON file")

    args = parser.parse_args(argv)
    if args.command == "demo":
        cmd_demo(args)
    elif args.command == "calendar":
        cmd_calendar(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
