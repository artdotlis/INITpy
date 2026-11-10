# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.core.names."""

import pytest

from shared_utils.core.names import (
    package_abbrev,
    package_env_file,
    package_env_var,
    sanitize_package_name,
    sanitize_package_name_dep_group,
)


class TestSanitizePackageName:
    """Tests for sanitize_package_name."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("my_project", "my_project"),
            ("my project name", "my_project_name"),
            ("my-project-name", "my_project_name"),
            ("my@project!name#", "myprojectname"),
            ("123project", "_123project"),
            ("MYPROJECT", "myproject"),
            ("My Project-Name", "my_project_name"),
            ("", "project"),
            ("123", "_123"),
        ],
    )
    def test_sanitizes(self, raw: str, expected: str) -> None:
        """Replace invalid characters and fix up the edges."""
        assert sanitize_package_name(raw) == expected


class TestSanitizePackageNameDepGroup:
    """Tests for sanitize_package_name_dep_group."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("my_project", "my-project"),
            ("my project name", "my-project-name"),
            ("my_project_name", "my-project-name"),
            ("my@project!name#", "myprojectname"),
            ("123project", "-123project"),
            ("MYPROJECT", "myproject"),
            ("", "project"),
            ("123", "-123"),
            ("my-project", "my-project"),
        ],
    )
    def test_sanitizes(self, raw: str, expected: str) -> None:
        """Replace invalid characters and fix up the edges."""
        assert sanitize_package_name_dep_group(raw) == expected


class TestPackageAbbrev:
    """Tests for package_abbrev."""

    def test_uses_first_three_chars_uppercased(self) -> None:
        """Abbreviate to the first three characters, uppercased."""
        assert package_abbrev("scaffolder") == "SCA"

    def test_short_name_kept_whole(self) -> None:
        """Uppercase names shorter than three characters as-is."""
        assert package_abbrev("ab") == "AB"


class TestPackageEnvNames:
    """Tests for package_env_var and package_env_file."""

    def test_env_var_prefixes_pkg(self) -> None:
        """Prefix the abbreviation with ``PKG_``."""
        assert package_env_var("scaffolder") == "PKG_SCA"

    def test_env_file_suffixes_env(self) -> None:
        """Suffix the abbreviation with ``_ENV``."""
        assert package_env_file("scaffolder") == "SCA_ENV"
