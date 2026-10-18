# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Core scaffold orchestration and CLI."""

from shared_utils.names import sanitize_package_name_dep_group
from scaffolder.scaffold.files import correct_core_project
from shared_utils.files import replace_authors
from scaffolder.scaffold.files import clean_root_md
from scaffolder.scaffold.files import set_entry_pod
from scaffolder.scaffold.files import write_package_files
from shared_utils.git import first_commit
from scaffolder.scaffold.package import create_package
from shared_utils.git import reset_git
from shared_utils.git import clone_git
from pathlib import Path
import sys

from shared_utils.names import sanitize_package_name
from scaffolder.scaffold.files import (
    amend_docs,
    update_envs,
    strip_spdx,
    update_licenses_sh,
    set_version,
    fix_licenses,
)


def run(
    project_name: str,
    output_dir: str,
    author_name: str,
    author_email: str,
    license_name: str,
    description: str,
) -> Path:
    """Execute the 19-step scaffold procedure.

    Returns:
    -------
    Path
        Path to the created project directory.
    """
    package_name = sanitize_package_name(project_name)
    dep_name = sanitize_package_name_dep_group(project_name)
    output_path = Path(output_dir) / project_name

    # clone INITpy
    clone_git(output_path, "https://github.com/artdotlis/INITpy.git")

    # reset git
    reset_git(output_path)

    # create package
    create_package(output_path, package_name, description)

    # write package files
    write_package_files(output_path, package_name)

    # amend docs / zensical
    amend_docs(output_path, package_name, project_name)

    # update env vars
    update_envs(output_path, package_name)

    # clean root README and CHANGELOG
    clean_root_md(output_path, project_name)

    # replace authors and project name
    replace_authors(output_path, author_email, author_name)

    # replace project name
    correct_core_project(output_path, project_name, package_name, dep_name, description)

    # version 0.1.0
    set_version(output_path)

    # 14 - strip SPDX + .license
    strip_spdx(output_path)

    # entry_pod.sh
    set_entry_pod(output_path)

    # 16 - licenses.sh
    update_licenses_sh(output_path)

    # 18 - LICENSES/ + LICENSE
    fix_licenses(output_path, license_name)

    # 19 - commit
    first_commit(output_path)

    return output_path


def run_cli() -> None:
    """Interactive CLI entry point."""
    print("📦 INITpy Project Scaffolder")
    print("─" * 40)

    project_name = input("Project name: ").strip()
    if len(project_name) < 3:
        print(
            "❌ Project name is required and must contain at least characters",
            file=sys.stderr,
        )
        sys.exit(1)

    project_description = input("Project description: ").strip()
    if not project_description:
        print("❌ Project description is required", file=sys.stderr)
        sys.exit(1)

    output_dir = input("Output directory: ").strip()
    if not output_dir:
        print("❌ Output directory is required", file=sys.stderr)
        sys.exit(1)

    author_name = input("Author name: ").strip()
    if not author_name:
        print("❌ Author name is required", file=sys.stderr)
        sys.exit(1)

    author_email = input("Author email: ").strip()
    if not author_email:
        print("❌ Author email is required", file=sys.stderr)
        sys.exit(1)

    print("\nAvailable licenses: Unlicense, MIT, Apache-2.0, GPL-3.0, CC0-1.0")
    license_name = input("License: ").strip()
    if not license_name:
        print("❌ License is required", file=sys.stderr)
        sys.exit(1)

    try:
        result = run(
            project_name,
            output_dir=output_dir,
            author_name=author_name,
            author_email=author_email,
            license_name=license_name,
            description=project_description,
        )
        print(f"\n✅ '{project_name}' → {result.absolute()}")
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
