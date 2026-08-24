# CLAUDE.md — okf-graph-eng

Instructions for **Claude Code** when working in this repository or when the plugin is installed.

## What this project is

**okf-graph-eng** is a Claude Code plugin that turns OKF (Open Knowledge Format) repos into a **graph engine**: validate, walk, pack, and impact-analyze Git-native Markdown + YAML.

It owns **Catalog** and **ContextPack**. It does not own domain nouns. PKC, SAC, DEKC, and AGER do.

**Hosts:** Claude Code (primary packaging) and **Grok Build** (native zero-config compatibility with Claude plugins). Do not add Grok-only features that break Claude Code.

## Plugin layout

```
.claude-plugin/plugin.json   # manifest (name: okf-graph-eng)
skills/                      # portable intelligence (SKILL.md per skill)
commands/                    # slash command wrappers
agents/graph-engineer.md     # specialist subagent
hooks/hooks.json             # post-edit fail-closed validate
scripts/                     # okf-hook-validate.sh, okf-graph.py
sample-okf/                  # Catalog + Knowledge about this engine
schemas/okf-concepts/        # BaseConcept envelope + Catalog + ContextPack
```

Use `${CLAUDE_PLUGIN_ROOT}` for all intra-plugin paths in hooks and skill instructions.

## Skills (auto-invoke)

| Skill | Trigger themes |
|-------|----------------|
| okf-init-graph | new OKF / scaffold / graph eng setup |
| okf-author | Catalog, ContextPack, envelope (domain types: hand off) |
| okf-impact | blast radius, what depends on, ripple |
| okf-query | subgraph, context pack, multi-hop |
| okf-maintain | curate, orphans, drift, migrate |
| okf-validate | validate bundle, graph quality |
| okf-visualize | mermaid, diagram, HTML map |

## Working rules

1. **Deterministic tools first** — prefer `okf` / `okfcli` when installed; else `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/okf-graph.py …`.
2. **Impact before structural edits** — especially for types whose owning plugin declared `x-impact: high`. Isolated, this plugin has none.
3. **Absolute Markdown links** — `[Title](/path/from/bundle/root.md)`.
4. **Frontmatter** — at least `type`, `title`, `description`, `timestamp` (ISO-8601).
5. **Progressive disclosure** — ship subgraphs / packs, not whole trees. Default pack: outbound-only, 2 hops, 20 nodes.
6. **Never invent edges** — only report links that exist (or clearly mark proposed new links).
7. Keep each `SKILL.md` focused; put deep reference material in skill `templates/` or `references/`.
8. **Do not author domain nouns here.** `AgentNode` / `Workflow` / `Harness` → AGER. `TicketLink` / `DecisionRecord` / work types → PKC. Architecture → SAC. Data plane → DEKC.
9. **Check your base before building in a worktree.** An isolated worktree may be
   cut from the repo default branch, not from the branch you are working on, so
   the commits you are building against can simply be absent. Run
   `git log --oneline -3` first and confirm you see the parent commit you expect.
   If not, `git reset --hard <intended-branch>` before writing code — a working
   tree with no commits of its own is safe to move. Skipping this check silently
   rebuilds work that already exists, or conflicts at merge time.
10. **Merge PRs with a merge commit, not a squash.** Use `gh pr merge --merge`.
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
python3 scripts/okf-graph.py impact sample-okf knowledge/plugin-architecture.md
python3 scripts/okf-graph.py pack sample-okf knowledge/plugin-architecture.md --hops 2
python3 scripts/okf-graph.py edges sample-okf --rel depends_on
python3 scripts/okf-graph.py orphans sample-okf
```

TicketLink emission lives in PKC:

```bash
bin/worklog fold | python3 path/to/project-knowledge-capture/scripts/pkc_ticket_link.py emit --bundle knowledge --open-only --dry-run
```

## When editing the plugin itself

- Bump `version` in root `plugin.json` **and** host copies (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, marketplaces) for releases.
- Keep sample-okf in sync when adding skills. Do not seed AGER/PKC nouns into the sample.
- After sample-okf edits, run `okf-graph.py validate sample-okf`.
- Frozen design-doc snapshots under `docs/designs/2026-*` stay frozen. Corrections go in the next release notes, not the stamp.
