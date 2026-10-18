# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""File manipulation utilities."""

from pathlib import Path
import tomlkit
import json


def strip_spdx_headers(path: Path) -> None:
    """Remove SPDX headers and .license files from a directory tree.

    Args:
        path: Root directory to scan
    """
    for root, dirs, files in path.walk():
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for fname in files:
            fpath = root / fname
            if fname.endswith(".license"):
                fpath.unlink()
            elif fpath.is_file() and "SPDX" in fpath.read_text():
                lines = [
                    l
                    for l in fpath.read_text().splitlines()
                    if "SPDX" not in l and l.strip() in ("", "--")
                ]
                fpath.write_text("\n".join(lines))


def update_pyproject_authors(path: Path, author_name: str, author_email: str) -> None:
    """Replace author info in a pyproject.toml file.

    Args:
        path: Path to pyproject.toml
        author_name: New author name
        author_email: New author email
    """
    doc = tomlkit.parse(path.read_text())
    if "project" in doc and "authors" in doc["project"]:
        del doc["project"]["authors"]
    doc["project"]["authors"] = [{"name": author_name, "email": author_email}]
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_name(
    path: Path,
    name: str,
) -> None:
    doc = tomlkit.parse(path.read_text())
    if "project" in doc and "name" in doc["project"]:
        del doc["project"]["name"]
    doc["project"]["name"] = name
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_description(
    path: Path,
    desc: str,
) -> None:
    doc = tomlkit.parse(path.read_text())
    if "project" in doc and "description" in doc["project"]:
        del doc["project"]["description"]
    doc["project"]["description"] = desc
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_workspace(
    path: Path,
    package_name: str,
) -> None:
    doc = tomlkit.parse(path.read_text())
    tool = "tool.uv.sources"
    if tool in doc:
        del doc[tool]
    doc[tool] = {package_name: {"workspace": True}}
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_workspace(
    path: Path,
    package_name: str,
) -> None:
    doc = tomlkit.parse(path.read_text())
    tool = "tool.uv.sources"
    if tool in doc:
        del doc[tool]
    doc[tool] = {package_name: {"workspace": True}}
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_dep_groups(
    path: Path,
    package_name: str,
) -> None:
    doc = tomlkit.parse(path.read_text())
    group = "dependency-groups"
    if group in doc and "mono" in doc[group]:
        del doc[group]["mono"]
    doc[group]["mono"] = [package_name]
    path.write_text(tomlkit.dumps(doc))


def clean_pyproject_dependencies(path: Path) -> None:
    doc = tomlkit.parse(path.read_text())
    if "project" in doc and "dependencies" in doc["project"]:
        del doc["project"]["dependencies"]
    dep: list[str] = []
    doc["project"]["dependencies"] = dep
    path.write_text(tomlkit.dumps(doc))


def update_pyproject_path(
    path: Path,
    package_name: str,
) -> None:
    doc = tomlkit.parse(path.read_text())
    tool = "tool.setuptools.packages.find"
    if tool in doc and "include" in doc[tool]:
        del doc[tool]["include"]
    doc[tool]["include"] = [package_name]
    path.write_text(tomlkit.dumps(doc))


def update_package_authors(path: Path, author_name: str, author_email: str) -> None:
    """Replace author info in a package.json file.

    Args:
        path: Path to package.json
        author_name: New author name
        author_email: New author email
    """
    data = json.loads(path.read_text())
    if "author" in data:
        del data["authors"]
    data["author"] = {"email": author_email, "name": author_name}
    path.write_text(json.dumps(data, indent=2) + "\n")


def update_package_devcon_name(path: Path, name: str) -> None:
    data = json.loads(path.read_text())
    if "name" in data:
        del data["name"]
    data["name"] = name
    path.write_text(json.dumps(data, indent=2) + "\n")


def replace_authors(path: Path, email: str, name: str | None = None) -> None:
    """Replace author info in all pyproject.toml and package.json files."""
    author_name = name or ""
    for fpath in path.rglob("*"):
        if not fpath.is_file():
            continue
        if fpath.name == "pyproject.toml":
            update_pyproject_authors(fpath, author_name, email)
        elif fpath.name == "package.json":
            update_package_authors(fpath, author_name, email)
