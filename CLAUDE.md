# Content Automation

This repository uses Claude Code Agent Teams to coordinate parallel work across multiple Claude instances.

## Agent Teams

Agent Teams is enabled via `.claude/settings.json`. The team lead orchestrates teammates who work independently in their own context windows.

### Available Subagent Roles

- **researcher** — Deep research and information gathering
- **implementer** — Code implementation and feature development
- **reviewer** — Code review, security audit, and quality checks
- **researcher-ml** — Autonomous ML experiments via autoresearch
- **content-optimizer** — Daily SEO/AEO/GEO blog content generation for webaiautomations.com

### Usage

Ask the lead to spawn teammates for tasks that benefit from parallel exploration:

```
Spawn a researcher teammate to investigate the API options.
Spawn an implementer teammate to build the data pipeline.
Spawn a reviewer teammate to audit the auth module.
Spawn a content-optimizer teammate to generate today's 5 blog posts.
```

## Autoresearch (ML Research)

The `autoresearch/` directory contains Karpathy's autonomous pretraining research framework. An AI agent modifies `train.py`, trains a GPT model for 5 minutes, and keeps improvements.

- `autoresearch/prepare.py` — Data prep and evaluation (DO NOT MODIFY)
- `autoresearch/train.py` — Model, optimizer, hyperparameters (agent edits this)
- `autoresearch/program.md` — Agent instructions for the experiment loop

Use `content-engine research` to check readiness or `content-engine research --results results.tsv` to view experiment logs.

## Blog Engine (Content Autoresearch)

The `blog_engine/` package generates 5 SEO/AEO/GEO optimized blog posts daily for webaiautomations.com.

- `blog_engine/seo_rules.json` — Fixed quality standards and keywords (DO NOT MODIFY)
- `blog_engine/generator.py` — Post generation, SEO/AEO/GEO scoring engine
- `blog_engine/publisher.py` — Topic planning, quality gates, batch publishing
- `blog_engine/posts/` — Published markdown posts (date-slug.md)
- `content_optimizer/program.md` — Autoresearch loop instructions

Content pillars rotate daily: Mon=AI Automation, Tue=Lead Gen, Wed=Hiring, Thu=Tools, Fri=Case Studies.

## Project Conventions

- Commit messages should be concise and describe the "why"
- All code changes should include relevant tests
- Use descriptive branch names
