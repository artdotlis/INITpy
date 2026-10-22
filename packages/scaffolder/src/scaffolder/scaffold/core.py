# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Core scaffold orchestration and CLI."""

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

from shared_utils.names import sanitize_package_name
from shared_utils.files import configure_licenses
from scaffolder.scaffold.files import (
    amend_docs,
    update_envs,
    update_licenses_sh,
    set_version,
)


def run(
    project_name: str,
    output_dir: str,
    author_name: str,
    author_email: str,
    license_name: str,
    description: str,
    /,
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

    # strip SPDX + .license
    strip_spdx_headers(output_path)

    # LICENSES/ + LICENSE
    configure_licenses(output_path, license_name)

    # entry_pod.sh
    set_entry_prod(output_path)

    # licenses.sh
    update_licenses_sh(output_path)

    # init and commit
    inti_and_commit(output_path)

    return output_path
