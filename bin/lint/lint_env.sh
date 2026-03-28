#!/bin/bash

ROOT="$(dirname "$(realpath "$0")")/../.."

# SHOULD ALWAYS BE CHANGED depending on the project: currently StrainInfo

ROOT_ENV="$ROOT/package.env"

ENV_FILES=("$ROOT_ENV" "$PKG1_ENV")

ALL_ENV=(
    "MAKEFILE_LIST"
    "HOME"
    "PATH" 
    "MAKE"
)

check_env_uniqueness() {
    cmd="$(awk 'match($0, /^.*=/) {print substr($0, RSTART, RLENGTH-1)}' "$1")"
    while SEP=' ' read -ra names; do
        for name in "${names[@]}"; do
            for known in "${ALL_ENV[@]}"; do
                if [[ "$known" = "$name" ]]; then
                    echo "found duplicate in $1 -> $name [FAIL]"
                    exit 1
                fi
            done
            ALL_ENV+=("$name")
        done
    done <<<"$cmd"
}

check_name_occurrence() {
    norm_reg="\${\?$1}\?"
    make_reg="\$($1)"
    docker_reg="\${\?$1}\?\|environment:\s*$1"
    if [[ "$2" = 1 ]]; then
        norm_reg="$1:\?\s*="
        make_reg="$1:\?="
        docker_reg="$1\s*[:=]"
    fi
    if [[ "$(grep -Rnw "$ROOT/bin" -e "$norm_reg" | wc -l)" -gt 0 ]]; then
        return 0
    fi
    if [[ "$(grep -c -e "$make_reg" "$ROOT/Makefile")" -gt 0 ]]; then
        return 0
    fi
    if [[ "$(grep -c -e "$docker_reg" "$ROOT/Dockerfile")" -gt 0 ]]; then
        return 0
    fi
    if [[ "$(grep -c -e "$docker_reg" "$ROOT/docker-compose.yml")" -gt 0 ]]; then
        return 0
    fi
    if [[ "$(grep -Rnw "$ROOT/.devcontainer" -e "$docker_reg" | wc -l)" -gt 0 ]]; then
        return 0
    fi
    if [[ "$(grep -Rnw "$ROOT/configs" -e "$docker_reg" | wc -l)" -gt 0 ]]; then
        return 0
    fi
    if [[ "$(grep --exclude-dir={__pycache__} -Rnw "$PKGS" -e "$norm_reg" | wc -l)" -gt 0 ]]; then
        return 0
    fi
    if [[ "$2" = 1 ]]; then
        return 1
    fi
    if [[ "$(grep --exclude-dir={__pycache__} -Rnw "$PKGS" -e "$1" | wc -l)" -gt 0 ]]; then
        return 0
    fi
    return 1
}

check_name_rev_occurrence() {
    while SEP=' ' read -ra names; do
        for name in "${names[@]}"; do
            found=0
            for known in "${ALL_ENV[@]}"; do
                if [[ "$known" = "$name" ]]; then
                    found=1
                fi
            done
            if [[ "$found" = 0 ]]; then
                check_name_occurrence "$name" 1
                if [[ "$?" = 1 ]]; then
                    echo "[FAIL] could not find $name -> $1"
                    exit 1
                fi
                echo "[OK] $name found"
            fi
            ALL_ENV+=("$name")
        done
    done <<<"$(awk "$2" "$1")"
}

echo "checking env files"
for env in "${ENV_FILES[@]}"; do
    if [[ ! -f "$env" ]]; then
        echo "missing env file -> $env"
    fi
    check_env_uniqueness "$env"
    echo "[OK] $env"
done
echo "-- occurrence check --"
for name in "${ALL_ENV[@]}"; do
    check_name_occurrence "$name" 0
    if [[ "$?" = 1 ]]; then
        echo "[FAIL] could not find $name"
        exit 1
    fi
    echo "[OK] $name found"
done
echo "-- reverse occurrence check --"
cmd='match($0, /\$[({][A-Z_]+[)}]/) {print substr($0, RSTART+2, RLENGTH-3)}'
check_name_rev_occurrence "$ROOT/Makefile" "$cmd"
check_name_rev_occurrence "$ROOT/Dockerfile" "$cmd"
check_name_rev_occurrence "$ROOT/docker-compose.yml" "$cmd"

while SEP=' ' read -ra files; do
    for file in "${files[@]}"; do
        check_name_rev_occurrence "$file" "$cmd"
    done
done <<<"$(find "$ROOT/.devcontainer" -type f)"

while SEP=' ' read -ra files; do
    for file in "${files[@]}"; do
        check_name_rev_occurrence "$file" "$cmd"
    done
done <<<"$(find "$ROOT/configs" -type f)"

while SEP=' ' read -ra files; do
    for file in "${files[@]}"; do
        check_name_rev_occurrence "$file" "$cmd"
    done
done <<<"$(find "$PKGS" -type f -regex '.*/packages/[^/]*/[^/]*')"

cmd='match($0, /\$[A-Z_]+/) {print substr($0, RSTART+1, RLENGTH-1)}'
while SEP=' ' read -ra files; do
    for file in "${files[@]}"; do
        check_name_rev_occurrence "$file" "$cmd"
    done
done <<<"$(find "$ROOT/bin" -type f)"

while SEP=' ' read -ra files; do
    for file in "${files[@]}"; do
        check_name_rev_occurrence "$file" "$cmd"
    done
done <<<"$(find "$PKGS" -type f -regex '.*/packages/[^/]*/bin/.*')"
