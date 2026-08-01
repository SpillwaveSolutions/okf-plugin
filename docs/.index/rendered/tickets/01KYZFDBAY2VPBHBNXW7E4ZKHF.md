# Fix okf-graph.py block-sequence YAML, Mermaid IDs, and add validate --strict

`01KYZFDBAY2VPBHBNXW7E4ZKHF` · task/feature · **done**

Parse standard YAML block sequences in frontmatter; derive Mermaid node IDs
from the full relative path via a shared mermaid_id/render_mermaid helper; add
a --strict flag so CI can gate on warnings while the skills keep the lenient
default.

## Hierarchy

- epic: [[Ticket-01KYZFDBAYGEG2FKWRADN46Z9W]] v0.3.0 — fix the plumbing, add the net — Fix three verified defects in shipped v0.2.0 code (no-op post-edit hook, silently dropped block-sequence YAML, colliding Mermaid node IDs) and add the first automated coverage of scripts/okf-graph.py, the plugin's graph engine.

## Linked PRs

- [[PR-8]]
