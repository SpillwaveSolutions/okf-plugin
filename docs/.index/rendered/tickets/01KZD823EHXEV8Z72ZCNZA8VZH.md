# File the missing-module gap upstream

`01KZD823EHXEV8Z72ZCNZA8VZH` · task/feature · **open**

Report that init.sh omits doc_verify.py and provenance.py while pre-commit
references the first, and that the file-exists guard makes the omission
silent.

## Hierarchy

- epic: [[Ticket-01KZD823EG6R5E1FXFX416RQ0G]] Upgrade the vendored worklog tooling to 0.22.2 — Upgrade this repo's vendored worklog tooling from 0.18.0 to 0.22.2 to pull in the plan-banner fix filed upstream as wiki_ticket_sdd#292, plus the trace-check scoping and merge-rescue correctness that shipped alongside it.
