# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""File manipulation utilities."""

from reuse.comment import CommentStyle
from pathlib import Path
import json
import tomlkit

from reuse.comment import get_comment_style
from reuse.download import put_license_in_file
from reuse.header import contains_reuse_info
from reuse.project import LICENSE_MAP


def _find_spdx_block(
    text: str, style_cls: type[CommentStyle], /
) -> tuple[int, str] | None:
    """Find the first SPDX comment block in *text*.

    Scans every newline boundary so it works even when the file starts
    with a shebang or other non-comment content (the same approach
    reuse's internal ``_find_first_spdx_comment`` uses).
    """
    if style_cls is None:
        return None
    start = 0
    while start < len(text):
        try:
            comment = style_cls.comment_at_first_character(text[start:])
        except Exception:
            nxt = text.find("\n", start)
            start = (nxt + 1) if nxt != -1 else len(text)
            continue
        if contains_reuse_info(comment):
            return start, comment
        nxt = text.find("\n", start)
        if nxt == -1:
            break
        start = nxt + 1
    return None


def strip_spdx_headers(path: Path, /) -> None:
    """Remove SPDX headers and .license files from a directory tree.

    Uses reuse's CommentStyle to find and remove the first SPDX comment
    block. Handles shebangs and preprocessor directives correctly by
    scanning every newline boundary.

    Args:
        path: Root directory to scan
    """
    for fpath in path.rglob("*"):
        if fpath.is_file() and fpath.name.endswith(".license"):
            fpath.unlink()
        elif fpath.is_file() and "SPDX" in (text := fpath.read_text()):
            style_cls = get_comment_style(fpath)
            if style_cls is None:
                continue
            found = _find_spdx_block(text, style_cls)
            if found is None:
                continue
            start, comment_block = found
            before = text[:start]
            after = text[start + len(comment_block) :].lstrip()
            fpath.write_text(before + after)


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
    doc = tomlkit.parse(path.read_text())
    sources = doc.setdefault("tool", tomlkit.table()).setdefault("uv", tomlkit.table())
    sources["sources"] = {package_name: {"workspace": True}}
    path.write_text(tomlkit.dumps(doc))
    doc = tomlkit.parse(path.read_text())


def update_pyproject_dep_groups(
    path: Path,
    package_name: str,
    /,
) -> None:
    doc = tomlkit.parse(path.read_text())
    if "dependency-groups" not in doc:
        doc["dependency-groups"] = {}
    doc["dependency-groups"]["mono"] = [package_name]
    path.write_text(tomlkit.dumps(doc))


def clean_pyproject_dependencies(path: Path, /) -> None:
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
    doc = tomlkit.parse(path.read_text())
    packages = (
        doc.setdefault("tool", tomlkit.table())
        .setdefault("setuptools", tomlkit.table())
        .setdefault("packages", tomlkit.table())
    )
    packages["find"]["include"] = [package_name]
    path.write_text(tomlkit.dumps(doc))


def update_package_authors(path: Path, author_name: str, author_email: str, /) -> None:
    """Replace author info in a package.json file.

    Args:
        path: Path to package.json
        author_name: New author name
        author_email: New author email
    """
    data = json.loads(path.read_text())
    data["author"] = {"email": author_email, "name": author_name}
    path.write_text(json.dumps(data, indent=2) + "\n")


def update_package_devcon_name(path: Path, name: str, /) -> None:
    data = json.loads(path.read_text())
    data["name"] = name
    path.write_text(json.dumps(data, indent=2) + "\n")


def replace_authors(path: Path, email: str, name: str | None = None, /) -> None:
    """Replace author info in all pyproject.toml and package.json files."""
    author_name = name or ""
    for fpath in path.rglob("*"):
        if not fpath.is_file():
            continue
        if fpath.name == "pyproject.toml":
            update_pyproject_authors(fpath, author_name, email)
        elif fpath.name == "package.json":
            update_package_authors(fpath, author_name, email)


def clear_licenses_dir(path: Path, /) -> None:
    """Remove all files from the LICENSES/ directory."""
    lic_dir = path / "LICENSES"
    if lic_dir.is_dir():
        for file in lic_dir.iterdir():
            if file.is_file():
                file.unlink()


def _write_license(path: Path, license_name: str, /) -> None:
    """Download and write the SPDX license text to the LICENSE file."""
    path.unlink()
    put_license_in_file(license_name, path)


def set_license_pyproject(path: Path, license_name: str, /) -> None:
    """Set the license field in pyproject.toml."""
    doc = tomlkit.parse(path.read_text())
    if "project" not in doc:
        doc["project"] = {}
    doc["project"]["license"] = license_name
    path.write_text(tomlkit.dumps(doc))


def set_license_package_json(path: Path, license_name: str, /) -> None:
    """Set the license field in package.json."""
    data = json.loads(path.read_text())
    data["license"] = license_name
    path.write_text(json.dumps(data, indent=2) + "\n")


def configure_licenses(path: Path, license_name: str, /) -> None:
    """Clear LICENSES/, download LICENSE, and set license in pyproject.toml and package.json."""
    _validate_license(license_name)
    clear_licenses_dir(path)
    _write_license(path / "LICENSE", license_name)
    set_license_pyproject(path / "pyproject.toml", license_name)
    set_license_package_json(path / "package.json", license_name)


def _validate_license(license_name: str, /) -> None:
    """Validate that *license_name* is a known SPDX license identifier."""
    if license_name not in LICENSE_MAP:
        raise ValueError(
            f"Unknown SPDX license: {license_name!r}. "
            f"Run `reuse fetch` to see supported licenses."
        )
