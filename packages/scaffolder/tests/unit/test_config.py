# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.config."""

import json
from pathlib import Path
from typing import Any, Callable

import pytest
import tomlkit
from scaffolder.scaffold.config import (
    correct_core_project,
    update_commitizen_version_files,
    update_pyproject_dep_groups,
)

pytest_plugins = ("tests.fixture.template",)


def _drop_tool_table(doc: Any) -> None:
    """Remove the whole [tool] table."""
    _ = doc.pop("tool")


def _drop_commitizen_table(doc: Any) -> None:
    """Remove the [tool.commitizen] table."""
    _ = doc["tool"].pop("commitizen")


def _make_version_files_a_string(doc: Any) -> None:
    """Replace the version_files list with a bare string."""
    doc["tool"]["commitizen"]["version_files"] = "pyproject.toml"


def _drop_version_files(doc: Any) -> None:
    """Remove version_files from the [tool.commitizen] table."""
    _ = doc["tool"]["commitizen"].pop("version_files")


class TestUpdateCommitizenVersionFiles:
    """Tests for update_commitizen_version_files (live root pyproject.toml)."""

    def test_retargets_and_removes_shared_utils(
        self, tmp_path: Path, pyproject_toml: Path
    ) -> None:
        """Drop shared_utils entries and rename scaffolder to new package."""
        update_commitizen_version_files(tmp_path, "my_pkg")

        doc = tomlkit.parse(pyproject_toml.read_text())
        files = doc["tool"]["commitizen"]["version_files"]
        # README badge entry is kept unchanged
        assert files[0].startswith("README.md:")
        assert "packages/shared_utils" not in "\n".join(files)
        assert files == [
            files[0],
            "package.json",
            "pyproject.toml",
            "packages/my_pkg/pyproject.toml",
            "packages/docs/package.json",
        ]

    def test_raises_when_missing(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when there is no pyproject.toml."""
        with pytest.raises(FileNotFoundError):
            update_commitizen_version_files(tmp_path, "my_pkg")

    @pytest.mark.parametrize(
        "mutate",
        [
            pytest.param(_drop_tool_table, id="no-tool-table"),
            pytest.param(_drop_commitizen_table, id="no-commitizen"),
            pytest.param(_make_version_files_a_string, id="version-files-not-a-list"),
            pytest.param(_drop_version_files, id="no-version-files"),
        ],
    )
    def test_leaves_incomplete_pyproject_untouched(
        self, tmp_path: Path, pyproject_toml: Path, mutate: Callable[[Any], None]
    ) -> None:
        """Skip the rewrite when the commitizen version_files block is absent."""
        doc = tomlkit.parse(pyproject_toml.read_text())
        mutate(doc)
        pyproject_toml.write_text(tomlkit.dumps(doc))
        before = pyproject_toml.read_text()

        update_commitizen_version_files(tmp_path, "my_pkg")

        assert pyproject_toml.read_text() == before


class TestCorrectCoreProject:
    """Tests for correct_core_project."""

    def test_updates_all_files(
        self,
        tmp_path: Path,
        pyproject_toml: Path,
        package_json: Path,
        devcontainer_json: Path,
    ) -> None:
        """Apply project metadata to the live root config files."""
        pyproject = pyproject_toml
        pkg_json = package_json
        devcontainer = devcontainer_json

        correct_core_project(tmp_path, "NewProject", "my_pkg", "my-pkg", "New desc")

        pydoc = tomlkit.parse(pyproject.read_text())
        assert pydoc["project"]["name"] == "NewProject"
        assert pydoc["project"]["description"] == "New desc"
        assert pydoc["tool"]["uv"]["sources"]["my_pkg"] == {"workspace": True}
        assert "mono" in pydoc["dependency-groups"]

        pkg_data = json.loads(pkg_json.read_text())
        assert pkg_data["name"] == "NewProject"

        dc_data = json.loads(devcontainer.read_text())
        assert dc_data["name"] == "NewProject"


class TestUpdatePyprojectDepGroups:
    """Tests for update_pyproject_dep_groups."""

    def test_adds_mono_group(self, tmp_path: Path) -> None:
        """Add the package to the mono dependency group."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        update_pyproject_dep_groups(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["dependency-groups"]["mono"] == ["my_pkg"]
