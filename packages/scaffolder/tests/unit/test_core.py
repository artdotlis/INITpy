# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.core."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from scaffolder.scaffold.core import ScaffoldArgs, clone_ref, run
from shared_utils.core.constants import VERSION

pytest_plugins = ("tests.fixture.mock", "tests.fixture.template")


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

    @pytest.mark.parametrize("pre_existing", [False, True])
    def test_creates_and_returns_output_path(
        self,
        tmp_path: Path,
        pipeline: tuple[dict[str, MagicMock], list[str]],
        pre_existing: bool,
    ) -> None:
        """Create the output directory, or reuse one that already exists."""
        if pre_existing:
            (tmp_path / "My Project").mkdir()
        result = run(_args(tmp_path))
        assert result == tmp_path / "My Project"
        assert result.is_dir()
        mocks, _ = pipeline
        mocks["clone_git"].assert_called_once()

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
