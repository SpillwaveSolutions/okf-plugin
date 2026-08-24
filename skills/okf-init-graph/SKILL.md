---
name: okf-init-graph
description: Scaffold an OKF bundle for the graph engine — catalogs, knowledge, packs, index.md, log.md. Does not seed AgentNode, Workflow, TicketLink, or other domain nouns; those belong to PKC, SAC, DEKC, and AGER.
---

# OKF Graph Init

Create a ready-to-use OKF bundle for **graph engineering** (validate, impact, ContextPack). Domain capture plugins add their own catalogs later.

## When to use

- User wants a new OKF bundle or `.okf/` tree
- Empty repo → pack-ready structure in under two minutes

## Steps

1. Confirm or create the target directory (default: `.okf/` at repo root; accept `knowledge/` if the user prefers).
2. Create this structure:

```
.okf/
├── index.md          # type: Catalog
├── log.md
├── catalogs/
│   └── index.md      # type: Catalog
├── knowledge/
│   └── index.md      # type: Catalog
└── packs/
    └── index.md      # type: Catalog (ContextPack outputs land here)
```

3. Write root `index.md` with `okf_version: "0.2"`, `type: Catalog`, and a one-line description of the bundle.
4. Do **not** seed `AgentNode`, `Workflow`, `DecisionRecord`, or `TicketLink`. Those nouns are owned by AGER and PKC.
5. Optionally seed one Catalog page and one empty ContextPack stub. Do not seed unknown types — `--strict` rejects them. BaseConcept fallback is read-only.
6. Initialize `log.md` with today’s date (ISO) and “Bundle created for OKF graph engine”.
7. Prefer **absolute Markdown links**: `[Label](/knowledge/example.md)`.
8. Run validation:
   - Prefer `okf validate <bundle>` or `okfcli validate <bundle>`
   - Fallback: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py validate <bundle>`
9. Report created paths and any validation issues.

## Rules

- Do **not** invent domain content beyond scaffolding.
- Every concept file needs YAML frontmatter with at least `type`, `title`.
- Keep subdirectory `index.md` files as `type: Catalog`.
- If the target already has OKF content, merge carefully—do not overwrite existing concepts without confirmation.

## Templates

Copy and fill from:

- `templates/index-root.md`
- `templates/knowledge-concept.md`
- `templates/log-entry.md`

Agent/workflow/ticket templates were removed in 0.8.0. Use AGER (`ager-init`) or PKC (`pkc-init`) for those nouns.

## Done when

- Bundle tree exists with root `index.md` + `log.md`
- Validation reports zero broken-link errors
