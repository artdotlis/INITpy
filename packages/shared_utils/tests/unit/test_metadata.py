# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.metadata."""

import json

from pathlib import Path


import tomlkit

from shared_utils.metadata import replace_authors

from shared_utils.metadata import set_version


class TestReplaceAuthors:
    """Tests for replace_authors."""

    def test_replaces_in_pyproject(self, tmp_path: Path) -> None:
        """Update the author in a pyproject.toml file."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
        replace_authors(tmp_path, "a@b.com", "Name")
        doc = tomlkit.parse((tmp_path / "pyproject.toml").read_text())
        assert doc["project"]["authors"][0]["email"] == "a@b.com"

    def test_replaces_in_package_json(self, tmp_path: Path) -> None:
        """Update the author in a package.json file."""
        (tmp_path / "package.json").write_text('{"name": "x"}\n')
        replace_authors(tmp_path, "a@b.com", "Name")
        data = json.loads((tmp_path / "package.json").read_text())
        assert data["author"]["email"] == "a@b.com"

    def test_ignores_non_matching_files(self, tmp_path: Path) -> None:
        """Leave files that are neither pyproject.toml nor package.json."""
        (tmp_path / "other.txt").write_text("content")
        (tmp_path / "subdir").mkdir()  # rglob returns dirs too
        replace_authors(tmp_path, "a@b.com", "Name")
        assert (tmp_path / "other.txt").read_text() == "content"


class TestSetVersion:
    """Tests for set_version."""

    def test_sets_pyproject_version(self, tmp_path: Path) -> None:
        """Set the version in a pyproject.toml file."""
        (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1.0.0"\n')
        set_version(tmp_path, "0.2.0")
        doc = tomlkit.parse((tmp_path / "pyproject.toml").read_text())
        assert doc["project"]["version"] == "0.2.0"

    def test_sets_package_json_version(self, tmp_path: Path) -> None:
        """Set the version in a package.json file."""
        (tmp_path / "package.json").write_text('{"name": "x", "version": "1.0.0"}\n')
        set_version(tmp_path, "0.3.0")
        data = json.loads((tmp_path / "package.json").read_text())
        assert data["version"] == "0.3.0"

    def test_ignores_unrelated_files(self, tmp_path: Path) -> None:
        """Leave non-version files untouched."""
        (tmp_path / "other.txt").write_text("content")
        set_version(tmp_path, "0.1.0")
        assert (tmp_path / "other.txt").read_text() == "content"

    def test_missing_version_field_left_alone(self, tmp_path: Path) -> None:
        """Leave files with no version field unchanged."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        set_version(tmp_path, "0.1.0")
        doc = tomlkit.parse(p.read_text())
        assert "version" not in doc["project"]
