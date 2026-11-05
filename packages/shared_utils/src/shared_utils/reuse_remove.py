# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Remove REUSE tooling from a repository."""

import shutil
from pathlib import Path

import tomlkit

from shared_utils.lefthook import remove_lefthook_jobs
from shared_utils.scripts import strip_marked_script_block


_REUSE_START = "# ===== REUSE:START ====="
_REUSE_END = "# ===== REUSE:END ====="


def remove_reuse(path: Path, /) -> None:
    """Remove reuse tooling from a repository, keeping the LICENSE file.

    Args:
        path: Repository root of the project.
    """
    target = path / "LICENSES"
    if target.is_dir():
        shutil.rmtree(target)
    _remove_reuse_files(path)
    _remove_reuse_dependency(path / "pyproject.toml")
    strip_marked_script_block(
        path / "bin" / "lint" / "licenses.sh", _REUSE_START, _REUSE_END
    )
    remove_lefthook_jobs(path / "lefthook.yml", "fix-all-addable-files")
    _prune_dockerignore(path / ".dockerignore")


def _prune_dockerignore(dockerignore: Path, /) -> None:
    """Drop the ``!LICENSES`` negation, keeping the ``LICENSE`` file included.

    Args:
        dockerignore: Path to the repository ``.dockerignore``.
    """
    if not dockerignore.is_file():
        return
    lines = dockerignore.read_text().splitlines(keepends=True)
    kept = [line for line in lines if line.strip() != "!LICENSES"]
    if kept != lines:
        dockerignore.write_text("".join(kept))


def _remove_reuse_files(path: Path, /) -> None:
    """Delete ``REUSE.toml`` configs."""
    for fpath in list(path.rglob("*")):
        if fpath.is_file() and fpath.name.lower() == "reuse.toml":
            fpath.unlink()


def _remove_reuse_dependency(pyproject: Path, /) -> None:
    """Drop the ``reuse`` dependency from ``pyproject.toml``."""
    doc = tomlkit.parse(pyproject.read_text())
    project = doc.get("project")
    if project is not None and project.get("dependencies") is not None:
        doc["project"]["dependencies"] = [
            dep
            for dep in project["dependencies"]
            if not (isinstance(dep, str) and dep.strip().lower().startswith("reuse"))
        ]
    groups = doc.get("dependency-groups")
    if groups is not None:
        for group_name, deps in list(groups.items()):
            groups[group_name] = [
                dep
                for dep in deps
                if not (isinstance(dep, str) and dep.strip().lower().startswith("reuse"))
            ]
    pyproject.write_text(tomlkit.dumps(doc))
