#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail

ROOT="$(dirname "$(realpath "$0")")/../.."
ENV_MK="$ROOT/.env.mk"

# Ensure .env.mk exists (regenerates if missing)
if [[ ! -f "$ENV_MK" ]]; then
    "./env.sh" "$ROOT/package.env" > "$ENV_MK" 2>/dev/null || true
fi

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    # Match "KEY := value" (space before := optional)
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*:?[[:space:]]*=[[:space:]]*(.+)[[:space:]]*$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        value="${value%\"}"; value="${value#\"}"
        value="${value%\'}"; value="${value#\'}"
        export "$key"="$value"
    fi
done < "$ENV_MK"

# Activate Python virtual environment if present
if [[ -d ".venv/bin" ]]; then
  export PATH="$ROOT/.venv/bin:$PATH"
fi

# Add pnpm bin to PATH if node_modules exists (for pnpm-installed tools)
if [[ -d "node_modules/.bin" ]]; then
  export PATH="node_modules/.bin:$PATH"
fi

cmd=()
files=()
found_sep=false

for arg in "$@"; do
  if [[ "$arg" == "--" ]]; then
    found_sep=true
    continue
  fi

  if [[ "$found_sep" == false ]]; then
    cmd+=("$arg")
  else
    files+=("$arg")
  fi
done

if [[ "$found_sep" == "false" ]]; then
  "${cmd[@]}"
else
  if [[ "${#files[@]}" -eq 0 ]]; then
    exit 0
  fi
  "${cmd[@]}" "${files[@]}"
fi
