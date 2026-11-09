# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Core scaffold orchestration and CLI."""

from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

import os

from scaffolder.scaffold.config import correct_core_project
from scaffolder.scaffold.docs import amend_docs, remove_docs
from scaffolder.scaffold.env import update_envs
from scaffolder.scaffold.licenses import configure_licenses
from scaffolder.scaffold.package import create_package
from scaffolder.scaffold.skeleton import clean_root_md
from scaffolder.scaffold.skeleton import remove_prod_docker
from scaffolder.scaffold.skeleton import remove_projects_output_folder
from scaffolder.scaffold.skeleton import write_package_files
from scaffolder.scaffold.tests import update_tests
from shared_utils.core.constants import VERSION
from shared_utils.repo.git import clone_git
from shared_utils.repo.git import init_and_commit
from shared_utils.repo.git import reset_git
from shared_utils.repo.make import lock_project
from shared_utils.core.names import sanitize_package_name
from shared_utils.core.names import sanitize_package_name_dep_group
from shared_utils.core.names import package_env_file
from shared_utils.core.names import package_env_var
from shared_utils.licenses.reuse_remove import remove_reuse
from shared_utils.licenses.spdx import strip_spdx_headers


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
    use_docs: bool
    """Whether to keep the docs (VitePress) subpackage."""


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
    use_docs = args.use_docs
    package_name = f"{sanitize_package_name(project_name)}_pkg"
    dep_name = sanitize_package_name_dep_group(package_name)
    output_path = Path(output_dir) / project_name
    output_path.mkdir(parents=True, exist_ok=True)

    package_ctx = {
        "package_name": package_name,
        "version": "0.1.0",
        "description": description,
        "author_name": author_name,
        "author_email": author_email,
        "copyright_holder": copyright,
        "year": datetime.now().year,
    }
    root_ctx = {
        **package_ctx,
        "project_name": project_name,
        "dep_name": dep_name,
        "license": license_name,
        "package_env_var": package_env_var(package_name),
        "package_env_file": package_env_file(package_name),
        "use_reuse": use_reuse,
        "use_docs": use_docs,
    }

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
    create_package(output_path, package_name, package_ctx)

    # write package files
    print("[scaffolder] writing package files ...")
    write_package_files(output_path, package_name)

    # amend docs / vitepress
    if use_docs:
        print("[scaffolder] amending docs ...")
        amend_docs(output_path, root_ctx)
    else:
        print("[scaffolder] skipping docs (requested removal) ...")

    # update env vars (package.env + lint_env.sh whole-file templates)
    print("[scaffolder] updating env vars ...")
    update_envs(output_path, package_name, root_ctx)

    # single package test wiring in lefthook + CI
    print("[scaffolder] wiring tests ...")
    update_tests(output_path, root_ctx)

    # clean root README and CHANGELOG
    print("[scaffolder] cleaning README and CHANGELOG ...")
    clean_root_md(output_path, project_name)

    # render root config files + JSON metadata (name, authors, license, version)
    print("[scaffolder] configuring project ...")
    correct_core_project(output_path, root_ctx)

    # strip SPDX + .license
    print("[scaffolder] stripping SPDX headers ...")
    strip_spdx_headers(output_path)

    # LICENSES/ + LICENSE
    print("[scaffolder] configuring licenses ...")
    configure_licenses(output_path, license_name)

    # remove production docker; dev compose becomes the root one
    print("[scaffolder] removing production docker ...")
    remove_prod_docker(output_path)

    # strip reuse tooling unless requested
    if not use_reuse:
        print("[scaffolder] removing reuse tooling ...")
        remove_reuse(output_path)

    # remove docs subpackage unless requested
    if not use_docs:
        print("[scaffolder] removing docs subpackage ...")
        remove_docs(output_path)

    # lock project dependencies
    print("[scaffolder] locking dependencies (may take a while) ...")
    lock_project(output_path)

    # init and commit
    print("[scaffolder] committing generated project ...")
    init_and_commit(output_path, author_name, author_email)

    print(f"[scaffolder] done: {output_path}")
    return output_path
