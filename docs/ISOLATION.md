# Write isolation for OKF bundles

One shared institutional second brain. Many agents. Many machines. Many project worktrees.

okf-graph-eng is the **graph substrate**. It does not own a private remote. When an agent uses this plugin to author or maintain concepts inside a shared OKF tree, isolation still applies.

Type ownership (and catalog ownership in `schemas/okf-concepts/registry.json`) says *what* you may write. Isolation says *where concurrent sessions do not collide*.

## Protocol

```
read  → origin/main (shared truth) + optional session overlay
write → brain/<actor>/<session-id> worktree only
close → commit, push to the checkout's existing remote, open PR
merge → human or green auto-merge on non-overlapping paths
```

```bash
# Prefer the canonical session helper from second-brain-core when available:
python3 path/to/second-brain-core/scripts/brain_session.py open \
  --repo "$BRAIN_REPO" \
  --bundle knowledge \
  --actor grok-bot/okf-graph-eng \
  --plugin okf-graph-eng \
  --host grok-bot

# JSON includes SECOND_BRAIN_ROOT for this session.
# Author concepts only inside that worktree.

python3 path/to/second-brain-core/scripts/brain_session.py close \
  --repo "$BRAIN_REPO" \
  --session <id>
```

Branch name: `brain/<sanitized-actor>/<session-id>`

## Why not only flock-on-main

Flock serializes writers on one machine. It fails across machines, long thinking sessions, and cloud Grok Bots. Worktree + PR is the multi-agent protocol. Flock remains optional *inside* one worktree.

## Read freshness

- Shared truth: pack or impact against `main` after a fast-forward pull.
- Session overlay: also see your own unmerged writes when packing with overlay support.
- Do not pack other agents' open branches by default.

## Conflicts

OKF concepts are one file per path. Two agents editing the same concept will conflict. That is useful. Prefer creating new nodes. Catalog indexes are regenerated-friendly; treat them as derived when possible.

## Grok Bot (cloud)

No local worktree required. Same branch naming via GitHub. Or mount a box and give each bot session its own worktree. Do not solve isolation by making the knowledge repo public.

## Public pack surface

This document never names a private remote. The knowledge root is a path the human already has, or `SECOND_BRAIN_ROOT` / the active session bundle.

## Related

- [second-brain-core docs/ISOLATION.md](https://github.com/SpillwaveSolutions/second-brain-core/blob/main/docs/ISOLATION.md) — canonical session helper
- [GROK_BOT.md](GROK_BOT.md) — Grok Bot binding for this plugin
- [LANG_CHAIN_DEEP_AGENTS.md](LANG_CHAIN_DEEP_AGENTS.md) — Deep Agents binding
