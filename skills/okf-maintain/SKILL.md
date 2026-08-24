---
name: okf-maintain
description: Curate OKF bundles — indexes, log.md, drift detection, broken links, orphan cleanup, staleness, and v0.1 to v0.2 migration. Use when the graph feels messy, catalogs are out of date, links break, content is stale, or the user asks to maintain, curate, or migrate an OKF bundle.
---

# OKF Maintain / Curate

Keep the knowledge graph healthy and reviewable. This plugin owns Catalog + ContextPack; do not invent domain nouns while curating.

## Maintenance checklist

1. **Broken links** — every Markdown link to a `.md` target resolves inside the bundle.
2. **Orphans** — concepts with no inbound or outbound edges (except intentional roots).
3. **Index drift** — subdirectory `index.md` catalogs (`type: Catalog`) list actual children.
4. **Log hygiene** — `log.md` has recent entries for structural changes.
5. **Staleness** — nodes past `stale_after` or long-unchanged high-degree concepts.
6. **Trust gaps** — schema-declared high-impact types (`x-impact: high` on the owning plugin) with `verified: false`.
7. **Frontmatter completeness** — `type`, `title`, `description`, `timestamp`.
8. **Migration** — if `okf_version` is missing or `0.1`, plan upgrade to `0.2`. Noun split (0.8 family): follow `docs/user_guide/noun-ownership-migration.md` — install owning plugins first; retype only DEKC pipeline `Workflow` → `IngestionJob`; do not invent domain nouns here.

## Process

1. Locate bundle root.
2. Run deterministic checks:
   ```bash
   # Prefer official CLI
   okf validate <bundle>
   # Fallback
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py" validate <bundle>
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py" orphans <bundle>
   ```
3. Produce a **curation report** with severity (`error` / `warn` / `info`) and suggested fixes.
4. Apply safe automatic fixes only when asked or clearly desired:
   - Regenerate index listings from directory contents
   - Append log entries for performed maintenance
   - Fix obvious relative→absolute link rewrites **only with confirmation** if many files change
5. For migrations v0.1 → v0.2:
   - Set `okf_version: "0.2"` on root index
   - Ensure absolute-link convention is documented
   - Add `catalogs/`, `knowledge/`, `packs/` only if missing
   - Do not seed AgentNode / Workflow / TicketLink catalogs (those belong to AGER / PKC)
   - Do not delete legacy concepts
6. For the 0.8 noun-ownership cut: do not retype files just because this plugin no longer ships their schema. Install the owning plugin. See `docs/user_guide/noun-ownership-migration.md`.

## Report template

```markdown
# OKF Curation Report — <bundle>
Date: ...

## Errors
- ...

## Warnings
- ...

## Info
- ...

## Applied fixes
- ...

## Recommended follow-ups
- [ ] ...
```

## Rules

- Prefer small, reviewable commits/changesets over mass rewrites.
- Never invent domain content while curating.
- Preserve user wording in concept bodies; only fix structure/metadata when needed.
- After fixes, re-validate.

## Done when

- Report delivered (and optional fixes applied)
- Validation error count is zero or remaining errors are explicitly listed as deferred
