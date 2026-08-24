---
type: Catalog
title: Plugin maintenance
description: Curate the OKF sample bundle and plugin docs — validate, fix drift, update log.
tags: [workflow, harness, maintenance]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# Plugin maintenance

## Stages

1. Validate — [okf-validate skill](/knowledge/skill-okf-validate.md) via [Skill Runner](/agents/skill-runner.md)
2. Curate — maintain indexes/links (okf-maintain skill in skill catalog)
3. Impact check — [okf-impact skill](/knowledge/skill-okf-impact.md) on changed high-degree nodes
4. Document — [Graph Engineer](/agents/graph-engineer.md) updates concepts and [log](/log.md)

## Shared state

- [Harness session](/shared/harness-session.md)

## Success criteria

- Validation PASS (zero broken links)
- Catalogs match directory contents
- log.md records the maintenance event
