---
type: AgentNode
title: Skill Runner
description: Host-side agent role that loads and executes OKF graph-eng skills (init, author, impact, validate, etc.).
resource: agents/skill-runner.md
tags: [agent, skills, host]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# Skill Runner

## Overview

Represents Claude Code or Grok Build when they auto-invoke plugin skills based on user language and skill descriptions.

## Responsibilities

- Match user intent to skills (`okf-init-graph`, `okf-author`, `okf-impact`, …)
- Execute skill procedures with access to `${CLAUDE_PLUGIN_ROOT}`
- Return structured reports to the user

## Routes to

- [Graph Engineer](/agents/graph-engineer.md) for deep multi-step graph work

## Uses knowledge

- [Skill catalog](/knowledge/skill-catalog.md)
- [Plugin architecture](/knowledge/plugin-architecture.md)

## Shared state

- [Harness session](/shared/harness-session.md)
