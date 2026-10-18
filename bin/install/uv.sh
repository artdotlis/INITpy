#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense
set -euo pipefail

ROOT="$(dirname "$(realpath "$0")")/../.."
set -a

source "$ROOT/bin/install/load_env_mk.sh"

[[ -d "$UV_INSTALL_DIR" ]] || (curl -LsSf "https://astral.sh/uv/$UV_VERSION/install.sh" | sh)
"$UVE" python install "$PYV" --force
rm -rf .venv
"$UVE" venv --python="$PYV" --relocatable --link-mode=copy --seed
"$UVE" pip install --upgrade pip

set +a
