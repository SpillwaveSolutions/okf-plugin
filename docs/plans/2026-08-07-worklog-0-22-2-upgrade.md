---
date: 2026-08-07
slug: worklog-0-22-2-upgrade
title: Upgrade the vendored worklog tooling to 0.22.2
epic: 01KZD823EG6R5E1FXFX416RQ0G
items: [01KZD823EHQRBSGQ76C4EK1TXT, 01KZD823EH6PBMN2DRD9WAX52F, 01KZD823EHZ7W4HG9N5CV4SRMT, 01KZD823EHXEV8Z72ZCNZA8VZH, 01KZD823EHMRAZH978P0EYQFB1, 01KZD823EHMC16WZNM4W193VVX, 01KZD823EHAFN2YF6WCG2T7XN8, 01KZD823EHGFVX6NSM2ZT057SY]
---

# Upgrade the vendored worklog tooling 0.18.0 to 0.22.2

## Why

The backlog is empty and the only outstanding thread was upstream
wiki_ticket_sdd#292 — the plan-banner defect filed rather than patched locally,
because bin/ia_render.py is vendored and init.sh overwrites it unconditionally.
That issue is now closed, fixed in worklog 0.20.0.

Pulling the fix in means upgrading: the vendored copy here is on 0.18.0 against
upstream 0.22.2, four minor versions, with ten of eleven vendored files changed.

The payoff is visible on the wiki. All three plan pages read "the latest status
report" while all three are status: completed. After the upgrade they name their
actual state. The same release also stops banner() defaulting kind on status
records, so broken data raises instead of rendering plausible prose over it.

Two upstream warnings were checked against this repo and do not apply: the
mid-file __main__ block that silently drops tests, and the hook manifest missing
its wrapper. Both verified clean here rather than assumed.

## Context

- Upstream: https://github.com/SpillwaveSolutions/wiki_ticket_sdd
- Fix we are pulling in: wiki_ticket_sdd#292, shipped in worklog 0.20.0
- The event log format changed additively; mixed versions are safe in both
  directions, so there is no migration and no backfill.

## Tasks

- [ ] (P1) Upgrade the vendored tooling to 0.22.2
  Run the init command, which is the documented and idempotent upgrade path. It
  re-copies bin/ and hooks/ and adds four modules this repo lacks: session.py,
  item_fields.py, wiki_flavor.py and changelog.py. Confirm the version actually
  moved afterwards rather than assuming the copy happened.

- [ ] (P2) Complete the three manual steps the upgrade requires
  Add .work/.sessions to .gitignore, since it is local advisory state that must
  never be committed and is not currently ignored. Wire the SessionEnd hook,
  which means creating a project settings file that does not exist here yet.
  Confirm the hooks path still points at this repo's hooks directory.

- [ ] (P1) Install the doc-verify modules the upgrade leaves out
  The pre-commit hook calls doc-verify behind a guard that tests whether
  bin/doc_verify.py exists, but init does not copy that module or provenance.py.
  The result is a gate that is present in the hook, never runs, and warns about
  nothing. This is the third time this project has met a check that was
  configured but could not fire. Copy both modules so the gate works, and mark
  the deviation from init's file set clearly so it can be removed later.

- [ ] (P2) File the missing-module gap upstream
  Report that init.sh omits doc_verify.py and provenance.py while pre-commit
  references the first, and that the file-exists guard makes the omission
  silent. Include the repro and note that uninstall.sh omits them too.

- [ ] (P2) Restore merge commits as the pull request merge style
  This repo used merge commits through pull request 37 and was switched to
  squash during the v0.3.2 work without the change being flagged. Upstream
  ADR-0008 records that document provenance depends on merge commits, because
  under squash the authoring commit never reaches the default branch and the
  citation verifier loses its ground truth. Record the reason so the convention
  is not quietly reversed later.

- [ ] (P2) Baseline the citation verifier and fix real defects only
  Run doc-verify once and separate fabricated citations, which were already
  wrong in the tree the author had open, from drift, which was correct when
  written and is expected in a frozen document. Fix the fabrications. Leave
  drift alone in frozen documents.

- [ ] (P3) Backfill document provenance
  Add the merge commit that brought each frozen document to the default branch.

- [ ] (P1) Republish and confirm the plan banners are fixed
  Publish first and then converge the index, because publishing rewrites the
  published ledger that the normalizer self-describes. Expect only the plan
  pages to republish, not the whole site. Confirm the three plan pages name
  their state, and confirm the plugin's own test suite and sample bundle are
  completely unaffected — a tooling upgrade that changes graph engine behaviour
  would itself be a bug.
