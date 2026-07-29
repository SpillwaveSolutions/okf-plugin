# okf-graph-eng (okf-plugin)

**Graph engineering for [OKF](https://github.com/topics/okf) repositories** — impact analysis, agent/harness graphs, progressive disclosure, and curation.

Works in **Claude Code** and **Grok Build** (zero-config: Grok Build reads Claude plugins natively).

| | |
|---|---|
| **Plugin name** | `okf-graph-eng` |
| **Repo** | [RichardHightower/okf-plugin](https://github.com/RichardHightower/okf-plugin) |
| **Version** | 0.1.0 |
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
# From marketplace (when published) or local path:
claude plugin install /path/to/okf-plugin
# or add as a local marketplace / project plugin per Claude Code docs
```

Project-local option: clone into your tools path and enable the plugin, or reference the repo as a marketplace source.

### Grok Build

Grok Build discovers Claude-compatible plugins automatically. Point it at this repo (or install via Claude marketplace metadata) — **no separate Grok-only config required**.

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
python3 scripts/okf-graph.py subgraph sample-okf agents/graph-engineer.md --hops 2
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

`/okf-init` · `/okf-author` · `/okf-impact` · `/okf-query` · `/okf-validate`

### Agent

- **graph-engineer** — specialist for dual-graph reasoning, impact, and curation

### Hooks

Post-edit (`Write|Edit`) on OKF paths runs `scripts/okf-curate.sh` (validate/lint when `okf` is present; lightweight checks otherwise).

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

- **v0.1 (MVP)** — skills, packaging, hooks, sample OKF, okfcli/Python wrappers  
- **v0.2** — richer typed edges, TicketLink SLDC helpers, GraphEngineer polish  
- **Later** — MCP server, CI action, enhanced visualization overlays  

## Related ecosystem

Complements general OKF tooling (okf-gem, okfcli, community skills) by focusing on impact analysis, harness graphs, and progressive disclosure — without replacing existing CLIs or visualizers.

## License

MIT — see [LICENSE](./LICENSE).
