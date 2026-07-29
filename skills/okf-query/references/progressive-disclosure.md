# Progressive disclosure defaults

## Defaults (v0.2)

| Knob | Default | Rationale |
|------|---------|-----------|
| Hops | **2** | Enough for agent → tool → knowledge without hairballs |
| Max nodes | **20** | Fits long-running agent context budgets |
| Trust bias | verified first | Prefer `verified: true` when trimming |
| High-impact retention | always flag | Never silently drop unverified AgentNode/Workflow/SharedState |

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

1. Entry concept  
2. High-impact harness types (`AgentNode`, `Workflow`, `SharedState`)  
3. Supporting knowledge  
4. Indexes last (usually excluded under max-nodes)

## Graph Engineer rule

Default answer shape for exploration:

1. 2-hop pack (markdown)  
2. One sentence on excluded count  
3. Offer impact analysis if structural change is next  
