---
date: 2026-08-02
slug: v031-correctness-and-traceability
title: v0.3.1 — correctness cleanup and traceability backfill
epic: 01KZ2CAAT5G2ND3RAF4TAXR5B9
items: [01KZ2CAAT56M9V49211G7NVBYV, 01KZ2CAAT5JS108XWJ4T00B3V1, 01KZ2CAAT5C7PGNP8QDXGJJB9E, 01KZ2CAAT6XQ5WCT70AS6QQNTY, 01KZ2CAAT6Z9Q09MMFFWD7XH1R, 01KZ2CAAT64CERBRZMR7AJZ5XW, 01KZ2CAAT6YNARXMA7HMNM1AZ1, 01KZ2CAAT61CM8G0N25MPDEHRQ, 01KZ2CAAT66ZFTBX9NQ7Z0AKKX]
merged_in: b61871e5a1d699daa56683f2309ebe6c1f003ff3
---

---
date: 2026-08-02
slug: v031-correctness-and-traceability
title: v0.3.1 — correctness cleanup and traceability backfill
---

# v0.3.1 — correctness cleanup and traceability backfill

## Why

v0.3.0 fixed the defects that stopped the plugin working at all. This release
clears the ones found while doing that: logic that is dead, silent, or wrong in
ways that do not crash, plus the public traceability gap left by the org move.

None of these break a run today. All of them make the graph engine quietly
report something other than the truth, which for a tool whose whole job is
"tell me what depends on what" is the failure mode that matters most.

## Context

- Repo: https://github.com/SpillwaveSolutions/okf-plugin
- Released: v0.3.0 (2026-08-01), tag on 6bf5d65
- Work is grouped into waves; each wave runs in its own git worktree so the
  waves can proceed in parallel without touching each other's files.

Wave 1 owns `scripts/okf-graph.py` and `tests/`. Wave 2 owns
`scripts/okf-curate.sh` and `hooks/`. Wave 3 owns `docs/`. Wave 4 is sync only
and touches no source.

## Tasks

- [ ] (P1) Escalate unverified medium-impact concepts in criticality_of
  The unverified branch reassigns medium to itself, so a medium-impact concept
  never escalates no matter its state. Only high ever becomes critical, which
  makes the medium tier decorative in every impact report.

- [ ] (P2) Make merge_edges precedence match what it documents
  The third clause of the precedence test is true for every frontmatter edge,
  so the two clauses before it can never decide anything. Frontmatter always
  wins regardless of the stated enrich-or-override intent. Either the code or
  the docstring is wrong; decide which and make them agree.

- [ ] (P2) Report ambiguous concept lookups instead of guessing
  Concept resolution accepts any path ending with the query, and returns
  whichever match comes first in iteration order. Two files sharing a suffix
  resolve to an arbitrary one of them with no warning, so impact and pack can
  silently answer about the wrong concept.

- [ ] (P2) Flag links that point outside the bundle
  A link resolving outside the bundle root is dropped before validation ever
  sees it, so a mistyped path is invisible rather than broken. Broken in-bundle
  links are already errors; an out-of-bundle target should be reported too.

- [ ] (P3) Skip dot-directories when loading a bundle
  Bundle loading skips dot-files but walks dot-directories, so pointing it at a
  repo root pulls the work log and other internal trees in as concepts.

- [ ] (P3) Build the undirected adjacency once in subgraph
  Subgraph walks the edge set twice to build one adjacency map, which is
  harmless only because the result is deduped immediately after. Collapse it.

- [ ] (P2) Curate the bundle wherever it is rooted
  The post-edit hook filters on three hard-coded path fragments, so a bundle
  rooted anywhere else is skipped entirely. This mattered less when the hook
  never fired; now that it does, the filter is the thing deciding whether
  curation happens at all.

- [ ] (P1) Correct the plan page published to the wiki
  The adoption plan shows seven unchecked tasks that the work log records as
  closed, and points at the pre-move repository. It is published to the wiki,
  so this is the public view of the project's own work tracking contradicting
  the tracker.

- [ ] (P2) Backfill external tickets for closed work
  Every closed item lacks an external ticket: the originals live in the
  pre-move repository and their keys were cleared in v0.3.0 because they
  collided with this repo's pull request numbers. Push the work log to the
  current tracker so the strict traceability check can pass.
