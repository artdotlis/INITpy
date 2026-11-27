# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Scaffold skeleton file operations."""

import shutil
from pathlib import Path

from scaffolder.template import render_template

_PROD_DOCKERFILES = (
    Path("configs") / "docker" / "prod.Dockerfile",
    Path("Dockerfile"),
)

_NODE_FILES = (
    "package.json",
    "pnpm-workspace.yaml",
    "pnpm-lock.yaml",
    "bin/install/pnpm.sh",
    "configs/lint/prettierrc.json",
    "package.json.license",
    "pnpm-lock.yaml.license",
    "configs/lint/prettierrc.json.license",
)


def write_package_files(path: Path, package_name: str, /, *, use_monorepo: bool) -> None:
    """Create empty files, add TODOs, and a placeholder test.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
        use_monorepo: Write under ``packages/<pkg>`` instead of the repo root.
    """
    pkg_dir = path / "packages" / package_name if use_monorepo else path
    src = pkg_dir / "src" / package_name

    src.mkdir(parents=True, exist_ok=True)
    (src / "main.py").write_text(f"# TODO: Implement {package_name}\n")
    (src / "py.typed").touch()
    (src / "__init__.py").write_text("__all__: list[str] = []")

    if use_monorepo:
        (pkg_dir / "README.md").write_text(f"# {package_name}\n")
        (pkg_dir / ".env").write_text("")

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


def remove_packages(path: Path, /) -> None:
    """Remove the monorepo ``packages`` directory entirely.

    Args:
        path: Root of the generated project.
    """
    packages = path / "packages"
    if packages.exists():
        shutil.rmtree(packages) if packages.is_dir() else packages.unlink()


def remove_node_tooling(path: Path, /) -> None:
    """Remove the Node/pnpm tooling files from a generated project.

    Args:
        path: Root of the generated project.
    """
    for name in _NODE_FILES:
        (path / name).unlink(True)


def remove_prod_docker(path: Path, /) -> None:
    """Remove the production ``Dockerfile`` and promote the dev compose.

    Supports both the current ``configs/docker/prod.Dockerfile`` and the
    legacy root ``Dockerfile`` layout used by older release tags.

    Args:
        path: Root of the generated project.
    """
    dockerfiles = [path / relative for relative in _PROD_DOCKERFILES]
    present = [dockerfile for dockerfile in dockerfiles if dockerfile.is_file()]
    if not present:
        raise FileNotFoundError(f"production Dockerfile missing: {dockerfiles[0]}")
    for dockerfile in present:
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
