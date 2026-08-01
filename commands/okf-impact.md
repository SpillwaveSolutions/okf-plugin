---
name: okf-impact
description: Compute transitive impact / blast radius for an OKF concept. Args: concept path or title.
---

Run **okf-impact** analysis on the concept given in `$ARGUMENTS` (path, title, or id).

1. Locate the OKF bundle (`.okf/`, `sample-okf/`, or user-specified).
2. Follow `${CLAUDE_PLUGIN_ROOT}/skills/okf-impact/SKILL.md`.
3. Prefer `okf` CLI; fallback to `${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py impact <bundle> <concept>`.
4. Return ranked human report plus optional JSON.
