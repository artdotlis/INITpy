#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail

ROOT="$(dirname "$(realpath "$0")")/../.."
ENV_MK="$ROOT/.env.mk"

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    # Match "KEY := value" (space before := optional)
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*:?[[:space:]]*=[[:space:]]*(.+)[[:space:]]*$ ]]; then
        key="${BASH_REMATCH[1]}"
        value="${BASH_REMATCH[2]}"
        value="${value%\"}"; value="${value#\"}"
        value="${value%\'}"; value="${value#\'}"
        export "$key"="$value"
    fi
done < "$ENV_MK"
