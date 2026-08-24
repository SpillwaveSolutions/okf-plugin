---
name: okf-validate
description: Validate OKF v0.2 conformance and graph quality — orphans, connectivity, staleness, unverified high-impact nodes, broken links, missing frontmatter. Use when checking bundle health, before commits/PRs, after bulk edits, or when the user asks if the OKF graph is valid.
---

# OKF Validate

## Goal

Confirm the bundle is structurally sound (OKF-oriented conventions) and graph-quality healthy for engineering use.

## Checks

### Conformance (structural)

- Root `index.md` present; prefer `okf_version: "0.2"`
- Concept files use YAML frontmatter starting with `---`
- Required-ish fields: `type`, `title` (warn if missing on non-index files)
- `log.md` present (warn if missing)

### Graph quality

- Broken Markdown links to missing `.md` targets (error)
- Orphan concepts (info/warn)
- Unverified high-impact nodes (`x-impact: high` from the owning plugin’s schema, `verified: false`) (warn). Isolated, this plugin declares no high-impact types.
- Stale nodes past `stale_after` (warn)

## Process

1. Resolve bundle path (argument, `.okf/`, `sample-okf/`, or user path).
2. Run tools:
   ```bash
   okf validate <bundle>     # preferred when installed
   # fallback:
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py" validate <bundle>
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py" orphans <bundle>
   ```
3. Optionally spot-check a sample of high-degree nodes for body quality (not just links).
4. Emit a pass/fail summary with issue table.

## Output format

```markdown
# Validation: <bundle>

**Result:** PASS | FAIL (N errors, M warnings)

| Severity | Path | Message |
|----------|------|---------|
| error | ... | ... |

## Graph stats
- Concepts: N
- Orphans: K
- Unverified high-impact: J
```

## Rules

- Deterministic tools first; LLM judgment only for qualitative notes.
- Do not modify files unless the user asks to fix issues (then hand off to `okf-maintain` / `okf-author`).
- Exit guidance: FAIL if any broken links or missing root index; otherwise PASS with warnings.

## Done when

- Clear PASS/FAIL and actionable issue list
