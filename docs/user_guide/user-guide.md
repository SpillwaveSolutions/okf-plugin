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

### Progressive disclosure packs

Default: **2 hops**, ~**20 nodes**.

```bash
python3 scripts/okf-graph.py pack <bundle> <concept> --hops 2 --max-nodes 20
```

### Validate

```bash
python3 scripts/okf-graph.py validate <bundle>
# or /okf-validate
```

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
