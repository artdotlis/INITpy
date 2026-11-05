# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""pyproject.toml editing helpers."""

from pathlib import Path

import tomlkit


def update_pyproject_authors(path: Path, author_name: str, author_email: str, /) -> None:
    """Replace author info in a pyproject.toml file.

    Args:
        path: Path to pyproject.toml
        author_name: New author name
        author_email: New author email
    """
    doc = tomlkit.parse(path.read_text())
    if "project" not in doc:
        doc["project"] = {}
    doc["project"]["authors"] = [{"name": author_name, "email": author_email}]
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_name(
    path: Path,
    name: str,
    /,
) -> None:
    """Set the project name in a pyproject.toml file.

    Args:
        path: Path to pyproject.toml.
        name: New project name.
    """
    doc = tomlkit.parse(path.read_text())
    if "project" not in doc:
        doc["project"] = {}
    doc["project"]["name"] = name
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_description(
    path: Path,
    desc: str,
    /,
) -> None:
    """Set the project description in a pyproject.toml file.

    Args:
        path: Path to pyproject.toml.
        desc: New project description.
    """
    doc = tomlkit.parse(path.read_text())
    if "project" not in doc:
        doc["project"] = {}
    doc["project"]["description"] = desc
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_workspace(
    path: Path,
    package_name: str,
    /,
) -> None:
    """Declare `package_name` as a workspace dependency in pyproject.toml.

    Args:
        path: Path to the root pyproject.toml.
        package_name: The workspace package name.
    """
    doc = tomlkit.parse(path.read_text())
    sources = doc.setdefault("tool", tomlkit.table()).setdefault("uv", tomlkit.table())
    sources["sources"] = {package_name: {"workspace": True}}
    path.write_text(tomlkit.dumps(doc))


def clean_pyproject_dependencies(path: Path, /) -> None:
    """Clear the project dependencies list in pyproject.toml.

    Args:
        path: Path to pyproject.toml.
    """
    doc = tomlkit.parse(path.read_text())
    dep: list[str] = []
    if "project" not in doc:
        doc["project"] = {}
    doc["project"]["dependencies"] = dep
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_path(
    path: Path,
    package_name: str,
    /,
) -> None:
    """Set setuptools package discovery to include `package_name`.

    Args:
        path: Path to pyproject.toml.
        package_name: The package to include.
    """
    doc = tomlkit.parse(path.read_text())
    packages = (
        doc.setdefault("tool", tomlkit.table())
        .setdefault("setuptools", tomlkit.table())
        .setdefault("packages", tomlkit.table())
    )
    packages["find"]["include"] = [package_name]
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_coverage(
    path: Path,
    package_name: str,
    /,
) -> None:
    """Retarget the coverage run section at `package_name`.

    The scaffolded package's pyproject.toml is copied from shared_utils, so
    its ``[tool.coverage.run]`` source and data_file still name
    ``shared_utils``. Point both at the new package.

    Args:
        path: Path to pyproject.toml.
        package_name: The package to measure.
    """
    doc = tomlkit.parse(path.read_text())
    run = doc.setdefault("tool", tomlkit.table()).setdefault("coverage", tomlkit.table())
    if "run" not in doc["tool"]["coverage"]:
        doc["tool"]["coverage"]["run"] = tomlkit.table()
    run = doc["tool"]["coverage"]["run"]
    run["source"] = [package_name]
    run["data_file"] = f".coverage.{package_name}"
    path.write_text(tomlkit.dumps(doc))
