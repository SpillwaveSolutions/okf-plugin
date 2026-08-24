---
name: okf-author
description: Create or update OKF concepts using the core envelope (type + title). This plugin owns Catalog and ContextPack only. For domain nouns, hand off to PKC, SAC, DEKC, or AGER.
---

# OKF Author

Author OKF concept files that the graph engine can pack and impact-analyze.

## Rules

1. Every concept file must have YAML frontmatter with at least `type` and `title`.
2. Include `description` and `timestamp` (ISO-8601) when you have them.
3. **Nouns this plugin owns:** `Catalog`, `ContextPack`.
4. Any other `type` is valid (unknown types fall back to BaseConcept) but **should be authored by the plugin that owns that noun**.
5. For derived or agent-generated content, set `generated: true` and populate `sources`.
6. Use **absolute** Markdown links: `[Label](/path/to/concept.md)`.
7. After writing, offer to run validation and, for high-degree nodes, impact analysis.

## Noun ownership (do not invent these here)

| Plugin | Nouns |
|--------|-------|
| **okf-plugin (this)** | Catalog, ContextPack |
| **PKC** | Meeting, Experiment, Discovery, Assumption, Question, Feature, Requirement, Specification, Design, Release, CodeChange, Package, Risk, Acceptance, DecisionRecord, TicketLink, Epic, Story, Task, Subtask, Bug, Branch, Project, Playbook, Runbook, Reference |
| **SAC** | System, Service, Component, architecture/runtime topology (see SAC README) |
| **DEKC** | Dataset, Table, View, Metric, Stream, Job, lineage, lakes, marts, semantic layer, glossary |
| **AGER** | AgentNode, Workflow, Harness, SharedState, ToolCapability, loop/runtime/ops types |

If the user asks to author an `AgentNode`, load AGER. If they ask for a `TicketLink` or `DecisionRecord`, load PKC.

## Process

1. Clarify concept purpose, type, and placement.
2. Choose a stable path/slug.
3. Fill frontmatter from `templates/knowledge.md` (or Catalog/ContextPack).
4. Write a concise body with absolute links.
5. Update parent `index.md` catalog entry if one exists (`type: Catalog`).
6. Append a one-line entry to `log.md`.
7. Validate (prefer `okf validate`; fallback `okf-graph.py validate`).

## Optional richer links

```yaml
links:
  - target: /knowledge/orders.md
    rel: depends_on
```

Core `rel` values: `depends_on`, `routes_to`, `implements`, `documents`, `uses`, `owns`, `supersedes`, `related_to`, `tracks`, `maps_to`, `released_in`.

Deep reference: `references/typed-edges.md`.

## TicketLink

TicketLink is a **PKC** noun. Use `project-knowledge-capture` `scripts/pkc_ticket_link.py`, not this plugin.

## Done when

- File written with `type` + `title` and at least one body section
- Catalog/index updated if applicable
- Links resolve
