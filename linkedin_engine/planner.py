"""Daily task planner. Pure stdlib.

Given today's date and the program start date, returns the day's task list:
the post to publish, distribution work, revenue work, and any milestone
specific to this week of the program.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field


# ── Day-of-week content rotation ────────────────────────────────────

CONTENT_BY_WEEKDAY: dict[int, dict[str, str]] = {
    0: {  # Monday
        "format": "Carousel (8-10 slides)",
        "pillar": "Hiring automation playbook",
        "sample_topic": "How I cut hiring from 6 weeks to 1 - the 7-step system",
        "cta_keyword": "HIRING",
    },
    1: {  # Tuesday
        "format": "Text post (story)",
        "pillar": "CRM / ATS war story",
        "sample_topic": "The 2 AM Lakeshore API reverse-engineering story",
        "cta_keyword": "CRM",
    },
    2: {  # Wednesday
        "format": "Native video (60-90 s)",
        "pillar": "Behind the build",
        "sample_topic": "60-second walkthrough of an n8n flow shipped this week",
        "cta_keyword": "AUTOMATION",
    },
    3: {  # Thursday
        "format": "NO POST - comment-only day",
        "pillar": "Distribution",
        "sample_topic": "Plant 15 thoughtful comments on Tier A creators",
        "cta_keyword": "",
    },
    4: {  # Friday
        "format": "Multi-image case study",
        "pillar": "Client win",
        "sample_topic": "40% -> 78% qualified candidates in 30 days. Here's the screening prompt.",
        "cta_keyword": "AUDIT",
    },
    5: {  # Saturday
        "format": "Long story post (optional)",
        "pillar": "Origin / opinion",
        "sample_topic": "The teacher-in-Thailand backstory. Or a contrarian thesis-reinforcement.",
        "cta_keyword": "",
    },
    6: {  # Sunday
        "format": "OFF - planning block (3 hrs)",
        "pillar": "Schedule next week, refresh comment targets, draft newsletter",
        "sample_topic": "",
        "cta_keyword": "",
    },
}


# ── Week-of-program milestones ──────────────────────────────────────

WEEK_MILESTONES: dict[int, list[str]] = {
    1: [
        "Apply for LinkedIn verification",
        "Rewrite headline + banner + About using docs/profile-audit.md paste blocks",
        "Add 50 skills, pin top 5, request endorsements from 5 past clients",
        "Build 30-creator target list in content_scripts/COMMENT_TARGETS.md",
        "Set up Sales Navigator + save 3 ICP Boolean searches",
        "Open Stripe Payment Link for $497 Hiring Pipeline Audit",
        "DM 50 warmest connections asking what content they want",
        "Pitch 5 podcasts (HR / staffing / recruitment / AI / SaaS)",
    ],
    2: [
        "Launch the $497 audit offer with one post + DM blast (target: 5 sales = $2,500)",
        "Ship newsletter issue 1: The Staffing Automation Brief",
        "Configure HeyReach: 5 invites/day warm-up only",
        "10 more podcast pitches",
        "Post VA job ad on Onlinejobs.ph",
    ],
    3: [
        "Daily rhythm locked - no new tactics, just execution",
        "Apply for LinkedIn Top Voice (5 collaborative-article answers per week)",
        "Email 5 past clients for case-study permission with real numbers",
        "Document 2 case studies with screenshots",
    ],
    4: [
        "VA starts - train on keyword-DM flow + inbox triage",
        "Reach out to 2 mid-tier creators for paid M2 collabs ($500-$1,500)",
        "M1 review: posts, impressions, followers, calls, MRR. Decide if offer needs simplifying.",
    ],
    5: [
        "First paid creator collab goes live",
        "Add the $4,997 done-with-you tier as audit-call upsell",
        "Survey design for 'State of Staffing Automation 2026' flagship asset (n=200 target)",
    ],
    8: [
        "Top Voice badge should land this month",
        "First podcast episode airs (from M1 pitches)",
        "Begin promoting flagship survey - target 200 responses by week 12",
    ],
    12: [
        "M3 PIVOT CHECK: followers, newsletter, MRR, calls/wk vs targets",
        "Decision matrix: continue, push Track D, kill audience goal, or full reset",
        "Flagship asset (State of Staffing Automation 2026) launches this week",
        "LinkedIn Thought Leader Ads turn on ($500-$1,500/mo budget)",
    ],
    16: [
        "Second wave of paid collabs",
        "Hot-take thesis-reinforcement post weekly",
        "Productize $4,997 group cohort",
    ],
    20: [
        "Host one LinkedIn Live with 4 panelists",
        "Press push: pitch 10 industry publications",
    ],
    24: [
        "Year-in-review flagship carousel",
        "Stretch shot at 100K via co-promoted launch",
    ],
}


# ── Daily distribution + revenue defaults ───────────────────────────

@dataclass
class DailyTasks:
    """One day's task list. Render via ``to_telegram_markdown``."""

    date: dt.date
    week_number: int
    weekday_name: str
    is_workday: bool
    content_block: dict[str, str]
    distribution_tasks: list[str] = field(default_factory=list)
    revenue_tasks: list[str] = field(default_factory=list)
    week_milestones: list[str] = field(default_factory=list)
    metrics_to_log: list[str] = field(default_factory=list)
    thesis: str = ""

    def to_telegram_markdown(self) -> str:
        """Render as MarkdownV2-safe Telegram message (we use plain Markdown
        because MarkdownV2 escaping is brittle; our content has no risky chars)."""
        date_str = self.date.strftime("%a %b %d")
        lines = [
            f"*LinkedIn Day Plan - {date_str} (Week {self.week_number})*",
            "",
            f"_Thesis:_ {self.thesis}",
            "",
        ]

        if self.is_workday:
            lines.extend([
                "*TODAY'S POST*",
                f"- Format: {self.content_block['format']}",
                f"- Pillar: {self.content_block['pillar']}",
                f"- Topic idea: {self.content_block['sample_topic']}",
            ])
            if self.content_block["cta_keyword"]:
                lines.append(f"- CTA keyword: `{self.content_block['cta_keyword']}` (auto-DM trigger)")
            lines.append("")
        else:
            lines.extend([
                "*TODAY*",
                f"- {self.content_block['format']}",
                f"- {self.content_block['pillar']}",
                "",
            ])

        if self.distribution_tasks:
            lines.append("*DISTRIBUTION*")
            for t in self.distribution_tasks:
                lines.append(f"- {t}")
            lines.append("")

        if self.revenue_tasks:
            lines.append("*REVENUE (Track A)*")
            for t in self.revenue_tasks:
                lines.append(f"- {t}")
            lines.append("")

        if self.week_milestones:
            lines.append(f"*WEEK {self.week_number} MILESTONES*")
            for m in self.week_milestones:
                lines.append(f"- {m}")
            lines.append("")

        if self.metrics_to_log:
            lines.append("*LOG TONIGHT*")
            for m in self.metrics_to_log:
                lines.append(f"- {m}")
            lines.append("")

        lines.append("_Distribution > Content. Always._")
        return "\n".join(lines)


