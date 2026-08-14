# Shared OKF concept schemas

This is the **canonical envelope** for every plugin in the second-brain family
(okf-plugin, PKC, SAC, DEKC, AGER).

## Rules (load-bearing)

1. Markdown body is always free-form. Only YAML frontmatter is schema-checked.
2. **Required on v1: `type` + `title` only.** Extra per-type fields are
   `x-recommended` (warn; error only with `--strict`). Never move extras into
   `required` without a major `schema_version` and a migration.
3. `additionalProperties: true` forever on BaseConcept.
4. Soft validation is the default. Old files must produce **zero errors**.
5. `truth_state` accepts the union of PKC/SAC and DEKC values:
   `current | snapshot | superseded | archived | historical | proposed`.
6. Unknown `type` values fall back to BaseConcept (info, not error).
7. **Work items are first-class:** `Epic`, `Story`, `Task`, `Subtask`, `Bug`.
   `TicketLink` stays valid for existing files. `Branch` is the source-control
   concept; prefer `on_branch` links over a bare `branch:` string.
8. Domain plugins add types under their own `schemas/okf-concepts/` and the
   validator merges directories. Do not fork BaseConcept.

## Catalog ownership

A plugin may only rewrite catalogs listed under its name in `registry.json`
`catalog_ownership`. Foreign catalogs are read-only.

In a shared second brain:

- `Module` lives in `modules/` (SAC convention).
- `Package` lives in `packages/`.
- Cross-plugin links are absolute in-bundle paths (`/tables/orders.md`).

## Validate

```bash
python3 scripts/okf_schema.py list
python3 scripts/okf-graph.py validate sample-okf
python3 scripts/okf-graph.py validate sample-okf --schema
```
