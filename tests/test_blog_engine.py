"""Tests for the blog engine — SEO/AEO/GEO scoring and publishing."""

import datetime as dt
import json
import tempfile
from pathlib import Path

import pytest

from blog_engine.generator import BlogPost, BlogEngine, SEOConfig


@pytest.fixture
def config():
    return SEOConfig.load()


@pytest.fixture
def sample_post():
    return BlogPost(
        title="How to Automate Lead Generation with AI in 2026",
        slug="automate-lead-generation-ai-2026",
        meta_description="Learn how to automate lead generation with AI tools like Make.com and Instantly. Step-by-step guide for solopreneurs in 2026.",
        primary_keyword="automate lead generation",
        secondary_keywords=["AI lead gen", "cold email automation", "LinkedIn automation"],
        pillar="Lead Generation",
        content="""# How to Automate Lead Generation with AI in 2026

Automate lead generation using AI tools to find, contact, and convert prospects on autopilot. According to research from HubSpot, companies using marketing automation see a 451% increase in qualified leads.

## What is AI-Powered Lead Generation?

AI-powered lead generation uses machine learning and automation tools to identify potential customers, personalize outreach, and nurture leads without manual effort. Studies indicate that 80% of marketers using automation software generate more leads.

## How to Set Up Your AI Lead Generation System

### Step 1: Define Your Ideal Customer Profile

Before automating anything, you need clarity on who you're targeting. Research shows that targeted campaigns have 14.6% higher conversion rates compared to non-targeted campaigns.

### Step 2: Set Up LinkedIn Sales Navigator

LinkedIn Sales Navigator costs $99/month and gives you advanced search filters. Use it to build targeted lead lists.

### Step 3: Connect Phantom Buster for Scraping

Phantom Buster ($59/month) automates LinkedIn profile visits and data extraction. Connect it to your Make.com workflow.

### Step 4: Configure Instantly for Cold Email

Instantly ($30/month) handles email warming, sending, and tracking. Set up your campaigns with personalized AI-written copy.

### Step 5: Build Your Make.com Automation

Make.com ($9/month) connects all these tools. Create a scenario that flows: LinkedIn → Phantom Buster → Google Sheets → Instantly.

## Make.com vs Zapier vs n8n Comparison 2026

Make.com is better than Zapier for complex automations. n8n is the best self-hosted alternative. Zapier is easier but more expensive at scale.

## Results You Can Expect

According to data from Instantly, automated cold email campaigns average a 2-5% reply rate. With AI personalization, this jumps to 5-12%.

Visit [Web AI Automations](https://webaiautomations.com) to see how we build these systems. Check out our [projects](https://webaiautomations.com/projects1) for real examples.

## Why Solopreneurs Need AI Automation

The average solopreneur spends 15 hours per week on manual outreach. AI automation reduces this to under 1 hour while generating 3-5x more leads.
""",
        faq=[
            {"q": "How much does AI lead generation cost?", "a": "A basic setup costs $100-200/month for tools like Instantly ($30), Phantom Buster ($59), and Make.com ($9)."},
            {"q": "How many leads can I generate per day?", "a": "With a properly configured system, you can reach 100-300 prospects daily on autopilot."},
            {"q": "What is the best AI tool for lead generation?", "a": "Instantly combined with Make.com and LinkedIn Sales Navigator is the most effective stack for 2026."},
            {"q": "How long does it take to set up?", "a": "A basic automated lead gen system takes 2-4 hours to set up and 1-2 weeks to optimize."},
            {"q": "What is a good reply rate for cold email?", "a": "Industry average is 2-5%. With AI personalization, aim for 5-12%."},
        ],
        stats_cited=[
            "451% increase in qualified leads (HubSpot)",
            "80% of marketers generate more leads with automation",
            "14.6% higher conversion rates for targeted campaigns",
            "2-5% average cold email reply rate",
        ],
        tools_mentioned=["Make.com", "Instantly", "Phantom Buster", "LinkedIn Sales Navigator", "Zapier", "n8n"],
        internal_links_used=["https://webaiautomations.com", "https://webaiautomations.com/projects1"],
    )


class TestSEOConfig:
    def test_load(self, config):
        assert config.site["name"] == "Web AI Automations"
        assert len(config.content_pillars) == 5
        assert len(config.target_keywords["primary"]) >= 5

    def test_pillar_for_monday(self, config):
        monday = dt.date(2026, 4, 6)  # A Monday
        pillar = config.pillar_for_date(monday)
        assert pillar["name"] == "AI Automation for Business"

    def test_pillar_for_tuesday(self, config):
        tuesday = dt.date(2026, 4, 7)
        pillar = config.pillar_for_date(tuesday)
        assert pillar["name"] == "Lead Generation"

    def test_pillar_for_friday(self, config):
        friday = dt.date(2026, 4, 10)
        pillar = config.pillar_for_date(friday)
        assert pillar["name"] == "Case Studies & ROI"


class TestBlogPost:
    def test_word_count(self, sample_post):
        assert sample_post.word_count > 0

    def test_evaluate_seo(self, sample_post, config):
        result = sample_post.evaluate(config)
        assert "seo" in result
        assert "aeo" in result
        assert "geo" in result
        assert result["seo"]["score"] > 0
        assert 0 <= result["overall"] <= 100

    def test_seo_title_check(self, sample_post, config):
        result = sample_post.evaluate(config)
        assert result["seo"]["checks"]["title_has_keyword"] is True

    def test_aeo_faq_check(self, sample_post, config):
        result = sample_post.evaluate(config)
        assert result["aeo"]["checks"]["has_faq"] is True

    def test_aeo_citation_tone(self, sample_post, config):
        result = sample_post.evaluate(config)
        assert result["aeo"]["checks"]["citation_tone"] is True

    def test_geo_stats_check(self, sample_post, config):
        result = sample_post.evaluate(config)
        assert result["geo"]["checks"]["enough_stats"] is True

    def test_geo_tools_check(self, sample_post, config):
        result = sample_post.evaluate(config)
        assert result["geo"]["checks"]["enough_tools"] is True

    def test_to_markdown_file(self, sample_post, config):
        sample_post.evaluate(config)
        md = sample_post.to_markdown_file()
        assert "---" in md
        assert sample_post.title in md
        assert "Frequently Asked Questions" in md
        assert sample_post.primary_keyword in md


class TestBlogEngine:
    def test_save_and_list_posts(self, sample_post, config):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = BlogEngine(config=config, posts_dir=tmpdir)
            engine.score_post(sample_post)
            path = engine.save_post(sample_post)
            assert path.exists()
            posts = engine.list_posts()
            assert len(posts) == 1

    def test_daily_summary(self, config):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = BlogEngine(config=config, posts_dir=tmpdir)
            summary = engine.daily_summary()
            assert "date" in summary
            assert summary["target"] == 5
            assert summary["posts_published"] == 0

    def test_todays_pillar(self, config):
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = BlogEngine(config=config, posts_dir=tmpdir)
            pillar = engine.todays_pillar()
            assert "name" in pillar
            assert "topics" in pillar
