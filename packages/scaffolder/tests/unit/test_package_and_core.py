# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.package and core."""

from pathlib import Path

import tomlkit
from scaffolder.scaffold.package import create_package


class TestCreatePackage:
    def test_creates_package_dir(self, tmp_path: Path) -> None:
        create_package(tmp_path, "my_pkg", "A package")
        assert (tmp_path / "packages" / "my_pkg").is_dir()

    def test_creates_src_package_dir(self, tmp_path: Path) -> None:
        create_package(tmp_path, "my_pkg", "A package")
        assert (tmp_path / "packages" / "my_pkg" / "src" / "my_pkg").is_dir()

    def test_creates_pyproject_with_correct_name(self, tmp_path: Path) -> None:
        create_package(tmp_path, "my_pkg", "A package")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["name"] == "my_pkg"

    def test_updates_pyproject_description(self, tmp_path: Path) -> None:
        create_package(tmp_path, "my_pkg", "A package desc")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["description"] == "A package desc"

    def test_cleans_other_packages(self, tmp_path: Path) -> None:
        # Create an existing package that should be removed
        existing = tmp_path / "packages" / "existing_pkg"
        existing.mkdir(parents=True)
        (existing / "file.txt").write_text("x")
        create_package(tmp_path, "my_pkg", "A package")
        assert not existing.exists()

    def test_keeps_docs_directory(self, tmp_path: Path) -> None:
        docs = tmp_path / "packages" / "docs"
        docs.mkdir(parents=True)
        (docs / "file.txt").write_text("x")
        create_package(tmp_path, "my_pkg", "A package")
        assert docs.exists()

    def test_cleans_pyproject_dependencies(self, tmp_path: Path) -> None:
        create_package(tmp_path, "my_pkg", "A package")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["dependencies"] == []

    def test_updates_pyproject_path(self, tmp_path: Path) -> None:
        create_package(tmp_path, "my_pkg", "A package")
        pyproject = tmp_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]
