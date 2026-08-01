#!/usr/bin/env bash
# Post-edit hook: validate OKF concepts after Write/Edit/MultiEdit.
# Takes a file path as $1, or reads the PostToolUse payload from stdin.
set -euo pipefail

# Claude Code delivers the tool payload as JSON on stdin; there is no
# $FILE_PATH in the hook environment. python3 rather than jq: the plugin
# already requires python3 everywhere, jq is not guaranteed present.
FILE="${1:-}"
if [[ -z "$FILE" ]]; then
  FILE="$(python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get("tool_input", {}).get("file_path", ""))
except Exception:
    pass' 2>/dev/null || true)"
fi

# Only act on OKF-related paths
if [[ -z "$FILE" ]]; then
  exit 0
fi
case "$FILE" in
  *.okf/*|*/.okf/*|*knowledge/*|*sample-okf/*) ;;
  *) exit 0 ;;
esac

# Resolve bundle root: nearest directory containing index.md with okf_version, or .okf/
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
  # Fallbacks
  local top
  top="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  if [[ -d "$top/.okf" ]]; then
    echo "$top/.okf"
    return 0
  fi
  if [[ -d "$top/sample-okf" ]]; then
    echo "$top/sample-okf"
    return 0
  fi
  return 1
}

BUNDLE_ROOT="$(find_bundle_root || true)"
if [[ -z "${BUNDLE_ROOT:-}" ]]; then
  echo "okf-curate: no OKF bundle root found for $FILE — skipping"
  exit 0
fi

echo "okf-curate: validating bundle at $BUNDLE_ROOT (touched: $FILE)"

if command -v okf >/dev/null 2>&1; then
  okf validate "$BUNDLE_ROOT" 2>&1 || true
  if okf lint --help >/dev/null 2>&1; then
    okf lint "$BUNDLE_ROOT" 2>&1 || true
  fi
elif command -v okfcli >/dev/null 2>&1; then
  okfcli validate "$BUNDLE_ROOT" 2>&1 || true
else
  # No external CLI: use this repo's own validator, which sits next to us and
  # understands typed edges. (The previous grep fallback also used `realpath
  # -m`, absent from stock macOS.)
  python3 "$(dirname "$0")/okf-graph.py" validate "$BUNDLE_ROOT" || true
fi

exit 0
