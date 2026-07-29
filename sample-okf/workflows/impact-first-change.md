---
type: Workflow
title: Impact-first change
description: Before editing a concept, compute blast radius and produce an ordered update plan.
tags: [workflow, harness, impact]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# Impact-first change

## Stages

1. Resolve target concept
2. Run [okf-impact skill](/knowledge/skill-okf-impact.md)
3. Optionally pack context with [okf-query skill](/knowledge/skill-okf-query.md)
4. Author changes (okf-author)
5. Re-validate

## Agents

- [Graph Engineer](/agents/graph-engineer.md)
- [Skill Runner](/agents/skill-runner.md)

## Shared state

- [Harness session](/shared/harness-session.md)
