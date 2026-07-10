#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense
set -euo pipefail

echo "prep setup"
dnf clean all && rm -rf /var/cache/dnf
update-ca-trust extract
dnf upgrade -y
dnf -y install epel-release
dnf -y install dnf-plugins-core
dnf config-manager --set-enabled crb
dnf upgrade --refresh -y
echo "prep finished"
