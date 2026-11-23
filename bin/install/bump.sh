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
CHANGELOG="CHANGELOG.md"


read_version() {
    local ver
    ver="$(grep -Eom1 '^version = "[0-9]+(\.[0-9]+){2}"' "$PYPROJECT" | grep -Eo '[0-9]+(\.[0-9]+){2}' || true)"
    if [[ -z "$ver" ]]; then
        echo "[calver] no version found in $PYPROJECT" >&2
        exit 1
    fi
    FILE_VER="$ver"
    IFS='.' read -r YEAR MONTH PATCH <<<"$ver"
    YEAR=$((10#$YEAR))
    MONTH=$((10#$MONTH))
    PATCH=$((10#$PATCH))
}

SCHEME="calver"

fmt_ver() {
    printf '%04d.%02d.%d' "$YEAR" "$MONTH" "$PATCH"
}

detect_scheme() {
    local major="${1#v}"
    major="${major%%.*}"
    if [[ "$major" =~ ^[0-9]{4}$ ]] && (( 10#$major >= 2000 )); then
        SCHEME="calver"
    else
        SCHEME="semver"
    fi
}

write_version() {
    local ver
    ver="$(fmt_ver)"
    sed -Ei "s/^version = \"[0-9]+(\.[0-9]+){2}\"/version = \"$ver\"/" "$PYPROJECT"
    if [[ -f "$PACKAGE_JSON" ]]; then
        sed -Ei "s/\"version\": \"[0-9]+(\.[0-9]+){2}\"/\"version\": \"$ver\"/" "$PACKAGE_JSON"
    fi
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


FETCHED_TAGS=""
last_tag() {
    if [[ -z "$FETCHED_TAGS" ]]; then
        git fetch --tags --quiet 2>/dev/null || \
            echo "[calver] warning: could not fetch tags; using local tags only" >&2
        FETCHED_TAGS=1
    fi
    git tag --list 'v*' --sort=-v:refname 2>/dev/null | head -1
}

changelog_version() {
    grep -Eom1 '^## v[0-9]+(\.[0-9]+){2}' "$CHANGELOG" 2>/dev/null | grep -Eo '[0-9]+(\.[0-9]+){2}' || true
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
    local latest="$1"
    local cur_year cur_month
    cur_year=$((10#$(date +%Y)))
    cur_month=$((10#$(date +%m)))

    if [[ "$SCHEME" == "semver" ]]; then
        echo "[calver] previous version is semver; switching to calver" >&2
        YEAR=$cur_year
        MONTH=$cur_month
        PATCH=0
        return
    fi

    if [[ -z "$latest" ]]; then
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
    local ver prev rev tagged=""
    ver="$(fmt_ver)"
    if [[ -z "$(last_tag)" ]]; then
        prev="$(changelog_version)"
        if [[ -z "$prev" ]]; then
            cz changelog --unreleased-version "v$ver"
            return
        fi
        rev="$(git log --format=%H -S"version = \"$prev\"" -- "$PYPROJECT" | head -1)"
        if [[ -z "$rev" ]]; then
            echo "[calver] no commit releases $prev, cannot anchor the changelog" >&2
            exit 1
        fi
        git tag "v$prev" "$rev"
        tagged="$prev"
    fi
    cz changelog --incremental --unreleased-version "v$ver"
    if [[ -n "$tagged" ]]; then
        git tag -d "v$tagged" >/dev/null
    fi
}


main() {
    read_version
    detect_scheme "$FILE_VER"

    local old_ver new_ver latest
    latest="$(last_tag)"
    old_ver="$FILE_VER"
    bump "$latest"
    new_ver="$(fmt_ver)"

    if [[ "$new_ver" == "$old_ver" ]]; then
        PATCH=$((PATCH + 1))
        new_ver="$(fmt_ver)"
    fi

    check_no_rewind "$latest" "$new_ver"

    if [[ "${1:-}" == "--dry-run" ]]; then
        echo "$new_ver"
    else
        echo "[calver] $old_ver -> $new_ver" >&2
        generate_changelog
        write_version
        echo "$new_ver"
    fi
}

main "$@"
