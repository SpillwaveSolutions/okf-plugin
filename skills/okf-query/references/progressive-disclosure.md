# Progressive disclosure defaults

## Defaults (v0.8)

| Knob | Default | Rationale |
|------|---------|-----------|
| Direction | **outbound-only** | Catalog indexes are hubs. Undirected walks dump the bundle. |
| Hops | **2** | Enough for entry → collaborator → evidence without hairballs |
| Max nodes | **20** | Fits long-running agent context budgets |
| Trust bias | verified first | Prefer `verified: true` when trimming |
| High-impact retention | always flag | Never silently drop unverified nodes whose owning schema set `x-impact: high` |

`--undirected` exists for “what would break?” neighborhood exploration. Prefer `impact` for that. Unlimited closure is `impact`, not `pack`.

## Pack command

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py" pack <bundle> <concept> \
  --hops 2 --max-nodes 20
```

JSON includes `markdown` (ready to paste), `included`, `excluded`, and typed `edges`.

## When to increase hops

- User asks for full blast radius → use `impact` (unlimited closure) not pack
- Debugging missing route → hop 3 temporarily, then shrink
- Whole-catalog review → validate/orphans, not a pack

## Read order inside packs

1. Entry concept (always first, always included)
2. Schema-declared high-impact types (`x-impact: high` on the owning plugin)
3. Verified supporting knowledge
4. Title
5. Indexes last (usually excluded under max-nodes)

Inclusion ranking decides *who makes the cut*. Read order is how the markdown is presented.

## Graph Engineer rule

Default answer shape for exploration:

1. 2-hop outbound pack (markdown)
2. One sentence on excluded count
3. Offer impact analysis if structural change is next
