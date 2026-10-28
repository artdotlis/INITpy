# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.files."""

from pathlib import Path
from unittest.mock import patch
import tomlkit

from shared_utils.files import (
    _find_spdx_block,
    strip_spdx_headers,
    update_pyproject_authors,
    update_pyproject_name,
    update_pyproject_description,
    update_pyproject_workspace,
    update_pyproject_dep_groups,
    clean_pyproject_dependencies,
    update_pyproject_path,
    update_package_authors,
    update_package_devcon_name,
    replace_authors,
    clear_licenses_dir,
    _write_license,
    set_license_pyproject,
    set_license_package_json,
    configure_licenses,
    _validate_license,
)


class TestFindSpdxBlock:
    def test_returns_none_when_no_spdx(self) -> None:
        from reuse.comment import PythonCommentStyle

        result = _find_spdx_block("# hello world", PythonCommentStyle)
        assert result is None

    def test_returns_block_when_spdx_exists(self) -> None:
        from reuse.comment import PythonCommentStyle

        # REUSE-IgnoreStart
        text = "# SPDX-License-Identifier: MIT"
        # REUSE-IgnoreEnd
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is not None
        start, block = result
        assert start == 0
        assert "SPDX" in block

    def test_skips_lines_without_spdx(self) -> None:
        from reuse.comment import PythonCommentStyle

        # REUSE-IgnoreStart
        text = "# no spdx\n# SPDX-License-Identifier: CC0-1.0"
        # REUSE-IgnoreEnd
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is not None
        start, block = result
        assert "SPDX" in block

    def test_iterates_when_no_spdx_found(self) -> None:
        from reuse.comment import PythonCommentStyle

        text = "# line1\n# line2\n# line3\n" * 10 + "end"
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is None

    def test_handles_first_line_only(self) -> None:
        from reuse.comment import PythonCommentStyle

        # Single line with no newline triggers the `nxt == -1` break
        text = "# no SPDX here"
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is None


