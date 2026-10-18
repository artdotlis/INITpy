# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""File manipulation utilities."""

from pathlib import Path


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
    text = path.read_text()
    text = text.replace("artdotlis", author_name)
    text = text.replace("artdotlis@pm.me", author_email)
    path.write_text(text)
