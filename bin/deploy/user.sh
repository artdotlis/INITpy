#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

#!/bin/bash

set -euo pipefail

USERNAME="${USERNAME:-devu}"
USER_UID="${USER_UID:-1000}"
USER_GID="${USER_GID:-1000}"
HOME_MAIN="/home/${USERNAME}"

# Validate required variables
[ -n "${USERNAME}" ] || { echo "ERROR: USERNAME is empty!" >&2; exit 1; }
[ -n "${USER_UID}" ] || { echo "ERROR: USER_UID is empty!" >&2; exit 1; }
[ -n "${USER_GID}" ] || { echo "ERROR: USER_GID is empty!" >&2; exit 1; }

# Detect OS
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "${ID}"
    else
        echo "unknown"
    fi
}

# Function: AlmaLinux / RHEL / CentOS
setup_alma_rhel() {
    local username="$1"
    local uid="$2"
    local gid="$3"
    local homedir="$4"

    # Group: ensure it exists with correct GID
    local group_name
    group_name=$(getent group "$gid" | cut -d: -f1 || true)
    if [ -n "$group_name" ] && [ "$group_name" != "$username" ]; then
        groupmod --new-name "$username" "$group_name"
    elif [ -z "$group_name" ]; then
        groupadd --gid "$gid" "$username"
    fi

    # User: ensure it exists with correct UID
    local user_name
    user_name=$(getent passwd "$uid" | cut -d: -f1 || true)
    if [ -n "$user_name" ] && [ "$user_name" != "$username" ]; then
        usermod \
            --login "$username" \
            --home "$homedir" \
            --move-home \
            --gid "$gid" \
            "$user_name"
    elif [ -z "$user_name" ]; then
        useradd \
            --uid "$uid" \
            --gid "$gid" \
            --create-home \
            --home-dir "$homedir" \
            --shell /bin/bash \
            "$username"
    fi

    # Ensure home directory ownership
    mkdir -p "$homedir/.local/bin"
    chown -R "$uid:$gid" "$homedir"
}

# Function: Alpine
setup_alpine() {
    local username="$1"
    local uid="$2"
    local gid="$3"
    local homedir="$4"

    # Free the requested UID and name before recreating
    local user_name
    user_name="$(getent passwd "$uid" | cut -d: -f1 || true)"
    if [ -n "$user_name" ] && [ "$user_name" != "$username" ]; then
        deluser "$user_name" 2>/dev/null || true
    fi
    if getent passwd "$username" >/dev/null 2>&1; then
        deluser "$username" 2>/dev/null || true
    fi

    # Free the requested GID and name before recreating
    local group_name
    group_name="$(getent group "$gid" | cut -d: -f1 || true)"
    if [ -n "$group_name" ] && [ "$group_name" != "$username" ]; then
        delgroup "$group_name" 2>/dev/null || true
    fi
    if getent group "$username" >/dev/null 2>&1; then
        delgroup "$username" 2>/dev/null || true
    fi

    # Create fresh group and user
    addgroup -g "$gid" "$username"
    adduser \
        -u "$uid" \
        -G "$username" \
        -s /bin/bash \
        -D \
        -H \
        "$username"

    # Ensure home directory and permissions
    mkdir -p "$homedir/.local/bin"
    chown -R "$uid:$gid" "$homedir"
}
# Main logic
main() {
    local distro
    distro=$(detect_distro)

    case "$distro" in
        almalinux|rhel|centos|rockylinux)
            setup_alma_rhel "$USERNAME" "$USER_UID" "$USER_GID" "$HOME_MAIN"
            ;;
        alpine)
            setup_alpine "$USERNAME" "$USER_UID" "$USER_GID" "$HOME_MAIN"
            ;;
        *)
            echo "ERROR: Unsupported or unknown distribution: $distro" >&2
            exit 1
            ;;
    esac
}

# Run main
main
