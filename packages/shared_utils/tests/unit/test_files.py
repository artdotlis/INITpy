# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.files."""

import json
from pathlib import Path
from unittest.mock import patch

import tomlkit
from reuse.comment import PythonCommentStyle
from shared_utils.files import (
    _find_spdx_block,
    clean_pyproject_dependencies,
    replace_authors,
    set_version,
    strip_spdx_headers,
    update_package_authors,
    update_package_devcon_name,
    update_pyproject_authors,
    update_pyproject_coverage,
    update_pyproject_description,
    update_pyproject_name,
    update_pyproject_path,
    update_pyproject_workspace,
    write_license,
)


class TestFindSpdxBlock:
    """Tests for _find_spdx_block."""

    def test_returns_none_when_no_spdx(self) -> None:
        """Return None for text with no SPDX block."""
        result = _find_spdx_block("# hello world", PythonCommentStyle)
        assert result is None

    def test_returns_block_when_spdx_exists(self) -> None:
        """Return the offset and content of an SPDX comment block."""
        # REUSE-IgnoreStart
        text = "# SPDX-License-Identifier: MIT"
        # REUSE-IgnoreEnd
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is not None
        start, block = result
        assert start == 0
        assert "SPDX" in block

    def test_skips_lines_without_spdx(self) -> None:
        """Find the block even when preceding lines lack SPDX markers."""
        # REUSE-IgnoreStart
        text = "# no spdx\n# SPDX-License-Identifier: CC0-1.0"
        # REUSE-IgnoreEnd
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is not None
        start, block = result
        assert "SPDX" in block

    def test_iterates_when_no_spdx_found(self) -> None:
        """Return None after exhausting the comment block."""
        text = "# line1\n# line2\n# line3\n" * 10 + "end"
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is None

    def test_handles_first_line_only(self) -> None:
        """Return None for a single line with no SPDX."""
        # Single line with no newline triggers the `nxt == -1` break
        text = "# no SPDX here"
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is None


class TestUpdatePyprojectAuthors:
    """Tests for update_pyproject_authors."""

    def test_updates_existing_pyproject(self, tmp_path: Path) -> None:
        """Replace the authors in an existing pyproject.toml."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "old"\n')
        update_pyproject_authors(p, "New Name", "new@mail.com")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["authors"] == [
            {"name": "New Name", "email": "new@mail.com"}
        ]

    def test_creates_project_section(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = tmp_path / "pyproject.toml"
        p.write_text("")
        update_pyproject_authors(p, "Name", "email")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["authors"][0]["name"] == "Name"


class TestUpdatePyprojectName:
    """Tests for update_pyproject_name."""

    def test_updates_name(self, tmp_path: Path) -> None:
        """Replace the project name in an existing pyproject.toml."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "old"\n')
        update_pyproject_name(p, "new_name")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["name"] == "new_name"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        update_pyproject_name(p, "new_name")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["name"] == "new_name"


class TestUpdatePyprojectDescription:
    """Tests for update_pyproject_description."""

    def test_updates_description(self, tmp_path: Path) -> None:
        """Replace the description in an existing pyproject.toml."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        update_pyproject_description(p, "New desc")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["description"] == "New desc"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        update_pyproject_description(p, "New desc")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["description"] == "New desc"


class TestUpdatePyprojectWorkspace:
    """Tests for update_pyproject_workspace."""

    def test_adds_source(self, tmp_path: Path) -> None:
        """Add the package as a workspace source."""
        p = tmp_path / "pyproject.toml"
        p.write_text("[tool.uv]\n")
        update_pyproject_workspace(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["tool"]["uv"]["sources"]["my_pkg"] == {"workspace": True}


class TestCleanPyprojectDependencies:
    """Tests for clean_pyproject_dependencies."""

    def test_clears_dependencies(self, tmp_path: Path) -> None:
        """Empty the dependencies list in an existing pyproject.toml."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\ndependencies = ["requests"]\n')
        clean_pyproject_dependencies(p)
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["dependencies"] == []

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        clean_pyproject_dependencies(p)
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["dependencies"] == []


class TestUpdatePyprojectPath:
    """Tests for update_pyproject_path."""

    def test_updates_packages_find_include(self, tmp_path: Path) -> None:
        """Set the package in the setuptools find include list."""
        p = tmp_path / "pyproject.toml"
        p.write_text("[tool.setuptools.packages.find]\ninclude = []\n")
        update_pyproject_path(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]


