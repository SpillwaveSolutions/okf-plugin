# Upgrade the vendored worklog tooling to 0.22.2

`01KZD823EG6R5E1FXFX416RQ0G` · epic/feature · **open**

Upgrade this repo's vendored worklog tooling from 0.18.0 to 0.22.2 to pull in the plan-banner fix filed upstream as wiki_ticket_sdd#292, plus the trace-check scoping and merge-rescue correctness that shipped alongside it.

## Children

- [[Ticket-01KZD823EH6PBMN2DRD9WAX52F]] Complete the three manual steps the upgrade requires — Add .work/.sessions to .gitignore, since it is local advisory state that must
never be committed and is not currently ignored. (done)
- [[Ticket-01KZD823EHAFN2YF6WCG2T7XN8]] Backfill document provenance — Add the merge commit that brought each frozen document to the default branch. (open)
- [[Ticket-01KZD823EHGFVX6NSM2ZT057SY]] Republish and confirm the plan banners are fixed — Publish first and then converge the index, because publishing rewrites the
published ledger that the normalizer self-describes. (open)
- [[Ticket-01KZD823EHMC16WZNM4W193VVX]] Baseline the citation verifier and fix real defects only — Run doc-verify once and separate fabricated citations, which were already
wrong in the tree the author had open, from drift, which was correct when
written and is expected in a frozen document. (done)
- [[Ticket-01KZD823EHMRAZH978P0EYQFB1]] Restore merge commits as the pull request merge style — This repo used merge commits through pull request 37 and was switched to
squash during the v0.3.2 work without the change being flagged. (open)
- [[Ticket-01KZD823EHQRBSGQ76C4EK1TXT]] Upgrade the vendored tooling to 0.22.2 — Run the init command, which is the documented and idempotent upgrade path. (done)
- [[Ticket-01KZD823EHXEV8Z72ZCNZA8VZH]] File the missing-module gap upstream — Report that init.sh omits doc_verify.py and provenance.py while pre-commit
references the first, and that the file-exists guard makes the omission
silent. (open)
- [[Ticket-01KZD823EHZ7W4HG9N5CV4SRMT]] Install the doc-verify modules the upgrade leaves out — The pre-commit hook calls doc-verify behind a guard that tests whether
bin/doc_verify.py exists, but init does not copy that module or provenance.py. (done)
- [[Ticket-01KZD84S62B5TWKQSX4XV9848M]] Restore the repo-local test gates the upgrade removed from pre-commit — The upgrade rewrites hooks/pre-commit wholesale, which deleted the two repo-local gate lines this project added in v0.3.0 and v0.3.1: the graph engine test suite and the post-edit hook shell test. (done)

Progress: 5/9 done
