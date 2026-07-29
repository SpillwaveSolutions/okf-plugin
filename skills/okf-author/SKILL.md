---
name: okf-author
description: Create or update OKF concepts for domain knowledge and agent/harness graphs. Use when documenting tables, metrics, agents, workflows, decision records, shared state, tools, ticket links, playbooks, or runbooks. Supports provenance, trust, lifecycle, and proper absolute Markdown linking.
---

# OKF Author

Author high-quality OKF concept files that work as both knowledge nodes and agent-graph nodes.

## Rules

1. Every concept file must have YAML frontmatter with at least `type`.
2. Always include `title`, `description`, and `timestamp` (ISO-8601).
3. Prefer recommended types (see below).
4. For derived or agent-generated content, set `generated: true` and populate `sources`.
5. Use **absolute** Markdown links: `[Label](/path/to/concept.md)`.
6. When the concept is an agent or workflow, document inputs, outputs, routing, and shared state.
7. After writing, offer to run validation and impact analysis on the new/changed concept.

## Recommended types

**Knowledge:** `Dataset`, `Table`, `Metric`, `Playbook`, `Runbook`, `API`, `Reference`

**Graph-engineering / harness:** `AgentNode`, `Workflow`, `Harness`, `DecisionRecord`, `SharedState`, `ToolCapability`, `TicketLink`

## Process

1. Clarify concept purpose, type, and placement (directory under the OKF bundle).
2. Choose a stable path/slug (`agents/researcher.md`, `knowledge/orders-table.md`).
3. Fill frontmatter from templates in `templates/`.
4. Write a concise body: overview, key sections, related links.
5. Update parent `index.md` catalog entry if one exists.
6. Append a one-line entry to `log.md`.
7. Validate (prefer `okf validate`; fallback `okf-graph.py validate`).
8. If this is an update to an existing high-degree node, run impact analysis.

## Optional richer links (non-breaking)

Skills interpret plain Markdown links first. Optional frontmatter form:

```yaml
links:
  - target: /agents/researcher.md
    rel: routes_to
  - target: /knowledge/orders.md
    rel: depends_on
```

Common `rel` values: `depends_on`, `routes_to`, `implements`, `documents`, `uses`, `owns`, `supersedes`.

## Provenance & trust

| Field | Purpose |
|-------|---------|
| `verified` | Human or CI confirmed correctness |
| `status` | `active`, `draft`, `deprecated`, `proposed`, `accepted` |
| `stale_after` | ISO date after which content should be rechecked |
| `generated` | `true` if agent-authored |
| `sources` | List of upstream concept paths or URLs |
| `owners` | Optional team or person tags |

## Templates

See `templates/` for AgentNode, Workflow, DecisionRecord, SharedState, knowledge, and TicketLink skeletons.

## Done when

- File written with complete frontmatter and at least one meaningful body section
- Catalog/index updated if applicable
- Links resolve (or known TODOs are marked clearly)
