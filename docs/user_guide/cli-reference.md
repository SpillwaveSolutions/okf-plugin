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
python3 scripts/okf-graph.py pack <bundle> <concept> [--hops 2] [--max-nodes 20] [--undirected]
python3 scripts/okf-graph.py edges <bundle> [--from PATH] [--rel REL]
python3 scripts/okf-graph.py graph <bundle> [--format mermaid|json|html] [--focus PATH] [--hops 2]
python3 scripts/okf-graph.py validate <bundle> [--strict]
python3 scripts/okf-graph.py orphans <bundle>
```

| Command | Output |
|---------|--------|
| `impact` | Inbound/outbound closures, typed `direct_edges`, suggested update order (JSON) |
| `backlinks` | Concepts linking *to* the target, with their rels (JSON) |
| `subgraph` | Undirected N-hop neighborhood: nodes + edges (JSON) |
| `pack` | Progressive disclosure pack; JSON includes ready-to-paste `markdown`. Outbound-only by default — `--undirected` also walks inbound edges, which can flood via hub indexes |
| `edges` | Edge list; filter by `--rel routes_to` etc. |
| `graph` | Whole bundle or `--focus` neighborhood. `--format json` prints JSON; `mermaid` (default) and `html` print the artifact itself |
| `validate` | Conformance + broken links + unverified high-impact (JSON). `--strict` also exits non-zero on warnings — used by CI |
| `orphans` | Concepts with no inbound or outbound edges (JSON) |

The `html` view is fully self-contained: Mermaid source plus concept/edge
tables, no CDN or network fetches.

```bash
python3 scripts/okf-graph.py graph sample-okf --focus agents/graph-engineer.md --hops 1
python3 scripts/okf-graph.py graph sample-okf --format html > docs/okf-graph.html
```

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

Post-edit hook helper, wired to `Write|Edit|MultiEdit` in `hooks/hooks.json`.
Takes a file path as `$1`, or reads the `PostToolUse` payload as JSON on stdin
(`.tool_input.file_path`) — which is how Claude Code actually delivers it.

Acts only on OKF-ish paths (`.okf/`, `knowledge/`, `sample-okf/`), resolves the
nearest bundle root, then runs `okf validate` (plus `okf lint` if available),
`okfcli validate`, or — with no external CLI — `okf-graph.py validate` from this
repo. Never fails the edit: every branch exits `0`.

```bash
scripts/okf-curate.sh sample-okf/knowledge/tool-okf-graph-py.md
```

## `scripts/substack_okf.py`

Maintainer-only integration harness, not part of the plugin's user-facing
surface. It pulls a Substack archive, classifies posts, emits an OKF bundle into
the gitignored `integration/` tree, and verifies it with `okf-graph.py`. Useful
for exercising the engine against a real corpus instead of `sample-okf`; nothing
in the installed plugin calls it. `python3 scripts/substack_okf.py --help` for
the subcommands.

## `tests/test_okf_graph.py`

```bash
python3 tests/test_okf_graph.py -q
```

Graph engine coverage — plain asserts, no test framework, no dependencies. Runs
in CI (alongside `validate sample-okf --strict`) and as a guarded pre-commit
check. Includes tripwires on `sample-okf`'s concept and edge counts and on
version consistency across the four manifests, so bumping a version in one place
fails here.

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
