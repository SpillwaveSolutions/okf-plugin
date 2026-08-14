# Changelog

Notable changes to **okf-graph-eng**. Newest first. Released sections are
frozen — corrections go in the next release's notes.

## 0.6.0 — 2026-08-14

### Added

- **First-class work items:** `Epic`, `Story`, `Task`, `Subtask`, `Bug` are
  concept types (catalogs `epics/`, `stories/`, `tasks/`, `subtasks/`, `bugs/`).
  `TicketLink` remains valid for existing files.
- **`Branch` concept** (`branches/`). Prefer `on_branch` links from Bug/CodeChange
  over a bare `branch:` string.
- **Per-type recommended fields** via `x-recommended` / `x-recommended-any` /
  `x-recommended-link-rels`. Soft (warn) by default; `--strict` promotes them
  to errors. BaseConcept required fields stay `type` + `title` only.

## 0.5.0 — 2026-08-13


### Added

- **Shared concept schema pack** at `schemas/okf-concepts/`. Canonical
  `BaseConcept` (required: `type` + `title` only; `additionalProperties: true`)
  plus TicketLink, Feature, DecisionRecord, Project, Catalog, ContextPack.
- `scripts/okf_schema.py` — stdlib subset validator. Soft by default. Merges
  sibling plugin schema directories so a mixed second brain validates as one.
- `okf-graph.py schemas` lists the merged registry.
- `okf-graph.py validate` now runs schema checks (unknown types fall back to
  BaseConcept as info; missing recommended fields are warnings).
- `truth_state` union: `current | snapshot | superseded | archived | historical | proposed`.
- TicketLink `kind=bug` refinement: warn unless the ticket links to a
  Module/Package/Release/CodeChange or sets `branch`. Epic/story/task/bug
  remain WikiTicket axes, not new concept types.
- Catalog ownership map in `registry.json` so plugins do not rewrite foreign catalogs.

## 0.4.1 — 2026-08-10

### Fixed

