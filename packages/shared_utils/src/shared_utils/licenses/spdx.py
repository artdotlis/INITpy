# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""SPDX header and license helpers."""

from pathlib import Path

from reuse.comment import CommentStyle
from reuse.comment import get_comment_style
from reuse.download import put_license_in_file
from reuse.header import contains_reuse_info


def _find_spdx_block(
    text: str, style_cls: type[CommentStyle], /
) -> tuple[int, str] | None:
    """Find the first SPDX comment block in `text`.

    Args:
        text: File content to scan.
        style_cls: Comment style to match against.

    Returns:
        A tuple of the block start offset and the comment block, or
        ``None`` if no SPDX block is found.
    """
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


def write_license(path: Path, license_name: str, /) -> None:
    """Download and write the SPDX license text to a file.

    Args:
        path: Path to the target license file.
        license_name: SPDX license identifier to fetch.

    Raises:
        FileNotFoundError: If the existing license file is absent.
    """
    if not path.is_file():
        raise FileNotFoundError(f"license file missing: {path}")
    path.unlink()
    put_license_in_file(license_name, path)
