# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.skeleton."""

import json
from pathlib import Path

import pytest
from scaffolder.scaffold.skeleton import (
    clean_root_md,
    remove_prod_docker,
    remove_projects_output_folder,
    write_package_files,
)

pytest_plugins = ("tests.fixture.template",)


class TestCleanRootMd:
    """Tests for clean_root_md."""

    def test_updates_readme(self, tmp_path: Path) -> None:
        """Reset the root README to a project header."""
        clean_root_md(tmp_path, "NewProject")
        assert (tmp_path / "README.md").read_text() == "# NewProject\n\n"

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

    @pytest.mark.parametrize("with_env", [False, True])
    def test_removes_prod_docker_and_promotes_dev(
        self,
        tmp_path: Path,
        dockerfile: Path,
        dev_compose: Path,
        devcontainer_json: Path,
        dot_env: Path,
        package_env: Path,
        with_env: bool,
    ) -> None:
        """Drop the prod setup and promote the dev compose to root."""
        env_files = (dot_env, package_env)
        if not with_env:
            for env_file in env_files:
                env_file.unlink()

        remove_prod_docker(tmp_path)

        assert not dockerfile.exists()
        assert (tmp_path / "docker-compose.yml").exists()
        assert not dev_compose.exists()
        config = json.loads(devcontainer_json.read_text())
        assert config["dockerComposeFile"] == ["../docker-compose.yml"]
        for env_file in env_files:
            text = env_file.read_text() if env_file.exists() else ""
            assert "SCAF_OUTPUT_DIR" not in text
            assert "mounted into the deploy container" not in text


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
