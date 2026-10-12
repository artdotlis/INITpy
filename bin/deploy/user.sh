#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

set -euo pipefail

USERNAME="${USERNAME:-devu}"
USER_UID="${USER_UID:-1000}"
USER_GID="${USER_GID:-1000}"
HOME_MAIN="/home/${USERNAME}"

[ -n "${USERNAME}" ] || { echo "ERROR: USERNAME is empty!" >&2; exit 1; }
[ -n "${USER_UID}" ] || { echo "ERROR: USER_UID is empty!" >&2; exit 1; }
[ -n "${USER_GID}" ] || { echo "ERROR: USER_GID is empty!" >&2; exit 1; }

GROUP_NAME="$(getent group "${USER_GID}" | cut -d: -f1 || true)"


if [ -n "${GROUP_NAME}" ] && [ "${GROUP_NAME}" != "${USERNAME}" ]; then
    groupmod \
        --new-name "${USERNAME}" \
        "${GROUP_NAME}"
elif [ -z "${GROUP_NAME}" ]; then
    groupadd \
        --gid "${USER_GID}" \
        "${USERNAME}"
fi

USER_NAME="$(getent passwd "${USER_UID}" | cut -d: -f1 || true)"

if [ -n "${USER_NAME}" ] && [ "${USER_NAME}" != "${USERNAME}" ]; then
    usermod \
        --login "${USERNAME}" \
        --home "${HOME_MAIN}" \
        --move-home \
        --gid "${USER_GID}" \
        "${USER_NAME}"
elif [ -z "${USER_NAME}" ]; then
    useradd \
        --uid "${USER_UID}" \
        --gid "${USER_GID}" \
        --create-home \
        --home-dir "${HOME_MAIN}" \
        --shell /bin/bash \
        "${USERNAME}"
fi
mkdir -p "${HOME_MAIN}/.local/bin"
chown -R "${USER_UID}:${USER_GID}" "${HOME_MAIN}"
