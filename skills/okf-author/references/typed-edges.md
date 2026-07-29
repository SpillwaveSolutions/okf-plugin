# Typed edges (non-breaking)

Plain Markdown links remain the universal edge form:

```markdown
[Researcher](/agents/researcher.md)
```

Optional frontmatter enriches the **same** targets with a relation type. Skills and `okf-graph.py` merge both; frontmatter `rel` wins over generic `links_to`.

```yaml
links:
  - target: /agents/writer.md
    rel: routes_to
  - target: /knowledge/orders.md
    rel: depends_on
  - target: /tickets/mvp-plugin-scaffold.md
    rel: tracks
```

## Recommended `rel` values

| rel | Meaning |
|-----|---------|
| `depends_on` | This concept needs the target to be correct |
| `routes_to` | Agent/workflow hands off to target |
| `implements` | This fulfills a decision, ticket, or interface |
| `documents` | Narrative about the target |
| `uses` | Runtime/tool dependency |
| `owns` | Accountability edge |
| `supersedes` | Replaces older concept |
| `related_to` | Soft association |
| `tracks` | TicketLink tracks this work/concept |
| `maps_to` | Ticket/external id maps to concept |

## Rules

1. Always keep a body Markdown link for human readers.
2. `target` is an absolute in-bundle path (`/agents/…`).
3. Unknown `rel` values are allowed but flagged as info during validate.
4. Never invent edges — only record real dependencies/routes.

## Tooling

```bash
python3 scripts/okf-graph.py edges sample-okf --from agents/graph-engineer.md
python3 scripts/okf-graph.py edges sample-okf --rel routes_to
python3 scripts/okf-graph.py impact sample-okf agents/graph-engineer.md
```