class TestUpdatePyprojectAuthors:
    def test_updates_existing_pyproject(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "old"\n')
        update_pyproject_authors(p, "New Name", "new@mail.com")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["authors"] == [
            {"name": "New Name", "email": "new@mail.com"}
        ]

    def test_creates_project_section(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text("")
        update_pyproject_authors(p, "Name", "email")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["authors"][0]["name"] == "Name"


class TestUpdatePyprojectName:
    def test_updates_name(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "old"\n')
        update_pyproject_name(p, "new_name")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["name"] == "new_name"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        update_pyproject_name(p, "new_name")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["name"] == "new_name"


class TestUpdatePyprojectDescription:
    def test_updates_description(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        update_pyproject_description(p, "New desc")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["description"] == "New desc"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        update_pyproject_description(p, "New desc")
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["description"] == "New desc"


class TestUpdatePyprojectWorkspace:
    def test_adds_source(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text("[tool.uv]\n")
        update_pyproject_workspace(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["tool"]["uv"]["sources"]["my_pkg"] == {"workspace": True}


class TestUpdatePyprojectDepGroups:
    def test_adds_mono_group(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        update_pyproject_dep_groups(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["dependency-groups"]["mono"] == ["my_pkg"]


class TestCleanPyprojectDependencies:
    def test_clears_dependencies(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\ndependencies = ["requests"]\n')
        clean_pyproject_dependencies(p)
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["dependencies"] == []

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        clean_pyproject_dependencies(p)
        doc = tomlkit.parse(p.read_text())
        assert "project" in doc
        assert doc["project"]["dependencies"] == []


class TestUpdatePyprojectPath:
    def test_updates_packages_find_include(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text("[tool.setuptools.packages.find]\ninclude = []\n")
        update_pyproject_path(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]


class TestUpdatePackageAuthors:
    def test_updates_author(self, tmp_path: Path) -> None:
        p = tmp_path / "package.json"
        p.write_text('{"name": "x"}\n')
        update_package_authors(p, "New Name", "new@mail.com")
        import json

        data = json.loads(p.read_text())
        assert data["author"] == {"email": "new@mail.com", "name": "New Name"}


class TestUpdatePackageDevconName:
    def test_updates_name(self, tmp_path: Path) -> None:
        p = tmp_path / "package.json"
        p.write_text('{"name": "old"}\n')
        update_package_devcon_name(p, "new_name")
        import json

        data = json.loads(p.read_text())
        assert data["name"] == "new_name"


class TestReplaceAuthors:
    def test_replaces_in_pyproject(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
        replace_authors(tmp_path, "a@b.com", "Name")
        doc = tomlkit.parse((tmp_path / "pyproject.toml").read_text())
        assert doc["project"]["authors"][0]["email"] == "a@b.com"

    def test_replaces_in_package_json(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text('{"name": "x"}\n')
        replace_authors(tmp_path, "a@b.com", "Name")
        import json

        data = json.loads((tmp_path / "package.json").read_text())
        assert data["author"]["email"] == "a@b.com"

    def test_ignores_non_matching_files(self, tmp_path: Path) -> None:
        (tmp_path / "other.txt").write_text("content")
        (tmp_path / "subdir").mkdir()  # rglob returns dirs too
        replace_authors(tmp_path, "a@b.com", "Name")
        assert (tmp_path / "other.txt").read_text() == "content"


class TestStripSpdxHeaders:
    def test_removes_spdx_from_file(self, tmp_path: Path) -> None:
        f = tmp_path / "file.py"
        f.write_text("# SPDX-License-Identifier: MIT\n# Copyright 2024\n\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        text = f.read_text()
        assert "SPDX" not in text
        assert "print('hi')" in text

    def test_removes_license_file(self, tmp_path: Path) -> None:
        (tmp_path / "MIT.license").write_text("license text")
        strip_spdx_headers(tmp_path)
        assert not (tmp_path / "MIT.license").exists()

    def test_skips_files_without_spdx(self, tmp_path: Path) -> None:
        f = tmp_path / "no_spdx.py"
        f.write_text("print('hello')\n")
        strip_spdx_headers(tmp_path)
        assert f.read_text() == "print('hello')\n"

    def test_handles_none_comment_style(self, tmp_path: Path) -> None:
        f = tmp_path / "file.py"
        f.write_text("# Contains SPDX somewhere\nprint('hi')\n")
        with patch("shared_utils.files.get_comment_style", return_value=None):
            strip_spdx_headers(tmp_path)
        # File should be unchanged since get_comment_style returned None
        assert f.read_text() == "# Contains SPDX somewhere\nprint('hi')\n"

    def test_handles_no_spdx_found(self, tmp_path: Path) -> None:
        f = tmp_path / "file.py"
        f.write_text("# just a comment\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        assert f.read_text() == "# just a comment\nprint('hi')\n"

    def test_handles_spdx_but_not_valid_block(self, tmp_path: Path) -> None:
        f = tmp_path / "file.py"
        f.write_text("# SPDX not valid here\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        assert "SPDX" in f.read_text()


class TestClearLicensesDir:
    def test_removes_files_from_licenses_dir(self, tmp_path: Path) -> None:
        lic = tmp_path / "LICENSES"
        lic.mkdir()
        (lic / "MIT.txt").write_text("license")
        (lic / "APACHE.txt").write_text("license")
        clear_licenses_dir(tmp_path)
        assert not any(lic.iterdir())

    def test_noop_when_no_licenses_dir(self, tmp_path: Path) -> None:
        clear_licenses_dir(tmp_path)  # should not raise


class TestSetLicensePyproject:
    def test_sets_license(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        set_license_pyproject(p, "MIT")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["license"] == "MIT"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        set_license_pyproject(p, "MIT")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["license"] == "MIT"


class TestSetLicensePackageJson:
    def test_sets_license(self, tmp_path: Path) -> None:
        p = tmp_path / "package.json"
        p.write_text('{"name": "x"}\n')
        set_license_package_json(p, "MIT")
        import json

        data = json.loads(p.read_text())
        assert data["license"] == "MIT"


class TestValidateLicense:
    def test_known_license_passes(self) -> None:
        _validate_license("MIT")  # should not raise

    def test_unknown_license_raises(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="Unknown SPDX license"):
            _validate_license("NONEXISTENT_LICENSE_XYZ")


class TestWriteLicense:
    def test_writes_license_file(self, tmp_path: Path) -> None:
        lic_file = tmp_path / "LICENSE"
        lic_file.write_text("old content")
        with patch("shared_utils.files.put_license_in_file") as mock_put:
            _write_license(lic_file, "MIT")
            mock_put.assert_called_once_with("MIT", lic_file)
        # file is recreated by put_license_in_file (which writes something)


class TestConfigureLicenses:
    def test_configures_licenses(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "x"\n')
        pkg_json = tmp_path / "package.json"
        pkg_json.write_text('{"name": "x"}\n')
        licenses_dir = tmp_path / "LICENSES"
        licenses_dir.mkdir()
        (licenses_dir / "MIT.txt").write_text("x")
        # LICENSE file must exist (it gets unlinked first by _write_license)
        (tmp_path / "LICENSE").write_text("old")

        with (
            patch("shared_utils.files._validate_license"),
            patch("shared_utils.files._write_license"),
            patch("shared_utils.files.clear_licenses_dir") as mock_clear,
        ):
            configure_licenses(tmp_path, "MIT")
            mock_clear.assert_called_once()

        pydoc = tomlkit.parse(pyproject.read_text())
        assert pydoc["project"]["license"] == "MIT"

        import json

        pkg_data = json.loads(pkg_json.read_text())
        assert pkg_data["license"] == "MIT"
