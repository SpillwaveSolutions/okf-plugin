---
name: okf-visualize
description: Render an OKF bundle as Mermaid, JSON, or a standalone HTML map. Args: optional focus concept, hop count, and format.
---

Visualize the OKF dual graph using the **okf-visualize** skill.

Parse `$ARGUMENTS` as an optional focus concept (path or title), hops (default 2), and format (`mermaid` | `json` | `html`, default `mermaid`).

1. Locate the OKF bundle (`.okf/`, `sample-okf/`, or user-specified).
2. Follow `${CLAUDE_PLUGIN_ROOT}/skills/okf-visualize/SKILL.md`.
3. Prefer `okf graph`; fallback to `${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py graph <bundle> [--format F] [--focus C] [--hops N]`.
4. Inline the Mermaid block in chat; write `html` to a file only when the user asks for one.
