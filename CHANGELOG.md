# Changelog

## 0.8.0 — 2026-08-24

### Changed

- **Noun split.** Core owns `Catalog` and `ContextPack` only. Domain schemas
  (`TicketLink`, `Feature`, `Epic`/`Story`/`Task`/`Subtask`/`Bug`/`Branch`/`Project`,
  `DecisionRecord`, …) moved to PKC. Agent/harness types were never supposed to
  live here; AGER owns them. DEKC keeps the data plane.
- Impact criticality is loaded from sibling schema `x-impact` instead of a
  hardcoded `AgentNode` / `Dataset` list. Isolated CI sees every type as `low`.
- `scripts/okf-ticket-link.py` is a stub. Emission lives in PKC
  (`scripts/pkc_ticket_link.py`).
- `sample-okf/` retyped to Catalog + Knowledge (same 22 files / 83 edges).
- README rewritten around OKF + how ContextPacks optimize reads
  (outbound-only, hop cap, node cap, trust-first ranking, read order).
- Domain templates (`agent-node`, `workflow`, `ticket-link`, `decision-record`,
  `shared-state`) removed from `okf-author` / `okf-init-graph`.
- Plugin description / keywords no longer claim agent-graph or TicketLink.

### Added

- Schema registry 2.0.0: `BaseConcept`, `Catalog`, `ContextPack`.

## 0.7.4

- Three-host hooks: Codex + Cursor-native when Claude hooks exist.


## 0.7.3 — 2026-08-17

- **Cursor host.** `.cursor-plugin/plugin.json` (Cursor Plugins) plus `.cursor/rules/second-brain.mdc`. Docs: `docs/CURSOR.md`. `docs/GROK_BOT.md` now covers Grok Bot spawning Cursor cloud agents.

Notable changes to **okf-graph-eng**. Newest first. Released sections are
frozen — corrections go in the next release's notes.

## Unreleased

- Host manifests (`.claude-plugin/plugin.json` and marketplace copies) now
  match root `plugin.json` **0.7.2**. Claude Code was still labeled 0.5.0
  so `claude plugin update` reported "already current."

## 0.7.2 — 2026-08-17

### Changed

- PostToolUse hook is **fail-closed validate**, named that way.
  `hooks/hooks.json` now runs `scripts/okf-hook-validate.sh`.
- This pack **validates**. It does not curate (no catalog rewrite after Write).
- `scripts/okf-curate.sh` remains a one-line exec shim for old skill text.
- Codex `.codex-plugin/plugin.json` still points at `hooks/hooks.json`; the
  command behind that file is now the validate script.
- Implements the hook close-bar on [okf-plugin#55](https://github.com/SpillwaveSolutions/okf-plugin/issues/55).

## 0.7.1 — 2026-08-16

### Changed

- Post-edit hook is **fail-closed**. `scripts/okf-curate.sh` now propagates
  `okf-graph.py validate` (or `okf` / `okfcli` on PATH) instead of swallowing
  the exit code.
- Matcher includes Codex `apply_patch` as well as Claude `Write|Edit|MultiEdit`.
- Hook parses `apply_patch` payloads. Writes outside an OKF bundle stay a
  silent no-op. No SessionStart reminder.

## 0.7.0 — 2026-08-15

### Added

- **Multi-host bindings** for Grok Bot, LangChain Deep Agents, Codex, and
  Agent Plugins 1.0 (master plan okf-plugin#55, implementation #56):
  - `docs/GROK_BOT.md` — Grok Bot binding contract (identity, isolation, pack-first)
  - `docs/LANG_CHAIN_DEEP_AGENTS.md` — SkillsMiddleware / filesystem `skills=` path
  - `docs/ISOLATION.md` — worktree + PR write isolation for shared OKF trees
  - `docs/ONBOARDING.md` — LLM-wiki history, destination state, public repo list
  - Root `plugin.json` conforming to Agent Plugins 1.0
  - `.codex-plugin/plugin.json` pointing at existing post-edit curation hooks
  - Thin host skills under `hosts/grok-bot/` and `hosts/deep-agents/`
- README multi-host install table covering Claude Code, Grok Build, Codex,
  Agent Plugins, Grok Bot, and Deep Agents.

### Notes

- No graph-engine behavior change. Existing Claude Code / Grok Build install
  paths are unchanged.
- Canonical session helper for multi-writer knowledge trees remains
  second-brain-core `scripts/brain_session.py`; this release documents how
  okf-graph-eng agents use that protocol.

## 0.6.0 — 2026-08-14

### Added

- **First-class work items:** `Epic`, `Story`, `Task`, `Subtask`, `Bug` are
  concept types (catalogs `epics/`, `stories/`, `tasks/`, `subtasks/`, `bugs/`).
  `TicketLink` remains valid for existing files.
- **`Branch` concept** (`branches/`). Prefer `on_branch` links from Bug/CodeChange
  over a bare `branch:` string.
- **Per-type recommended fields** via `x-recommended` / `x-recommended-any` /
  `x-recommended-link-rels`. Soft (warn) by default; `--strict` promotes them
  to errors. BaseConcept required fields stay `type` + `title` only.

## 0.5.0 — 2026-08-13

### Added

- **Shared concept schema pack** at `schemas/okf-concepts/`.
- `scripts/okf_schema.py` — stdlib subset validator.
- `okf-graph.py schemas` and schema-aware `validate`.
- Catalog ownership map in `registry.json`.

## 0.4.1 — 2026-08-10

### Fixed

- `KNOWN_RELS` expanded to cover sibling plugin vocabularies (AGER, PKC, SAC, DEKC). (#51)

## 0.4.0 — 2026-08-10

### Fixed

- Bracketed link labels no longer drop edges. (#48)

### Added

- `released_in` is a known relation. (#49)

## 0.3.2 — 2026-08-03

### Fixed

- Root `index.md` and `log.md` now participate in link checks.

## 0.3.1 — 2026-08-02

Correctness release. See git history for full notes.

## 0.3.0 — 2026-08-01

Bug-fix and hardening release. See git history for full notes.

## 0.2.0 — 2026-07-31

First tagged release. See
<https://github.com/SpillwaveSolutions/okf-plugin/releases/tag/v0.2.0>
