# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.package and core."""

from pathlib import Path
from unittest.mock import patch

import pytest
import tomlkit
from scaffolder.scaffold.package import create_package
from scaffolder.scaffold.core import clone_ref
from shared_utils.constants import VERSION

TEMPLATE = """\
[project]
name = "shared_utils"
description = "template"
dependencies = []

[tool.setuptools.packages.find]
include = ["shared_utils"]
"""


@pytest.fixture
def clone_path(tmp_path: Path) -> Path:
    """Clone root containing the shared_utils pyproject template."""
    template = tmp_path / "packages" / "shared_utils" / "pyproject.toml"
    template.parent.mkdir(parents=True)
    template.write_text(TEMPLATE)
    return tmp_path


class TestCreatePackage:
    """Tests for create_package."""

    def test_creates_package_dir(self, clone_path: Path) -> None:
        """Create the package directory under packages/."""
        create_package(clone_path, "my_pkg", "A package")
        assert (clone_path / "packages" / "my_pkg").is_dir()

    def test_creates_src_package_dir(self, clone_path: Path) -> None:
        """Create the nested src/<package> directory."""
        create_package(clone_path, "my_pkg", "A package")
        assert (clone_path / "packages" / "my_pkg" / "src" / "my_pkg").is_dir()

    def test_creates_pyproject_with_correct_name(self, clone_path: Path) -> None:
        """Copy a pyproject.toml with the package name set."""
        create_package(clone_path, "my_pkg", "A package")
        pyproject = clone_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["name"] == "my_pkg"

    def test_updates_pyproject_description(self, clone_path: Path) -> None:
        """Write the given description into the pyproject.toml."""
        create_package(clone_path, "my_pkg", "A package desc")
        pyproject = clone_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["description"] == "A package desc"

    def test_cleans_other_packages(self, clone_path: Path) -> None:
        """Remove pre-existing top-level packages other than the new one."""
        # Create an existing package that should be removed
        existing = clone_path / "packages" / "existing_pkg"
        existing.mkdir(parents=True)
        (existing / "file.txt").write_text("x")
        create_package(clone_path, "my_pkg", "A package")
        assert not existing.exists()

    def test_keeps_docs_directory(self, clone_path: Path) -> None:
        """Keep the docs directory during cleanup."""
        docs = clone_path / "packages" / "docs"
        docs.mkdir(parents=True)
        (docs / "file.txt").write_text("x")
        create_package(clone_path, "my_pkg", "A package")
        assert docs.exists()

    def test_cleans_pyproject_dependencies(self, clone_path: Path) -> None:
        """Start the new package with an empty dependencies list."""
        create_package(clone_path, "my_pkg", "A package")
        pyproject = clone_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["project"]["dependencies"] == []

    def test_updates_pyproject_path(self, clone_path: Path) -> None:
        """Register the package in the setuptools find include list."""
        create_package(clone_path, "my_pkg", "A package")
        pyproject = clone_path / "packages" / "my_pkg" / "pyproject.toml"
        doc = tomlkit.parse(pyproject.read_text())
        assert doc["tool"]["setuptools"]["packages"]["find"]["include"] == ["my_pkg"]


class TestCloneRef:
    """Tests for the cloned INITpy ref selection."""

    def test_defaults_to_version_tag(self) -> None:
        """Clone the tag matching the release version by default."""
        with patch.dict("os.environ", {}, clear=True):
            assert clone_ref() == f"v{VERSION}"

    def test_dev_env_clones_dev(self) -> None:
        """Clone the dev branch when SCAF_DEV is set."""
        with patch.dict("os.environ", {"SCAF_DEV": "1"}, clear=True):
            assert clone_ref() == "dev"
