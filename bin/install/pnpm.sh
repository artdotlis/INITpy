#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense
set -euo pipefail

ROOT="$(dirname "$(realpath "$0")")/../.."
set -a

source "$ROOT/bin/install/load_env_mk.sh"

echo "$PNPM_HOME"
echo "$PNPM_VERSION"

if [[ ! -x "$PNPM_HOME/bin" ]]; then
    curl -fsSL https://get.pnpm.io/install.sh | sh -
fi

set +a
