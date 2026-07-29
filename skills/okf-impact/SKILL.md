---
name: okf-impact
description: Compute the transitive impact (blast radius / ripple) of changing a concept in an OKF bundle. Use when the user asks what depends on a concept, what breaks if something changes, needs a ranked update list, or wants blast-radius / ripple analysis before editing agents, workflows, or knowledge nodes.
---

# OKF Impact Analysis

## Goal

Given a concept ID/path (or a proposed change), return the full affected subgraph plus a practical update order.

## Process

1. **Resolve** the target concept (relative path, absolute path, title, or ID). Locate the bundle root (`.okf/`, `knowledge/`, `sample-okf/`).
2. **Use deterministic tools first:**
   - Prefer `okf graph <bundle>`, `okf backlinks`, or equivalent `okfcli` commands.
   - Fallback:
     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py" impact <bundle> <concept>
     ```
3. Build both:
   - **Outbound** closure — what the concept depends on / routes to
   - **Inbound** closure — who cites / depends on / routes through it
4. **Classify** nodes by type and trust/lifecycle (`verified`, `status`, `stale_after`).
5. **Produce two outputs:**
   - **Human report** — ranked list (critical → low), with reasons and suggested actions
   - **Structured JSON** (optional): `{ target, inbound, outbound, critical_path, suggested_order }`

## Ranking heuristics

| Signal | Effect on rank |
|--------|----------------|
| Type `AgentNode`, `Workflow`, `Harness`, `SharedState` | Higher impact |
| `verified: false` on high-type nodes | Escalate to critical |
| `status: deprecated` | Flag for cleanup, lower urgency for feature work |
| Shallow hop depth with many dependents | Higher priority |
| Leaf knowledge nodes | Usually lower |

## Report template

```markdown
# Impact: <title> (`<path>`)

## Summary
- Inbound dependents: N
- Outbound dependencies: M
- Critical / unverified highlights: ...

## Ranked dependents (update order)
1. **[Name](path)** — type, why it matters, suggested action
2. ...

## Outbound dependencies to review
- ...

## Recommended next steps
- [ ] ...
```

## Rules

- Never invent links. Only report edges found by tools or careful Markdown crawl.
- If graph tools are unavailable, state the limitation and use link crawl.
- Prefer high-trust paths when ranking recommendations.
- After structural edits, re-run impact on the same target.

## Related

- Progressive disclosure packs: use `okf-query` / `okf-graph.py subgraph`
- Validation before big refactors: `okf-validate`
