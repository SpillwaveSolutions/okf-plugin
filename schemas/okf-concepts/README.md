# Core OKF concept schemas

Canonical **envelope** for every plugin in the second-brain family, plus the two nouns this plugin owns.

## Nouns in this pack

| Type | Role |
|------|------|
| `BaseConcept` | Envelope. Required on v1: **`type` + `title` only**. |
| `Catalog` | Directory index. Structural. |
| `ContextPack` | Generated progressive-disclosure pack. May include nodes from any plugin. |

Domain plugins add types under **their own** `schemas/okf-concepts/`. The validator merges directories. Do not fork BaseConcept. Do not put AgentNode, Dataset, TicketLink, Meeting, System, … in this folder.

## Rules (load-bearing)

1. Markdown body is always free-form. Only YAML frontmatter is schema-checked.
2. Extra per-type fields are `x-recommended` (warn; error only with `--strict`).
3. `additionalProperties: true` forever on BaseConcept.
4. Soft validation is the default. Old files must produce **zero errors**.
5. `truth_state` accepts the union of PKC/SAC and DEKC values:
   `current | snapshot | superseded | archived | historical | proposed`.
6. Unknown `type` values fall back to BaseConcept for read-only envelope parsing (info). `--strict` rejects unknown types (error, fail-closed). Fallback is not a write authorization.
7. Domain plugins declare blast-radius with `x-impact: high|medium` on **their** schemas. Core declares none.

## Catalog ownership

A plugin may only rewrite catalogs listed under its name in `registry.json` `catalog_ownership`. Foreign catalogs are read-only.

## Validate

```bash
python3 scripts/okf_schema.py list
python3 scripts/okf-graph.py validate sample-okf
python3 scripts/okf-graph.py validate sample-okf --schema
```
