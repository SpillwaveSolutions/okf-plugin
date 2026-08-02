#!/usr/bin/env bash
# Checks for scripts/okf-curate.sh — the PostToolUse curation hook.
# Plain bash, no framework: silent on success, loud + non-zero on failure.
# Run: bash tests/test_okf_curate.sh
set -uo pipefail

CURATE="$(cd "$(dirname "$0")/.." && pwd)/scripts/okf-curate.sh"
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
mkdir -p "$TMP/my-graph/agents" "$TMP/unrelated"
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
type: AgentNode
title: Agent A
description: An agent node.
timestamp: 2026-01-01T00:00:00Z
---

# Agent A
EOF
echo "just some notes" > "$TMP/unrelated/notes.md"
echo "print('hi')" > "$TMP/my-graph/agents/script.py"

# 1. File in a non-standard bundle root IS curated, via explicit $1.
out="$("$CURATE" "$TMP/my-graph/agents/a.md" 2>&1)"
rc=$?
[[ $rc -eq 0 ]] || fail "arg invocation should exit 0, got $rc"
case "$out" in
  *"validating bundle at $TMP/my-graph"*) ;;
  *) fail "non-standard bundle root not curated" "$out" ;;
esac

# 2. File in an unrelated directory is NOT curated, and says nothing about it.
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
  *) fail "stdin JSON payload not curated" "$out" ;;
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

exit $FAILED
