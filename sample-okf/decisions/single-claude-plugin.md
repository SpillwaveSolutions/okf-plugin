---
type: DecisionRecord
title: Ship as one Claude Code plugin
description: Deliver okf-graph-eng as a single Claude Code plugin so Grok Build gets zero-config compatibility.
status: accepted
tags: [decision, adr, packaging]
timestamp: 2026-07-29T00:00:00Z
verified: true
---

# Ship as one Claude Code plugin

## Context

Grok Build automatically reads Claude plugins, skills, agents, hooks, and marketplaces. Maintaining separate Grok-only packaging would increase drift risk.

## Decision

Primary deliverable is one Claude Code plugin (`.claude-plugin/plugin.json` + skills/agents/hooks). Document dual-host support in README, CLAUDE.md, and AGENTS.md.

## Consequences

- One install path, two hosts
- Optional later: thin `.grok-plugin/marketplace.json` for native Grok marketplace listing
- No Grok-only features that break Claude compatibility

## Related

- [Plugin architecture](/knowledge/plugin-architecture.md)
