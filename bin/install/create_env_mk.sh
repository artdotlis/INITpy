#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail

declare -A SEEN_FILES
declare -A ENV_VARS

ROOT="$(dirname "$(realpath "$0")")/../.."
ENV_MK="$ROOT/.env.mk"

load_env_file() {
    local env_file="$1"

    if [[ "$env_file" != /* ]]; then
        env_file="$(cd "$(dirname "$env_file")" && pwd)/$(basename "$env_file")"
    fi

    [ -f "$env_file" ] || return

    if [[ -n "${SEEN_FILES[$env_file]+x}" ]]; then
        return
    fi
    SEEN_FILES[$env_file]=1

    # shellcheck disable=SC2094
    while IFS= read -r line || [ -n "$line" ]; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue

        if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"

            # Strip quotes
            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"

            if [ -z "${!key+x}" ]; then
                printf '%s := %s\n' "$key" "$value"
            fi
            ENV_VARS["$key"]="$value"

            if [[ -f "$value" && "$value" =~ (^\.env|\.env$) && ! "$value" =~ license ]]; then
                # shellcheck disable=SC2094
                local base_dir
                base_dir="$(dirname "$env_file")"

                local potential_path="$value"
                if [[ "$potential_path" != /* ]]; then
                    potential_path="$base_dir/$potential_path"
                fi

                load_env_file "$potential_path"
            fi
        fi
    done < "$env_file"
}

if [[ ! -f "$ENV_MK" ]]; then
    load_env_file "$ROOT/package.env" > "$ENV_MK" 2>/dev/null || true

    FNM_HOME="${ENV_VARS[FNM_HOME]:-}"
    UV_PYTHON_BIN_DIR="${ENV_VARS[UV_PYTHON_BIN_DIR]:-}"
    UV_INSTALL_DIR="${ENV_VARS[UV_INSTALL_DIR]:-}"
    PNPM_HOME="${ENV_VARS[PNPM_HOME]:-}"

    UVE="$ROOT/$UV_INSTALL_DIR/uv"
    PNPME="$ROOT/$PNPM_HOME/bin/pnpm"

    declare -a PATH_DIRS
    PATH_DIRS+=("$ROOT/$FNM_HOME/aliases/default/bin")
    PATH_DIRS+=("$ROOT/$FNM_HOME")
    PATH_DIRS+=("$ROOT/$UV_PYTHON_BIN_DIR")
    PATH_DIRS+=("$ROOT/$UV_INSTALL_DIR")
    PATH_DIRS+=("$ROOT/$PNPM_HOME/bin")

    PATH_BUILD="$PATH"
    declare -A _seen
    for d in "${PATH_DIRS[@]}"; do
        if [[ -z "${_seen[$d]:-}" ]]; then
            PATH_BUILD="$PATH_BUILD:$d"
            _seen[$d]=1
        fi
    done

    {
        printf 'PATH := %s\n' "$PATH_BUILD"
        printf 'PNPME := %s\n' "$PNPME"
        printf 'UVE := %s\n' "$UVE"
        printf 'SHELL := /bin/bash\n'
    } >> "$ENV_MK" 2>/dev/null || true

fi
