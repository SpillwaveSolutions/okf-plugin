---
name: okf-author
description: Create or update an OKF Catalog, ContextPack, or envelope concept. Domain nouns belong to PKC, SAC, DEKC, or AGER. Args: free-text description of what to author.
---

Author an OKF concept using the **okf-author** skill.

User request: `$ARGUMENTS`

Follow `${CLAUDE_PLUGIN_ROOT}/skills/okf-author/SKILL.md` — complete frontmatter, absolute links, update indexes/log, offer validation + impact.

This plugin owns `Catalog` and `ContextPack` only. If the user asks for AgentNode / Workflow, load AGER. TicketLink / DecisionRecord / work types → PKC. Architecture → SAC. Data plane → DEKC.
