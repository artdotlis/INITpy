#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -eo pipefail

ROOT="$(dirname "$(realpath "$0")")/../.."
set -a

source "$ROOT/bin/install/env.sh"

echo "Cleaning project tool directories..."

DIRS=("$FNM_HOME" "$UV_HOME" "$PNPM_HOME" "$PNPM_STORE" "$VENV_DIR")

for dir in "${DIRS[@]}"; do
    [[ -z "$dir" ]] && continue
    [[ -e "$ROOT/$dir" ]] || continue
    echo "  removing $dir"
    rm -rf -- "$ROOT/${dir:?}"
done

echo "Cleaning project caches, test artifacts, and build output..."

# Nested cache/build dirs the project generates (pytest, ruff, python bytecode)
while IFS= read -r dir; do
    [[ -n "$dir" ]] || continue
    echo "  removing ${dir##*/}"
    rm -rf -- "$dir"
done < <(find "$ROOT" \
    \( -path "*/.git" -o -path "$ROOT/.venv" -o -path "*/node_modules" \) -prune \
    -o -type d \( -name ".pytest_cache" -o -name ".ruff_cache" -o -name "__pycache__" \) -print 2>/dev/null)

# coverage data files (one per package)
while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    rm -f -- "$f"
done < <(find "$ROOT" \
    \( -path "*/.git" -o -path "$ROOT/.venv" -o -path "*/node_modules" \) -prune \
    -o -type f -name ".coverage*" -print 2>/dev/null)

# package manager install trees
if [[ -e "$ROOT/node_modules" ]]; then
    echo "  removing node_modules"
    rm -rf -- "$ROOT/node_modules"
fi

# build output
if [[ -e "$ROOT/public" ]]; then
    echo "  removing public"
    rm -rf -- "$ROOT/public"
fi

echo "Done."
