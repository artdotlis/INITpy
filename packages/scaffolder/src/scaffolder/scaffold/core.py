# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Core scaffold orchestration."""

from pathlib import Path

from shared_utils.names import sanitize_package_name

from . import git as git_mod
from . import package as pkg_mod
from . import files as files_mod


def run(
    project_name: str,
    output_dir: str = ".",
    author_name: str = "Default Author",
    author_email: str = "author@example.com",
    license_name: str = "Unlicense",
    skip_git: bool = False,
) -> Path:
    """Execute the 19-step scaffold procedure.

    Returns:
    -------
    Path
        Path to the created project directory.
    """
    package_name = sanitize_package_name(project_name)
    output_path = Path(output_dir) / project_name

    # 1 - clone INITpy
    git_mod.clone(output_path)

    # 2 - reset git
    git_mod.reset(output_path)

    # 3-5 - create package
    pkg_mod.create(output_path, package_name, author_name, author_email)

    # 6-8 - write package files
    pkg_mod.write_files(output_path, package_name)

    # 9 - amend docs / zensical
    files_mod.amend_docs(output_path, package_name, project_name)

    # 10 - update env vars
    files_mod.update_envs(output_path, package_name)

    # 11 - root README
    (output_path / "README.md").write_text(f"# {project_name}\n\n")

    # 12 - replace authors
    files_mod.replace_authors(output_path, author_email)

    # 13 - replace project name
    files_mod.replace_project_name(output_path, project_name)

    # 14 - strip SPDX + .license
    files_mod.strip_spdx(output_path)

    # 15 - entry_pod.sh
    _set_entry_pod(output_path)

    # 16 - licenses.sh
    files_mod.update_licenses_sh(output_path)

    # 17 - version 0.1.0
    files_mod.set_version(output_path)

    # 18 - LICENSES/ + LICENSE
    files_mod.fix_licenses(output_path, license_name)

    # 19 - commit
    if not skip_git:
        git_mod.commit(output_path)

    return output_path


def _set_entry_pod(path: Path) -> None:
    """Step 15: write entry_pod.sh."""
    entry = path / "bin" / "deploy" / "entry_pod.sh"
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text("#!/bin/bash\n\nset -euo pipefail\n\nsleep infinity\n")
