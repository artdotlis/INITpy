#!/bin/bash

echo "prep setup"
dnf clean all && rm -rf /var/cache/dnf
dnf -y install dnf-plugins-core
dnf upgrade --refresh -y
echo "prep finished"
