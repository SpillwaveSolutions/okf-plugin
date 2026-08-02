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

The plugin treats your OKF bundle as a **dual graph**:

1. **Knowledge graph** — datasets, metrics, runbooks, APIs, references  
2. **Agent / harness graph** — `AgentNode`, `Workflow`, `SharedState`, `DecisionRecord`, `ToolCapability`, `TicketLink`

Edges are absolute Markdown links (`[Label](/path/to/concept.md)`). Optional typed relations live in frontmatter:

```yaml
links:
  - target: /agents/writer.md
    rel: routes_to
```

## Common workflows

### Scaffold a bundle

- Slash: `/okf-init`  
- Or ask to initialize an OKF graph-engineering bundle (skill: `okf-init-graph`)

Default tree: `.okf/` with `agents/`, `workflows/`, `knowledge/`, `decisions/`, `shared/`, `tickets/`, plus `index.md` and `log.md`.

### Author concepts

Use skill `okf-author` (or `/okf-author`). Every concept needs at least `type`, `title`, `description`, `timestamp`.

### Impact before structure changes

```bash
python3 scripts/okf-graph.py impact <bundle> <concept>
# or /okf-impact
```

Prefer this before renaming or splitting high-degree agents, workflows, or shared state.

Each affected concept carries a **criticality** tier derived from its type —
`AgentNode`, `Workflow`, `Harness`, `SharedState` are high; `Dataset`, `Table`,
`Metric`, `API`, `ToolCapability` are medium; everything else is low. A concept
that is not `verified` escalates one level: `medium` → `high`, `high` →
`critical`. `low` never escalates — an unverified `Reference` is not news.

`<concept>` is a bundle-relative path, a stem, or a title. If a shorthand
matches several concepts the command lists every candidate and exits `1` instead
of guessing:

```console
$ python3 scripts/okf-graph.py impact sample-okf index
{"error": "ambiguous concept: index", "candidates": ["agents/index.md", "decisions/index.md", "index.md", ...]}
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
- an unverified high-impact concept
- a `TicketLink` with no `external_id`/`worklog_id`

Use `--strict` to make warnings gate CI. Every skill and the post-edit hook call
the lenient form.

### Maintain

```bash
python3 scripts/okf-graph.py orphans <bundle>    # concepts with no edges either way
python3 scripts/okf-graph.py edges <bundle> --rel routes_to
# or /okf-maintain
```

### Curation on save

The post-edit hook (`Write|Edit|MultiEdit`) runs `scripts/okf-curate.sh` on
every Markdown edit. The script walks up from the edited file looking for a
bundle root — the nearest ancestor with an `index.md` containing `okf_version`,
or a `.okf/` directory — and validates that bundle. A bundle rooted anywhere
qualifies, not just `.okf/`, `knowledge/` or `sample-okf/`.

Edit a Markdown file that is in no bundle and the hook does nothing and says
nothing: there is no fallback to some other bundle in the repo. It reports; it
never blocks the edit.

### Tickets (WikiTicket / worklog)

This repo is managed with [WikiTicket SDD](https://github.com/SpillwaveSolutions/wiki_ticket_sdd). Map work items into OKF:

```bash
bin/worklog fold | python3 scripts/okf-ticket-link.py emit --bundle sample-okf --open-only
```

## Sample bundle

`sample-okf/` models **this plugin** as both knowledge and agent graph. Use it as a template and for demos.

## See also

- [[CLI-Reference]] — scripts and flags  
- [[Plugin-Guide]] — install on Claude Code / Grok Build  
- [[Roadmap]] — generated from the worklog  
