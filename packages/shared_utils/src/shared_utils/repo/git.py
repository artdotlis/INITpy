# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Git-related utilities."""

import shutil
import subprocess
from pathlib import Path


def clone_git(path: Path, template_url: str, ref: str = "dev", /) -> None:
    """Clone `template_url` into `path` from the given `ref` (branch or tag).

    Removes `path` first if it already exists, and creates parent
    directories as needed.

    Args:
        path: Destination directory for the clone.
        template_url: Git repository URL to clone.
        ref: Branch or tag to clone. Defaults to ``dev``.
    """
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["git", "clone", "--branch", ref, template_url, str(path)],
        check=True,
        capture_output=True,
    )


def reset_git(path: Path, /) -> None:
    """Remove the ``.git`` metadata directory from `path`.

    Args:
        path: The project directory to reset.
    """
    shutil.rmtree(path / ".git")


def inti_and_commit(path: Path, author_name: str, author_email: str, /) -> None:
    """Initialize a git repository in `path` and create the initial commit.

    Runs ``git init``, stages all files, and commits with the message
    ``init`` while skipping pre-commit hooks. A local author identity is
    supplied so the commit works without a global git config.

    Args:
        path: The project directory to commit.
        author_name: Name for the commit author.
        author_email: Email for the commit author.
    """
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            f"user.name={author_name}",
            "-c",
            f"user.email={author_email}",
            "commit",
            "-m",
            "init",
            "--no-verify",
        ],
        cwd=path,
        check=True,
        capture_output=True,
    )
