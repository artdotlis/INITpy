# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.config."""

import json
import tomllib
from pathlib import Path
from typing import Any

from scaffolder.scaffold.config import correct_core_project

pytest_plugins = ("tests.fixture.template",)


def _toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


class TestCorrectCoreProject:
    """Tests for correct_core_project."""

    def test_renders_all_root_files(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Write every root config file with the project metadata."""
        (tmp_path / "packages" / "docs").mkdir(parents=True)
        (tmp_path / ".devcontainer").mkdir(parents=True)
        (tmp_path / "bin" / "lint").mkdir(parents=True)
        correct_core_project(tmp_path, context)

        assert (
            _toml(tmp_path / "pyproject.toml")["project"]["name"]
            == (context["project_name"])
        )
        assert (
            json.loads((tmp_path / "package.json").read_text())["name"]
            == context["project_name"]
        )
        assert (
            json.loads((tmp_path / ".devcontainer" / "devcontainer.json").read_text())[
                "name"
            ]
            == context["project_name"]
        )
        assert (
            f"{context['year']} {context['copyright_holder']}"
            in (tmp_path / "pnpm-workspace.yaml").read_text()
        )
        assert (
            context["license"] in (tmp_path / "bin" / "lint" / "licenses.sh").read_text()
        )

    def test_writes_docs_package_when_docs(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Write packages/docs/package.json when docs are kept."""
        (tmp_path / "packages" / "docs").mkdir(parents=True)
        (tmp_path / ".devcontainer").mkdir(parents=True)
        (tmp_path / "bin" / "lint").mkdir(parents=True)
        correct_core_project(tmp_path, dict(context, use_docs=True))
        assert (tmp_path / "packages" / "docs" / "package.json").is_file()

    def test_skips_docs_package_when_no_docs(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Leave packages/docs/package.json absent when docs are dropped."""
        (tmp_path / "packages" / "docs").mkdir(parents=True)
        (tmp_path / ".devcontainer").mkdir(parents=True)
        (tmp_path / "bin" / "lint").mkdir(parents=True)
        correct_core_project(tmp_path, dict(context, use_docs=False))
        assert not (tmp_path / "packages" / "docs" / "package.json").exists()
