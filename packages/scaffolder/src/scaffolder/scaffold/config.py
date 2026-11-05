# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Root project configuration for a generated project."""

from pathlib import Path

import tomlkit

from shared_utils.package_json import update_package_devcon_name
from shared_utils.pyproject import update_pyproject_description
from shared_utils.pyproject import update_pyproject_name
from shared_utils.pyproject import update_pyproject_workspace


def correct_core_project(
    path: Path,
    project_name: str,
    package_name: str,
    dep_name: str,
    description: str,
    /,
) -> None:
    """Apply project metadata to root config files.

    Updates the root ``pyproject.toml`` and ``package.json`` files with
    the project name, workspace dependency, description, and the
    ``mono`` dependency group.

    Args:
        path: Root of the generated project.
        project_name: The new project name.
        package_name: The workspace package name.
        dep_name: Name used for the ``mono`` dependency group.
        description: Short description of the new project.
    """
    update_pyproject_name(path / "pyproject.toml", project_name)
    update_pyproject_workspace(path / "pyproject.toml", package_name)
    update_pyproject_dep_groups(path / "pyproject.toml", dep_name)
    update_pyproject_description(path / "pyproject.toml", description)
    update_package_devcon_name(path / "package.json", project_name)
    update_package_devcon_name(path / ".devcontainer" / "devcontainer.json", project_name)


def update_commitizen_version_files(path: Path, package_name: str, /) -> None:
    """Scope :ref:`[tool.commitizen] version_files` to the new package.

    Removes entries referencing shared_utils and renames the scaffolder
    entry to the scaffolded package's pyproject.toml.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
    root_pyproject = path / "pyproject.toml"
    doc = tomlkit.parse(root_pyproject.read_text())
    tool = doc.get("tool")
    if tool is None:
        return
    commitizen = tool.get("commitizen")
    if commitizen is None:
        return

    version_files = commitizen.get("version_files")
    if not isinstance(version_files, list):
        return

    # Drop shared_utils entries; retarget scaffolder to the new package.
    cleaned = [
        (
            f"packages/{package_name}/pyproject.toml"
            if entry == "packages/scaffolder/pyproject.toml"
            else entry
        )
        for entry in version_files
        if "shared_utils" not in entry
    ]
    commitizen["version_files"] = cleaned

    root_pyproject.write_text(tomlkit.dumps(doc))


def update_pyproject_dep_groups(
    path: Path,
    package_name: str,
    /,
) -> None:
    """Add `package_name` to the ``mono`` dependency group.

    Args:
        path: Path to pyproject.toml.
        package_name: The package to add.
    """
    doc = tomlkit.parse(path.read_text())
    if "dependency-groups" not in doc:
        doc["dependency-groups"] = {}
    doc["dependency-groups"]["mono"] = [package_name]
    path.write_text(tomlkit.dumps(doc))
