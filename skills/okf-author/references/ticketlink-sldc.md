# TicketLink (moved to PKC)

TicketLink is a **project-knowledge-capture** noun as of okf-plugin 0.8.0.

Do not author TicketLink concepts from this plugin. Use:

```bash
bin/worklog fold | python3 path/to/project-knowledge-capture/scripts/pkc_ticket_link.py emit --bundle <bundle> --open-only
```

Schema: `project-knowledge-capture/schemas/okf-concepts/TicketLink.schema.json`.

Typed edges that still apply when a mixed bundle includes TicketLinks: `tracks`, `maps_to`.
