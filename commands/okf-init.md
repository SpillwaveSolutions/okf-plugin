---
name: okf-init
description: Scaffold a graph-engine OKF bundle (.okf/) with catalogs, knowledge, and packs. Does not seed domain nouns.
---

Scaffold an OKF graph-engineering bundle using the **okf-init-graph** skill.

1. Confirm target directory (default `.okf/` at repo root).
2. Follow `${CLAUDE_PLUGIN_ROOT}/skills/okf-init-graph/SKILL.md` completely.
3. Seed catalogs + knowledge + packs only. Do **not** seed AgentNode, Workflow, or TicketLink — those belong to AGER and PKC.
4. Run validation and report results.
