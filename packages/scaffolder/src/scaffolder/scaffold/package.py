# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Package creation for scaffolding."""

from shared_utils.files import update_pyproject_path
from shared_utils.files import clean_pyproject_dependencies
from shared_utils.files import update_pyproject_description
from shared_utils.files import update_pyproject_name
import shutil

from pathlib import Path


def create_package(path: Path, package_name: str, description: str) -> None:
    """Create new package, copy pyproject.toml, clean packages/."""
    pkg_dir = path / "packages" / package_name
    (pkg_dir / "src" / package_name).mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        Path(__file__).resolve().parent.parent.parent / "shared_utils" / "pyproject.toml",
        pkg_dir / "pyproject.toml",
    )
    update_pyproject_name(pkg_dir / "pyproject.toml", package_name)
    update_pyproject_description(pkg_dir / "pyproject.toml", description)
    clean_pyproject_dependencies(pkg_dir / "pyproject.toml")
    update_pyproject_path(pkg_dir / "pyproject.toml", package_name)
    for item in (path / "packages").iterdir():
        if item.name not in ("docs", package_name):
            shutil.rmtree(item) if item.is_dir() else item.unlink()
