# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Makefile automation helpers."""

import os
import shutil
import subprocess
from pathlib import Path


def _tools_available() -> bool:
    """Return True when uv and pnpm are on PATH."""
    return shutil.which("uv") is not None and shutil.which("pnpm") is not None


def lock_project(path: Path, /) -> None:
    """Lock project dependencies via ``make run-lock``.

    Args:
        path: Directory containing the Makefile to run.
    """
    env = dict(os.environ)
    if not _tools_available():
        subprocess.run(
            ["make", "setup"], cwd=path, check=True, capture_output=True, env=env
        )
    subprocess.run(
        ["make", "run-lock"],
        cwd=path,
        check=True,
        capture_output=True,
        env=env,
    )
