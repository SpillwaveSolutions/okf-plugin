---
doc_type: guide
slug: cli-reference
title: CLI Reference
truth_state: current
wiki_key: cli-reference
---

# CLI Reference

Deterministic tools used by okf-graph-eng skills and the GraphEngineer agent.

## `scripts/okf-graph.py`

Fallback when `okf` / `okfcli` is not installed. Operates on an OKF bundle directory (e.g. `sample-okf`, `.okf`).

```bash
python3 scripts/okf-graph.py impact <bundle> <concept>
python3 scripts/okf-graph.py backlinks <bundle> <concept>
python3 scripts/okf-graph.py subgraph <bundle> <concept> [--hops N]
python3 scripts/okf-graph.py pack <bundle> <concept> [--hops 2] [--max-nodes 20]
python3 scripts/okf-graph.py edges <bundle> [--from PATH] [--rel REL]
python3 scripts/okf-graph.py validate <bundle>
python3 scripts/okf-graph.py orphans <bundle>
```

| Command | Output |
|---------|--------|
| `impact` | Inbound/outbound closures, typed `direct_edges`, suggested update order (JSON) |
| `pack` | Progressive disclosure pack; JSON includes ready-to-paste `markdown` |
| `edges` | Edge list; filter by `--rel routes_to` etc. |
| `validate` | Conformance + broken links + unverified high-impact (JSON) |

Concepts resolve by path, stem, or title. Typed edges come from Markdown links plus optional frontmatter `links[].rel`.

## `scripts/okf-ticket-link.py`

Emit OKF `TicketLink` concepts from WikiTicket worklog items.

```bash
bin/worklog fold | python3 scripts/okf-ticket-link.py emit --bundle <bundle> --open-only
python3 scripts/okf-ticket-link.py emit --bundle <bundle> --id <ULID> --title "..." --github-issue N
python3 scripts/okf-ticket-link.py emit --bundle <bundle> --dry-run   # preview paths
```

Default GitHub project: `SpillwaveSolutions/okf-plugin`.

## `scripts/okf-curate.sh`

Post-edit hook helper: validates OKF paths after Write/Edit when `okf` is available; otherwise lightweight frontmatter/link checks.

## `bin/worklog` (WikiTicket SDD)

Repo project management (not OKF-specific):

```bash
bin/worklog list
bin/worklog add "Title" --level task --kind feature --body "what and why"
bin/worklog update <ulid> --status in_progress
bin/worklog close <ulid> --status done --resolution "..."
bin/worklog roadmap-render
bin/worklog ia-index
bin/worklog sync          # needs WORKLOG_TICKET_* / adapters/github
```

See [[Worklog-Spec]] and upstream [wiki_ticket_sdd](https://github.com/SpillwaveSolutions/wiki_ticket_sdd).

## Prefer official OKF CLI when present

```bash
okf validate <bundle>
okf graph <bundle>
# okfcli variants if installed as okfcli
```
