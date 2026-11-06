# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.package."""

from pathlib import Path

import tomlkit
from scaffolder.scaffold.package import create_package

pytest_plugins = ("tests.fixture.template",)


class TestCreatePackage:
    """Tests for create_package."""

    def test_writes_package_pyproject(self, clone_path: Path) -> None:
        """Carry the live template into the new package, retargeted at it."""
        create_package(clone_path, "my_pkg", "A package desc")

        pyproject = clone_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["name"] == "my_pkg"
        assert doc["project"]["description"] == "A package desc"
        assert doc["project"]["dependencies"] == []
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]
        run = doc["tool"]["coverage"]["run"]
        assert run["source"] == ["my_pkg"]
        assert run["data_file"] == ".coverage.my_pkg"

    def test_creates_package_dirs(self, clone_path: Path) -> None:
        """Create the package directory and its nested src package."""
        create_package(clone_path, "my_pkg", "A package")
        assert (clone_path / "packages" / "my_pkg" / "src" / "my_pkg").is_dir()

    def test_replaces_other_packages_but_keeps_docs(self, clone_path: Path) -> None:
        """Drop pre-existing packages, keep the docs package."""
        existing = clone_path / "packages" / "existing_pkg"
        existing.mkdir(parents=True)
        (existing / "file.txt").write_text("x")
        docs = clone_path / "packages" / "docs"
        docs.mkdir(parents=True)
        (docs / "file.txt").write_text("x")

        create_package(clone_path, "my_pkg", "A package")

        assert not existing.exists()
        assert docs.exists()
