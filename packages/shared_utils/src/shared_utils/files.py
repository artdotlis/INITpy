# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""File manipulation utilities."""

from reuse.comment import CommentStyle
from reuse.comment import get_comment_style
from reuse.download import put_license_in_file
from reuse.header import contains_reuse_info
from pathlib import Path
import json
import tomlkit


def _find_spdx_block(
    text: str, style_cls: type[CommentStyle], /
) -> tuple[int, str] | None:
    """Find the first SPDX comment block in `text`.

    Scans every newline boundary so it works even when the file starts
    with a shebang or other non-comment content (the same approach
    reuse's internal ``_find_first_spdx_comment`` uses).

    Args:
        text: File content to scan.
        style_cls: Comment style to match against.

    Returns:
        A tuple of the block start offset and the comment block, or
        ``None`` if no SPDX block is found.
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
    """Set the ``name`` field in a package.json file.

    Args:
        path: Path to package.json.
        name: New name value.
    """
    data = json.loads(path.read_text())
    data["name"] = name
    path.write_text(json.dumps(data, indent=2) + "\n")


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


def write_license(path: Path, license_name: str, /) -> None:
    """Download and write the SPDX license text to a file.

    Args:
        path: Path to the target license file.
        license_name: SPDX license identifier to fetch.
    """
    path.unlink()
    put_license_in_file(license_name, path)
