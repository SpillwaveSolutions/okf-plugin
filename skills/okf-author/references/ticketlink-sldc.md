# TicketLink ↔ WikiTicket SDD (worklog)

`TicketLink` concepts bridge the OKF dual graph to external SLDC systems.
This plugin standardizes on **WikiTicket SDD / worklog** plus optional GitHub Issues.

## Frontmatter fields

```yaml
type: TicketLink
title: ...
description: ...
status: open | in_progress | blocked | done | cancelled
external_id: "3"                 # issue number or tracker key
external_system: github | worklog | jira | other
worklog_id: 01KYQZ4PAMZCM9N56K8F3034F2   # 26-char ULID when known
verified: true
links:
  - target: /workflows/plugin-maintenance.md
    rel: tracks
```

## Mapping rules

| Worklog field | TicketLink field |
|---------------|------------------|
| item ULID | `worklog_id` |
| `external.key` (GitHub) | `external_id` + `external_system: github` |
| `status` todo/in_progress/done… | `status` open/in_progress/done… |
| `title` / `body` | `title` / description body |

## Generate from worklog

```bash
# Open items → TicketLink files under the bundle
bin/worklog fold | python3 scripts/okf-ticket-link.py emit \
  --bundle sample-okf --open-only

# Single ULID
python3 scripts/okf-ticket-link.py emit --bundle .okf \
  --id 01KYQZ4PAMZCM9N56K8F3034F2 \
  --title "Adopt WikiTicket" \
  --github-issue 1 \
  --maps-to /knowledge/plugin-architecture.md
```

## Agent workflow

1. Prefer worklog as source of truth for status.
2. After `worklog sync`, refresh TicketLinks if the OKF graph must show ticket nodes.
3. Use `rel: tracks` from tickets to workflows/agents they drive.
4. Use `rel: implements` from concepts back to the decision/ticket that authorized them.

## Compatibility

- Does **not** require worklog to validate OKF bundles.
- Markdown-only readers ignore `worklog_id` safely.
- Wicked Ticket / worklog CLIs remain optional; helpers degrade gracefully.
