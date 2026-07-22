#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail
ROOT="$(dirname "$(realpath "$0")")/../.."
source "$ROOT/package.env" || { echo "Failed to source $ROOT/package.env"; exit 1; }

while IFS= read -r -d '' license || [[ -n "$license" ]]; do
  original="${license%.license}"
  if [[ ! -e "$original" ]]; then
    echo "Removing orphan license: $license"
    rm -f "$license" || true
  fi
done < <(find "$ROOT" -type f -name "*.license" -print0 2>/dev/null || true)

SOFTWARE_LIC="Unlicense"
DATA_LIC="CC0-1.0"
YEAR=$(date +%Y)

if [[ -z "${COPYRIGHT:-}" ]]; then
    echo "COPYRIGHT is not set or is empty"
    exit 1
fi
echo "COPYRIGHT is set: $COPYRIGHT"

LICENSE_FILES=(
    "$ROOT/configs/REUSE.toml"
    "$ROOT/.zensical.toml"
)

for license_file in "${LICENSE_FILES[@]}"; do
    if [[ ! -f "$license_file" ]]; then
        echo "License file $license_file does not exist"
        exit 1
    fi
    if ! grep -Pv '^[^sS]+\s*SPDX-' "$license_file" | grep -q "$COPYRIGHT" 2>/dev/null; then
        echo "License file $license_file does not contain COPYRIGHT"
        exit 1
    fi
    if ! grep -Pv '^[^sS]+\s*SPDX-' "$license_file" | grep -q "$YEAR" 2>/dev/null; then
        echo "Current year ($YEAR) could not be found in $license_file"
        exit 1
    fi
    if ! grep -Pv '^[^sS]+\s*SPDX-' "$license_file" | grep -q -e "$SOFTWARE_LIC" -e "$DATA_LIC" 2>/dev/null; then
        echo "Neither license ($SOFTWARE_LIC) nor ($DATA_LIC) found in $license_file"
        exit 1
    fi
done

LICENSE_SHORT_FILES=(
    "$ROOT/pyproject.toml"
)

for file_path in "${LICENSE_SHORT_FILES[@]}"; do
    if [ ! -f "$file_path" ]; then
        echo "File not found: $file_path"
        exit 1
    fi
    if ! grep -q "$SOFTWARE_LIC" "$file_path" 2>/dev/null; then
        echo "License ($SOFTWARE_LIC) not found in $file_path"
        exit 1
    fi
done

FILES=()

IGNORE=(
    '^bin/lint/licenses\.sh$'
    '^bin/install/wrap\.sh$'
    '^LICENSES/'
    '^configs/prompt/'
    '^configs/REUSE\.toml$'
    '^packages/docs/REUSE\.toml$'
    '^packages/docs/src/.+\.md$'
    'uv\.lock$'
    'pnpm-lock\.yaml$'
)

should_ignore() {
    local name="$1"
    for pattern in "${IGNORE[@]}"; do
        if [[ "$name" =~ $pattern ]]; then
            return 0
        fi
    done
    return 1
}

filter_and_collect() {
    local input_file
    while IFS= read -r input_file || [[ -n "$input_file" ]]; do
        [[ -z "$input_file" ]] && continue
        if should_ignore "$input_file"; then
            continue
        fi
        if [[ -e "$input_file" ]]; then
            FILES+=("$input_file")
        fi
    done
}

if [ "$#" -gt 0 ]; then
    filter_and_collect < <(printf "%s\n" "$@")
else
    filter_and_collect < <(git ls-files 2>/dev/null || true)
fi

SOFTWARE=(
    '\.py$'
    '\.sh$'
)

CC0_FILES=(
    '\.(jpg|png|ico|webp|avif)$'
    '\.gitignore$'
    '\.gitattributes$'
    '\.env$'
    'package\.env$'
    '\.dockerignore$'
    'shellcheckrc$'
    '\.(md|txt|yaml|yml|json|toml)$'
)

UNL_FILES=(
    'Makefile$'
    'Dockerfile$'
)

UNL_FOLDERS=()

unl_to_annotate=()
cc0_to_annotate=()

matches_pattern() {
    local value="$1"
    shift
    local -a patterns=("$@")

    for pattern in "${patterns[@]}"; do
        if [[ "$value" =~ $pattern ]]; then
            return 0
        fi
    done
    return 1
}

for file in "${FILES[@]}"; do
    file_name="${file##*/}"
    file_dir="${file%/*}"
    if matches_pattern "$file_dir" "${UNL_FOLDERS[@]}"; then
        unl_to_annotate+=("$file")
        continue
    fi
    if matches_pattern "$file_name" "${SOFTWARE[@]}"; then
        unl_to_annotate+=("$file")
        continue
    fi
    if matches_pattern "$file_name" "${UNL_FILES[@]}"; then
        unl_to_annotate+=("$file")
        continue
    fi
    if matches_pattern "$file_name" "${CC0_FILES[@]}"; then
        cc0_to_annotate+=("$file")
        continue
    fi
done

if [ ${#unl_to_annotate[@]} -gt 0 ]; then
    echo "annotating Unlicense"
    reuse annotate -c "$COPYRIGHT" -l "$SOFTWARE_LIC" -y "$YEAR" --merge-copyrights --fallback-dot-license "${unl_to_annotate[@]}" || {
        echo "Failed to annotate Unlicense files"
        exit 1
    }
else
    echo "No Unlicense files to annotate"
fi

if [ ${#cc0_to_annotate[@]} -gt 0 ]; then
    echo "annotating CC0"
    reuse annotate -c "$COPYRIGHT" -l "$DATA_LIC" -y "$YEAR" --merge-copyrights --fallback-dot-license "${cc0_to_annotate[@]}" || {
        echo "Failed to annotate CC0 files"
        exit 1
    }
else
    echo "No CC0 files to annotate"
fi

if ! reuse lint; then
    echo "Linting failed!"
    exit 1
fi
