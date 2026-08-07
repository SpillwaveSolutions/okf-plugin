# Install the doc-verify modules the upgrade leaves out

`01KZD823EHZ7W4HG9N5CV4SRMT` · task/feature · **done**

The pre-commit hook calls doc-verify behind a guard that tests whether
bin/doc_verify.py exists, but init does not copy that module or provenance.py.

## Hierarchy

- epic: [[Ticket-01KZD823EG6R5E1FXFX416RQ0G]] Upgrade the vendored worklog tooling to 0.22.2 — Upgrade this repo's vendored worklog tooling from 0.18.0 to 0.22.2 to pull in the plan-banner fix filed upstream as wiki_ticket_sdd#292, plus the trace-check scoping and merge-rescue correctness that shipped alongside it.
