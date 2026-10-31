# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Makefile automation helpers."""

import subprocess
from pathlib import Path


def lock_project(path: Path, /) -> None:
    """Run the ``make run-lock`` target in `path`.

    Args:
        path: Directory containing the Makefile to run.
    """
    subprocess.run(
        ["make", "run-lock"],
        cwd=path,
        check=True,
        capture_output=True,
    )
