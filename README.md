# okf-graph-eng (okf-plugin)

**OKF graph engine** — validate, walk, pack, and impact-analyze Git-native knowledge graphs. This plugin does **not** own domain nouns. It owns the envelope and two infrastructure types: **Catalog** and **ContextPack**.

Works in **Claude Code**, **Grok Build** (zero-config), **Cursor**, **Codex**, **Grok Bot**, and **LangChain Deep Agents**.

| | |
|---|---|
| **Plugin name** | `okf-graph-eng` |
| **Repo** | [SpillwaveSolutions/okf-plugin](https://github.com/SpillwaveSolutions/okf-plugin) |
| **Version** | 0.8.1 |
| **License** | MIT |
| **Nouns this plugin owns** | `Catalog`, `ContextPack` |

Domain types live in sibling plugins. This engine **reads** whatever `type` you put in YAML frontmatter: unknown types fall back to `BaseConcept` (`type` + `title` only). That fallback is read-only envelope parsing — it does not authorize a write. `validate --strict` rejects unknown types (fail-closed).

## Nouns (this plugin)

| Noun | Role |
|------|------|
| `Catalog` | Index page for a directory of concepts. Structural. Pack walks skip flooding through hub catalogs by using **outbound-only** BFS. |
| `ContextPack` | Generated progressive-disclosure view: a ranked, hop-capped, node-capped subgraph ready to paste into an agent context window. |

Everything else is **not** an okf-plugin noun:

| Plugin | Owns |
|--------|------|
| [PKC](https://github.com/SpillwaveSolutions/project-knowledge-capture) | Meeting, Experiment, Discovery, Assumption, Question, Feature, Requirement, Specification, Design, Release, CodeChange, Package, Risk, Acceptance, DecisionRecord, TicketLink, Epic, Story, Task, Subtask, Bug, Branch, Project, Playbook, Runbook, Reference |
| [SAC](https://github.com/SpillwaveSolutions/system-architecture-capture) | System, Service, Component, and the rest of the architecture/runtime topology set |
| [DEKC](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture) | Dataset, Table, View, Metric, lineage, lakes, marts, streams, jobs, semantic layer, glossary |
| [AGER](https://github.com/SpillwaveSolutions/okf-agent-graph) | AgentNode, Workflow, Harness, SharedState, ToolCapability, loop/runtime/ops/eval types |

Validators **merge** sibling `schemas/okf-concepts/` directories. Isolated, this plugin only knows Catalog + ContextPack.

## Why this plugin exists

OKF is Markdown + YAML in Git. Agents cannot read a whole second brain. This plugin is the **read path optimizer**:

1. Treat the bundle as a directed graph (absolute Markdown links + optional `links[].rel`).
2. Compute **blast radius** (`impact`) before structural edits.
3. Emit a **ContextPack** — the smallest subgraph that is still useful.

It is not a capture plugin, not an agent runtime, and not a data catalog.

## How ContextPacks optimize reads

`okf-graph.py pack` (skill `okf-query`) is the default way a long-running agent should *read* an OKF tree. It is deliberately lossy.

### 1. Outbound-only walk

Default BFS follows **outbound** edges only. Catalog indexes that link to every child are hubs. Walking them undirected dumps the whole bundle into context. Outbound-from-a-concept stays inside a theme (agent → tools → knowledge, table → lineage → metric).

`--undirected` exists for “what would break?” neighborhood exploration. It floods. Prefer `impact` for that.

### 2. Hop cap (default 2)

Two hops is usually agent → collaborator → evidence. Hop 3 is a debug knob, not a default. Unlimited closure is `impact`, not `pack`.

### 3. Node cap (default 20)

Fits a long-running agent’s working set. Ranked overflow goes in `## Excluded (available on request)` so the model can ask for a named follow-up instead of guessing.

### 4. Trust-first ranking

Inside the neighborhood, nodes sort as:

1. The **entry** concept (always first, always included)
2. **Verified** over unverified
3. Domain-declared **high-impact** types (`x-impact: high` on the owning plugin’s schema — AGER `AgentNode` / `Workflow` / `Harness` / `SharedState`, etc.)
4. Title

Unverified high-impact nodes are flagged in the pack (`⚠ unverified high-impact`) so the model does not treat a draft harness node as truth.

### 5. Read order ≠ inclusion order

Inclusion ranking decides *who makes the cut*. **Read order** is how the markdown is presented: entry, then high-impact, then verified, then title. The model sees the question it asked first, then the dangerous neighbors, then the supporting evidence.

### 6. Criticality for impact (not pack)

`impact` ranks dependents with a criticality tier from the same `x-impact` field:

| Schema `x-impact` | verified | unverified |
|-------------------|----------|------------|
| high | high | **critical** |
| medium | medium | **high** |
| (unset / low) | low | low (never escalates) |

Core declares **no** impact tiers. If you run this plugin alone, every type is `low` — correct, because Catalog/ContextPack are not blast-radius hubs.

### 7. Token-budgeted sibling packs

PKC / DEKC / AGER ship their own `*_pack.py` that wrap this graph and add a **fail-closed token budget** (default ¼ of `SECOND_BRAIN_WINDOW_TOKENS`, 128000 → 32000). Those packs:

- do not `--write` an over-budget ContextPack
- omit neighbor **bodies** (title, type, path, `description` only) unless the node is the pack root
- treat catalog `index.md` as non-concepts

Use this plugin’s `pack` for a portable subgraph. Use the domain pack when you are already inside that second brain and must fit a model window.

### Pack command

```bash
python3 scripts/okf-graph.py pack <bundle> <concept> --hops 2 --max-nodes 20
```

JSON includes `markdown` (ready to paste), `included`, `excluded`, and typed `edges`.

## Install

### Claude Code

```bash
claude plugin marketplace add SpillwaveSolutions/okf-plugin
claude plugin install okf-graph-eng@okf-plugin-marketplace
```

### Grok Build

Zero-config Claude plugin load. Optional identity pin: `.grok-plugin/marketplace.json`.

### Cursor / Codex

Root Agent Plugins 1.0 `plugin.json` plus `.cursor-plugin/` / `.codex-plugin/`. See [docs/CURSOR.md](docs/CURSOR.md).

### Optional CLI

Prefer [`okfcli`](https://github.com/okfcli/okf) / `okf` when present. Fallback: `scripts/okf-graph.py`.

## Quick start

```bash
python3 scripts/okf-graph.py validate sample-okf
python3 scripts/okf-graph.py impact sample-okf knowledge/skill-okf-impact.md
python3 scripts/okf-graph.py pack sample-okf knowledge/plugin-architecture.md --hops 2
python3 scripts/okf-graph.py graph sample-okf --format html > okf-graph.html
```

Scaffold a bundle with `/okf-init` (catalogs + knowledge + packs only). Author domain nouns with **PKC / SAC / DEKC / AGER**, not this plugin.

TicketLink emission lives in PKC:

```bash
bin/worklog fold | python3 path/to/project-knowledge-capture/scripts/pkc_ticket_link.py emit --bundle knowledge --open-only
```

## What’s included

| Skill | Purpose |
|-------|---------|
| `okf-init-graph` | Scaffold `.okf/` with catalogs, knowledge, packs |
| `okf-author` | Envelope + Catalog / ContextPack (domain types: use the owning plugin) |
| `okf-impact` | Transitive blast radius + ranked update order |
| `okf-query` | Multi-hop subgraph / ContextPack |
| `okf-maintain` | Indexes, log, drift, orphans |
| `okf-validate` | Conformance + graph quality |
| `okf-visualize` | Mermaid / HTML / JSON |

Commands: `/okf-init` · `/okf-author` · `/okf-impact` · `/okf-query` · `/okf-validate` · `/okf-visualize` · `/okf-maintain`

**graph-engineer** agent: pack-first, impact-before-structure, no domain-noun authorship.

Post-edit hook is **fail-closed validate** (`scripts/okf-hook-validate.sh`).

```bash
python3 tests/test_okf_graph.py -q
python3 tests/test_okf_schema.py
bash tests/test_okf_curate.sh
```

`sample-okf/` is a self-describing **Catalog + ContextPack** bundle for this engine (not an AGER graph).

Existing second brains: [noun-ownership migration](docs/user_guide/noun-ownership-migration.md) (0.8 family).

## Related ecosystem

| Repo | Role |
|------|------|
| this | Graph engine, Catalog, ContextPack |
| [project-knowledge-capture](https://github.com/SpillwaveSolutions/project-knowledge-capture) | Project memory + TicketLink |
| [system-architecture-capture](https://github.com/SpillwaveSolutions/system-architecture-capture) | Runtime / architecture topology |
| [data-engineering-knowledge-capture](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture) | Data plane |
| [okf-agent-graph](https://github.com/SpillwaveSolutions/okf-agent-graph) | AGER multi-agent graphs |
| [wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd) | Worklog |
| [second-brain-marketplace](https://github.com/SpillwaveSolutions/second-brain-marketplace) | Pack install |

## Project management (WikiTicket SDD)

See [wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd). Commit messages must reference a worklog ULID or `#issue`. Prefer feature branches.

## License

MIT — see [LICENSE](./LICENSE).
