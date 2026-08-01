# Fix the no-op post-edit hook and curate fallback

`01KYZFDBAY0AX03XQ6SAT6SXJW` · task/feature · **done**

Read the file path from the PostToolUse stdin JSON instead of a nonexistent
$FILE_PATH, widen the matcher to include MultiEdit, and replace the grep-based
fallback with the repo's own okf-graph.py validate (which also deletes a
realpath -m call that is broken on stock macOS).

## Hierarchy

- epic: [[Ticket-01KYZFDBAYGEG2FKWRADN46Z9W]] v0.3.0 — fix the plumbing, add the net — Fix three verified defects in shipped v0.2.0 code (no-op post-edit hook, silently dropped block-sequence YAML, colliding Mermaid node IDs) and add the first automated coverage of scripts/okf-graph.py, the plugin's graph engine.

## Linked PRs

- [[PR-8]]
