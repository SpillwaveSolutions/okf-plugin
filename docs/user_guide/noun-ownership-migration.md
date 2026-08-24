---
doc_type: guide
slug: noun-ownership-migration
title: Noun-ownership migration
truth_state: current
wiki_key: noun-ownership-migration
---

# Noun-ownership migration (0.8 family)

Upgrade an **existing** Git-native second brain after the 24 Aug 2026 noun split.

This is not a new capture format. YAML frontmatter `type:` strings stay. **Who owns the schema** moved. Most trees only need plugin upgrades. A few DEKC pipeline nodes need a retype.

| Plugin | Tag | Owns |
|--------|-----|------|
| [okf-plugin](https://github.com/SpillwaveSolutions/okf-plugin) `okf-graph-eng` | **v0.8.0** | `Catalog`, `ContextPack` (+ `BaseConcept` envelope) |
| [project-knowledge-capture](https://github.com/SpillwaveSolutions/project-knowledge-capture) | **v0.8.0** | Project memory + WikiTicket work types |
| [system-architecture-capture](https://github.com/SpillwaveSolutions/system-architecture-capture) | **v0.5.0** | Architecture / runtime topology |
| [okf-agent-graph](https://github.com/SpillwaveSolutions/okf-agent-graph) | **v0.7.0** | Agent / harness / loop / ops / eval |
| [data-engineering-knowledge-capture](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture) | **v0.4.0** | Data plane |

Pack-specific notes:

- [PKC](https://github.com/SpillwaveSolutions/project-knowledge-capture/blob/main/docs/user_guide/noun-ownership-migration.md)
- [SAC](https://github.com/SpillwaveSolutions/system-architecture-capture/blob/main/docs/user_guide/noun-ownership-migration.md)
- [AGER](https://github.com/SpillwaveSolutions/okf-agent-graph/blob/main/docs/user_guide/noun-ownership-migration.md)
- [DEKC](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture/blob/main/docs/user_guide/noun-ownership-migration.md)

Frozen design-doc snapshots in each repo are historical. Do not edit them to match this cut.

## 1. What broke if you do nothing

| Symptom | Cause |
|---------|--------|
| `validate --strict` exits 1 with `unknown type \`Foo\`` | Isolated engine no longer ships Foo’s schema |
| `okf-ticket-link.py` exits 2 | Stub. Emission moved to PKC |
| Impact ranks everything `low` | Criticality now comes from sibling `x-impact`, not a hardcoded AgentNode/Dataset list |
| `/okf-init` no longer seeds agents/workflows/tickets | Those catalogs belong to AGER / PKC |
| Unverified `JudgeAgent` / `LoopPolicy` warned as high-impact | AGER schemas now declare `x-impact` |
| DEKC `type: Workflow` still looks like an agent graph | `Workflow` is an AGER noun. Data jobs are `IngestionJob` |

Lenient `validate` (no `--strict`) still **reads** unknown types via the BaseConcept envelope (`type` + `title` only). That fallback is **not** a write authorization. Post-edit hooks that call `--strict` will fail-closed.

## 2. Upgrade plugins first

Install order matches merge order: engine, then capture packs.

```bash
# Claude Code / marketplace
claude plugin marketplace add SpillwaveSolutions/okf-plugin
claude plugin install okf-graph-eng@okf-plugin-marketplace
claude plugin marketplace add SpillwaveSolutions/project-knowledge-capture
claude plugin install project-knowledge-capture@pkc-plugin-marketplace
claude plugin marketplace add SpillwaveSolutions/system-architecture-capture
claude plugin install system-architecture-capture@sac-plugin-marketplace
claude plugin marketplace add SpillwaveSolutions/okf-agent-graph
claude plugin install okf-agent-graph@okf-agent-graph-marketplace
claude plugin marketplace add SpillwaveSolutions/data-engineering-knowledge-capture
claude plugin install data-engineering-knowledge-capture@dekc-plugin-marketplace
```

Pin checkouts, not floating `main`, if CI clones siblings:

| Repo | Pin |
|------|-----|
| okf-plugin | `v0.8.0` (or later 0.8.x) |
| project-knowledge-capture | `v0.8.0` |
| system-architecture-capture | `v0.5.0` |
| okf-agent-graph | `v0.7.0` |
| data-engineering-knowledge-capture | `v0.4.0` |

A mixed second brain **should keep every pack you write nouns for**. Validators merge `schemas/okf-concepts/` from siblings. Dropping AGER from a tree that still has `type: AgentNode` makes `--strict` fail.

## 3. Inventory the bundle

From a clone of this plugin (or any host that has `okf-graph.py`):

```bash
BUNDLE="${SECOND_BRAIN_ROOT:-knowledge}"

python3 scripts/okf-graph.py validate "$BUNDLE"
python3 scripts/okf-graph.py validate "$BUNDLE" --strict
python3 scripts/okf-graph.py schemas
```

Count `type:` values (frontmatter only):

```bash
python3 - "$BUNDLE" <<'PY'
from pathlib import Path
import re, collections, sys
root = Path(sys.argv[1] if len(sys.argv) > 1 else "knowledge")
counts = collections.Counter()
for p in root.rglob("*.md"):
    text = p.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        continue
    m = re.search(r"(?m)^type:\s*[\"']?([A-Za-z][A-Za-z0-9]*)", text)
    if not m:
        continue
    counts[m.group(1)] += 1
for t, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
    print(f"{n:4d}  {t}")
print("# files with a type:", sum(counts.values()))
PY
```

Save the type histogram. That is the before-state.

## 4. Type → owner (keep the type)

Do **not** bulk-rename these. Keep `type:` and install the owner.

| `type` | Owner after the cut |
|--------|---------------------|
| `Catalog`, `ContextPack` | okf-plugin |
| `Meeting`, `Experiment`, `Discovery`, `Assumption`, `Question`, `Feature`, `Requirement`, `Specification`, `Design`, `Release`, `CodeChange`, `Package`, `Risk`, `Acceptance`, `DecisionRecord`, `TicketLink`, `Epic`, `Story`, `Task`, `Subtask`, `Bug`, `Branch`, `Project`, `Playbook`, `Runbook`, `Reference` | PKC |
| SAC topology set (`System`, `Service`, `Component`, `ApiContract`, `Diagram`, `Wireframe`, … — 139 types) | SAC |
| `Dataset`, `Table`, `View`, `Metric`, `Stream`, `IngestionJob`, `Transformation`, `LineagePath`, lakes/marts/semantic/glossary, … — 29 types | DEKC |
| `AgentNode`, `Workflow`, `Harness`, `SharedState`, `ToolCapability`, role agents, loop/runtime/ops/eval — 51 types | AGER |
| `WriteEvent` | Write journal (`second-brain-core` / pack `*_common.emit_write_event`). **Not** an AGER noun. Leave the files. |

Unknown `type` after the owning plugin is installed means the name was never in a registry. Do not invent a new noun to make `--strict` pass. Fix the file or add the plugin that actually owns it.

## 5. When to retype (the exceptions)

### 5.1 DEKC data jobs stored as `Workflow`

Before 0.4.0, DEKC used `Workflow` for Glue/ADF/Airflow/Fabric jobs. `Workflow` is now an **AGER** multi-agent graph.

| If the node is… | Do this |
|-----------------|---------|
| A data pipeline / orchestrated job | Change `type: Workflow` → `type: IngestionJob`. Keep path and body. Point `links[].rel` at tables/streams as before. |
| A multi-agent AGER graph | Leave `type: Workflow`. Install AGER. |

```bash
# review candidates first
rg -n '^type:[[:space:]]*Workflow' "$BUNDLE"
```

Retype one file, validate, then the rest. Do not sed the whole tree if some Workflows are AGER graphs.

### 5.2 Engine-only sample / `Knowledge`

okf-plugin’s own `sample-okf` no longer uses domain types. A fork of the old sample that still has `type: AgentNode` / `TicketLink` / `DecisionRecord` / generic `Knowledge` should either:

- install the owning plugins and keep the types, or
- retype indexes to `Catalog` and generated packs to `ContextPack` (engine-only tree)

`--strict` on an isolated okf-plugin rejects anything else.

### 5.3 Do not retype `WriteEvent`

AGER 0.7.0 **deleted** `WriteEvent.schema.json`. Nodes under `write-events/` stay `type: WriteEvent`. They are the write journal, not harness config. Isolated `ager-validate --strict` already skips them as a non-AGER type.

## 6. Tooling that moved

| Old | New |
|-----|-----|
| `scripts/okf-ticket-link.py emit …` | `project-knowledge-capture/scripts/pkc_ticket_link.py emit …` |
| `/okf-author` for AgentNode / Workflow / TicketLink | `/ager-author` or `/pkc-capture-*` / `pkc_ticket_link.py` |
| `/okf-init` seeding `agents/`, `workflows/`, `tickets/` | `/ager-init` and `/pkc-init` |
| Hardcoded impact list (AgentNode, Dataset, …) | Schema `x-impact: high\|medium` on the **owning** plugin |

Hook rewrite (shell aliases, CI, Cursor rules, Codex `hooks.json`):

```bash
# before
bin/worklog fold | python3 scripts/okf-ticket-link.py emit --bundle knowledge --open-only

# after
bin/worklog fold | python3 path/to/project-knowledge-capture/scripts/pkc_ticket_link.py emit --bundle knowledge --open-only
```

`okf-ticket-link.py` prints a pointer and exits 2. Do not wrap that stub.

## 7. Dual-owned **names** (same string, different meaning)

A shared tree has one `type:` field. These collisions are documented, not granted:

| Name | Meanings |
|------|----------|
| `Package` | PKC: what shipped. SAC: build/module in the topology |
| `Dashboard` | SAC: observability. DEKC: analytics |
| `DataLake` | SAC: platform lake. DEKC: medallion lake |
| `GlossaryTerm` | SAC: architecture glossary. DEKC: data-domain glossary |
| `RateLimit` | SAC: gateway quota. AGER: tool/loop runtime quota |
| `Risk` | PKC: project-memory risk. executive-coordination: company risk |
| `Experiment` | PKC: spike. GTM: growth experiment |

Do not write both meanings into one bundle without a routing row. Prefer the pack you are actually in.

`Question` stays PKC. Research Knowledge Capture uses `ResearchQuestion`. Do not collapse those.

## 8. Validate after the upgrade

```bash
# engine (always)
python3 path/to/okf-plugin/scripts/okf-graph.py validate "$BUNDLE"
python3 path/to/okf-plugin/scripts/okf-graph.py validate "$BUNDLE" --strict

# pack validators if those trees exist
python3 path/to/project-knowledge-capture/scripts/pkc_validate.py --bundle "$BUNDLE"
python3 path/to/system-architecture-capture/scripts/sac_validate.py --bundle "$BUNDLE" --schema
python3 path/to/okf-agent-graph/scripts/ager-validate.py "$BUNDLE" --strict
python3 path/to/data-engineering-knowledge-capture/scripts/dekc_schemas.py validate --bundle "$BUNDLE"
```

Done when:

1. Plugin versions match the table in this doc (or newer patch on the same minor).
2. `--strict` unknown-type errors are gone **or** explicitly deferred with the owning plugin still missing.
3. DEKC pipeline `Workflow` nodes that are jobs are `IngestionJob`.
4. TicketLink emission uses `pkc_ticket_link.py`.
5. `log.md` has a one-line entry for the upgrade.

Append to `log.md`:

```markdown
- 2026-08-24: noun-ownership cut — plugins at okf 0.8.0 / PKC 0.8.0 / SAC 0.5.0 / AGER 0.7.0 / DEKC 0.4.0
```

## 9. Isolation sessions

If the brain is shared, upgrade inside a `brain/<actor>/<session-id>` worktree and open a PR. Do not rewrite catalogs you do not own (`catalog_ownership` in each pack’s `registry.json`). Foreign catalogs are read-only.

Public samples stay Northstar / Lumenfield. Do not copy a live client tree into a public pack to “test” this migration.