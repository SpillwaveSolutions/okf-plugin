# CLAUDE.md — okf-graph-eng

Instructions for **Claude Code** when working in this repository or when the plugin is installed.

## What this project is

**okf-graph-eng** is a Claude Code plugin that turns OKF (Open Knowledge Format) repos into platforms for **graph engineering**: knowledge graphs *and* agent/harness graphs in portable Markdown + YAML.

**Hosts:** Claude Code (primary packaging) and **Grok Build** (native zero-config compatibility with Claude plugins). Do not add Grok-only features that break Claude Code.

## Plugin layout

```
.claude-plugin/plugin.json   # manifest (name: okf-graph-eng)
skills/                      # portable intelligence (SKILL.md per skill)
commands/                    # slash command wrappers
agents/graph-engineer.md     # specialist subagent
hooks/hooks.json             # post-edit curation
scripts/                     # okf-curate.sh, okf-graph.py
sample-okf/                  # self-describing dual graph
```

Use `${CLAUDE_PLUGIN_ROOT}` for all intra-plugin paths in hooks and skill instructions.

## Skills (auto-invoke)

| Skill | Trigger themes |
|-------|----------------|
| okf-init-graph | new OKF / scaffold / graph eng setup |
| okf-author | document concept, agent, workflow, ADR |
| okf-impact | blast radius, what depends on, ripple |
| okf-query | subgraph, context pack, multi-hop |
| okf-maintain | curate, orphans, drift, migrate |
| okf-validate | validate bundle, graph quality |
| okf-visualize | mermaid, diagram, HTML map |

## Working rules

1. **Deterministic tools first** — prefer `okf` / `okfcli` when installed; else `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py …`.
2. **Impact before structural edits** — especially for AgentNode, Workflow, SharedState.
3. **Absolute Markdown links** — `[Title](/path/from/bundle/root.md)`.
4. **Frontmatter** — at least `type`, `title`, `description`, `timestamp` (ISO-8601).
5. **Progressive disclosure** — ship subgraphs / packs, not whole trees.
6. **Never invent edges** — only report links that exist (or clearly mark proposed new links).
7. Keep each `SKILL.md` focused; put deep reference material in skill `templates/` or `references/`.

## Common commands

```bash
python3 scripts/okf-graph.py validate sample-okf
python3 scripts/okf-graph.py impact sample-okf agents/graph-engineer.md
python3 scripts/okf-graph.py subgraph sample-okf knowledge/plugin-architecture.md --hops 2
python3 scripts/okf-graph.py orphans sample-okf
```

## When editing the plugin itself

- Bump `version` in `.claude-plugin/plugin.json` for releases.
- Keep sample-okf in sync when adding skills or architectural decisions.
- After sample-okf edits, run `okf-graph.py validate sample-okf`.
- Post-edit hook may run curate on OKF paths; keep scripts portable (`bash` + `python3`).

## Dual-host note

Grok Build loads this same tree. Prefer Claude plugin conventions so both hosts stay aligned. See [AGENTS.md](./AGENTS.md) for Grok/Codex-oriented wording of the same rules.
