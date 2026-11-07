#!/bin/bash

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense
set -euo pipefail

echo "installing requirements"
dnf -y install python3.13 python3.13-pip git git-lfs make wget coreutils-single jq vim which openssl
ln -s /usr/bin/python3.13 /usr/bin/python
ln -s /usr/bin/pip3.13 /usr/bin/pip
dnf -y group install "Development Tools"
dnf -y install bzip2-devel ncurses-devel libffi-devel \
    readline-devel openssl-devel sqlite-devel tk-devel
echo "requirements installed"
