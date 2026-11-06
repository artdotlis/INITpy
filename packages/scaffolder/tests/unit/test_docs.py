# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.docs."""

from pathlib import Path

import pytest
import tomlkit
from scaffolder.scaffold.docs import _drop_docs_make_targets, amend_docs, remove_docs

pytest_plugins = ("tests.fixture.template",)


class TestAmendDocs:
    """Tests for amend_docs (run against the live docs package)."""

    def test_updates_index_title(self, tmp_path: Path, docs_pkg: Path) -> None:
        """Retitle the docs index hero with the project name."""
        amend_docs(tmp_path, "my_pkg", "NewProject")
        index = docs_pkg / "src" / "index.md"
        assert "name: NewProject" in index.read_text()
        assert "name: INITpy" not in index.read_text()

    def test_updates_ref_index(self, tmp_path: Path, docs_pkg: Path) -> None:
        """Rewrite the module reference index for the single package."""
        amend_docs(tmp_path, "my_pkg", "NewProject")
        content = (docs_pkg / "src" / "ref" / "index.md").read_text()
        assert "- [my_pkg](my_pkg)" in content
        assert "shared_utils" not in content

    def test_updates_config_title_and_drops_repo_link(
        self, tmp_path: Path, docs_pkg: Path
    ) -> None:
        """Set the site title and drop the template repo social link in config."""
        config = docs_pkg / ".vitepress" / "config.toml"

        amend_docs(tmp_path, "my_pkg", "NewProject")

        doc = tomlkit.parse(config.read_text())
        assert doc["site"]["title"] == "NewProject"
        links = doc["vitepress"]["themeConfig"].get("socialLinks", [])
        assert all("artdotlis" not in str(link.get("link", "")) for link in links)


class TestRemoveDocs:
    """Tests for remove_docs."""

    def test_removes_docs_package_dir(self, docs_template: Path) -> None:
        """Delete the packages/docs directory."""
        remove_docs(docs_template)
        assert not (docs_template / "packages" / "docs").exists()
        assert (docs_template / "packages" / "scaffolder").exists()

    def test_cleans_pyproject(self, docs_template: Path) -> None:
        """Strip docs from workspace exclude, dep groups, vulture and commitizen."""
        remove_docs(docs_template)
        doc = tomlkit.parse((docs_template / "pyproject.toml").read_text())
        ws = doc["tool"]["uv"]["workspace"]
        assert "exclude" not in ws
        assert "docs" not in doc["dependency-groups"]
        assert "packages/docs" not in "".join(doc["tool"]["vulture"]["exclude"])
        assert "packages/docs/package.json" not in [
            str(e) for e in doc["tool"]["commitizen"]["version_files"]
        ]

    def test_cleans_pnpm_workspace(self, docs_template: Path) -> None:
        """Remove the docs package from the pnpm workspace."""
        remove_docs(docs_template)
        assert "packages/docs" not in (docs_template / "pnpm-workspace.yaml").read_text()

    def test_cleans_makefile(self, docs_template: Path) -> None:
        """Drop the docs targets from the live Makefile."""
        remove_docs(docs_template)
        makefile = (docs_template / "Makefile").read_text()
        assert "docs" not in makefile.lower()
        assert not makefile.startswith("\n")
        assert "clean:" in makefile

    def test_strips_docs_targets_robustly(self, tmp_path: Path) -> None:
        """Drop docs blocks (with and without recipes) and PKG_DOCS lines."""
        makefile = tmp_path / "Makefile"
        makefile.write_text(
            "dev: setup\n"
            "\techo dev\n"
            "\n"
            "build-docs: docs-ref\n"
            "\tcd $(PKG_DOCS) && $(PNPME) run build\n"
            "\n"
            "run-docs: build-docs\n"
            "\t@echo hi\n"
            "\n"
            # recipe-less docs target (phony aggregate)
            "serve-docs: build-docs\n"
            "\n"
            "docs-ref:\n"
            "\t$(UVE) run griffe2md -o $(DOCS_REF_DIR)/x.md\n"
            "\n"
            "exp-run-lock:\n"
            "\t$(UVE) lock\n"
            "\tcd $(PKG_DOCS) && $(PNPME) install --lockfile-only\n"
            "\n"
            "RAN := $(shell echo hi)\n"
            "run-bump: DISABLE_GIT_ADD = 0\n"
            "\techo bump\n"
        )
        _drop_docs_make_targets(makefile)
        makefile_text = makefile.read_text()
        for frag in (
            "build-docs:",
            "run-docs:",
            "serve-docs:",
            "docs-ref:",
            "PKG_DOCS",
        ):
            assert frag not in makefile_text
        # no leading blank residue from removed target blocks
        assert not makefile_text.startswith("\n")
        # unrelated rules and assignments untouched
        assert "dev: setup\n\techo dev\n" in makefile_text
        assert "exp-run-lock:\n\t$(UVE) lock\n" in makefile_text
        assert "RAN := $(shell echo hi)\n" in makefile_text
        assert "run-bump: DISABLE_GIT_ADD = 0\n\techo bump\n" in makefile_text

    def test_strips_docs_targets_raises_on_missing(self, tmp_path: Path) -> None:
        """Fail loudly when a docs target is absent from the Makefile."""
        makefile = tmp_path / "Makefile"
        makefile.write_text(
            "build-docs: docs-ref\n"
            "\tcd $(PKG_DOCS) && $(PNPME) run build\n"
            "\n"
            "docs-ref:\n"
            "\t$(UVE) run griffe2md -o $(DOCS_REF_DIR)/x.md\n"
        )
        with pytest.raises(ValueError, match="missing docs target"):
            _drop_docs_make_targets(makefile)

    def test_cleans_env_and_lint_scripts(self, docs_template: Path) -> None:
        """Drop docs vars from package.env, lint_env.sh and licenses.sh."""
        remove_docs(docs_template)
        env = (docs_template / "package.env").read_text()
        assert "DOCS" not in env
        assert "PKG_SCAF" in env
        lint_env = (docs_template / "bin" / "lint" / "lint_env.sh").read_text()
        assert "DOCS_ENV" not in lint_env
        clean = (docs_template / "bin" / "install" / "clean.sh").read_text()
        assert "PKG_DOCS" not in clean
        assert "DOCS:START" not in clean
        assert "vitepress" not in clean.lower()
        assert 'if [[ -e "$ROOT/node_modules" ]]; then' in clean
        assert 'if [[ -e "$ROOT/public" ]]; then' in clean
        licenses = (docs_template / "bin" / "lint" / "licenses.sh").read_text()
        assert "CONFIG_DOCS" not in licenses
        assert "packages/docs" not in licenses

    def test_cleans_lefthook(self, docs_template: Path) -> None:
        """Remove the docs test job from lefthook.yml."""
        remove_docs(docs_template)
        text = (docs_template / "lefthook.yml").read_text()
        assert "name: docs" not in text
        assert "PKG_DOCS" not in text
        assert "name: scaffolder" in text

    def test_removes_gitignore_and_workflow(self, docs_template: Path) -> None:
        """Drop the VitePress ignore blocks and the docs workflow."""
        remove_docs(docs_template)
        gitignore = (docs_template / ".gitignore").read_text()
        assert ".vitepress" not in gitignore
        assert "docs/_build" not in gitignore
        assert not (docs_template / ".github" / "workflows" / "docs.yml").exists()
        assert (docs_template / ".github" / "workflows" / "main.yml").exists()
