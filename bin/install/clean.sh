#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -eo pipefail

ROOT="$(dirname "$(realpath "$0")")/../.."
set -a

source "$ROOT/bin/install/load_env_mk.sh"

echo "Cleaning project tool directories..."

DIRS=("$FNM_HOME" "$UV_HOME" "$PNPM_HOME" "$PNPM_STORE" "$VENV_DIR")

for dir in "${DIRS[@]}"; do
    [[ -z "$dir" ]] && continue
    [[ -e "$ROOT/$dir" ]] || continue
    echo "  removing $dir"
    rm -rf -- "$ROOT/${dir:?}"
done

[[ -f "$ROOT/.env.mk" ]] && echo "  removing .env.mk" && rm -f "$ROOT/.env.mk"

echo "Done."
