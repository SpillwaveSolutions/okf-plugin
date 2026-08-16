#!/usr/bin/env bash
# PostToolUse hook: fail-closed validate of the touched OKF bundle.
# Takes a file path as $1, or reads a Claude / Codex PostToolUse payload
# from stdin (Write/Edit file_path, or apply_patch patch text).
set -euo pipefail

FILE="${1:-}"
if [[ -z "$FILE" ]]; then
  FILE="$(python3 -c '
import json, re, sys
def extract(data):
    if not isinstance(data, dict):
        return ""
    nests = [data.get("tool_input"), data.get("arguments"), data]
    for nest in nests:
        if not isinstance(nest, dict):
            continue
        for key in ("file_path", "path", "file"):
            v = nest.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
        for key in ("input", "patch"):
            v = nest.get(key)
            if not isinstance(v, str):
                continue
            m = re.search(r"\*\*\* (?:Add|Update|Delete) File: (.+)", v)
            if m:
                return m.group(1).strip()
    return ""
try:
    print(extract(json.load(sys.stdin)))
except Exception:
    pass
' 2>/dev/null || true)"
fi

# Cheap pre-check only: OKF bundles are Markdown, so anything else can never
# need validation and is not worth a filesystem walk. Bundle membership itself
# is decided by find_bundle_root below — a hard-coded list of path fragments
# ("knowledge/", "sample-okf/") is not a bundle test.
if [[ -z "$FILE" ]]; then
  exit 0
fi
case "$FILE" in
  *.md|*.markdown) ;;
  *) exit 0 ;;
esac

if [[ "$FILE" != /* ]]; then
  FILE="$(pwd)/$FILE"
fi

# Resolve bundle root: nearest ancestor containing index.md with okf_version,
# or a .okf/ bundle directory. No fallback to a repo's .okf/ or sample-okf/:
# a file that is not inside a bundle must not be validated against an
# unrelated one just because the repo happens to ship a bundle somewhere.
find_bundle_root() {
  local dir
  dir="$(cd "$(dirname "$FILE")" 2>/dev/null && pwd)" || return 1
  while [[ "$dir" != "/" ]]; do
    if [[ -f "$dir/index.md" ]] && grep -q 'okf_version' "$dir/index.md" 2>/dev/null; then
      echo "$dir"
      return 0
    fi
    if [[ -d "$dir/.okf" && -f "$dir/.okf/index.md" ]]; then
      echo "$dir/.okf"
      return 0
    fi
    dir="$(dirname "$dir")"
  done
  return 1
}

# Silent when the file is not in a bundle: every Markdown edit in every repo
# reaches this point, and the hook must not narrate non-events.
BUNDLE_ROOT="$(find_bundle_root || true)"
if [[ -z "${BUNDLE_ROOT:-}" ]]; then
  exit 0
fi

echo "okf-validate: validating bundle at $BUNDLE_ROOT (touched: $FILE)"

if command -v okf >/dev/null 2>&1; then
  okf validate "$BUNDLE_ROOT"
elif command -v okfcli >/dev/null 2>&1; then
  okfcli validate "$BUNDLE_ROOT"
else
  # No external CLI: use this repo's own validator, which sits next to us and
  # understands typed edges. Fail-closed: propagate the validator exit code.
  python3 "$(dirname "$0")/okf-graph.py" validate "$BUNDLE_ROOT"
fi
