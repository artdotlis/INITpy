#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail

# Activate Python virtual environment if present
if [[ -f ".venv/bin/activate" ]]; then
  source .venv/bin/activate
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
