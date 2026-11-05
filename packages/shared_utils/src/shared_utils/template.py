# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Copy template files and directories out of the repository."""

import shutil
from pathlib import Path

__all__ = ["load_template"]


def load_template(root: Path, target: Path, rel: str, /) -> Path:
    """Copy template ``rel`` (file or dir, relative to ``root``) into ``target``.

    Args:
        root: Repository root that holds the template files.
        target: Directory the template piece is copied into.
        rel: Path of the template piece relative to ``root``.

    Returns:
        The destination path (``target / rel``).
    """
    src = root / rel
    dst = target / rel
    if src.is_dir():
        shutil.copytree(src, dst)
    elif src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text())
    else:
        raise FileNotFoundError(f"template file missing: {src}")
    return dst
