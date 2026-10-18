# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Git operations for scaffolding."""

import shutil
import subprocess

from pathlib import Path

from shared_utils.git import clone_template


def clone(path: Path) -> None:
    """Step 1: clone INITpy into the target directory."""
    path.mkdir(parents=True, exist_ok=True)
    clone_template("https://github.com/artdotlis/INITpy.git", path)


def reset(path: Path) -> None:
    """Step 2: remove .git and initialise a new one."""
    shutil.rmtree(path / ".git")
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)


def commit(path: Path) -> None:
    """Step 19: git add + commit."""
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=path,
        check=True,
        capture_output=True,
    )
