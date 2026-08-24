---
doc_type: guide
slug: worklog-spec
title: Worklog Spec
truth_state: current
wiki_key: spec
---

# Worklog Spec

This repository uses **WikiTicket SDD** (worklog) for visible WIP: plans, event-log tickets, generated roadmap, and wiki publish.

## Canonical specification

The full worklog specification lives upstream:

- Repo: [SpillwaveSolutions/wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd)  
- Spec: `docs/worklog-spec.md` in that repository  
- Plugin install: `worklog@worklog-marketplace` from the upstream marketplace  

This page is a **project-local pointer**, not a fork of the full spec.

## How okf-plugin uses worklog

| Artifact | Path |
|----------|------|
| Event log | `.work/todo.jsonl`, `.work/done.jsonl` |
| Config | `.work/config.yml` (GitHub Issues + github-wiki) |
| Roadmap | `docs/roadmap.md` (generated) |
| Plans | `docs/plans/` |
| CLI | `bin/worklog` |
| Publish ledger | `.work/published.json` |

### Day-to-day

```bash
bin/worklog list
bin/worklog add "Title" --level task --kind feature --body "what and why"
bin/worklog roadmap-render
bin/worklog ia-index
```

Commits should reference a worklog ULID or `#issue`. Prefer feature branches (hooks reject direct commits on `main`).

### Bridge to OKF

TicketLink concepts (a **PKC** noun) map worklog ULIDs / GitHub issues into the knowledge graph — see PKC `scripts/pkc_ticket_link.py`. `scripts/okf-ticket-link.py` in this repo is a stub as of 0.8.0.

## See also

- [[Roadmap]]  
- [[Index-Traceability]]  
- Upstream [graph engineering note](https://github.com/SpillwaveSolutions/wiki_ticket_sdd/blob/main/docs/graph-engineering.md)  
