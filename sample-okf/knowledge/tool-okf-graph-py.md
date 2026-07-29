---
type: ToolCapability
title: okf-graph.py
description: Bundled Python fallback for impact, subgraph, validate, and orphan detection when okfcli is unavailable.
tags: [tool, cli, python]
timestamp: 2026-07-29T00:00:00Z
status: active
verified: true
---

# okf-graph.py

## Overview

Portable graph utility shipped under `scripts/okf-graph.py`.

## Commands

```bash
python3 scripts/okf-graph.py impact <bundle> <concept>
python3 scripts/okf-graph.py backlinks <bundle> <concept>
python3 scripts/okf-graph.py subgraph <bundle> <concept> [--hops N]
python3 scripts/okf-graph.py pack <bundle> <concept> [--hops 2] [--max-nodes 20]
python3 scripts/okf-graph.py edges <bundle> [--from PATH] [--rel REL]
python3 scripts/okf-graph.py validate <bundle>
python3 scripts/okf-graph.py orphans <bundle>
```

Related: `scripts/okf-ticket-link.py` emits TicketLink concepts from worklog fold JSON.

## Used by

- [okf-impact skill](/knowledge/skill-okf-impact.md)
- [okf-query skill](/knowledge/skill-okf-query.md)
- [okf-validate skill](/knowledge/skill-okf-validate.md)
- [Graph Engineer](/agents/graph-engineer.md)
