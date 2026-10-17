#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail
ROOT="$(dirname "$(realpath "$0")")/.."

if [[ "${DISABLE_GIT_ADD:-0}" == "1" ]]; then
    echo "Skipping unstaged check (DISABLE_GIT_ADD=1)"
    exit 0
fi

if ! git -C "$ROOT" diff --quiet --exit-code; then
    echo "ERROR: Unstaged changes found!"
    git -C "$ROOT" diff
    exit 1
fi

echo "No unstaged changes. Proceeding..."
