# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Git-related utilities."""

import shutil
import subprocess
from pathlib import Path


def clone_git(path: Path, template_url: str, ref: str = "dev", /) -> None:
    """Clone `template_url` into `path` from the given `ref` (branch or tag).

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

    Raises:
        FileNotFoundError: If the ``.git`` directory is absent.
    """
    git_dir = path / ".git"
    if not git_dir.is_dir():
        raise FileNotFoundError(f".git directory missing: {git_dir}")
    shutil.rmtree(git_dir)


def init_and_commit(path: Path, author_name: str, author_email: str, /) -> None:
    """Initialize a git repository in `path` and make the initial commit.

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
