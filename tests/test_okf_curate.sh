#!/usr/bin/env bash
# Checks for scripts/okf-curate.sh — the PostToolUse fail-closed validate hook.
# Plain bash, no framework: silent on success, loud + non-zero on failure.
# Run: bash tests/test_okf_curate.sh
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CURATE="$ROOT/scripts/okf-hook-validate.sh"
HOOKS_JSON="$ROOT/hooks/hooks.json"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/okf-curate-test.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
# TMPDIR may end in a slash (macOS) and may be a symlink (/var -> /private/var);
# the hook reports the path it resolved with cd+pwd, so compare against that.
TMP="$(cd "$TMP" && pwd -P)"
FAILED=0

fail() {
  echo "FAIL: $1" >&2
  [[ $# -gt 1 ]] && echo "  got: $2" >&2
  FAILED=1
}

# A bundle rooted somewhere the old hard-coded filter never matched:
# not .okf/, not knowledge/, not sample-okf/.
mkdir -p "$TMP/my-graph/agents" "$TMP/unrelated" "$TMP/broken-graph/agents"
cat > "$TMP/my-graph/index.md" <<'EOF'
---
okf_version: "0.2"
title: Test Bundle
description: Bundle rooted outside every legacy path fragment.
timestamp: 2026-01-01T00:00:00Z
---

# Test Bundle

- [Agent A](/agents/a.md)
EOF
cat > "$TMP/my-graph/agents/a.md" <<'EOF'
---
type: Catalog
title: Agent A
description: A catalog page.
timestamp: 2026-01-01T00:00:00Z
---

# Agent A
EOF
cat > "$TMP/broken-graph/index.md" <<'EOF'
---
okf_version: "0.2"
title: Broken Bundle
description: Has a broken link so validate must fail-closed.
timestamp: 2026-01-01T00:00:00Z
---

# Broken Bundle

- [Missing](/agents/missing.md)
EOF
cat > "$TMP/broken-graph/agents/b.md" <<'EOF'
---
type: Catalog
title: Agent B
description: Points at a file that does not exist.
timestamp: 2026-01-01T00:00:00Z
links:
  - target: /agents/missing.md
    rel: related_to
---

See [missing](/agents/missing.md).
EOF
echo "just some notes" > "$TMP/unrelated/notes.md"
echo "print('hi')" > "$TMP/my-graph/agents/script.py"

# 1. File in a non-standard bundle root IS validated, via explicit $1.
out="$("$CURATE" "$TMP/my-graph/agents/a.md" 2>&1)"
rc=$?
[[ $rc -eq 0 ]] || fail "arg invocation should exit 0, got $rc"
case "$out" in
  *"validating bundle at $TMP/my-graph"*) ;;
  *) fail "non-standard bundle root not validated" "$out" ;;
esac

# 2. File in an unrelated directory is NOT validated, and says nothing about it.
out="$("$CURATE" "$TMP/unrelated/notes.md" 2>&1)"
rc=$?
[[ $rc -eq 0 ]] || fail "unrelated file should exit 0, got $rc"
[[ -z "$out" ]] || fail "unrelated file should produce no output" "$out"

# 3. The real invocation path: PostToolUse JSON payload on stdin.
out="$(printf '{"tool_name":"Write","tool_input":{"file_path":"%s"}}' \
  "$TMP/my-graph/agents/a.md" | "$CURATE" 2>&1)"
rc=$?
[[ $rc -eq 0 ]] || fail "stdin invocation should exit 0, got $rc"
case "$out" in
  *"validating bundle at $TMP/my-graph"*) ;;
  *) fail "stdin JSON payload not validated" "$out" ;;
esac

# 4. Empty / malformed stdin is a no-op, not a crash.
out="$(echo 'not json' | "$CURATE" 2>&1)"
rc=$?
[[ $rc -eq 0 ]] || fail "malformed stdin should exit 0, got $rc"
[[ -z "$out" ]] || fail "malformed stdin should produce no output" "$out"

# 5. Non-markdown inside a bundle is rejected by the cheap pre-check.
out="$("$CURATE" "$TMP/my-graph/agents/script.py" 2>&1)"
rc=$?
[[ $rc -eq 0 ]] || fail "non-markdown should exit 0, got $rc"
[[ -z "$out" ]] || fail "non-markdown should be skipped silently" "$out"

# 6. Invalid bundle is fail-closed (non-zero).
out="$("$CURATE" "$TMP/broken-graph/agents/b.md" 2>&1)"
rc=$?
[[ $rc -ne 0 ]] || fail "invalid bundle should exit non-zero, got $rc" "$out"
case "$out" in
  *"validating bundle at $TMP/broken-graph"*) ;;
  *) fail "invalid bundle did not announce validate" "$out" ;;
esac

# 7. Codex apply_patch payload extracts the file and validates.
out="$(printf '{"tool_name":"apply_patch","tool_input":{"input":"*** Begin Patch\\n*** Update File: %s\\n*** End Patch\\n"}}' \
  "$TMP/my-graph/agents/a.md" | "$CURATE" 2>&1)"
rc=$?
[[ $rc -eq 0 ]] || fail "apply_patch payload should exit 0, got $rc" "$out"
case "$out" in
  *"validating bundle at $TMP/my-graph"*) ;;
  *) fail "apply_patch payload not validated" "$out" ;;
esac

# 8. Manifest is PostToolUse fail-closed validate, not a SessionStart reminder
#    and not a curate-after-Write.
if ! python3 - "$HOOKS_JSON" <<'PY'
import json, sys
p = sys.argv[1]
data = json.loads(open(p, encoding="utf-8").read())
hooks = data.get("hooks") or {}
if "SessionStart" in hooks:
    raise SystemExit("hooks.json still has SessionStart")
post = hooks.get("PostToolUse") or []
matchers = " ".join(e.get("matcher") or "" for e in post)
if "apply_patch" not in matchers or "Write" not in matchers:
    raise SystemExit("matcher must include apply_patch and Write")
commands = []
for entry in post:
    for hook in entry.get("hooks") or []:
        commands.append(hook.get("command") or "")
joined = " ".join(commands)
if "okf-hook-validate.sh" not in joined:
    raise SystemExit("hooks.json must invoke okf-hook-validate.sh")
if "okf-curate.sh" in joined:
    raise SystemExit("hooks.json still invokes okf-curate.sh")
PY
then
  fail "hooks.json is not fail-closed PostToolUse validate"
fi

exit $FAILED
