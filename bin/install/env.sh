#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense


# Single source of env truth.
#
# Executed -> prints make assignments  (Makefile: $(eval $(shell env.sh)))
# Sourced  -> exports the same vars for shell scripts
#
# Merges package.env plus any *.env file it references (e.g. packages/web/.env).
# Ambient values always win; this only fills gaps.

set -euo pipefail

ROOT="$(dirname "$(realpath "${BASH_SOURCE[0]}")")/../.."
if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    MODE="make"
else
    MODE="sh"
fi

declare -A SEEN_FILES=()
declare -a KEYS=()
declare -a VALS=()
declare -A KEY_IDX=()

add() {
    local key="$1"
    local value="$2"
    if [[ -n "${KEY_IDX[$key]:-}" ]]; then
        VALS[${KEY_IDX[$key]}]="$value"
    else
        KEY_IDX[$key]="${#KEYS[@]}"
        KEYS+=("$key")
        VALS+=("$value")
    fi
}

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

    local line key value potential_path
    # shellcheck disable=SC2094
    while IFS= read -r line || [ -n "$line" ]; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue

        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=(.*)$ ]]; then
            key="${BASH_REMATCH[1]}"
            value="${BASH_REMATCH[2]}"

            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"

            add "$key" "$value"

            if [[ -f "$value" && "$value" =~ (^\.env|\.env$) && ! "$value" =~ license ]]; then
                potential_path="$value"
                if [[ "$potential_path" != /* ]]; then
                    potential_path="$(dirname "$env_file")/$potential_path"
                fi
                load_env_file "$potential_path"
            fi
        fi
    done < "$env_file"
}

load_env_file "$ROOT/package.env"

get() {
    if [[ -n "${KEY_IDX[$1]:-}" ]]; then
        printf '%s' "${VALS[${KEY_IDX[$1]}]}"
    fi
}

_dir_uv_install="$(get UV_INSTALL_DIR)"
_dir_pnpm="$(get PNPM_HOME)"

path_dirs=(
    "$ROOT/$(get FNM_HOME)/aliases/default/bin"
    "$ROOT/$(get FNM_HOME)"
    "$ROOT/$(get UV_PYTHON_BIN_DIR)"
    "$ROOT/$_dir_uv_install"
    "$ROOT/$_dir_pnpm/bin"
)

if [[ "$MODE" == make ]]; then
    # ?= keeps ambient (environment) values winning over package.env
    for i in "${!KEYS[@]}"; do
        printf '%s ?= %s\n' "${KEYS[$i]}" "${VALS[$i]}"
    done
    # shellcheck disable=SC2016  # $(PATH) is for make, not the shell
    printf 'PATH := $(PATH):%s\n' "$(IFS=:; printf '%s' "${path_dirs[*]}")"
    printf 'UVE := %s\n' "$ROOT/$_dir_uv_install/uv"
    printf 'PNPME := %s\n' "$ROOT/$_dir_pnpm/bin/pnpm"
    printf 'SHELL := /bin/bash\n'
else
    for i in "${!KEYS[@]}"; do
        key="${KEYS[$i]}"
        if [[ -z "${!key+x}" ]]; then
            printf -v "$key" '%s' "${VALS[$i]}"
            export "${key?}"
        fi
    done
    UVE="$ROOT/$_dir_uv_install/uv"
    PNPME="$ROOT/$_dir_pnpm/bin/pnpm"
    export UVE PNPME
    for dir in "${path_dirs[@]}"; do
        case ":$PATH:" in
            *":$dir:"*) ;;
            *) PATH="$PATH:$dir" ;;
        esac
    done
    export PATH
fi
