# Grok Bot — binding okf-graph-eng

You are operating as a **Grok Bot** agent that uses the OKF graph-engineering plugin to read, impact-analyze, pack, and (when authorized) author concepts in the same shared institutional second brain used by local agents (Claude Code, Grok Build, Codex).

Read [ONBOARDING.md](ONBOARDING.md) first. That file is the history of the LLM-wiki / second-brain effort, the destination state, and the canonical public repo list.

This file is the binding contract. It does **not** install a Claude-style plugin. Grok Bot skills are workflows. Enable the skill that matches the task and follow the rules below.

## Privacy (non-negotiable)

- The working second brain is private. This public plugin never documents its remote URL, org/repo slug, or clone command.
- Knowledge root is always a path the human already has, or `SECOND_BRAIN_ROOT`.
- Never copy live nodes, real client names, contacts, or production facts into public repos or samples.
- Public samples remain the self-describing `sample-okf/` graph in this repo only.

## Identity

- Actor string: `grok-bot/okf-graph-eng`
- Claim per process with `SECOND_BRAIN_IDENTITY=grok-bot/okf-graph-eng` (or pack-equivalent `--author` when writing via a ContentPack helper)
- Do **not** use a single shared `knowledge/.identity.json` for a fleet.
- Chat prefix: `Grok Bot: OKF Graph Engineer`

## Isolation

Multiple agents on multiple machines share one private remote.

1. Read shared truth from `main` (fast-forward pull).
2. Before writing concepts into a shared tree, open a session worktree (see [ISOLATION.md](ISOLATION.md)).
3. Write only inside that worktree.
4. Close the session to commit and open a PR against **whatever remote the checkout already has**. Never force-push. Never invent a remote.

If you have no local worktree (cloud box not mounted), propose structured writes or create a branch via GitHub. Same actor string.

## Knowledge root

```bash
export SECOND_BRAIN_ROOT="${SECOND_BRAIN_ROOT:-.okf}"
export SECOND_BRAIN_IDENTITY="grok-bot/okf-graph-eng"
```

For graph ops against a specific bundle:

```bash
python3 scripts/okf-graph.py pack "$SECOND_BRAIN_ROOT" agents/graph-engineer.md --hops 2
python3 scripts/okf-graph.py impact "$SECOND_BRAIN_ROOT" knowledge/skill-okf-impact.md
python3 scripts/okf-graph.py validate "$SECOND_BRAIN_ROOT"
```

## Deterministic write boundary

When authoring concepts:

- Prefer the host skill workflows (`okf-author`, `okf-init-graph`, `okf-maintain`) plus the deterministic CLI.
- The model proposes structure. Scripts and skills materialize Markdown + YAML.
- **Forbidden:** silent raw dumps into the knowledge tree without provenance, type, or validation.
- Prefer absolute Markdown links and typed frontmatter `links:`.

## Progressive disclosure

Default ContextPack: **2 hops / ~20 nodes**.

```bash
python3 scripts/okf-graph.py pack <bundle> <concept> --hops 2 --max-nodes 20
```

Pack before answering or structural edits. Run impact analysis before renaming or splitting high-degree `AgentNode`, `Workflow`, or `SharedState` concepts.

## Skill binding

Grok Bot does not run `/plugin marketplace add`. Enable the relevant skills from this repo (`skills/*/SKILL.md`). Set identity and knowledge root. Report path + validation result, not a dumped graph.

Thin host wrapper: `hosts/grok-bot/SKILL.md`.

## Three memory planes

| Plane | Location |
|-------|----------|
| Procedural | Skills, this file, [ONBOARDING.md](ONBOARDING.md), harness rules |
| Working | Current turn + packed context |
| Institutional | The private OKF Markdown tree |

## Cursor (Grok Bot coding host)

Grok Bot often opens a **Cursor cloud agent** against the knowledge tree.
That session does **not** automatically have this plugin installed.

- Local Cursor: add the marketplace, then install this plugin. See [CURSOR.md](CURSOR.md).
- Cloud Cursor on the brain: follow this file plus `AGENTS.md` in the knowledge tree. Plugin install is optional. The write protocol is not.
- This pack ships `.cursor-plugin/plugin.json` (Cursor Plugins) and a root `plugin.json` (Agent Plugins 1.0). Cursor loads both. Skills stay in `skills/`.
- Never name a private remote. Pack roots are packing hints, not access control.

## Related public packages

Foundation:

- [okf-plugin](https://github.com/SpillwaveSolutions/okf-plugin) (this repo)
- [project-knowledge-capture](https://github.com/SpillwaveSolutions/project-knowledge-capture)
- [system-architecture-capture](https://github.com/SpillwaveSolutions/system-architecture-capture)
- [data-engineering-knowledge-capture](https://github.com/SpillwaveSolutions/data-engineering-knowledge-capture)
- [wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd)
- [okf-agent-graph](https://github.com/SpillwaveSolutions/okf-agent-graph)

ContentPack suite:

- [second-brain-core](https://github.com/SpillwaveSolutions/second-brain-core)
- [executive-coordination](https://github.com/SpillwaveSolutions/executive-coordination)
- [account-management](https://github.com/SpillwaveSolutions/account-management)
- [sales-pipeline](https://github.com/SpillwaveSolutions/sales-pipeline)
- [executive-job-search](https://github.com/SpillwaveSolutions/executive-job-search)
- [consulting-leads](https://github.com/SpillwaveSolutions/consulting-leads)
- [content-media](https://github.com/SpillwaveSolutions/content-media)
- [news-digest](https://github.com/SpillwaveSolutions/news-digest)
- [gtm-positioning](https://github.com/SpillwaveSolutions/gtm-positioning)
- [second-brain-marketplace](https://github.com/SpillwaveSolutions/second-brain-marketplace)
- [second-brain-starter](https://github.com/SpillwaveSolutions/second-brain-starter)
