# Content Automation

This repository uses Claude Code Agent Teams to coordinate parallel work across multiple Claude instances.

## Agent Teams

Agent Teams is enabled via `.claude/settings.json`. The team lead orchestrates teammates who work independently in their own context windows.

### Available Subagent Roles

- **researcher** — Deep research and information gathering
- **implementer** — Code implementation and feature development
- **reviewer** — Code review, security audit, and quality checks
- **researcher-ml** — Autonomous ML experiments via autoresearch

### Usage

Ask the lead to spawn teammates for tasks that benefit from parallel exploration:

```
Spawn a researcher teammate to investigate the API options.
Spawn an implementer teammate to build the data pipeline.
Spawn a reviewer teammate to audit the auth module.
```

## Autoresearch (ML Research)

The `autoresearch/` directory contains Karpathy's autonomous pretraining research framework. An AI agent modifies `train.py`, trains a GPT model for 5 minutes, and keeps improvements.

- `autoresearch/prepare.py` — Data prep and evaluation (DO NOT MODIFY)
- `autoresearch/train.py` — Model, optimizer, hyperparameters (agent edits this)
- `autoresearch/program.md` — Agent instructions for the experiment loop

Use `content-engine research` to check readiness or `content-engine research --results results.tsv` to view experiment logs.

## Project Conventions

- Commit messages should be concise and describe the "why"
- All code changes should include relevant tests
- Use descriptive branch names
