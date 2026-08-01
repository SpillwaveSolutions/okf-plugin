# Changelog

Notable changes to **okf-graph-eng**. Newest first. Released sections are
frozen — corrections go in the next release's notes.

## 0.3.0 — 2026-08-01

Bug-fix and hardening release. Three defects in shipped v0.2.0 code, the first
automated coverage of the graph engine, and a real backing for the
`okf-visualize` skill.

### Fixed

- **The post-edit hook had never run, in any install.** `hooks/hooks.json`
  passed `"$FILE_PATH"`, but Claude Code delivers the `PostToolUse` payload as
  JSON on stdin — there is no such environment variable — so `okf-curate.sh`
  bound an empty string and exited at its first guard on every edit. It now
  reads `.tool_input.file_path` from stdin, and the matcher covers `MultiEdit`,
  which bypassed curation entirely.
- **`parse_frontmatter` silently dropped standard YAML block sequences.**
  `tags:` followed by `- item` lines returned `''`, which the `isinstance`
  guard in `load_bundle` then converted to `[]` with no warning. Every
  generator in this repo emits inline `tags: [a, b]`, so `sample-okf` looked
  clean; the bug only ever affected user-authored bundles.
- **Mermaid node IDs collided.** They derived from the path stem, so all seven
  `index.md` files in `sample-okf` collapsed into a single node and
  `agents/foo.md` merged with `docs/foo.md`. IDs now come from the full
  relative path.
- **Isolated concepts vanished from whole-bundle diagrams.** The emitter only
  declared nodes it saw on an edge, so unlinked concepts appeared in
  `--format json` but not in the rendered graph.
- `okf-curate.sh`'s fallback no longer hand-rolls grep link checks; it calls
  this repo's own `okf-graph.py validate`. That also removes a `realpath -m`
  call, absent from stock macOS without coreutils.
- Command files reference their skills via `${CLAUDE_PLUGIN_ROOT}` instead of
  bare relative paths, which do not resolve from a consuming project.
- Ticket sync state no longer maps work items to issue numbers from the
  pre-org-move repository. GitHub shares one number space between issues and
  pull requests, so those keys resolved to this repo's PRs.

### Added

- **`graph` subcommand** — `okf-graph.py graph <bundle> [--format
  mermaid|json|html] [--focus <concept>] [--hops N]`, backing the
  `okf-visualize` skill, which previously instructed the model to crawl
  concepts by hand. The HTML output is a single self-contained file with no
  CDN or network references.
- **`validate --strict`** — exits non-zero on warnings so CI can gate. The
  default stays lenient; the skills call `validate` and expect `0` on warnings.
- **`tests/test_okf_graph.py`** — 16 cases, plain asserts, no framework. Run in
  CI and as a guarded pre-commit check. Includes tripwires for `sample-okf`'s
  concept and edge counts and for version consistency across the four
  manifests.
- **`commands/okf-visualize.md`** and **`commands/okf-maintain.md`** — all
  seven skills now have a slash command, up from five.

### Changed

- CI runs the graph engine test suite and `validate sample-okf --strict`. It
  previously validated worklog log invariants only and never invoked the graph
  engine.
- `docs/user_guide/cli-reference.md` documents all eight subcommands;
  `backlinks`, `subgraph` and `orphans` had no entries.
- Both host guides now tell agents to verify their base commit before building
  in an isolated worktree.

## 0.2.0 — 2026-07-31

First tagged release. Impact analysis, progressive-disclosure packs, typed
edges, the TicketLink/worklog bridge, seven skills with five commands, the
self-describing `sample-okf` dual graph, and a local Substack→OKF integration
runner. Full notes:
<https://github.com/SpillwaveSolutions/okf-plugin/releases/tag/v0.2.0>
