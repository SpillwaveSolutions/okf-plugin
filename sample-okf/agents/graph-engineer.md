---
type: AgentNode
title: Graph Engineer
description: Specialist agent for OKF impact analysis, multi-hop reasoning, progressive disclosure, and dual-graph curation.
resource: agents/graph-engineer.md
tags: [agent, graph-engineering]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
links:
  - target: /agents/skill-runner.md
    rel: routes_to
  - target: /knowledge/skill-okf-impact.md
    rel: uses
  - target: /knowledge/skill-okf-query.md
    rel: uses
  - target: /knowledge/skill-okf-validate.md
    rel: uses
  - target: /shared/harness-session.md
    rel: uses
  - target: /workflows/plugin-maintenance.md
    rel: implements
---

# Graph Engineer

## Overview

Specialist agent shipped with the okf-graph-eng plugin. Treats the OKF repo as a dual knowledge + agent/harness graph.

## Responsibilities

- Run impact / blast-radius analysis before structural changes
- Build progressive disclosure packs (subgraphs)
- Curate indexes, links, and trust signals
- Prefer deterministic CLI (`okf` / `okf-graph.py`) before free-form reasoning

## Routes to

- [Skill Runner](/agents/skill-runner.md) for skill-backed operations

## Uses knowledge

- [okf-impact skill](/knowledge/skill-okf-impact.md)
- [okf-query skill](/knowledge/skill-okf-query.md)
- [okf-validate skill](/knowledge/skill-okf-validate.md)
- [Plugin architecture](/knowledge/plugin-architecture.md)

## Shared state

- [Harness session](/shared/harness-session.md)

## Implements

- Part of [Plugin maintenance workflow](/workflows/plugin-maintenance.md)
