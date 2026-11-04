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

# ===== DOCS:START =====
if [[ -e "$ROOT/$PKG_DOCS/node_modules" ]]; then
    echo "  removing docs node_modules"
    rm -rf -- "$ROOT/$PKG_DOCS/node_modules"
fi

# docs build output and VitePress workdir (cache/dist only; .vitepress source is tracked)
if [[ -e "$ROOT/$PKG_DOCS/.vitepress/.vitepress" ]]; then
    echo "  removing vitepress workdir"
    rm -rf -- "$ROOT/$PKG_DOCS/.vitepress/.vitepress"
fi
# ===== DOCS:END =====

# build output
if [[ -e "$ROOT/public" ]]; then
    echo "  removing public"
    rm -rf -- "$ROOT/public"
fi

[[ -f "$ROOT/.env.mk" ]] && echo "  removing .env.mk" && rm -f "$ROOT/.env.mk"

echo "Done."
