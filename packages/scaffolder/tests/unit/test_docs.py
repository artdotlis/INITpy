# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.docs."""

from pathlib import Path

import tomllib

from scaffolder.scaffold.docs import amend_docs, remove_docs

pytest_plugins = ("tests.fixture.template",)


class TestAmendDocs:
    """Tests for amend_docs (renders the docs package files)."""

    def _setup(self, tmp_path: Path) -> None:
        for rel in (
            "packages/docs/src/ref",
            "packages/docs/.vitepress",
        ):
            (tmp_path / rel).mkdir(parents=True)

    def test_updates_index_and_ref(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Render the docs index hero and the single-package reference."""
        self._setup(tmp_path)
        amend_docs(tmp_path, context)
        index = (tmp_path / "packages" / "docs" / "src" / "index.md").read_text()
        assert f"name: {context['project_name']}" in index
        ref = (tmp_path / "packages" / "docs" / "src" / "ref" / "index.md").read_text()
        assert ref == (
            f"# Reference\n\n- [{context['package_name']}]({context['package_name']})\n"
        )

    def test_sets_site_title(self, tmp_path: Path, context: dict[str, object]) -> None:
        """Set the VitePress site title to the project name."""
        self._setup(tmp_path)
        amend_docs(tmp_path, context)
        config = tmp_path / "packages" / "docs" / ".vitepress" / "config.toml"
        doc = tomllib.loads(config.read_text())
        assert doc["site"]["title"] == context["project_name"]


class TestRemoveDocs:
    """Tests for remove_docs."""

    def test_removes_docs_package_and_workflow(self, tmp_path: Path) -> None:
        """Delete packages/docs and the docs workflow, keep the rest."""
        (tmp_path / "packages" / "docs").mkdir(parents=True)
        (tmp_path / "packages" / "scaffolder").mkdir(parents=True)
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        (tmp_path / ".github" / "workflows" / "docs.yml").write_text("x")
        (tmp_path / ".github" / "workflows" / "mac_win_test.yml").write_text("x")

        remove_docs(tmp_path)

        assert not (tmp_path / "packages" / "docs").exists()
        assert (tmp_path / "packages" / "scaffolder").exists()
        assert not (tmp_path / ".github" / "workflows" / "docs.yml").exists()
        assert (tmp_path / ".github" / "workflows" / "mac_win_test.yml").exists()
