# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Remove REUSE tooling from a repository."""

import shutil
from pathlib import Path


def remove_reuse(path: Path, /) -> None:
    """Remove reuse tooling from a repository, keeping the LICENSE file.

    The ``.dockerignore`` ``!LICENSES`` line is already absent when reuse is
    off because that file is rendered from its ``use_reuse``-aware template;
    only the ``LICENSES/`` tree and the ``REUSE.toml`` configs need removing
    here.

    Args:
        path: Repository root of the project.
    """
    target = path / "LICENSES"
    if target.is_dir():
        shutil.rmtree(target)
    _remove_reuse_files(path)


def _remove_reuse_files(path: Path, /) -> None:
    """Delete ``REUSE.toml`` configs."""
    for fpath in list(path.rglob("*")):
        if fpath.is_file() and fpath.name.lower() == "reuse.toml":
            fpath.unlink()
