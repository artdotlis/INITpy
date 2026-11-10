# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.package."""

import tomllib
from pathlib import Path
from typing import Any

from scaffolder.scaffold.package import create_package

pytest_plugins = ("tests.fixture.template",)


def _toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


class TestCreatePackage:
    """Tests for create_package."""

    def test_renders_package_pyproject(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Render the package pyproject from its whole-file template."""
        package_name = context["package_name"]
        create_package(tmp_path, package_name, context)
        doc = _toml(tmp_path / "packages" / package_name / "pyproject.toml")
        assert doc["project"]["name"] == package_name
        assert doc["project"]["description"] == context["description"]
        assert doc["project"]["dependencies"] == []
        assert doc["tool"]["coverage"]["run"]["source"] == [package_name]
        assert doc["tool"]["coverage"]["run"]["data_file"] == f".coverage.{package_name}"

    def test_creates_package_dirs(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Create the package directory and its nested src package."""
        package_name = context["package_name"]
        create_package(tmp_path, package_name, context)
        assert (tmp_path / "packages" / package_name / "src" / package_name).is_dir()

    def test_replaces_other_packages_but_keeps_docs(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Drop pre-existing packages, keep the docs package."""
        package_name = context["package_name"]
        (tmp_path / "packages" / "existing_pkg").mkdir(parents=True)
        (tmp_path / "packages" / "docs").mkdir(parents=True)

        create_package(tmp_path, package_name, context)

        assert not (tmp_path / "packages" / "existing_pkg").exists()
        assert (tmp_path / "packages" / "docs").exists()
