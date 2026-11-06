# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.package and core."""

from collections.abc import Iterator
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import tomlkit
from scaffolder.scaffold.package import create_package
from scaffolder.scaffold.core import ScaffoldArgs, clone_ref, run
from shared_utils.core.constants import VERSION

pytest_plugins = ("tests.fixture.template",)

CORE = "scaffolder.scaffold.core"


@pytest.fixture
def pipeline() -> Iterator[tuple[dict[str, MagicMock], list[str]]]:
    """Patch every run() collaborator and record the call order."""
    names = [
        "clone_git",
        "reset_git",
        "remove_projects_output_folder",
        "create_package",
        "write_package_files",
        "amend_docs",
        "update_envs",
        "update_copyright",
        "update_tests",
        "clean_root_md",
        "replace_authors",
        "correct_core_project",
        "set_version",
        "update_commitizen_version_files",
        "strip_spdx_headers",
        "configure_licenses",
        "remove_prod_docker",
        "update_licenses_sh",
        "remove_reuse",
        "remove_docs",
        "lock_project",
        "init_and_commit",
    ]
    with ExitStack() as stack:
        mocks = {name: stack.enter_context(patch(f"{CORE}.{name}")) for name in names}
        order: list[str] = []

        def _record(name: str) -> object:
            def _side_effect(*args: object, **kwargs: object) -> None:
                del args, kwargs
                order.append(name)

            return _side_effect

        for name, mock in mocks.items():
            mock.side_effect = _record(name)
        yield mocks, order


def _args(tmp_path: Path, **overrides: object) -> ScaffoldArgs:
    """Build scaffold args pointing at tmp_path."""
    kwargs: dict[str, object] = {
        "project_name": "My Project",
        "output_dir": str(tmp_path),
        "author_name": "Ann",
        "author_email": "ann@example.com",
        "license_name": "MIT",
        "description": "A demo",
        "copyright": "2026 Ann",
        "use_reuse": True,
        "use_docs": True,
    }
    kwargs.update(overrides)
    return ScaffoldArgs(**kwargs)  # type: ignore[arg-type]


@pytest.fixture
def clone_path(shared_utils_pyproject: Path) -> Path:
    """Clone root seeded with the live shared_utils pyproject."""
    return shared_utils_pyproject.parents[2]


class TestCreatePackage:
    """Tests for create_package."""

    def test_writes_package_pyproject(self, clone_path: Path) -> None:
        """Carry the live template into the new package, retargeted at it."""
        create_package(clone_path, "my_pkg", "A package desc")

        pyproject = clone_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["name"] == "my_pkg"
        assert doc["project"]["description"] == "A package desc"
        assert doc["project"]["dependencies"] == []
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]
        run = doc["tool"]["coverage"]["run"]
        assert run["source"] == ["my_pkg"]
        assert run["data_file"] == ".coverage.my_pkg"

    def test_creates_package_dirs(self, clone_path: Path) -> None:
        """Create the package directory and its nested src package."""
        create_package(clone_path, "my_pkg", "A package")
        assert (clone_path / "packages" / "my_pkg" / "src" / "my_pkg").is_dir()

    def test_replaces_other_packages_but_keeps_docs(self, clone_path: Path) -> None:
        """Drop pre-existing packages, keep the docs package."""
        existing = clone_path / "packages" / "existing_pkg"
        existing.mkdir(parents=True)
        (existing / "file.txt").write_text("x")
        docs = clone_path / "packages" / "docs"
        docs.mkdir(parents=True)
        (docs / "file.txt").write_text("x")

        create_package(clone_path, "my_pkg", "A package")

        assert not existing.exists()
        assert docs.exists()


class TestCloneRef:
    """Tests for the cloned INITpy ref selection."""

    def test_defaults_to_version_tag(self) -> None:
        """Clone the tag matching the release version by default."""
        with patch.dict("os.environ", {}, clear=True):
            assert clone_ref() == f"v{VERSION}"

    def test_dev_env_clones_dev(self) -> None:
        """Clone the dev branch when SCAF_DEV is set."""
        with patch.dict("os.environ", {"SCAF_DEV": "1"}, clear=True):
            assert clone_ref() == "dev"


class TestRun:
    """Tests for the run() orchestration."""

    def test_creates_and_returns_output_path(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Create the output directory and return it."""
        result = run(_args(tmp_path))
        assert result == tmp_path / "My Project"
        assert result.is_dir()

    def test_reuses_existing_output_path(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Accept an output directory that already exists."""
        (tmp_path / "My Project").mkdir()
        assert run(_args(tmp_path)).is_dir()

    def test_clones_template_at_ref(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Clone INITpy at the computed ref into the output path."""
        mocks, _ = pipeline
        result = run(_args(tmp_path))
        mocks["clone_git"].assert_called_once_with(
            result, "https://github.com/artdotlis/INITpy.git", clone_ref()
        )

    def test_derives_package_names(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Sanitize the project name into package and dep-group names."""
        mocks, _ = pipeline
        result = run(_args(tmp_path))
        mocks["create_package"].assert_called_once_with(
            result, "my_project_pkg", "A demo"
        )
        assert mocks["correct_core_project"].call_args.args == (
            result,
            "My Project",
            "my_project_pkg",
            "my-project-pkg",
            "A demo",
        )

    def test_passes_metadata_to_collaborators(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Pass author, copyright and license data to their handlers."""
        mocks, _ = pipeline
        result = run(_args(tmp_path))
        mocks["replace_authors"].assert_called_once_with(result, "ann@example.com", "Ann")
        mocks["update_copyright"].assert_called_once_with(result, "2026 Ann")
        mocks["configure_licenses"].assert_called_once_with(result, "MIT")
        mocks["set_version"].assert_called_once_with(result, "0.1.0")
        mocks["init_and_commit"].assert_called_once_with(result, "Ann", "ann@example.com")

    def test_runs_steps_in_order(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Run every mandatory step exactly once in the documented order."""
        _, order = pipeline
        run(_args(tmp_path))
        assert order == [
            "clone_git",
            "reset_git",
            "remove_projects_output_folder",
            "create_package",
            "write_package_files",
            "amend_docs",
            "update_envs",
            "update_copyright",
            "update_tests",
            "clean_root_md",
            "replace_authors",
            "correct_core_project",
            "set_version",
            "update_commitizen_version_files",
            "strip_spdx_headers",
            "configure_licenses",
            "remove_prod_docker",
            "update_licenses_sh",
            "lock_project",
            "init_and_commit",
        ]

    def test_keeps_docs_and_reuse_when_requested(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Keep the docs subpackage and reuse tooling when requested."""
        mocks, _ = pipeline
        run(_args(tmp_path, use_docs=True, use_reuse=True))
        mocks["amend_docs"].assert_called_once()
        mocks["remove_docs"].assert_not_called()
        mocks["remove_reuse"].assert_not_called()

    def test_removes_docs_and_reuse_when_declined(
        self, tmp_path: Path, pipeline: tuple[dict[str, MagicMock], list[str]]
    ) -> None:
        """Drop the docs subpackage and reuse tooling when declined."""
        mocks, _ = pipeline
        result = run(_args(tmp_path, use_docs=False, use_reuse=False))
        mocks["remove_docs"].assert_called_once_with(result)
        mocks["remove_reuse"].assert_called_once_with(result)
        mocks["amend_docs"].assert_not_called()
