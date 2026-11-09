# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Scaffold skeleton file operations."""

import shutil
from pathlib import Path

from scaffolder.template import render_template


def write_package_files(path: Path, package_name: str, /) -> None:
    """Create empty files, add TODOs, and a placeholder test.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
    pkg_dir = path / "packages" / package_name
    src = pkg_dir / "src" / package_name

    src.mkdir(parents=True, exist_ok=True)
    (src / "main.py").write_text(f"# TODO: Implement {package_name}\n")
    (src / "py.typed").touch()
    (src / "__init__.py").write_text("__all__: list[str] = []")

    # empty README.md and .env; README gets a package-name header
    (pkg_dir / "README.md").write_text(f"# {package_name}\n")
    (pkg_dir / ".env").write_text("")

    # template unit test with TODO
    tests = pkg_dir / "tests" / "unit"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / f"test_{package_name}.py").write_text(
        """
def test_placeholder() -> None:
    # TODO finish tests
    assert False
"""
    )


def remove_projects_output_folder(path: Path, /) -> None:
    """Remove the template PROJECTS output folder from a generated project.

    Args:
        path: Root of the generated project.
    """
    output_path = path / "PROJECTS"
    if output_path.exists():
        shutil.rmtree(output_path) if output_path.is_dir() else output_path.unlink()


def remove_prod_docker(path: Path, /) -> None:
    """Remove the production Docker setup and promote the dev compose.

    Deletes the root production ``Dockerfile`` and moves the dev compose
    (``.devcontainer/dev.docker-compose.yml``) up to the repo root as
    ``docker-compose.yml``. The devcontainer and env files are rendered from
    whole-file templates, so no further edits are needed here.

    Args:
        path: Root of the generated project.
    """
    dockerfile = path / "Dockerfile"
    if not dockerfile.is_file():
        raise FileNotFoundError(f"production Dockerfile missing: {dockerfile}")
    dockerfile.unlink()

    dev_compose = path / ".devcontainer" / "dev.docker-compose.yml"
    if not dev_compose.is_file():
        raise FileNotFoundError(f"dev compose missing: {dev_compose}")
    shutil.move(str(dev_compose), str(path / "docker-compose.yml"))


def clean_root_md(path: Path, project_name: str, /) -> None:
    """Reset root README, CHANGELOG, and lockfiles for the new project.

    Args:
        path: Root of the generated project.
        project_name: The new project name.
    """
    (path / "README.md").write_text(
        render_template("root/README.md.jinja", {"project_name": project_name})
    )
    (path / "CHANGELOG.md").write_text("")
    (path / "uv.lock").unlink(True)
    (path / "pnpm-lock.yaml").unlink(True)
