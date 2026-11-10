# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Package creation for scaffolding."""

import shutil

from pathlib import Path
from typing import Any

from scaffolder.template import render_template


def create_package(path: Path, package_name: str, context: dict[str, Any], /) -> None:
    """Create a new package and write its ``pyproject.toml``.

    Args:
        path: Root of the generated project.
        package_name: Name of the package to create.
        context: Template variables for the package pyproject.
    """
    pkg_dir = path / "packages" / package_name
    (pkg_dir / "src" / package_name).mkdir(parents=True, exist_ok=True)
    (pkg_dir / "pyproject.toml").write_text(
        render_template("root/package.toml.jinja", context)
    )
    for item in (path / "packages").iterdir():
        if item.name not in ("docs", package_name):
            shutil.rmtree(item)
