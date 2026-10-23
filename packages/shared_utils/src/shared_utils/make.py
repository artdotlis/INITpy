# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

import subprocess
from pathlib import Path


def lock_project(path: Path, /) -> None:
    subprocess.run(
        ["make", "ryn-lock"],
        cwd=path,
        check=True,
        capture_output=True,
    )
