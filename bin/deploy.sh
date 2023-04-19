#!/bin/bash

root_path=$(dirname "$(realpath "$0")")

echo "prepare step"
/bin/bash "$root_path/deploy/prep.sh"
echo -e "---\ninstalling requirements"
/bin/bash "$root_path/deploy/req.sh"
echo -e "---\ninstalling package"
/bin/bash "$root_path/deploy/init.sh"
echo -e "---\ncleaning installation"
/bin/bash "$root_path/deploy/clean.sh"
echo -e "---\ncopy health"
cp "$root_path/deploy/health.sh" / && chmod +x /health.sh
echo -e "---\ncopy entrypoint"
cp "$root_path/deploy/entrypoint.sh" / && chmod +x /entrypoint.sh
echo "---"
