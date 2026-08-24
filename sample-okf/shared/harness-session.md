---
type: Catalog
title: Harness session
description: Cross-agent scratchpad for a graph-engineering harness run (goal, findings, open questions, artifacts).
tags: [state, harness]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# Harness session

## Schema

| Field | Meaning |
|-------|---------|
| `goal` | User objective for this run |
| `target_concept` | Path under analysis or edit |
| `impact_summary` | Last impact report pointer |
| `open_questions` | Unresolved items |
| `artifacts` | Paths produced (reports, diagrams) |

## Readers / writers

- [Graph Engineer](/agents/graph-engineer.md)
- [Skill Runner](/agents/skill-runner.md)

## Used in

- [Plugin maintenance](/workflows/plugin-maintenance.md)
- [Impact-first change](/workflows/impact-first-change.md)
