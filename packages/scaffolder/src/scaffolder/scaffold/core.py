# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Core scaffold orchestration and CLI."""

from scaffolder.scaffold.files import remove_projects_output_folder
from shared_utils.constants import VERSION
from shared_utils.make import lock_project
from shared_utils.files import strip_spdx_headers
from shared_utils.names import sanitize_package_name_dep_group
from scaffolder.scaffold.files import correct_core_project
from shared_utils.files import replace_authors
from scaffolder.scaffold.files import clean_root_md
from scaffolder.scaffold.files import set_entry_prod
from scaffolder.scaffold.files import write_package_files
from shared_utils.git import inti_and_commit
from scaffolder.scaffold.package import create_package
from shared_utils.git import reset_git
from shared_utils.git import clone_git
from pathlib import Path
from dataclasses import dataclass

import os

from shared_utils.names import sanitize_package_name
from shared_utils.files import configure_licenses
from shared_utils.files import remove_reuse
from scaffolder.scaffold.files import (
    amend_docs,
    update_copyright,
    update_envs,
    update_licenses_sh,
    set_version,
    update_tests,
)


def clone_ref() -> str:
    """Return the INITpy ref to clone.

    Clones the ``dev`` branch in dev mode (``SCAF_DEV`` set), otherwise
    the tag matching this scaffolder's release.
    """
    if os.environ.get("SCAF_DEV"):
        return "dev"
    return f"v{VERSION}"


@dataclass(slots=True, frozen=True)
class ScaffoldArgs:
    """Bundle of user-provided scaffold options."""

    project_name: str
    """New project name."""
    output_dir: str
    """Destination for the generated project."""
    author_name: str
    """Author / copyright holder name."""
    author_email: str
    """Author contact email."""
    license_name: str
    """SPDX license identifier for the project."""
    description: str
    """One-line project description."""
    copyright: str
    """Full copyright owner string."""
    use_reuse: bool
    """Whether to keep the REUSE tooling."""


def run(args: ScaffoldArgs) -> Path:
    """Execute the multi-step scaffolding procedure.

    Clones the INITpy template, creates and wires a single package,
    applies project metadata, and resets version, licenses, and git state.

    Args:
        args: Bundled scaffold options.

    Returns:
        Path to the created project directory.
    """
    project_name = args.project_name
    output_dir = args.output_dir
    author_name = args.author_name
    author_email = args.author_email
    license_name = args.license_name
    description = args.description
    copyright = args.copyright
    use_reuse = args.use_reuse
    package_name = f"{sanitize_package_name(project_name)}_pkg"
    dep_name = sanitize_package_name_dep_group(package_name)
    output_path = Path(output_dir) / project_name
    output_path.mkdir(parents=True, exist_ok=True)

    # clone INITpy at the tag matching this scaffolder's release
    print(f"[scaffolder] cloning INITpy at {clone_ref()} ...")
    clone_git(output_path, "https://github.com/artdotlis/INITpy.git", clone_ref())

    # reset git
    reset_git(output_path)

    # drop the template's PROJECTS output folder from the generated project
    print("[scaffolder] removing template PROJECTS folder ...")
    remove_projects_output_folder(output_path)

    # create package
    print(f"[scaffolder] creating package {package_name} ...")
    create_package(output_path, package_name, description)

    # write package files
    print("[scaffolder] writing package files ...")
    write_package_files(output_path, package_name)

    # amend docs / vitepress
    print("[scaffolder] amending docs ...")
    amend_docs(output_path, package_name, project_name)

    # update env vars
    print("[scaffolder] updating env vars ...")
    update_envs(output_path, package_name)

    # replace copyright holder in package.env
    print("[scaffolder] updating copyright ...")
    update_copyright(output_path, copyright)

    # single package test wiring in lefthook + CI
    print("[scaffolder] wiring tests ...")
    update_tests(output_path, package_name)

    # clean root README and CHANGELOG
    print("[scaffolder] cleaning README and CHANGELOG ...")
    clean_root_md(output_path, project_name)

    # replace authors and project name
    print("[scaffolder] replacing authors ...")
    replace_authors(output_path, author_email, author_name)

    # replace project name
    print("[scaffolder] configuring project ...")
    correct_core_project(output_path, project_name, package_name, dep_name, description)

    # version 0.1.0
    set_version(output_path)

    # strip SPDX + .license
    print("[scaffolder] stripping SPDX headers ...")
    strip_spdx_headers(output_path)

    # LICENSES/ + LICENSE
    print("[scaffolder] configuring licenses ...")
    configure_licenses(output_path, license_name)

    # entry_pod.sh
    print("[scaffolder] writing entrypoint ...")
    set_entry_prod(output_path)

    # licenses.sh
    print("[scaffolder] updating licenses.sh ...")
    update_licenses_sh(output_path)

    # strip reuse tooling unless requested
    if not use_reuse:
        print("[scaffolder] removing reuse tooling ...")
        remove_reuse(output_path)

    # lock project dependencies
    print("[scaffolder] locking dependencies (may take a while) ...")
    lock_project(output_path)

    # init and commit
    print("[scaffolder] committing generated project ...")
    inti_and_commit(output_path, author_name, author_email)

    print(f"[scaffolder] done: {output_path}")
    return output_path
