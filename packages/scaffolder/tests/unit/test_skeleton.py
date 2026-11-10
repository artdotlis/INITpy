# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.skeleton."""

from pathlib import Path

import pytest
from scaffolder.scaffold.skeleton import (
    clean_root_md,
    remove_prod_docker,
    remove_projects_output_folder,
    write_package_files,
)


class TestCleanRootMd:
    """Tests for clean_root_md."""

    def test_updates_readme(self, tmp_path: Path) -> None:
        """Reset the root README from its template."""
        clean_root_md(tmp_path, "NewProject")
        assert "NewProject" in (tmp_path / "README.md").read_text()

    def test_clears_changelog(self, tmp_path: Path) -> None:
        """Empty the CHANGELOG file."""
        clean_root_md(tmp_path, "Proj")
        assert (tmp_path / "CHANGELOG.md").read_text() == ""

    def test_removes_lock_files(self, tmp_path: Path) -> None:
        """Delete the uv and pnpm lockfiles."""
        (tmp_path / "uv.lock").write_text("x")
        (tmp_path / "pnpm-lock.yaml").write_text("y")
        clean_root_md(tmp_path, "Proj")
        assert not (tmp_path / "uv.lock").exists()
        assert not (tmp_path / "pnpm-lock.yaml").exists()


class TestRemoveProjectsOutputFolder:
    """Tests for remove_projects_output_folder."""

    def test_removes_directory(self, tmp_path: Path) -> None:
        """Delete the PROJECTS directory and its contents."""
        projects = tmp_path / "PROJECTS"
        (projects / "demo").mkdir(parents=True)
        remove_projects_output_folder(tmp_path)
        assert not projects.exists()

    def test_removes_file_named_projects(self, tmp_path: Path) -> None:
        """Unlink a PROJECTS path that is a plain file."""
        (tmp_path / "PROJECTS").write_text("stale")
        remove_projects_output_folder(tmp_path)
        assert not (tmp_path / "PROJECTS").exists()

    def test_noop_without_projects(self, tmp_path: Path) -> None:
        """Do nothing when there is no PROJECTS path."""
        remove_projects_output_folder(tmp_path)
        assert list(tmp_path.iterdir()) == []


class TestRemoveProdDocker:
    """Tests for remove_prod_docker."""

    def _seed(self, tmp_path: Path) -> None:
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text("# prod\n")
        dev = tmp_path / ".devcontainer"
        dev.mkdir(parents=True, exist_ok=True)
        (dev / "dev.docker-compose.yml").write_text("services: {}\n")

    def test_removes_prod_docker_and_promotes_dev(self, tmp_path: Path) -> None:
        """Drop the prod Dockerfile and promote the dev compose to root."""
        self._seed(tmp_path)
        dev_compose = tmp_path / ".devcontainer" / "dev.docker-compose.yml"
        remove_prod_docker(tmp_path)
        assert not (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").exists()
        assert not dev_compose.exists()

    def test_raises_when_dockerfile_missing(self, tmp_path: Path) -> None:
        """Fail loudly when the production Dockerfile is absent."""
        self._seed(tmp_path)
        (tmp_path / "Dockerfile").unlink()
        with pytest.raises(FileNotFoundError):
            remove_prod_docker(tmp_path)

    def test_raises_when_dev_compose_missing(self, tmp_path: Path) -> None:
        """Fail loudly when the dev compose is absent."""
        self._seed(tmp_path)
        (tmp_path / ".devcontainer" / "dev.docker-compose.yml").unlink()
        with pytest.raises(FileNotFoundError):
            remove_prod_docker(tmp_path)


class TestWritePackageFiles:
    """Tests for write_package_files."""

    def test_writes_package_skeleton(self, tmp_path: Path) -> None:
        """Write the package layout and its placeholder files."""
        write_package_files(tmp_path, "my_pkg")
        pkg = tmp_path / "packages" / "my_pkg"

        assert (pkg / "src" / "my_pkg").is_dir()
        assert (pkg / "src" / "my_pkg" / "main.py").read_text() == (
            "# TODO: Implement my_pkg\n"
        )
        assert (pkg / "src" / "my_pkg" / "py.typed").exists()
        assert (pkg / "src" / "my_pkg" / "__init__.py").read_text() == (
            "__all__: list[str] = []"
        )
        assert (pkg / "README.md").read_text() == "# my_pkg\n"
        assert (pkg / ".env").exists()
        assert (pkg / "tests" / "unit").is_dir()

        placeholder = (pkg / "tests" / "unit" / "test_my_pkg.py").read_text()
        assert placeholder == (
            "\ndef test_placeholder() -> None:\n"
            "    # TODO finish tests\n"
            "    assert False\n"
        )
