#!/usr/bin/env bash
# Post-edit hook: validate OKF concepts after Write/Edit.
# Expects a file path as $1 (or $FILE_PATH from the hook environment).
set -euo pipefail

FILE="${1:-${FILE_PATH:-}}"

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
  # Lightweight fallback: frontmatter + link checks on the touched file
  if [[ -f "$FILE" ]]; then
    if ! head -1 "$FILE" | grep -q '^---'; then
      echo "WARN: $FILE missing YAML frontmatter (expected --- opener)"
    fi
    # Report broken relative/absolute md links that don't resolve under bundle
    while IFS= read -r link; do
      target="${link#*(}"
      target="${target%)}"
      target="${target%%#*}"
      [[ -z "$target" || "$target" == http* || "$target" == mailto:* ]] && continue
      if [[ "$target" == /* ]]; then
        cand="${BUNDLE_ROOT}${target}"
      else
        cand="$(cd "$(dirname "$FILE")" && realpath -m "$target" 2>/dev/null || echo "$(dirname "$FILE")/$target")"
      fi
      if [[ ! -f "$cand" && ! -f "${BUNDLE_ROOT}${target}" ]]; then
        # also try relative to bundle with leading slash stripped
        alt="${BUNDLE_ROOT}/${target#/}"
        if [[ ! -f "$alt" ]]; then
          echo "WARN: possible broken link in $(basename "$FILE"): $target"
        fi
      fi
    done < <(grep -oE '\[[^]]+\]\([^)]+\)' "$FILE" 2>/dev/null || true)
    echo "okf-curate: okf CLI not found — ran lightweight checks only"
  fi
fi

exit 0
