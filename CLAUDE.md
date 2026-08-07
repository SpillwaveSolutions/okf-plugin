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
8. **Check your base before building in a worktree.** An isolated worktree may be
   cut from the repo default branch, not from the branch you are working on, so
   the commits you are building against can simply be absent. Run
   `git log --oneline -3` first and confirm you see the parent commit you expect.
   If not, `git reset --hard <intended-branch>` before writing code — a working
   tree with no commits of its own is safe to move. Skipping this check silently
   rebuilds work that already exists, or conflicts at merge time.
9. **Merge PRs with a merge commit, not a squash.** Use `gh pr merge --merge`.
   Frozen documents (design docs, plans, snapshots) are stamped with the commit
   they were written against, and `worklog doc-verify` resolves every code
   citation at that commit. A squash never puts the authoring commit on the
   default branch, so in a fresh clone `git show <sha>:<path>` fails and the
   verifier loses its ground truth — it must then report `unresolvable` rather
   than degrade to HEAD, which is the assumption that produced the bad
   citations it exists to catch. Upstream ADR-0008 records the same rule.
   PRs #38–#45 were squashed before this was understood; they happen to resolve
   because their stamps landed on main anyway, but do not take them as
   precedent.

## Common commands

```bash
python3 scripts/okf-graph.py validate sample-okf
python3 scripts/okf-graph.py impact sample-okf agents/graph-engineer.md
python3 scripts/okf-graph.py pack sample-okf agents/graph-engineer.md --hops 2
python3 scripts/okf-graph.py edges sample-okf --rel routes_to
python3 scripts/okf-graph.py orphans sample-okf
bin/worklog fold | python3 scripts/okf-ticket-link.py emit --bundle sample-okf --open-only --dry-run
```

## When editing the plugin itself

- Bump `version` in `.claude-plugin/plugin.json` for releases.
- Keep sample-okf in sync when adding skills or architectural decisions.
- After sample-okf edits, run `okf-graph.py validate sample-okf`.
- Post-edit hook may run curate on OKF paths; keep scripts portable (`bash` + `python3`).

## Dual-host note

Grok Build loads this same tree. Prefer Claude plugin conventions so both hosts stay aligned. See [AGENTS.md](./AGENTS.md) for Grok/Codex-oriented wording of the same rules.

<!-- worklog:policy:start -->
## Work tracking policy

- Every plan MUST end by running `worklog plan-capture` — it writes
  `docs/plans/<date>-<slug>.md` and appends the plan's steps as work items.
- Work discovered mid-flight that wasn't in the plan: run
  `worklog add --unplanned --discovered-during <item>` BEFORE doing the work.
- Never hand-edit `.work/*.jsonl` (use `worklog`) or `docs/roadmap.md`
  (it is generated; change the work items instead).
- After changing work items, run `worklog roadmap-render` and commit the log
  and roadmap together.
<!-- worklog:policy:end -->

<!-- worklog:taxonomy:start -->
## Work taxonomy

Every work item sits on four independent axes:

| Axis | Field | Values | Answers |
|---|---|---|---|
| Level | `level` | epic / story / task / subtask | size & place in the parent tree |
| Kind | `kind` | feature / bug / ops / triage | nature of the work |
| Milestone | `milestone` | free string (e.g. v0.6.0) or null | what ships together |
| Planned | `unplanned` + `discovered_during` | bool + ULID | deliberate vs discovered |

Rules (the validator enforces these; apply them when proposing items):
1. Kind is free at story/task/subtask.
2. Epics are `feature` or `ops` only — a bug is never epic-sized.
3. `kind` defaults to `triage` when omitted — never silently default to feature.
4. `bug.parent` is optional; bugs may float free of any epic.
5. `milestone` lives on leaves (story and below); an epic's milestone derives from its children.
6. `triage` and `ops` both trend down: triage shrinks by classifying, ops by automating.

When trackable work surfaces in conversation, propose an item inline as part of
the normal response — "want me to file this? `level:story kind:feature
parent:<ulid> milestone:v0.6.0`" — and create it only on assent, via the
work-track or plan-capture skill. When unsure of the kind, propose `kind:triage`
with the open question stated — triage is the honest default, never a confident
guess. This inline path is the default; the flag-gated classifier (`classifier:`
in `.work/config.yml`, off by default) is the escape hatch for teams where work
keeps escaping the log.
<!-- worklog:taxonomy:end -->
