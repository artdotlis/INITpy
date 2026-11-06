# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Scaffold skeleton file operations."""

import json
import shutil
from pathlib import Path


def write_package_files(path: Path, package_name: str, /) -> None:
    """Create empty files, add TODOs, and a placeholder test.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
    pkg_dir = path / "packages" / package_name
    src = pkg_dir / "src" / package_name

    src.mkdir(parents=True, exist_ok=True)
    # create empty files
    (src / "main.py").write_text("")
    (src / "py.typed").touch()
    (src / "__init__.py").write_text("__all__: list[str] = []")

    # empty README.md and .env
    (pkg_dir / "README.md").write_text("")
    (pkg_dir / ".env").write_text("")

    # main.py: add TODO comment
    (src / "main.py").write_text(f"# TODO: Implement {package_name}\n")

    # README.md: add package name header
    (pkg_dir / "README.md").write_text(f"# {package_name}\n")

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

    Deletes the root production ``Dockerfile`` and compose file, moves the
    dev compose up to the repo root, and points the devcontainer at the
    single (dev) compose.

    Args:
        path: Root of the generated project.
    """
    dockerfile = path / "Dockerfile"
    dockerfile.unlink()

    dev_compose = path / ".devcontainer" / "dev.docker-compose.yml"
    root_compose = path / "docker-compose.yml"
    shutil.move(str(dev_compose), str(root_compose))

    devcontainer = path / ".devcontainer" / "devcontainer.json"
    data = json.loads(devcontainer.read_text())
    data["dockerComposeFile"] = ["../docker-compose.yml"]
    devcontainer.write_text(json.dumps(data, indent=2) + "\n")


def clean_root_md(path: Path, project_name: str, /) -> None:
    """Reset root README, CHANGELOG, and lockfiles for the new project.

    Args:
        path: Root of the generated project.
        project_name: The new project name.
    """
    (path / "README.md").write_text(f"# {project_name}\n\n")
    (path / "CHANGELOG.md").write_text("")
    (path / "uv.lock").unlink(True)
    (path / "pnpm-lock.yaml").unlink(True)
