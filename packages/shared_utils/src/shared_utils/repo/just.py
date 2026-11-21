# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Justfile automation helpers."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _tools_available() -> bool:
    """Return True when uv, pnpm and just are on PATH."""
    return (
        shutil.which("uv") is not None
        and shutil.which("pnpm") is not None
        and shutil.which("just") is not None
    )


def lock_project(path: Path, /) -> None:
    """Lock project dependencies via ``just lock``.

    Args:
        path: Directory containing the justfile to run.
    """
    if not _tools_available():
        print("[scaffolder] uv/pnpm/just missing, skipping lock", file=sys.stderr)
        return
    subprocess.run(  # noqa: S603
        [shutil.which("just") or "just", "lock"],
        cwd=path,
        check=True,
        capture_output=True,
        env=dict(os.environ),
    )
