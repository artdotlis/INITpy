#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense


set -Eeuo pipefail

trap 'echo "Error: command failed (exit=$?): ${BASH_COMMAND}" >&2' ERR

ROOT="$(dirname "$(realpath "$0")")/../.."
cd "$ROOT"

if ! command -v cz >/dev/null 2>&1 && [[ -x "$ROOT/.venv/bin/cz" ]]; then
    export PATH="$ROOT/.venv/bin:$PATH"
fi

PYPROJECT="pyproject.toml"
PACKAGE_JSON="package.json"
README="README.md"


read_version() {
    local ver
    ver="$(grep -Eom1 '^version = "[0-9]+(\.[0-9]+){2}"' "$PYPROJECT" | grep -Eo '[0-9]+(\.[0-9]+){2}' || true)"
    if [[ -z "$ver" ]]; then
        echo "[calver] no version found in $PYPROJECT" >&2
        exit 1
    fi
    IFS='.' read -r YEAR MONTH PATCH <<<"$ver"
    YEAR=$((10#$YEAR))
    MONTH=$((10#$MONTH))
    PATCH=$((10#$PATCH))
}

write_version() {
    local ver
    ver="$(printf '%04d.%02d.%d' "$YEAR" "$MONTH" "$PATCH")"
    sed -Ei "s/^version = \"[0-9]+(\.[0-9]+){2}\"/version = \"$ver\"/" "$PYPROJECT"
    sed -Ei "s/\"version\": \"[0-9]+(\.[0-9]+){2}\"/\"version\": \"$ver\"/" "$PACKAGE_JSON"
    if [[ -f "$README" ]]; then
        sed -Ei "s/(release: |rel-)[0-9]+(\.[0-9]+){2}/\\1$ver/g" "$README"
    fi
    local f
    for f in packages/*/pyproject.toml packages/*/package.json; do
        [[ -f "$f" ]] || continue
        sed -Ei "s/^version = \"[0-9]+(\.[0-9]+){2}\"/version = \"$ver\"/" "$f"
        sed -Ei "s/\"version\": \"[0-9]+(\.[0-9]+){2}\"/\"version\": \"$ver\"/" "$f"
    done
    for f in packages/*/src/*/core/constants.py; do
        [[ -f "$f" ]] || continue
        sed -Ei "s/^VERSION: Final\[str\] = \"[0-9]+(\.[0-9]+){2}\"/VERSION: Final[str] = \"$ver\"/" "$f"
    done
}


last_tag() {
    git tag --list 'v*' --sort=-v:refname 2>/dev/null | head -1
}


check_no_rewind() {
    local latest="$1" new_ver="$2"
    [[ -z "$latest" ]] && return 0
    local latest_ver="${latest#v}"
    if [[ "$(printf '%s\n%s\n' "$new_ver" "$latest_ver" | sort -V | head -1)" == "$new_ver" ]]; then
        echo "[calver] refusing to rewind: $new_ver is not above $latest" >&2
        exit 1
    fi
}


bump() {
    local cur_year cur_month
    cur_year=$((10#$(date +%Y)))
    cur_month=$((10#$(date +%m)))

    if [[ -z "$(last_tag)" ]]; then
        YEAR=$cur_year
        MONTH=$cur_month
        PATCH=0
    elif (( cur_year > YEAR || (cur_year == YEAR && cur_month > MONTH) )); then
        YEAR=$cur_year
        MONTH=$cur_month
        PATCH=0
    else
        if (( cur_year < YEAR )) || { (( cur_year == YEAR )) && (( cur_month < MONTH )); }; then
            echo "[calver] warning: local clock ($(printf '%04d' "$cur_year")-$(printf '%02d' "$cur_month")) is behind last release ($(printf '%04d' "$YEAR")-$(printf '%02d' "$MONTH")); keeping last release's year.month" >&2
        fi
        PATCH=$((PATCH + 1))
    fi
}


generate_changelog() {
    local ver
    ver="$(printf '%04d.%02d.%d' "$YEAR" "$MONTH" "$PATCH")"
    cz changelog --incremental --unreleased-version "v$ver"
}


main() {
    read_version

    local old_ver new_ver
    old_ver="$(printf '%04d.%02d.%d' "$YEAR" "$MONTH" "$PATCH")"
    bump
    new_ver="$(printf '%04d.%02d.%d' "$YEAR" "$MONTH" "$PATCH")"
    check_no_rewind "$(last_tag)" "$new_ver"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "$new_ver"
        return
    fi

    echo "[calver] $old_ver -> $new_ver" >&2
    write_version
    generate_changelog
    echo "$new_ver"
}

main "$@"
