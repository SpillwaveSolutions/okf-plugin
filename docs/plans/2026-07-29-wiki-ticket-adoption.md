---
date: 2026-07-29
slug: wiki-ticket-adoption
title: Adopt WikiTicket SDD for okf-plugin
epic: 01KYQZ4PAMZCM9N56K8F3034F2
items: [01KYQZ4PAMK1ND4XKH8A1VHMFN, 01KYQZ4PAN1WHT2YGX667F3EX6, 01KYQZ4PANSHKME2QNA8FZVVGC, 01KYQZ4PAN6A8EX36M2ZRWMDAZ, 01KYQZ4PAN551JXFMH2GF82BXF, 01KYQZ4PANS9D55RG19VMXGQ1V, 01KYQZ4PANG2JE670X42GCZY6S, 01KYQZ4PAN71X19C6ZZVM42ZS2, 01KYQZ4PANQFYAMMEBBHYPPG6P]
merged_in: d2d900aff7a9b9e8bfdb3b7d7e36a46e27916e60
---

# Adopt WikiTicket SDD for okf-plugin

## Why

Make all plugin work fishbowl-visible: plans, tickets, and a generated roadmap
instead of ad-hoc chat history. Aligns with the plugin's own graph-engineering
story (nodes, edges, durable state).

## Context

- Repo: https://github.com/SpillwaveSolutions/okf-plugin
- Tooling: https://github.com/SpillwaveSolutions/wiki_ticket_sdd (worklog v0.18.0)
- Hosts: Claude Code + Grok Build
- Ticketing: GitHub Issues · Wiki: GitHub wiki

## Tasks

- [x] (P0) Scaffold worklog tooling in okf-plugin
  Install bin/worklog, git hooks, .work/, CI workflow, and policy blocks so every
  commit and plan is tracked the same way as other Spillwave projects.

- [x] (P0) Configure GitHub Issues and GitHub wiki in .work/config.yml
  Point ticketing and wiki systems at RichardHightower/okf-plugin so ticket-sync
  and wiki-publish have a real target.

- [x] (P1) Capture MVP v0.1 delivery as closed worklog history
  Record the completed plugin scaffold (skills, agent, hooks, sample-okf, docs)
  as done items so the roadmap reflects what already shipped.

- [x] (P1) Publish initial roadmap and plan to GitHub wiki
  Run ia-index and wiki-publish so Home/roadmap/plan pages are visible outside
  the repo for collaborators.

- [x] (P1) Sync open work items to GitHub Issues
  Push active roadmap items to Issues so non-CLI stakeholders can track work.

- [x] (P2) Link sample-okf TicketLink concepts to real worklog ULIDs
  Replace the placeholder OKF-001 ticket with live worklog / GitHub issue ids
  so the dual graph points at real managed work.

- [x] (P2) v0.2 — richer typed-edge conventions and TicketLink SLDC helpers
  Teach skills optional YAML links.rel and helpers that map Wicked Ticket /
  worklog items into TicketLink concepts without breaking plain Markdown links.

- [x] (P2) v0.2 — GraphEngineer polish and progressive-disclosure defaults
  Tighten the specialist agent prompts and default 2-hop pack behavior based on
  real usage of impact and query skills.

- [x] (P3) Optional Claude marketplace listing for okf-graph-eng
  Package and publish the plugin for one-command install once MVP is stable.
