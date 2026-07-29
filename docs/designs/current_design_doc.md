---
doc_type: design
truth_state: current
wiki_key: design/current-design-doc
title: Design Doc
git_hash: main
---

# OKF Graph Engineering Plugin — Design Document

## 1. Purpose

Deliver a single Claude Code plugin (`okf-graph-eng`) that turns OKF (Open Knowledge Format) repositories into a platform for **graph engineering**: durable knowledge graphs *and* agent/harness graphs, with impact analysis and progressive disclosure as primary differentiators.

Grok Build consumes the same Claude plugin layout with zero configuration.

## 2. Goals

1. OKF Markdown + YAML remains the source of truth (no proprietary runtime).  
2. Impact / blast-radius analysis is first-class.  
3. Agent graphs use first-class types (`AgentNode`, `Workflow`, `SharedState`, …).  
4. Intelligence lives in portable `SKILL.md` files; deterministic work prefers CLI.  
5. One packaging path for Claude Code and Grok Build.  

## 3. Architecture

```
.claude-plugin/plugin.json     # manifest
skills/                        # okf-init-graph, author, impact, query, maintain, validate, visualize
commands/                      # thin slash wrappers
agents/graph-engineer.md       # specialist
hooks/                         # post-edit curate
scripts/okf-graph.py           # graph ops fallback
scripts/okf-ticket-link.py     # worklog → TicketLink
sample-okf/                    # self-describing dual graph
```

**Integration:** Prefer `okf`/`okfcli` when present; else `scripts/okf-graph.py`. Project management is WikiTicket SDD (`bin/worklog`), orthogonal to skill logic.

## 4. Concept model

| Kind | Types |
|------|--------|
| Knowledge | Dataset, Table, Metric, Playbook, Runbook, API, Reference |
| Harness | AgentNode, Workflow, Harness, DecisionRecord, SharedState, ToolCapability, TicketLink |

**Edges:** Markdown links required. Optional `links: [{ target, rel }]` with `depends_on`, `routes_to`, `tracks`, etc.

## 5. Key behaviors

| Concern | Design |
|---------|--------|
| Impact | Transitive inbound/outbound; rank by type + trust |
| Progressive disclosure | Default 2-hop pack, max ~20 nodes, trust-biased trim |
| Validation | Broken links, orphans, unverified high-impact |
| Tickets | TicketLink + worklog ULID / GitHub issue bridge |
| Hosts | Claude plugin packaging only; Grok reads it natively |

## 6. Non-goals (current)

- Replacing okfcli or full catalog integrations  
- Embeddings / semantic search (future)  
- Grok-only features that break Claude  

## 7. Related

- [[Code-Walkthrough]]  
- [[User-Guide]]  
- [[Plugin-Guide]]  
- Plan: [[Plan-wiki-ticket-adoption]]  
