---
name: okf-validate
description: Validate OKF bundle conformance and graph quality. Optional args: bundle path.
---

Validate the OKF bundle using the **okf-validate** skill.

Bundle path: use `$ARGUMENTS` if provided, else auto-detect `.okf/` or `sample-okf/`.

Follow `${CLAUDE_PLUGIN_ROOT}/skills/okf-validate/SKILL.md`. Prefer `okf validate`; fallback to `okf-graph.py validate`.
