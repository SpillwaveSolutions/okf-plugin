---
name: okf-graph-eng-deep-agents
description: Bind okf-graph-eng for LangChain Deep Agents / Deep Agents Code. Use when a Deep Agents process needs OKF impact, pack, validate, or authoring skills.
---

# okf-graph-eng for LangChain Deep Agents

Read and follow:

1. [docs/ONBOARDING.md](../../docs/ONBOARDING.md)
2. [docs/LANG_CHAIN_DEEP_AGENTS.md](../../docs/LANG_CHAIN_DEEP_AGENTS.md)
3. [docs/ISOLATION.md](../../docs/ISOLATION.md)

## Quick binding

Point `skills=` or SkillsMiddleware at this repo's `skills/` directory. Set:

```bash
export SECOND_BRAIN_IDENTITY="deep-agents/okf-graph-eng"
export SECOND_BRAIN_ROOT="${SECOND_BRAIN_ROOT:-.okf}"
```

Open an isolation session before writing a shared institutional tree. Prefer `scripts/okf-graph.py` for deterministic pack / impact / validate.
