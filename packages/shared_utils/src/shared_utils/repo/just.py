# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Justfile automation helpers."""

import os
import shutil
import subprocess
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
    env = dict(os.environ)
    if not _tools_available():
        subprocess.run(
            ["just", "setup"], cwd=path, check=True, capture_output=True, env=env
        )
    subprocess.run(
        ["just", "lock"],
        cwd=path,
        check=True,
        capture_output=True,
        env=env,
    )
