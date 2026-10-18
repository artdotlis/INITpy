# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Git-related utilities."""

import shutil
import subprocess
from pathlib import Path


def clone_git(path: Path, template_url: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.rmtree(path)

    subprocess.run(
        ["git", "clone", template_url, str(path)], check=True, capture_output=True
    )


def reset_git(path: Path) -> None:
    shutil.rmtree(path / ".git")
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)


def first_commit(path: Path) -> None:
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=path,
        check=True,
        capture_output=True,
    )
