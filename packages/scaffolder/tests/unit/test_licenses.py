# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.licenses."""

from pathlib import Path
from unittest.mock import patch

import pytest

from scaffolder.scaffold.licenses import (
    _validate_license,
    clear_licenses_dir,
    configure_licenses,
)

pytest_plugins = ("tests.fixture.template",)


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

    def test_clears_and_downloads_license(self, tmp_path: Path) -> None:
        """Clear LICENSES/ and write the license document."""
        (tmp_path / "LICENSES").mkdir()
        with patch("scaffolder.scaffold.licenses.write_license") as mock_write:
            configure_licenses(tmp_path, "MIT")
        mock_write.assert_called_once_with(tmp_path / "LICENSE", "MIT")

    def test_rejects_unknown_license(self, tmp_path: Path) -> None:
        """Fail before writing anything when the license is unknown."""
        with (
            pytest.raises(ValueError, match="Unknown SPDX license"),
            patch("scaffolder.scaffold.licenses.write_license") as mock_write,
        ):
            configure_licenses(tmp_path, "NOPE_XYZ")
        mock_write.assert_not_called()
