#!/usr/bin/env bash
# Compatibility shim. The PostToolUse hook is fail-closed validate.
# Prefer scripts/okf-hook-validate.sh. This name stays so old skill text
# and operator muscle memory still work.
set -euo pipefail
exec "$(cd "$(dirname "$0")" && pwd)/okf-hook-validate.sh" "$@"
