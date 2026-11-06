# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.config.pyproject."""

from pathlib import Path

import tomlkit

from shared_utils.config.pyproject import (
    clean_pyproject_dependencies,
    update_pyproject_authors,
    update_pyproject_coverage,
    update_pyproject_description,
    update_pyproject_name,
    update_pyproject_path,
    update_pyproject_workspace,
)


def _pyproject(tmp_path: Path, text: str, /) -> Path:
    """Seed a pyproject.toml holding text and return its path."""
    path = tmp_path / "pyproject.toml"
    path.write_text(text)
    return path


class TestUpdatePyprojectAuthors:
    """Tests for update_pyproject_authors."""

    def test_updates_existing_pyproject(self, tmp_path: Path) -> None:
        """Replace the authors in an existing pyproject.toml."""
        p = _pyproject(tmp_path, '[project]\nname = "old"\n')
        update_pyproject_authors(p, "New Name", "new@mail.com")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["authors"] == [
            {"name": "New Name", "email": "new@mail.com"}
        ]

    def test_creates_project_section(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = _pyproject(tmp_path, "")
        update_pyproject_authors(p, "Name", "email")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["authors"][0]["name"] == "Name"


class TestUpdatePyprojectName:
    """Tests for update_pyproject_name."""

    def test_updates_name(self, tmp_path: Path) -> None:
        """Replace the project name in an existing pyproject.toml."""
        p = _pyproject(tmp_path, '[project]\nname = "old"\n')
        update_pyproject_name(p, "new_name")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["name"] == "new_name"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = _pyproject(tmp_path, '[build-system]\nrequires = ["setuptools"]\n')
        update_pyproject_name(p, "new_name")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["name"] == "new_name"


class TestUpdatePyprojectDescription:
    """Tests for update_pyproject_description."""

    def test_updates_description(self, tmp_path: Path) -> None:
        """Replace the description in an existing pyproject.toml."""
        p = _pyproject(tmp_path, '[project]\nname = "x"\n')
        update_pyproject_description(p, "New desc")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["description"] == "New desc"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = _pyproject(tmp_path, '[build-system]\nrequires = ["setuptools"]\n')
        update_pyproject_description(p, "New desc")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["description"] == "New desc"


class TestUpdatePyprojectWorkspace:
    """Tests for update_pyproject_workspace."""

    def test_adds_source(self, tmp_path: Path) -> None:
        """Add the package as a workspace source."""
        p = _pyproject(tmp_path, "[tool.uv]\n")
        update_pyproject_workspace(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["tool"]["uv"]["sources"]["my_pkg"] == {"workspace": True}


class TestCleanPyprojectDependencies:
    """Tests for clean_pyproject_dependencies."""

    def test_clears_dependencies(self, tmp_path: Path) -> None:
        """Empty the dependencies list in an existing pyproject.toml."""
        p = _pyproject(tmp_path, '[project]\ndependencies = ["requests"]\n')
        clean_pyproject_dependencies(p)
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["dependencies"] == []

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = _pyproject(tmp_path, '[build-system]\nrequires = ["setuptools"]\n')
        clean_pyproject_dependencies(p)
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["dependencies"] == []


class TestUpdatePyprojectPath:
    """Tests for update_pyproject_path."""

    def test_updates_packages_find_include(self, tmp_path: Path) -> None:
        """Set the package in the setuptools find include list."""
        p = _pyproject(tmp_path, "[tool.setuptools.packages.find]\ninclude = []\n")
        update_pyproject_path(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]


class TestUpdatePyprojectCoverage:
    """Tests for update_pyproject_coverage."""

    def test_retargets_source_and_data_file(self, tmp_path: Path) -> None:
        """Point coverage source and data_file at the new package."""
        p = _pyproject(
            tmp_path,
            "[tool.coverage.run]\n"
            'source = ["shared_utils"]\n'
            'data_file = ".coverage.shared_utils"\n',
        )
        update_pyproject_coverage(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        run = doc["tool"]["coverage"]["run"]
        assert run["source"] == ["my_pkg"]
        assert run["data_file"] == ".coverage.my_pkg"

    def test_creates_coverage_run_when_missing(self, tmp_path: Path) -> None:
        """Create the coverage section when it is missing."""
        p = _pyproject(tmp_path, '[project]\nname = "x"\n')
        update_pyproject_coverage(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        run = doc["tool"]["coverage"]["run"]
        assert run["source"] == ["my_pkg"]
        assert run["data_file"] == ".coverage.my_pkg"
