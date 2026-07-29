---
doc_type: design
truth_state: current
wiki_key: design/current-code-walkthrough
title: Code Walkthrough
git_hash: main
---

# OKF Graph Engineering Plugin — Code Walkthrough

Map of the repository as implemented. Read with [[Design-Doc]].

## Top level

| Path | Role |
|------|------|
| `.claude-plugin/` | `plugin.json`, `marketplace.json` |
| `.grok-plugin/` | Optional Grok marketplace pin |
| `skills/` | Seven skills with templates/references |
| `commands/` | Slash command wrappers |
| `agents/graph-engineer.md` | Specialist agent |
| `hooks/hooks.json` | PostToolUse → curate |
| `scripts/` | `okf-graph.py`, `okf-ticket-link.py`, `okf-curate.sh` |
| `sample-okf/` | Dual-graph sample |
| `bin/worklog` + friends | WikiTicket SDD tooling (vendored) |
| `.work/` | Event log, config, publish ledger |
| `docs/` | Plans, roadmap, guides, designs, IA index |

## Skills

```
skills/
  okf-init-graph/   # scaffold bundle + templates
  okf-author/       # concepts + typed edges + TicketLink refs
  okf-impact/       # blast radius
  okf-query/        # packs / multi-hop
  okf-maintain/     # curation
  okf-validate/     # health checks
  okf-visualize/    # mermaid / html / json
```

## Graph script (`scripts/okf-graph.py`)

Loads all `*.md` under a bundle, parses frontmatter (including `links[]`), merges Markdown + typed edges, then:

- BFS impact / subgraph  
- Trust-aware `pack`  
- `edges` listing  
- validate / orphans  

## Sample OKF

Entry: `sample-okf/index.md`. Agents under `agents/`, workflows under `workflows/`, skills documented as knowledge nodes. Useful for:

```bash
python3 scripts/okf-graph.py validate sample-okf
python3 scripts/okf-graph.py pack sample-okf agents/graph-engineer.md
```

## Worklog integration

- Hooks under `hooks/` enforce ULID-in-commit and roadmap freshness  
- `bin/worklog ia-index` builds `docs/.index/` and Home/Sidebar  
- Wiki publish reads `docs/.index/publish-manifest.json`  

## Extension points

1. New skill directory under `skills/` with `SKILL.md`  
2. New concept type taught in `okf-author`  
3. Richer `okf-graph.py` once official `okf` CLI covers the case  
4. MCP server / CI overlays (roadmap later)  
