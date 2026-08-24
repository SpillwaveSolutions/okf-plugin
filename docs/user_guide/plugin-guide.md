---
doc_type: guide
slug: plugin-guide
title: Plugin Guide
truth_state: current
wiki_key: plugin-guide
---

# Plugin Guide

Install and host notes for **okf-graph-eng**.

## Plugin identity

| Field | Value |
|-------|--------|
| Name | `okf-graph-eng` |
| Version | see root `plugin.json` (0.8.0) |
| Marketplace | `okf-plugin-marketplace` |
| Repo | https://github.com/SpillwaveSolutions/okf-plugin |
| Nouns | `Catalog`, `ContextPack` |

## Claude Code

```bash
claude plugin marketplace add SpillwaveSolutions/okf-plugin
claude plugin install okf-graph-eng@okf-plugin-marketplace
```

Local path:

```bash
claude plugin marketplace add /path/to/okf-plugin
claude plugin install okf-graph-eng@okf-plugin-marketplace
```

Metadata: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`.

### Components discovered automatically

- **Skills** — `skills/*/SKILL.md`
- **Commands** — `commands/*.md` (`/okf-init`, `/okf-impact`, …)
- **Agent** — `agents/graph-engineer.md`
- **Hooks** — `hooks/hooks.json` → fail-closed `okf-hook-validate.sh`

Use `${CLAUDE_PLUGIN_ROOT}` for script paths inside skills/hooks.

## Grok Build

Grok Build loads Claude-compatible plugins, skills, agents, and hooks with **zero extra config**. Optional pin: `.grok-plugin/marketplace.json`.

Do not add Grok-only features that break Claude Code.

## Slash commands

| Command | Skill |
|---------|--------|
| `/okf-init` | okf-init-graph |
| `/okf-author` | okf-author |
| `/okf-impact` | okf-impact |
| `/okf-query` | okf-query |
| `/okf-validate` | okf-validate |
| `/okf-visualize` | okf-visualize |
| `/okf-maintain` | okf-maintain |

## Specialist agent

**graph-engineer** — pack-first, impact-before-structure. Prefer for multi-step graph work. Does not author domain nouns.

## Project management plugin

Work tracking uses the separate **worklog** tooling vendored into this repo (`bin/worklog`, hooks). That is WikiTicket SDD, not part of the Claude skill pack itself. See [[Worklog-Spec]]. TicketLink emission lives in PKC (`pkc_ticket_link.py`).
