# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.licenses."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import tomlkit
from scaffolder.scaffold.licenses import (
    _validate_license,
    clear_licenses_dir,
    configure_licenses,
    set_license_licenses_sh,
    set_license_package_json,
    set_license_pyproject,
    update_licenses_sh,
)

pytest_plugins = ("tests.fixture.template",)


class TestUpdateLicensesSh:
    """Tests for update_licenses_sh."""

    def test_adds_exit_on_failure(self, tmp_path: Path, licenses_sh: Path) -> None:
        """Insert an early error exit right after the shebang."""
        update_licenses_sh(tmp_path)

        lines = licenses_sh.read_text().splitlines(keepends=True)
        assert lines[0].startswith("#!")
        assert "".join(lines[1:5]) == (
            "# TODO: Complete license implementation before use.\n"
            "# This script should fail until licenses are properly configured.\n"
            'echo "Licenses are not configured. Complete license implementation '
            'before use." >&2\n'
            "exit 1\n"
        )

    def test_raises_when_file_missing(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when licenses.sh is absent."""
        with pytest.raises(FileNotFoundError):
            update_licenses_sh(tmp_path)


class TestClearLicensesDir:
    """Tests for clear_licenses_dir."""

    def test_removes_files_from_licenses_dir(self, tmp_path: Path) -> None:
        """Delete every file inside the LICENSES directory."""
        lic = tmp_path / "LICENSES"
        lic.mkdir()
        (lic / "MIT.txt").write_text("license")
        (lic / "APACHE.txt").write_text("license")
        clear_licenses_dir(tmp_path)
        assert not any(lic.iterdir())

    def test_noop_when_no_licenses_dir(self, tmp_path: Path) -> None:
        """Do nothing when the LICENSES directory is absent."""
        clear_licenses_dir(tmp_path)  # should not raise


class TestSetLicensePyproject:
    """Tests for set_license_pyproject."""

    def test_sets_license(self, tmp_path: Path) -> None:
        """Set the license field in an existing pyproject.toml."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        set_license_pyproject(p, "MIT")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["license"] == "MIT"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        set_license_pyproject(p, "MIT")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["license"] == "MIT"


class TestSetLicensePackageJson:
    """Tests for set_license_package_json."""

    def test_sets_license(self, tmp_path: Path) -> None:
        """Set the license field in a package.json file."""
        p = tmp_path / "package.json"
        p.write_text('{"name": "x"}\n')
        set_license_package_json(p, "MIT")
        data = json.loads(p.read_text())
        assert data["license"] == "MIT"


class TestSetLicenseLicensesSh:
    """Tests for set_license_licenses_sh."""

    def test_sets_software_lic(self, licenses_sh: Path) -> None:
        """Replace the default SOFTWARE_LIC with the user's choice."""
        sh = licenses_sh
        set_license_licenses_sh(sh, "MIT")
        text = sh.read_text()
        assert 'SOFTWARE_LIC="MIT"' in text
        assert 'DATA_LIC="CC0-1.0"' in text

    def test_raises_when_assignment_missing(self, tmp_path: Path) -> None:
        """Fail loudly when SOFTWARE_LIC is not present."""
        sh = tmp_path / "licenses.sh"
        sh.write_text('DATA_LIC="CC0-1.0"\n')
        with pytest.raises(ValueError):
            set_license_licenses_sh(sh, "MIT")


class TestValidateLicense:
    """Tests for _validate_license."""

    def test_known_license_passes(self) -> None:
        """Accept a known SPDX license identifier."""
        _validate_license("MIT")  # should not raise

    def test_unknown_license_raises(self) -> None:
        """Raise ValueError for an unknown SPDX license identifier."""
        with pytest.raises(ValueError, match="Unknown SPDX license"):
            _validate_license("NONEXISTENT_LICENSE_XYZ")


class TestConfigureLicenses:
    """Tests for configure_licenses."""

    def test_configures_licenses(
        self,
        tmp_path: Path,
        pyproject_toml: Path,
        package_json: Path,
        licenses_sh: Path,
    ) -> None:
        """Clear, download, and set the license in all config files."""
        pyproject = pyproject_toml
        pkg_json = package_json

        with (
            patch("scaffolder.scaffold.licenses._validate_license"),
            patch("scaffolder.scaffold.licenses.write_license"),
            patch("scaffolder.scaffold.licenses.clear_licenses_dir") as mock_clear,
        ):
            configure_licenses(tmp_path, "MIT")
            mock_clear.assert_called_once()

        pydoc = tomlkit.parse(pyproject.read_text())
        assert pydoc["project"]["license"] == "MIT"

        pkg_data = json.loads(pkg_json.read_text())
        assert pkg_data["license"] == "MIT"
        assert 'SOFTWARE_LIC="MIT"' in licenses_sh.read_text()
