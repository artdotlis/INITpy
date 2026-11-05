# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Environment variable updates for a generated project."""

import re
from pathlib import Path

from shared_utils.core.names import package_env_file
from shared_utils.core.names import package_env_var


def update_copyright(path: Path, copyright: str, /) -> None:
    """Set COPYRIGHT in the project's ``package.env``.

    Args:
        path: Root of the generated project.
        copyright: Copyright holder of the new project.
    """
    package_env = path / "package.env"
    content = package_env.read_text()
    content = re.sub(r"^COPYRIGHT=.*$", f'COPYRIGHT="{copyright}"', content, flags=re.M)
    package_env.write_text(content)


def update_envs(path: Path, package_name: str, /) -> None:
    """Point package env variables at the new package.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
    package_env = path / "package.env"
    content = package_env.read_text()
    content = content.replace(
        "PKG_SCAF=packages/scaffolder",
        f"{package_env_var(package_name)}=packages/{package_name}",
    )
    content = content.replace("PKG_SHAR=packages/shared_utils", "")
    content = content.replace(
        "SCAF_ENV=packages/scaffolder/.env",
        f"{package_env_file(package_name)}=packages/{package_name}",
    )
    package_env.write_text(content)
    lint_env = path / "bin" / "lint" / "lint_env.sh"
    content = lint_env.read_text()
    content = content.replace("SCAF_ENV", package_env_file(package_name))
    lint_env.write_text(content)
