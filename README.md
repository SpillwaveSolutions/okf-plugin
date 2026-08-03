# okf-graph-eng (okf-plugin)

**Graph engineering for [OKF](https://github.com/topics/okf) repositories** — impact analysis, agent/harness graphs, progressive disclosure, and curation.

Works in **Claude Code** and **Grok Build** (zero-config: Grok Build reads Claude plugins natively).

| | |
|---|---|
| **Plugin name** | `okf-graph-eng` |
| **Repo** | [SpillwaveSolutions/okf-plugin](https://github.com/SpillwaveSolutions/okf-plugin) |
| **Version** | 0.3.2 |
| **License** | MIT |

## Why this plugin

OKF already gives you a clean, Git-native knowledge graph (Markdown + YAML). Graph engineering is the next layer: treat the same portable graph as the model of **agents, workflows, shared state, and decisions** — then compute **blast radius** when anything changes.

This plugin specializes OKF workflows for:

- First-class **impact / ripple analysis**
- **Agent-graph modeling** inside the OKF repo
- **Progressive disclosure** (minimal context packs for long-running agents)
- **Validation & curation** hooks
- Dual-host packaging: one install for Claude Code **and** Grok Build

## Install

### Claude Code

```bash
# Marketplace (from this repo)
claude plugin marketplace add SpillwaveSolutions/okf-plugin
claude plugin install okf-graph-eng@okf-plugin-marketplace

# Or local path
claude plugin marketplace add /path/to/okf-plugin
claude plugin install okf-graph-eng@okf-plugin-marketplace
```

Marketplace metadata: `.claude-plugin/marketplace.json`.

### Grok Build

Grok Build discovers Claude-compatible plugins automatically — **no separate Grok-only config required**. Optional identity pin: `.grok-plugin/marketplace.json`.

Skills, agents, commands, and hooks under this tree load the same way as in Claude Code.

### Optional: okf CLI

For richer deterministic operations, install [`okfcli`](https://github.com/search?q=okfcli) / `okf` if available. If missing, the plugin falls back to `scripts/okf-graph.py`.

## Quick start

1. **Scaffold** a graph-eng OKF bundle:
   - Slash: `/okf-init`
   - Or ask: “Initialize an OKF graph engineering bundle”
2. **Author** agents, workflows, or knowledge concepts (skill: `okf-author`)
3. **Impact** before large edits: `/okf-impact agents/graph-engineer.md`
4. **Validate**: `/okf-validate`

Try the included self-describing sample:

```bash
python3 scripts/okf-graph.py validate sample-okf
python3 scripts/okf-graph.py impact sample-okf knowledge/skill-okf-impact.md
python3 scripts/okf-graph.py pack sample-okf agents/graph-engineer.md --hops 2
python3 scripts/okf-graph.py edges sample-okf --rel routes_to
python3 scripts/okf-graph.py graph sample-okf --focus agents/graph-engineer.md --hops 2
python3 scripts/okf-graph.py graph sample-okf --format html > okf-graph.html
# TicketLink from worklog:
bin/worklog fold | python3 scripts/okf-ticket-link.py emit --bundle sample-okf --open-only --dry-run
```

## What’s included

### Skills

| Skill | Purpose |
|-------|---------|
| `okf-init-graph` | Scaffold `.okf/` with agent/workflow/knowledge/decision catalogs |
| `okf-author` | Create/update concepts with provenance, trust, absolute links |
| `okf-impact` | Transitive blast radius + ranked update order |
| `okf-query` | Multi-hop subgraph / progressive disclosure packs |
| `okf-maintain` | Indexes, log, drift, orphans, migration helpers |
| `okf-validate` | Conformance + graph quality |
| `okf-visualize` | Mermaid / HTML / JSON with agent-graph overlays |

### Commands

`/okf-init` · `/okf-author` · `/okf-impact` · `/okf-query` · `/okf-validate` · `/okf-visualize` · `/okf-maintain`

### Agent

- **graph-engineer** — specialist for dual-graph reasoning, impact, and curation

### Hooks

Post-edit (`Write|Edit|MultiEdit`) runs `scripts/okf-curate.sh`: `okf validate`/`okf lint` when the official CLI is present, otherwise this repo's own `okf-graph.py validate`. It reads the tool payload from stdin, so it fires on every matching edit.

The bundle it curates is found by walking up from the edited file for an `index.md` containing `okf_version` (or a `.okf/` directory) — so a bundle rooted anywhere works, not just `.okf/`, `knowledge/` or `sample-okf/`. Edits outside any bundle are a silent no-op.

### Tests

```bash
python3 tests/test_okf_graph.py -q      # graph engine — 24 cases
bash tests/test_okf_curate.sh           # post-edit hook — 5 checks
```

Plain asserts, no framework. Run in CI alongside `okf-graph.py validate sample-okf --strict`, and as a guarded pre-commit check.

### Sample OKF

`sample-okf/` models **this plugin** as both a knowledge graph and an agent/harness graph — useful as a template and for demos.

## Concept types

**Knowledge:** `Dataset`, `Table`, `Metric`, `Playbook`, `Runbook`, `API`, `Reference`

**Graph-engineering / harness:** `AgentNode`, `Workflow`, `Harness`, `DecisionRecord`, `SharedState`, `ToolCapability`, `TicketLink`

Prefer absolute Markdown links: `[Graph Engineer](/agents/graph-engineer.md)`.

## Host docs

| File | Audience |
|------|----------|
| [CLAUDE.md](./CLAUDE.md) | Claude Code agent conventions for this repo |
| [AGENTS.md](./AGENTS.md) | Grok Build / Codex-style agent conventions (same dual-host story) |

## Roadmap

Generated live from WikiTicket worklog: [`docs/roadmap.md`](./docs/roadmap.md) · [wiki Roadmap](https://github.com/SpillwaveSolutions/okf-plugin/wiki/Roadmap)

- **v0.1 (MVP)** — skills, packaging, hooks, sample OKF, okfcli/Python wrappers  
- **v0.2** — typed edges, TicketLink ↔ worklog helpers, GraphEngineer progressive-disclosure defaults, marketplace metadata  
- **v0.3.0** — `graph` subcommand (mermaid/json/html), `validate --strict`, a slash command for every skill, first automated coverage of the graph engine, working post-edit hook  
- **v0.3.1** — engine correctness: ambiguous concept lookups error instead of guessing, off-bundle links are reported by `validate`, unverified concepts escalate a criticality tier, curation finds bundles rooted anywhere, plus a shell test suite for the hook  
- **Later** — MCP server, richer agent-graph overlays  

## Related ecosystem

Complements general OKF tooling (okf-gem, okfcli, community skills) by focusing on impact analysis, harness graphs, and progressive disclosure — without replacing existing CLIs or visualizers.


## Project management (WikiTicket SDD)

This repo is managed with [WikiTicket SDD / worklog](https://github.com/SpillwaveSolutions/wiki_ticket_sdd):

| Artifact | Path |
|----------|------|
| Event log | `.work/todo.jsonl`, `.work/done.jsonl` |
| Config | `.work/config.yml` |
| Roadmap (generated) | `docs/roadmap.md` |
| Plans | `docs/plans/` |
| Status reports | `docs/status/` |
| CLI | `bin/worklog` |

```bash
bin/worklog list
bin/worklog roadmap-render
bin/worklog plan-capture --slug my-plan --title "My plan" --file draft.md
```

GitHub Issues + GitHub wiki are configured as the ticket/wiki systems. Commit messages must reference a worklog ULID or `#issue`. Prefer feature branches (hooks block direct commits on `main`).

## License

MIT — see [LICENSE](./LICENSE).
