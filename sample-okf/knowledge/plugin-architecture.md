---
type: Knowledge
title: Plugin architecture
description: Layout and runtime model of the okf-graph-eng Claude Code / Grok Build plugin.
tags: [architecture, plugin]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# Plugin architecture

## Overview

Single Claude Code plugin (`okf-graph-eng`) with zero-config Grok Build compatibility. Intelligence lives in portable `SKILL.md` files; deterministic work uses `okf` CLI or the bundled Python fallback.

## Layout

```
.claude-plugin/plugin.json
skills/           # okf-init-graph, author, impact, query, maintain, validate, visualize
commands/         # thin slash wrappers
agents/           # graph-engineer
hooks/            # post-edit curate
scripts/          # okf-curate.sh, okf-graph.py
sample-okf/       # this self-describing bundle
```

## Host compatibility

- **Claude Code** — native plugin install (marketplace or local path)
- **Grok Build** — reads Claude plugins, skills, agents, hooks with zero configuration

## Related

- [Skill catalog](/knowledge/skill-catalog.md)
- [ToolCapability: okf-graph.py](/knowledge/tool-okf-graph-py.md)
- [Graph Engineer](/agents/graph-engineer.md)
