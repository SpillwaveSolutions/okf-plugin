# Restore the repo-local test gates the upgrade removed from pre-commit

`01KZD84S62B5TWKQSX4XV9848M` · task/bug · **done**

The upgrade rewrites hooks/pre-commit wholesale, which deleted the two repo-local gate lines this project added in v0.3.0 and v0.3.1: the graph engine test suite and the post-edit hook shell test.

## Hierarchy

- epic: [[Ticket-01KZD823EG6R5E1FXFX416RQ0G]] Upgrade the vendored worklog tooling to 0.22.2 — Upgrade this repo's vendored worklog tooling from 0.18.0 to 0.22.2 to pull in the plan-banner fix filed upstream as wiki_ticket_sdd#292, plus the trace-check scoping and merge-rescue correctness that shipped alongside it.
