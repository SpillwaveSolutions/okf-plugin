---
name: okf-init-graph
description: Scaffold a graph-engineering optimized OKF bundle with recommended directories, index.md, log.md, and templates for AgentNode, Workflow, DecisionRecord, knowledge concepts, and TicketLink. Use when starting a new OKF repo, initializing .okf/, converting a project for graph engineering, or setting up harness/agent graph scaffolding.
---

# OKF Graph Init

Create a ready-to-use OKF bundle optimized for **graph engineering** (knowledge graph + agent/harness graph).

## When to use

- User wants a new OKF bundle or `.okf/` tree
- Project needs agent/workflow modeling alongside domain knowledge
- Empty repo → graph-eng ready structure in under two minutes

## Steps

1. Confirm or create the target directory (default: `.okf/` at repo root; accept `knowledge/` if the user prefers).
2. Create this structure:

```
.okf/
├── index.md
├── log.md
├── agents/
│   └── index.md
├── workflows/
│   └── index.md
├── knowledge/
│   └── index.md
├── decisions/
│   └── index.md
├── shared/
│   └── index.md
└── tickets/          # optional TicketLink concepts
    └── index.md
```

3. Write root `index.md` with `okf_version: "0.2"` and a short dual-purpose description (knowledge + agent graph).
4. Seed **one** example `AgentNode` and **one** `Workflow` from `templates/` in this skill.
5. Optionally seed one `DecisionRecord` and one knowledge concept (`Reference` or `Playbook`).
6. Initialize `log.md` with today’s date (ISO) and a “Bundle created for graph engineering” entry.
7. Prefer **absolute Markdown links** from the start: `[Label](/agents/example.md)`.
8. Run validation:
   - Prefer `okf validate <bundle>` or `okfcli validate <bundle>`
   - Fallback: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py validate <bundle>`
9. Report created paths and any validation issues.

## Rules

- Do **not** invent domain content beyond scaffolding and one illustrative example per major type.
- Every concept file needs YAML frontmatter with at least `type`, `title`, `description`, `timestamp`.
- Keep subdirectory `index.md` files as lightweight catalogs linking to children.
- If the target already has OKF content, merge carefully—do not overwrite existing concepts without confirmation.

## Templates

Copy and fill from:

- `templates/agent-node.md`
- `templates/workflow.md`
- `templates/decision-record.md`
- `templates/knowledge-concept.md`
- `templates/ticket-link.md`
- `templates/index-root.md`
- `templates/log-entry.md`

## Done when

- Bundle tree exists with root `index.md` + `log.md`
- At least one AgentNode and one Workflow example exist and link correctly
- Validation reports zero broken-link errors