- **`KNOWN_RELS` only knew 11 of the ~170 typed relations the four sibling
  capture plugins declare, so `validate` buried real typos in noise on any
  bundle built with them.** Each of `okf-agent-graph` (AGER),
  `project-knowledge-capture` (PKC), `system-architecture-capture` (SAC),
  and `data-engineering-knowledge-capture` (DEKC) declares its own
  typed-edge vocabulary — in `docs/AGER_SPEC.md` / `docs/typed-edges.md`,
  cross-checked against each plugin's own `DEFAULT_RELATIONS` constant and,
  for SAC, its `schemas/types.json` relation registry (the one
  `sac_validate.py` actually loads at runtime, which turned out to be more
  complete than SAC's own prose doc — it was missing the entire C4 vocabulary
  and 6 code-structure relations). `KNOWN_RELS` is now `CORE_RELS |
  AGER_RELS | PKC_RELS | SAC_RELS | DEKC_RELS` (11 + 26 + 15 + 84 + 38 = 161
  after de-duplication), each a named, source-cited `frozenset` instead of
  one flat literal. On the field-ops-knowledge-base project's two live
  bundles this took `non-standard rel (allowed but uncommon)` info lines
  from 8 → 0 (`knowledge/`, mostly PKC's `originates_from`) and 14 → 0
  (`agent-graph/`, AGER — already fixed by the first half of this change).
  The drift-guard test now parses each installed sibling plugin's live
  vocabulary source at test time (`test_known_rels_covers_sibling_plugin_vocabularies`)
  instead of comparing two hardcoded literals, so a future plugin release
  adding a relation fails the test instead of silently degrading back into
  info-line noise; it falls back to a subset sanity check when the sibling
  plugins aren't installed (e.g. in CI). (#51)

## 0.4.0 — 2026-08-10

### Fixed

- **A bracketed link label dropped the edge, and nothing reported it.**
  `LINK_RE`'s label class was `[^\]]+`, which stops at the first `]`, so
  `- [[AREA NAME]](/requirements/area-name.md)` matched nothing. The result was
  a *missing* edge rather than a broken one, and `validate` only reports broken
  edges — the `orphan` check needs a concept to have neither inbound nor
  outbound links, so any concept with one outbound link lost its catalog
  backlink in silence. Bracketed titles are routine in exported wiki content
  (`[AREA]` prefixes, `[DEPRECATED]` suffixes), and the capture plugins
  interpolate titles into catalog links unescaped.

  The label alternation now keeps `[^\]]` — the whole of the previous pattern's
  language — and adds balanced `[...]` pairs, tried first. Keeping the old
  branch is what makes it a superset: a label may legitimately end in a
  backslash, which an escape-aware branch alone swallows. Two earlier drafts of
  this fix regressed exactly that way, and on `*` vs `+` letting the empty label
  start matching. Verified: 0 losses across 20k generated links, identical edge
  sets on `sample-okf`, empty label still unmatched, no backtracking blowup.
  (#48)

### Added

- **`released_in` is now a known relation.** A bundle that models releases
  previously emitted one `non-standard rel 'released_in' (allowed but uncommon)`
  info per edge — one per shipped work item. The relation always worked (the
  guard passes unknown non-empty rels through unchanged); only the vocabulary
  was missing, and the noise made piping `validate` through a severity filter a
  habit, which is how a real warning gets missed.

  The repo already models a release axis on the worklog side: `milestone` is a
  core work-item field and `bin/ia_graph.py` turns it into
  `edge(key, "targets", "release/" + milestone)`. This gives bundles a way to
  express the same idea. Whether the two should be unified is left open. The
  relation list is duplicated in three prose files, so those are updated too and
  a test now pins them together. (#49)

## 0.3.2 — 2026-08-03

### Fixed

- **The bundle's root `index.md` and `log.md` skipped every link check.** The
  exemption meant to excuse two structural files from `type`/`title` warnings
  sat at the top of the validation loop as a `continue`, so it also skipped
  broken links, out-of-bundle links, non-standard rels, and TicketLink
  hygiene — leaving the entry point, the most linked-from file a bundle has,
  as the one place a broken link went unreported. The two metadata checks are
  now excused individually and everything else applies to every file.

## 0.3.1 — 2026-08-02

Correctness release. v0.3.0 fixed the defects that stopped the plugin working
at all; this one clears the defects found while doing that — logic that was
dead, silent, or wrong without ever crashing. For a tool whose whole job is
"tell me what depends on what", quietly reporting something other than the
truth is the failure mode that matters most.

### Fixed

- **Medium-impact concepts never escalated.** The unverified branch of
  `criticality_of` assigned the tier to itself, so only `high` could ever
  become `critical` and the entire medium tier was decorative. Unverified
  concepts now escalate one level: `medium` → `high`, `high` → `critical`.
  `low` still never escalates.
- **Ambiguous concept lookups guessed silently.** A query matching several
  concepts by path suffix or stem resolved to whichever came first in
  iteration order, so `impact` and `pack` could answer about the wrong
  concept without saying so. Lookup now resolves in tiers — exact path, then
  stem or title, then suffix — and an ambiguous tier returns an error listing
  every candidate. Full paths, which the skills pass, are unaffected.
- **Links pointing outside the bundle vanished.** A target resolving outside
  the bundle root was dropped before validation ever saw it, so a mistyped
  `../../` was invisible rather than broken. `validate` now reports it as a
  warning; the default exit code is unchanged and `--strict` gates it.
- **Bundle loading walked dot-directories.** Only dot-*files* were skipped, so
  pointing the engine at a repo root pulled `.git/`, `.work/` and `.claude/`
  in as concepts. Matched on bundle-relative parts, so a bundle that itself
  lives under a dot-directory still loads.
- **Post-edit curation only recognised three hard-coded paths.** A bundle
  rooted anywhere other than `.okf/`, `knowledge/` or `sample-okf/` was
  skipped entirely — which mattered from v0.3.0 onward, when the hook started
  firing at all. Bundle membership is now decided by the walk-up test that was
  already in the script; the cheap pre-check only rejects non-Markdown. The
  repo-level `.okf/` and `sample-okf/` fallbacks are gone, so a file outside
  any bundle is no longer curated against an unrelated one.
- **The plan pages published to the wiki contradicted the tracker.** Two
  completed plans showed unchecked task boxes, and one linked to the
  pre-move repository. Prose describing what a task did at the time was left
  frozen; only the status mirrors and the stale link changed.
- **Ticket sync still targeted the pre-move repository.** v0.3.0 cleared the
  adapter's cache, but the event log carried its own external keys — and
  since GitHub shares one number space between issues and pull requests, a
  push would have rewritten this repo's pull requests 1 through 6. Unlinked
  through the supported command rather than editing the log.

### Changed

- `merge_edges` no longer carries a three-clause precedence guard in which
  every clause was true for every frontmatter edge. The behaviour was already
  correct — markdown links are always `links_to`, so a frontmatter edge is
  always at least as specific — and the condition only made it look
  conditional.
- `subgraph` builds its undirected adjacency in one pass instead of two.
  Output is byte-identical.

### Added

- `tests/test_okf_curate.sh` — the repo's first shell test, covering bundle
  detection, the stdin payload, and the argument form.
- The graph engine suite grows from 16 cases to 24.

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
