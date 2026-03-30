#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

FILES=()

filter_and_collect() {
    local input_file
    while IFS= read -r input_file; do
        [[ -z "$input_file" ]] && continue
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

for file in "${FILES[@]}"; do
  if git lfs ls-files | grep -q "$file"; then
    status=$(git status --porcelain "$file")
    if [[ "$status" =~ ^D || -z "$status" ]]; then
      continue
    fi
    size=$(stat --format=%s "$file")
    if [ "$size" -gt 512000 ]; then
      echo "LFS file $file is larger than 500 KB ($size bytes). Please reduce its size."
      exit 1
    fi
  fi
done
