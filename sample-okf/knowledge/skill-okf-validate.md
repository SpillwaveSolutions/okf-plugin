---
type: Playbook
title: okf-validate skill
description: Validate OKF structural conventions and graph quality (links, orphans, trust gaps).
tags: [skill, validate]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# okf-validate skill

## Overview

Pass/fail validation for bundle health. Prefer before commits and after bulk edits.

## Uses tools

- [ToolCapability: okf-graph.py](/knowledge/tool-okf-graph-py.md) (`validate`, `orphans`)
- Post-edit hook script `okf-curate.sh`

## Used by

- [Plugin maintenance](/workflows/plugin-maintenance.md)
- [Skill Runner](/agents/skill-runner.md)

## Related

- [OKF conventions](/knowledge/okf-conventions.md)
