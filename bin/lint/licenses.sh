#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

ROOT="$(dirname "$(realpath "$0")")/../.."
source "$ROOT/package.env"

while IFS= read -r -d '' license; do
  original="${license%.license}"

  if [[ ! -e "$original" ]]; then
    echo "Removing orphan license: $license"
    rm "$license"
  fi
done < <(find "$ROOT" -type f -name "*.license" -print0)

SOFTWARE_LIC="Unlicense"
DATA_LIC="CC0-1.0"
YEAR=$(date +%Y)

if [[ -n "$COPYRIGHT" ]]; then
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
        if ! grep -Pv '^[^s]+\s*SPDX-' "$license_file" | grep -q "$COPYRIGHT"; then
            echo "License file $license_file does not exist or COPYRIGHT not found"
            exit 1
        fi
        if ! grep -Pv '^[^s]+\s*SPDX-' "$license_file" | grep -q "$YEAR"; then
            echo "Current year ($YEAR) could not be found in $license_file"
            exit 1
        fi
        if ! grep -Pv '^[^s]+\s*SPDX-' "$license_file" | grep -q -e "$SOFTWARE_LIC" -e "$DATA_LIC"; then
            echo "Neither license ($SOFTWARE_LIC) nor ($DATA_LIC) found in $license_file"
            exit 1
        fi
    done
else
    echo "COPYRIGHT is not set or is empty"
    exit 1
fi

# For python projects
if ! grep -q "$SOFTWARE_LIC" "$ROOT/pyproject.toml"; then
    echo "License ($SOFTWARE_LIC) not be found in pyproject.toml"
    exit 1
fi

FILES=()

IGNORE=(
    '^configs/prompt/.+$'
    '^bin/lint/licenses.sh'
    '^bin/install/wrap.sh'
    '^LICENSES/.+$'
    '^configs/REUSE.toml'
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
    while IFS= read -r input_file; do
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
    filter_and_collect < <(git ls-files)
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
    'uv\.lock$'
    '\.dockerignore$'
    'shellcheckrc$'
    '\.(md|txt|yaml|yml|json|toml)$'
)

UNL_FILES=(
    'Makefile$'
    'Dockerfile$'
)

UNL_FOLDERS=(
    '^docs/'
)

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
    reuse annotate -c "$COPYRIGHT" -l "$SOFTWARE_LIC" -y "$YEAR" --merge-copyrights --fallback-dot-license "${unl_to_annotate[@]}"
else
    echo "No Unlicense files to annotate"
fi

if [ ${#cc0_to_annotate[@]} -gt 0 ]; then
    echo "annotating CC0"
    reuse annotate -c "$COPYRIGHT" -l "$DATA_LIC" -y "$YEAR" --merge-copyrights --fallback-dot-license "${cc0_to_annotate[@]}"
else
    echo "No CC0 files to annotate"
fi

if ! reuse lint; then
    echo "Linting failed!"
    exit 1
fi
