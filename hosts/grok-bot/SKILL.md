---
name: okf-graph-eng-grok-bot
description: Bind okf-graph-eng for Grok Bot agents. Use when a Grok Bot needs impact analysis, progressive-disclosure packs, validation, or authoring on an OKF second-brain tree.
---

# okf-graph-eng for Grok Bot

Read and follow:

1. [docs/ONBOARDING.md](../../docs/ONBOARDING.md)
2. [docs/GROK_BOT.md](../../docs/GROK_BOT.md)
3. [docs/ISOLATION.md](../../docs/ISOLATION.md)

## Quick binding

```bash
export SECOND_BRAIN_IDENTITY="grok-bot/okf-graph-eng"
export SECOND_BRAIN_ROOT="${SECOND_BRAIN_ROOT:-.okf}"
python3 scripts/okf-graph.py pack "$SECOND_BRAIN_ROOT" <concept> --hops 2
```

Do not install this as a Claude marketplace plugin inside Grok Bot. Enable skills. Claim identity. Pack before answering. Isolate before writing a shared tree.