def week_number(today: dt.date, start_date: dt.date) -> int:
    """1-indexed week of the program."""
    days = (today - start_date).days
    return max(1, (days // 7) + 1)


def plan_day(today: dt.date, start_date: dt.date, thesis: str,
             cadence: dict | None = None) -> DailyTasks:
    """Build the task list for a specific date."""
    cadence = cadence or {}
    weekday = today.weekday()  # Mon=0
    week = week_number(today, start_date)
    content = CONTENT_BY_WEEKDAY[weekday]
    is_workday = weekday < 5  # Mon-Fri are workdays; Sat optional; Sun off

    distribution: list[str] = []
    revenue: list[str] = []

    if is_workday:
        distribution = [
            f"{cadence.get('comments_per_day', 15)} thoughtful comments "
            "(3-Sentence Rule: Acknowledge / Expand / Engage)",
            "5 comments BEFORE you publish (Tier A creators) - lifts your reach ~20%",
            f"{cadence.get('invites_per_day', 10)} connection invites "
            "to people who liked/commented on your last 3 posts (warm only)",
            "Reply to every comment on today's post within 60 minutes",
            "Trigger keyword-DM follow-ups (24h) for yesterday's magnet grabbers",
        ]
        revenue = [
            f"{cadence.get('warm_dms_per_day', 20)} warm DM follow-ups "
            "(D2 voice notes for non-repliers)",
            "1 audit call slot held open (block 14:00-15:00)",
            "If sales call today: send recap + Stripe link within 1 hr",
        ]
    elif weekday == 5:  # Saturday
        distribution = [
            "10 thoughtful comments (lighter day - Tier B/C)",
            "Engage with 2 podcast hosts you've pitched - signal interest before they reply",
        ]
        revenue = [
            "Send 3 cold pitches to dream clients (manual, personalized)",
            "Update sales pipeline in CRM",
        ]
    else:  # Sunday
        distribution = [
            "Schedule next week's 4 posts in your scheduler",
            "Refresh COMMENT_TARGETS.md - update last-touched dates",
            "Refresh Sales Nav lead lists (filter: posted in last 30 days)",
        ]
        revenue = [
            "Newsletter issue draft for upcoming Friday",
            "Review week's metrics, write 3 lines on what worked / didn't",
        ]

    milestones = WEEK_MILESTONES.get(week, [])

    metrics = []
    if is_workday:
        metrics = [
            "Today's post impressions (Shield/Authoredup)",
            "Followers added today",
            "Connection accept rate (must stay >=40%)",
            "Magnet grabs (comment-keyword DMs sent)",
            "Calls booked",
            "Sales today ($)",
        ]

    return DailyTasks(
        date=today,
        week_number=week,
        weekday_name=today.strftime("%A"),
        is_workday=is_workday,
        content_block=content,
        distribution_tasks=distribution,
        revenue_tasks=revenue,
        week_milestones=milestones,
        metrics_to_log=metrics,
        thesis=thesis,
    )
