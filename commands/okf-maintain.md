---
name: okf-maintain
description: Curate an OKF bundle — indexes, log, orphans, broken links, drift, staleness, migration. Optional args: bundle path or focus area.
---

Curate the OKF bundle using the **okf-maintain** skill.

Bundle path: use `$ARGUMENTS` if provided, else auto-detect `.okf/` or `sample-okf/`.

1. Follow `${CLAUDE_PLUGIN_ROOT}/skills/okf-maintain/SKILL.md`.
2. Prefer `okf validate`; fallback to `${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py validate <bundle>` plus `orphans <bundle>`.
3. Return a curation report with severities; apply fixes only when asked, then re-validate.
