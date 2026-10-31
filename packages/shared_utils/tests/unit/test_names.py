# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.names."""

from shared_utils.names import sanitize_package_name, sanitize_package_name_dep_group


class TestSanitizePackageName:
    """Tests for sanitize_package_name."""

    def test_already_valid(self) -> None:
        """Return an already-valid name unchanged."""
        assert sanitize_package_name("my_project") == "my_project"

    def test_with_spaces(self) -> None:
        """Replace spaces with underscores."""
        assert sanitize_package_name("my project name") == "my_project_name"

    def test_with_hyphens(self) -> None:
        """Replace hyphens with underscores."""
        assert sanitize_package_name("my-project-name") == "my_project_name"

    def test_with_special_chars(self) -> None:
        """Strip characters that are invalid in a package name."""
        assert sanitize_package_name("my@project!name#") == "myprojectname"

    def test_leading_digit(self) -> None:
        """Prefix an underscore when the name starts with a digit."""
        assert sanitize_package_name("123project") == "_123project"

    def test_all_caps(self) -> None:
        """Lowercase uppercase input."""
        assert sanitize_package_name("MYPROJECT") == "myproject"

    def test_mixed_case_hyphens(self) -> None:
        """Normalize mixed-case input with separators."""
        assert sanitize_package_name("My Project-Name") == "my_project_name"

    def test_empty_string(self) -> None:
        """Return the fallback name for empty input."""
        assert sanitize_package_name("") == "project"

    def test_numeric_only(self) -> None:
        """Prefix an underscore when the input is all digits."""
        assert sanitize_package_name("123") == "_123"


class TestSanitizePackageNameDepGroup:
    """Tests for sanitize_package_name_dep_group."""

    def test_already_valid(self) -> None:
        """Convert underscores to hyphens for an otherwise-valid input."""
        assert sanitize_package_name_dep_group("my_project") == "my-project"

    def test_with_spaces(self) -> None:
        """Replace spaces with hyphens."""
        assert sanitize_package_name_dep_group("my project name") == "my-project-name"

    def test_with_underscores(self) -> None:
        """Replace underscores with hyphens."""
        assert sanitize_package_name_dep_group("my_project_name") == "my-project-name"

    def test_with_special_chars(self) -> None:
        """Strip characters that are invalid in a dependency group name."""
        assert sanitize_package_name_dep_group("my@project!name#") == "myprojectname"

    def test_leading_digit(self) -> None:
        """Prefix a hyphen when the name starts with a digit."""
        assert sanitize_package_name_dep_group("123project") == "-123project"

    def test_all_caps(self) -> None:
        """Lowercase uppercase input."""
        assert sanitize_package_name_dep_group("MYPROJECT") == "myproject"

    def test_empty_string(self) -> None:
        """Return the fallback name for empty input."""
        assert sanitize_package_name_dep_group("") == "project"

    def test_numeric_only(self) -> None:
        """Prefix a hyphen when the input is all digits."""
        assert sanitize_package_name_dep_group("123") == "-123"

    def test_preserves_existing_hyphens(self) -> None:
        """Leave an already-hyphenated name unchanged."""
        assert sanitize_package_name_dep_group("my-project") == "my-project"
