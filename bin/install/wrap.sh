#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail

ROOT="$(dirname "$(realpath "$0")")/../.."
set -a
source "$ROOT/bin/install/env.sh"

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

if [[ "$found_sep" == false ]]; then
  # shellcheck disable=SC2294
  eval "${cmd[@]}"
else
  if [[ "${#files[@]}" -eq 0 ]]; then
    exit 0
  fi
  # shellcheck disable=SC2294
  eval "${cmd[@]}" "${files[@]}"
fi

set +a
