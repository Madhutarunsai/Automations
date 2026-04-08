# Content Automation

This repository uses Claude Code Agent Teams to coordinate parallel work across multiple Claude instances.

## Agent Teams

Agent Teams is enabled via `.claude/settings.json`. The team lead orchestrates teammates who work independently in their own context windows.

### Available Subagent Roles

- **researcher** — Deep research and information gathering
- **implementer** — Code implementation and feature development
- **reviewer** — Code review, security audit, and quality checks

### Usage

Ask the lead to spawn teammates for tasks that benefit from parallel exploration:

```
Spawn a researcher teammate to investigate the API options.
Spawn an implementer teammate to build the data pipeline.
Spawn a reviewer teammate to audit the auth module.
```

## Project Conventions

- Commit messages should be concise and describe the "why"
- All code changes should include relevant tests
- Use descriptive branch names
