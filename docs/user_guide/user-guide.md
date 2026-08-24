---
doc_type: guide
slug: user-guide
title: User Guide
truth_state: current
wiki_key: user-guide
---

# User Guide

Day-to-day use of **okf-graph-eng** on an OKF repository.

## Concepts

The plugin treats your OKF bundle as a **directed graph** of Markdown + YAML. It is a **read-path optimizer**, not a capture plugin.

Nouns this plugin owns:

| Noun | Role |
|------|------|
| `Catalog` | Directory index. Structural. Outbound-only pack walks skip flooding through hub catalogs. |
| `ContextPack` | Generated progressive-disclosure view: ranked, hop-capped, node-capped subgraph. |

Everything else (`AgentNode`, `TicketLink`, `Dataset`, `System`, …) is owned by PKC / SAC / DEKC / AGER. Unknown types fall back to `BaseConcept` for **read-only** envelope parsing (`type` + `title` only). That fallback does not authorize a write. `--strict` rejects unknown types.

Edges are absolute Markdown links (`[Label](/path/to/concept.md)`). Optional typed relations live in frontmatter:

```yaml
links:
  - target: /knowledge/plugin-architecture.md
    rel: depends_on
```

## How ContextPacks optimize reads

`okf-graph.py pack` (skill `okf-query`) is how a long-running agent should *read* an OKF tree. It is deliberately lossy.

1. **Outbound-only walk.** Catalog indexes that link to every child are hubs. Walking them undirected dumps the whole bundle. `--undirected` exists for neighborhood exploration. Prefer `impact` for “what would break?”.
2. **Hop cap (default 2).** Two hops is usually entry → collaborator → evidence. Hop 3 is a debug knob. Unlimited closure is `impact`, not `pack`.
3. **Node cap (default 20).** Ranked overflow goes in `## Excluded (available on request)`.
4. **Trust-first ranking.** Entry first, then verified, then schema-declared high-impact (`x-impact: high` on the owning plugin), then title. Isolated, this plugin has no high-impact types.
5. **Read order ≠ inclusion order.** The model sees the question first, then dangerous neighbors, then supporting evidence.
6. **Criticality for impact (not pack).** `x-impact: high` + unverified → **critical**. `medium` + unverified → **high**. Unset/low never escalates.

Sibling PKC / DEKC / AGER packs wrap this graph with a **fail-closed token budget** (default ¼ of `SECOND_BRAIN_WINDOW_TOKENS`). Use this plugin’s `pack` for a portable subgraph. Use the domain pack when you must fit a model window.

## Common workflows

### Scaffold a bundle

- Slash: `/okf-init`
- Or ask to initialize an OKF graph-engineering bundle (skill: `okf-init-graph`)

Default tree: `.okf/` with `catalogs/`, `knowledge/`, `packs/`, plus `index.md` and `log.md`. Do **not** seed AgentNode / Workflow / TicketLink here — those belong to AGER and PKC.

### Author concepts

Use skill `okf-author` (or `/okf-author`) for Catalog, ContextPack, and envelope files. Every concept needs at least `type`, `title`, `description`, `timestamp`. Domain nouns: use the owning plugin.

### Impact before structure changes

```bash
python3 scripts/okf-graph.py impact <bundle> <concept>
# or /okf-impact
```

Prefer this before renaming or splitting high-degree concepts.

Criticality comes from the owning plugin’s schema `x-impact` field, not a hardcoded type list in this repo. A concept that is not `verified` escalates one level: `medium` → `high`, `high` → `critical`. `low` never escalates.

`<concept>` is a bundle-relative path, a stem, or a title. If a shorthand
matches several concepts the command lists every candidate and exits `1` instead
of guessing:

```console
$ python3 scripts/okf-graph.py impact sample-okf index
{"error": "ambiguous concept: index", "candidates": ["knowledge/index.md", "index.md", ...]}
```

Pass the full path to disambiguate.

### Progressive disclosure packs

Default: **2 hops**, ~**20 nodes**, following **outbound** edges only. Add
`--undirected` to walk inbound edges too — useful for "what would break", but it
floods easily through hub index pages.

```bash
python3 scripts/okf-graph.py pack <bundle> <concept> --hops 2 --max-nodes 20
python3 scripts/okf-graph.py subgraph <bundle> <concept> --hops 2
# or /okf-query
```

### Visualize

```bash
python3 scripts/okf-graph.py graph <bundle>                          # mermaid (default)
python3 scripts/okf-graph.py graph <bundle> --focus <concept> --hops 2
python3 scripts/okf-graph.py graph <bundle> --format html > graph.html
python3 scripts/okf-graph.py graph <bundle> --format json
# or /okf-visualize
```

Whole-bundle by default, including isolated concepts. `--focus` scopes to one
concept's neighborhood. The `html` output is a single self-contained file — no
CDN, no network fetches — so it opens straight from disk.

### Validate

```bash
python3 scripts/okf-graph.py validate <bundle>
python3 scripts/okf-graph.py validate <bundle> --strict   # warnings also exit non-zero
# or /okf-validate
```

Default is lenient. Only **errors** — a broken link, a missing root `index.md` —
exit non-zero. **Warnings** print but still exit `0`:

- missing `type` or `title`
- `link outside bundle → …` — a link whose target resolves above the bundle
  root, usually a mistyped `../../`. It is not an edge, so it used to vanish
  silently; it is now reported
- an unverified high-impact concept (from sibling `x-impact`, not a core type list)

Use `--strict` to make warnings gate CI. Every skill and the post-edit hook call
the lenient form.

The bundle's root `index.md` and `log.md` carry no `type`/`title` of their own
and are exempt from those two warnings — but **their links are checked like
everyone else's**. Through v0.3.1 the exemption skipped those files entirely, so
the entry point was the one file where a broken link went unreported. A broken
link there is now an error; one pointing outside the bundle is a warning, which
`--strict` gates. The metadata exemption is unchanged: any `index.md` is excused
at any depth, but only the *root* `log.md` is structural — a nested `sub/log.md`
still wants a `type` and `title`.

### Maintain

```bash
python3 scripts/okf-graph.py orphans <bundle>    # concepts with no edges either way
python3 scripts/okf-graph.py edges <bundle> --rel depends_on
# or /okf-maintain
```

### Validate on save

The post-edit hook (`apply_patch|Write|Edit|MultiEdit`) runs
`scripts/okf-hook-validate.sh` on every Markdown edit. The script walks up from
the edited file looking for a bundle root — the nearest ancestor with an
`index.md` containing `okf_version`, or a `.okf/` directory — and **validates**
that bundle. This pack does not curate. A bundle rooted anywhere qualifies,
not just `.okf/`, `knowledge/` or `sample-okf/`.

Edit a Markdown file that is in no bundle and the hook does nothing and says
nothing: there is no fallback to some other bundle in the repo. Inside a
bundle a failed validate is fail-closed (non-zero).

### Tickets (WikiTicket / worklog)

This repo is managed with [WikiTicket SDD](https://github.com/SpillwaveSolutions/wiki_ticket_sdd). Map work items into OKF with **PKC**:

```bash
bin/worklog fold | python3 path/to/project-knowledge-capture/scripts/pkc_ticket_link.py emit --bundle knowledge --open-only
```

`scripts/okf-ticket-link.py` in this repo is a stub (moved in 0.8.0).

## Sample bundle

`sample-okf/` is a self-describing **Catalog + ContextPack** bundle about this engine. It is not an AGER graph.

## See also

- [[CLI-Reference]] — scripts and flags
- [[Plugin-Guide]] — install on Claude Code / Grok Build
- [[Roadmap]] — generated from the worklog
