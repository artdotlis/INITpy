# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Git-related utilities."""

import shutil
import subprocess
from pathlib import Path


def clone_git(path: Path, template_url: str, /) -> None:
    """Clone `template_url` into `path` from its ``dev`` branch.

    Removes `path` first if it already exists, and creates parent
    directories as needed.

    Args:
        path: Destination directory for the clone.
        template_url: Git repository URL to clone.
    """
    path.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.rmtree(path)

    subprocess.run(
        ["git", "clone", "--branch", "dev", template_url, str(path)],
        check=True,
        capture_output=True,
    )


def reset_git(path: Path, /) -> None:
    """Remove the ``.git`` metadata directory from `path`.

    Args:
        path: The project directory to reset.
    """
    shutil.rmtree(path / ".git")


def inti_and_commit(path: Path, /) -> None:
    """Initialize a git repository in `path` and create the initial commit.

    Runs ``git init``, stages all files, and commits with the message
    ``init`` while skipping pre-commit hooks.

    Args:
        path: The project directory to commit.
    """
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=path,
        check=True,
        capture_output=True,
    )
