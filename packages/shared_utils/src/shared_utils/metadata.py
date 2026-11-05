# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Recursive project metadata (authors, version) editing helpers."""

import json
from pathlib import Path

import tomlkit

from shared_utils.package_json import update_package_authors
from shared_utils.pyproject import update_pyproject_authors


def replace_authors(path: Path, email: str, name: str | None = None, /) -> None:
    """Replace author info in all pyproject.toml and package.json files.

    Args:
        path: Root directory to scan recursively.
        email: New author email.
        name: New author name (defaults to an empty string).
    """
    author_name = name or ""
    for fpath in path.rglob("*"):
        if not fpath.is_file():
            continue
        if fpath.name == "pyproject.toml":
            update_pyproject_authors(fpath, author_name, email)
        elif fpath.name == "package.json":
            update_package_authors(fpath, author_name, email)


def set_version(path: Path, version: str, /) -> None:
    """Set the ``version`` field in pyproject.toml and package.json files.

    Recursively updates only the ``version`` field in matching config files so
    other version strings (e.g. dependency pins) are left untouched.

    Args:
        path: Root directory to scan.
        version: New version value to set.
    """
    for fpath in path.rglob("*"):
        if not fpath.is_file() or fpath.name not in ("pyproject.toml", "package.json"):
            continue
        if fpath.name == "pyproject.toml":
            doc = tomlkit.parse(fpath.read_text())
            project = doc.get("project")
            if project is not None and "version" in project:
                project["version"] = version
            fpath.write_text(tomlkit.dumps(doc))
        else:
            data = json.loads(fpath.read_text())
            if "version" in data:
                data["version"] = version
            fpath.write_text(json.dumps(data, indent=2) + "\n")
