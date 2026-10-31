# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.package and core."""

from pathlib import Path

import tomlkit
from scaffolder.scaffold.package import create_package


class TestCreatePackage:
    """Tests for create_package."""

    def test_creates_package_dir(self, tmp_path: Path) -> None:
        """Create the package directory under packages/."""
        create_package(tmp_path, "my_pkg", "A package")
        assert (tmp_path / "packages" / "my_pkg").is_dir()

    def test_creates_src_package_dir(self, tmp_path: Path) -> None:
        """Create the nested src/<package> directory."""
        create_package(tmp_path, "my_pkg", "A package")
        assert (tmp_path / "packages" / "my_pkg" / "src" / "my_pkg").is_dir()

    def test_creates_pyproject_with_correct_name(self, tmp_path: Path) -> None:
        """Copy a pyproject.toml with the package name set."""
        create_package(tmp_path, "my_pkg", "A package")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["name"] == "my_pkg"

    def test_updates_pyproject_description(self, tmp_path: Path) -> None:
        """Write the given description into the pyproject.toml."""
        create_package(tmp_path, "my_pkg", "A package desc")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["description"] == "A package desc"

    def test_cleans_other_packages(self, tmp_path: Path) -> None:
        """Remove pre-existing top-level packages other than the new one."""
        # Create an existing package that should be removed
        existing = tmp_path / "packages" / "existing_pkg"
        existing.mkdir(parents=True)
        (existing / "file.txt").write_text("x")
        create_package(tmp_path, "my_pkg", "A package")
        assert not existing.exists()

    def test_keeps_docs_directory(self, tmp_path: Path) -> None:
        """Keep the docs directory during cleanup."""
        docs = tmp_path / "packages" / "docs"
        docs.mkdir(parents=True)
        (docs / "file.txt").write_text("x")
        create_package(tmp_path, "my_pkg", "A package")
        assert docs.exists()

    def test_cleans_pyproject_dependencies(self, tmp_path: Path) -> None:
        """Start the new package with an empty dependencies list."""
        create_package(tmp_path, "my_pkg", "A package")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["dependencies"] == []

    def test_updates_pyproject_path(self, tmp_path: Path) -> None:
        """Register the package in the setuptools find include list."""
        create_package(tmp_path, "my_pkg", "A package")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]
