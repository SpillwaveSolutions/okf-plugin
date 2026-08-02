---
date: 2026-08-01
slug: v030-plumbing-and-tests
title: v0.3.0 — fix the plumbing, add the net
epic: 01KYZFDBAYGEG2FKWRADN46Z9W
items: [01KYZFDBAY0AX03XQ6SAT6SXJW, 01KYZFDBAY2VPBHBNXW7E4ZKHF, 01KYZFDBAZ0T4W5TZYVXSBXADV, 01KYZFDBAZ62YTTMN7SRGD2QKC, 01KYZFDBAZ6G090EZ3FSS0FXS9, 01KYZFDBAZW0F3RCN8P9J1R29A]
---

---
date: 2026-08-01
slug: v030-plumbing-and-tests
title: v0.3.0 — fix the plumbing, add the net
---

# v0.3.0 — fix the plumbing, add the net

## Why

All v0.2.0 work is closed and the roadmap is empty. An audit of the shipped
plugin surface found three real defects plus zero automated coverage of
`scripts/okf-graph.py`, which is the thing the plugin exists to do. Fix what is
broken, then leave a check behind so it stays fixed.

## Context

- Repo: https://github.com/SpillwaveSolutions/okf-plugin
- Released: v0.2.0 (only tag); v0.2.1 exists in generated docs but was never cut
- Hosts: Claude Code + Grok Build

Verified defects:

1. The plugin's only hook has never run. `hooks/hooks.json` passed `"$FILE_PATH"`,
   but Claude Code delivers the PostToolUse payload as JSON on stdin, so
   `okf-curate.sh` bound an empty string and exited immediately on every edit.
2. `parse_frontmatter` silently dropped standard YAML: `tags:` followed by
   `- item` lines returned `''`, coerced to `[]` with no warning. The repo's own
   generators emit inline lists, so this was invisible in-repo and hit only
   user-authored bundles.
3. Mermaid node IDs came from the path stem, so all seven `index.md` files in
   sample-okf collapsed into one node and `agents/foo.md` merged with
   `docs/foo.md`.
4. No tests existed anywhere, and CI never invoked the graph engine or sample-okf.

## Tasks

- [x] (P0) Fix the no-op post-edit hook and curate fallback
  Read the file path from the PostToolUse stdin JSON instead of a nonexistent
  $FILE_PATH, widen the matcher to include MultiEdit, and replace the grep-based
  fallback with the repo's own okf-graph.py validate (which also deletes a
  realpath -m call that is broken on stock macOS).

- [x] (P0) Fix okf-graph.py block-sequence YAML, Mermaid IDs, and add validate --strict
  Parse standard YAML block sequences in frontmatter; derive Mermaid node IDs
  from the full relative path via a shared mermaid_id/render_mermaid helper; add
  a --strict flag so CI can gate on warnings while the skills keep the lenient
  default.

- [x] (P0) Add tests/test_okf_graph.py and wire it into CI and pre-commit
  Plain-assert suite covering frontmatter parsing, link normalization, edge
  merging, Mermaid ID uniqueness, sample-okf validity, and version consistency
  across the four manifests. Runs in CI and as a guarded pre-commit check.

- [x] (P1) Qualify intra-plugin paths with CLAUDE_PLUGIN_ROOT
  Command files referenced skills by bare relative path, which does not resolve
  in a consuming project. Annotate repo-local bin/worklog references honestly
  rather than pretending they resolve from the plugin root.

- [x] (P2) Add graph subcommand and the two missing slash commands
  Back the okf-visualize skill with a real graph subcommand (mermaid/json/html)
  built on the shared emitter, and add commands for okf-visualize and
  okf-maintain so all seven skills have a command. Non-blocking for the release.

- [x] (P2) Release chore — bump to 0.3.0 across the four manifests and README
  The version lives in four places and drifts silently; the new test asserts
  they agree.