class TestUpdatePyprojectCoverage:
    """Tests for update_pyproject_coverage."""

    def test_retargets_source_and_data_file(self, tmp_path: Path) -> None:
        """Point coverage source and data_file at the new package."""
        p = tmp_path / "pyproject.toml"
        p.write_text(
            "[tool.coverage.run]\n"
            'source = ["shared_utils"]\n'
            'data_file = ".coverage.shared_utils"\n'
        )
        update_pyproject_coverage(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        run = doc["tool"]["coverage"]["run"]
        assert run["source"] == ["my_pkg"]
        assert run["data_file"] == ".coverage.my_pkg"

    def test_creates_coverage_run_when_missing(self, tmp_path: Path) -> None:
        """Create the coverage section when it is missing."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        update_pyproject_coverage(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        run = doc["tool"]["coverage"]["run"]
        assert run["source"] == ["my_pkg"]
        assert run["data_file"] == ".coverage.my_pkg"


class TestUpdatePackageAuthors:
    """Tests for update_package_authors."""

    def test_updates_author(self, tmp_path: Path) -> None:
        """Set the author object in a package.json file."""
        p = tmp_path / "package.json"
        p.write_text('{"name": "x"}\n')
        update_package_authors(p, "New Name", "new@mail.com")
        data = json.loads(p.read_text())
        assert data["author"] == {"email": "new@mail.com", "name": "New Name"}


class TestUpdatePackageDevconName:
    """Tests for update_package_devcon_name."""

    def test_updates_name(self, tmp_path: Path) -> None:
        """Replace the name field in a JSON file."""
        p = tmp_path / "package.json"
        p.write_text('{"name": "old"}\n')
        update_package_devcon_name(p, "new_name")
        data = json.loads(p.read_text())
        assert data["name"] == "new_name"


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


class TestStripSpdxHeaders:
    """Tests for strip_spdx_headers."""

    def test_removes_spdx_from_file(self, tmp_path: Path) -> None:
        """Remove SPDX headers from a file."""
        f = tmp_path / "file.py"
        f.write_text("# SPDX-License-Identifier: MIT\n# Copyright 2024\n\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        text = f.read_text()
        assert "SPDX" not in text
        assert "print('hi')" in text

    def test_removes_license_file(self, tmp_path: Path) -> None:
        """Delete the companion .license file."""
        (tmp_path / "MIT.license").write_text("license text")
        strip_spdx_headers(tmp_path)
        assert not (tmp_path / "MIT.license").exists()

    def test_skips_files_without_spdx(self, tmp_path: Path) -> None:
        """Leave files that contain no SPDX block unchanged."""
        f = tmp_path / "no_spdx.py"
        f.write_text("print('hello')\n")
        strip_spdx_headers(tmp_path)
        assert f.read_text() == "print('hello')\n"

    def test_handles_none_comment_style(self, tmp_path: Path) -> None:
        """Leave the file unchanged when no comment style is detected."""
        f = tmp_path / "file.py"
        f.write_text("# Contains SPDX somewhere\nprint('hi')\n")
        with patch("shared_utils.files.get_comment_style", return_value=None):
            strip_spdx_headers(tmp_path)
        # File should be unchanged since get_comment_style returned None
        assert f.read_text() == "# Contains SPDX somewhere\nprint('hi')\n"

    def test_handles_no_spdx_found(self, tmp_path: Path) -> None:
        """Leave a comment-only file unchanged."""
        f = tmp_path / "file.py"
        f.write_text("# just a comment\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        assert f.read_text() == "# just a comment\nprint('hi')\n"

    def test_handles_spdx_but_not_valid_block(self, tmp_path: Path) -> None:
        """Keep the text when SPDX is not part of a valid comment block."""
        f = tmp_path / "file.py"
        f.write_text("# SPDX not valid here\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        assert "SPDX" in f.read_text()


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


class TestWriteLicense:
    """Tests for write_license."""

    def test_writes_license_file(self, tmp_path: Path) -> None:
        """Download the license text into the target file."""
        lic_file = tmp_path / "LICENSE"
        lic_file.write_text("old content")
        with patch("shared_utils.files.put_license_in_file") as mock_put:
            write_license(lic_file, "MIT")
            mock_put.assert_called_once_with("MIT", lic_file)
