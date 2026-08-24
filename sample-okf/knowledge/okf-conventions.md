---
type: Catalog
title: OKF conventions
description: Frontmatter, types, absolute links, and dual-graph conventions used by okf-graph-eng.
tags: [okf, conventions]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# OKF conventions

## Frontmatter

Minimum: `type`, `title`, `description`, `timestamp`. Recommended: `status`, `verified`, `tags`.

## Types

This engine owns `Catalog` and `ContextPack` only. `validate --strict` rejects
unknown types (fail-closed). BaseConcept fallback is read-only envelope
parsing — it does not authorize writing an unregistered type.

Domain types (`AgentNode`, `TicketLink`, `DecisionRecord`, `Dataset`, `System`,
…) are authored by AGER, PKC, DEKC, and SAC.

## Links

Prefer absolute Markdown links from bundle root: `[Label](/agents/graph-engineer.md)`.

## Related

- [Plugin architecture](/knowledge/plugin-architecture.md)
- [okf-validate skill](/knowledge/skill-okf-validate.md)
