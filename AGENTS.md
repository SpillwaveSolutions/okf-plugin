# AGENTS.md — okf-graph-eng

Agent-facing instructions for **Grok Build**, Codex-style runners, and any host that loads this repository as a Claude-compatible plugin.

## Host compatibility

| Host | How this plugin loads |
|------|------------------------|
| **Claude Code** | Native plugin (`.claude-plugin/plugin.json`, skills, agents, hooks, commands) |
| **Grok Build** | Zero-config Claude plugin compatibility — skills/agents/hooks discovered automatically |

This repo is intentionally **one plugin, two hosts**. Do not introduce Grok-only packaging that diverges from Claude conventions unless adding optional metadata later (e.g. `.grok-plugin/marketplace.json`).

## Mission

Turn any OKF repository into a **graph engineering** workspace:

- Knowledge concepts (datasets, runbooks, APIs, …)
- Agent/harness concepts (`AgentNode`, `Workflow`, `SharedState`, `DecisionRecord`, `ToolCapability`, `TicketLink`)
- Impact analysis, validation, progressive disclosure packs

## Component map

- **Skills** — `skills/*/SKILL.md` (core intelligence)
- **Commands** — `commands/*.md` (slash entry points)
- **Agent** — `agents/graph-engineer.md`
- **Hooks** — `hooks/hooks.json` → `scripts/okf-curate.sh`
- **CLI fallback** — `scripts/okf-graph.py`
- **Sample dual graph** — `sample-okf/`

Plugin root variable in Claude/Grok plugin context: `${CLAUDE_PLUGIN_ROOT}`.

## Operating principles

1. Prefer **okf / okfcli** for graph ops; fallback to `scripts/okf-graph.py`.
2. Always consider **impact** before changing high-degree or harness concepts.
3. Emit **minimal context packs** (2-hop default) for long runs.
4. Use **absolute** in-bundle Markdown links.
5. Complete YAML frontmatter on every concept (`type`, `title`, `description`, `timestamp`).
6. Do not fabricate graph edges.
7. High-trust first: prefer `verified: true`, non-stale, `status: active|accepted`.

## Skill routing (natural language)

| User language | Skill |
|---------------|--------|
| scaffold / init OKF / graph eng setup | okf-init-graph |
| document agent / workflow / metric / ADR | okf-author |
| blast radius / what breaks / dependents | okf-impact |
| context pack / multi-hop / neighborhood | okf-query |
| curate / orphans / fix indexes / migrate | okf-maintain |
| is this valid / graph quality | okf-validate |
| diagram / mermaid / visualize | okf-visualize |

## Specialist agent

Invoke **graph-engineer** for multi-step dual-graph work (impact + pack + curation in one arc).

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
