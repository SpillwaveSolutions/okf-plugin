# AGENTS.md — okf-graph-eng

Agent-facing instructions for **Grok Build**, Codex-style runners, and any host that loads this repository as a Claude-compatible plugin.

## Host compatibility

| Host | How this plugin loads |
|------|------------------------|
| **Claude Code** | Native plugin (`.claude-plugin/plugin.json`, skills, agents, hooks, commands) |
| **Grok Build** | Zero-config Claude plugin compatibility — skills/agents/hooks discovered automatically |

This repo is intentionally **one plugin, two hosts**. Do not introduce Grok-only packaging that diverges from Claude conventions unless adding optional metadata later (e.g. `.grok-plugin/marketplace.json`).

## Mission

Turn any OKF repository into a **graph engine** workspace:

- Treat Markdown + YAML as a directed graph (absolute links + optional `links[].rel`)
- **Validate** the bundle
- Compute **impact** (blast radius) before structural edits
- Emit **ContextPacks** — hop-capped, node-capped, outbound-only by default

This plugin does **not** own domain nouns. It owns the envelope (`BaseConcept`) and two infrastructure types:

| Noun | Role |
|------|------|
| `Catalog` | Directory index. Structural. Pack walks skip flooding through hub catalogs by using outbound-only BFS. |
| `ContextPack` | Generated progressive-disclosure view of a ranked, hop-capped subgraph. |

Domain types live in sibling plugins. Unknown `type` values fall back to `BaseConcept` (`type` + `title` only). Validators merge sibling `schemas/okf-concepts/` directories.

| Plugin | Owns |
|--------|------|
| [PKC](https://github.com/SpillwaveSolutions/project-knowledge-capture) | Meeting, Experiment, Discovery, Assumption, Question, Feature, Requirement, Specification, Design, Release, CodeChange, Package, Risk, Acceptance, DecisionRecord, TicketLink, Epic, Story, Task, Subtask, Bug, Branch, Project, Playbook, Runbook, Reference |
| [SAC](https://github.com/SpillwaveSolutions/system-architecture-capture) | System, Service, Component, and the rest of the architecture/runtime topology set |
| [DEKC](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture) | Dataset, Table, View, Metric, lineage, lakes, marts, streams, jobs, semantic layer, glossary |
| [AGER](https://github.com/SpillwaveSolutions/okf-agent-graph) | AgentNode, Workflow, Harness, SharedState, ToolCapability, loop/runtime/ops/eval types |

## Component map

- **Skills** — `skills/*/SKILL.md` (core intelligence)
- **Commands** — `commands/*.md` (slash entry points)
- **Agent** — `agents/graph-engineer.md`
- **Hooks** — `hooks/hooks.json` → `scripts/okf-hook-validate.sh` (fail-closed validate)
- **CLI fallback** — `scripts/okf-graph.py`
- **Sample** — `sample-okf/` (Catalog + Knowledge about this engine; not an AGER graph)

Plugin root variable in Claude/Grok plugin context: `${CLAUDE_PLUGIN_ROOT}`.

## Operating principles

1. Prefer **okf / okfcli** for graph ops; fallback to `scripts/okf-graph.py`.
2. Always consider **impact** before changing high-degree or schema-declared high-impact concepts (`x-impact` on the owning plugin’s schema). Isolated, this plugin has no high-impact types.
3. Emit **minimal context packs** (2-hop default, max 20 nodes, outbound-only) for long runs.
4. Use **absolute** in-bundle Markdown links.
5. Complete YAML frontmatter on every concept (`type`, `title`, `description`, `timestamp`).
6. Do not fabricate graph edges.
7. High-trust first: prefer `verified: true`, non-stale, `status: active|accepted`.
8. Do not author domain nouns here. Hand `AgentNode` / `Workflow` to AGER, `TicketLink` / `DecisionRecord` to PKC, architecture types to SAC, data-plane types to DEKC.
9. Working in an isolated worktree: verify your base commit with
   `git log --oneline -3` before writing code. A worktree may be cut from the
   repo default branch rather than the branch you were told to build on, so the
   commits you depend on can be missing. `git reset --hard <intended-branch>`
   while the tree is clean, then build.
10. Merge PRs with `gh pr merge --merge`, never `--squash`. Frozen documents are
    stamped with the commit they were written against and `worklog doc-verify`
    resolves their code citations at that commit; a squash keeps that commit off
    the default branch, so a fresh clone cannot resolve it.

## Skill routing (natural language)

| User language | Skill |
|---------------|--------|
| scaffold / init OKF / graph eng setup | okf-init-graph |
| document Catalog / ContextPack / envelope | okf-author |
| blast radius / what breaks / dependents | okf-impact |
| context pack / multi-hop / neighborhood | okf-query |
| curate / orphans / fix indexes / migrate | okf-maintain |
| is this valid / graph quality | okf-validate |
| diagram / mermaid / visualize | okf-visualize |

## Specialist agent

Invoke **graph-engineer** for multi-step graph work (impact + pack + curation in one arc). Pack-first. Impact-before-structure. No domain-noun authorship.

## Validation loop

```bash
python3 scripts/okf-graph.py validate sample-okf
```

Treat broken links as errors; orphans and unverified high-impact nodes as warnings to surface.

## Docs

- Human overview: [README.md](./README.md)
- Claude Code detail: [CLAUDE.md](./CLAUDE.md)
- Design sample graph: [sample-okf/index.md](./sample-okf/index.md)

<!-- worklog:policy:start -->
## Work tracking policy

This project is managed with **WikiTicket SDD** ([SpillwaveSolutions/wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd)) — local-first worklog, generated roadmap, optional GitHub Issues + wiki sync.

- Every plan MUST end by running `bin/worklog plan-capture` — it writes
  `docs/plans/<date>-<slug>.md` and appends the plan's steps as work items.
- Work discovered mid-flight that wasn't in the plan: run
  `bin/worklog add --unplanned --discovered-during <item>` BEFORE doing the work.
- Never hand-edit `.work/*.jsonl` (use `bin/worklog`) or `docs/roadmap.md`
  (it is generated; change the work items instead).
- After changing work items, run `bin/worklog roadmap-render` and commit the log
  and roadmap together.
- Commits must reference a worklog ULID or ticket (`#123`). Prefer feature branches — hooks reject direct commits on `main`.
<!-- worklog:policy:end -->

<!-- worklog:taxonomy:start -->
## Work taxonomy

Every work item sits on four independent axes:

| Axis | Field | Values | Answers |
|---|---|---|---|
| Level | `level` | epic / story / task / subtask | size & place in the parent tree |
| Kind | `kind` | feature / bug / ops / triage | nature of the work |
| Milestone | `milestone` | free string (e.g. v0.2.0) or null | what ships together |
| Planned | `unplanned` + `discovered_during` | bool + ULID | deliberate vs discovered |

Rules: epics are `feature` or `ops` only; unclassified defaults to `triage`; propose items inline and create only on assent via `bin/worklog`.
<!-- worklog:taxonomy:end -->
