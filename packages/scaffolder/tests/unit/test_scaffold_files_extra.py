# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.files (remaining functions)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import tomlkit
from scaffolder.scaffold.files import (
    _drop_docs_make_targets,
    _validate_license,
    amend_docs,
    clean_root_md,
    clear_licenses_dir,
    configure_licenses,
    correct_core_project,
    remove_docs,
    remove_prod_docker,
    remove_reuse,
    set_license_package_json,
    set_license_pyproject,
    update_commitizen_version_files,
    update_copyright,
    update_envs,
    update_licenses_sh,
    update_pyproject_dep_groups,
    update_tests,
)


class TestAmendDocs:
    """Tests for amend_docs."""

    @staticmethod
    def _write_docs(tmp_path: Path, index: str = "name: INITpy\n") -> None:
        """Create the default scaffolded docs files."""
        index_md = tmp_path / "packages" / "docs" / "src" / "index.md"
        index_md.parent.mkdir(parents=True, exist_ok=True)
        index_md.write_text(index)
        config = tmp_path / "packages" / "docs" / ".vitepress" / "config.toml"
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text('[site]\ntitle = "INIT - Python"\n')

    def test_updates_index_title(self, tmp_path: Path) -> None:
        """Retitle the docs index hero with the project name."""
        self._write_docs(tmp_path, "hero:\n    name: INITpy\n\ncontent")
        amend_docs(tmp_path, "my_pkg", "NewProject")
        index = tmp_path / "packages" / "docs" / "src" / "index.md"
        assert "name: NewProject" in index.read_text()

    def test_updates_ref_index_when_exists(self, tmp_path: Path) -> None:
        """Rewrite the module reference index for the single package."""
        ref_index = tmp_path / "packages" / "docs" / "src" / "ref" / "index.md"
        ref_index.parent.mkdir(parents=True)
        ref_index.write_text("# old content\n")
        self._write_docs(tmp_path)
        amend_docs(tmp_path, "my_pkg", "NewProject")
        content = ref_index.read_text()
        assert "- [my_pkg](my_pkg)" in content

    def test_updates_config_title_and_drops_repo_link(self, tmp_path: Path) -> None:
        """Set the site title and drop the template repo social link in config."""
        self._write_docs(tmp_path)
        config = tmp_path / "packages" / "docs" / ".vitepress" / "config.toml"
        config.write_text(
            '[site]\ntitle = "INIT - Python"\n'
            '[vitepress]\nbase = "/INITpy/"\n'
            "[vitepress.themeConfig]\n"
            '[[vitepress.themeConfig.socialLinks]]\nicon = "github"\n'
            'link = "https://github.com/artdotlis/INITpy"\n'
        )
        amend_docs(tmp_path, "my_pkg", "NewProject")
        doc = tomlkit.parse(config.read_text())
        assert doc["site"]["title"] == "NewProject"
        links = doc["vitepress"]["themeConfig"].get("socialLinks", [])
        assert all("artdotlis" not in str(link.get("link", "")) for link in links)


class TestUpdateCopyright:
    """Tests for update_copyright."""

    def test_updates_package_env(self, tmp_path: Path) -> None:
        """Replace the COPYRIGHT value in package.env."""
        pkg_env = tmp_path / "package.env"
        pkg_env.write_text('COPYRIGHT="Artur Lissin"\nPYV=3.13\n')
        update_copyright(tmp_path, "New Owner")
        content = pkg_env.read_text()
        assert 'COPYRIGHT="New Owner"' in content
        assert "Artur Lissin" not in content
        assert "PYV=3.13" in content


class TestUpdateEnvs:
    """Tests for update_envs."""

    def test_updates_package_env(self, tmp_path: Path) -> None:
        """Repoint the package env variables at the new package."""
        pkg_env = tmp_path / "package.env"
        pkg_env.write_text(
            "PKG_SCAF=packages/scaffolder\nPKG_SHAR=packages/shared_utils\nSCAF_ENV=packages/scaffolder/.env\n"
        )
        lint_env = tmp_path / "bin" / "lint" / "lint_env.sh"
        lint_env.parent.mkdir(parents=True)
        lint_env.write_text("#!/bin/bash\n$SCAF_ENV\n")
        update_envs(tmp_path, "my_pkg")
        content = pkg_env.read_text()
        assert "PKG_MY_" in content  # first 3 chars of "MY_PKG" are "MY_"
        assert "PKG_SHAR" not in content

    def test_updates_lint_env(self, tmp_path: Path) -> None:
        """Repoint the lint script's env variable at the new package."""
        pkg_env = tmp_path / "package.env"
        pkg_env.write_text(
            "PKG_SCAF=packages/scaffolder\nPKG_SHAR=packages/shared_utils\nSCAF_ENV=packages/scaffolder/.env\n"
        )
        lint_env = tmp_path / "bin" / "lint" / "lint_env.sh"
        lint_env.parent.mkdir(parents=True)
        lint_env.write_text("#!/bin/bash\n$SCAF_ENV\n")
        update_envs(tmp_path, "my_pkg")
        assert "$SCAF_ENV" not in lint_env.read_text()
        assert "MY__ENV" in lint_env.read_text()


class TestUpdateTests:
    """Tests for update_tests."""

    LEFTHOOK = """\
tests:
  parallel: true
  jobs:
    - name: scaffolder
      run: bin/install/wrap.sh 'cd $PKG_SHAR && coverage run -m pytest'
    - name: shared-utils
      run: bin/install/wrap.sh 'cd $PKG_SCAF && coverage run -m pytest'
"""

    MAIN = """\
name: main

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - name: Run shared_utils tests
        working-directory: packages/shared_utils
        run: uv run coverage run -m pytest
      - name: Run scaffolder tests
        working-directory: packages/scaffolder
        run: uv run coverage run -m pytest
"""

    def _write(self, tmp_path: Path) -> None:
        (tmp_path / "lefthook.yml").write_text(self.LEFTHOOK)
        main = tmp_path / ".github" / "workflows" / "main.yml"
        main.parent.mkdir(parents=True)
        main.write_text(self.MAIN)

    def test_collapses_lefthook_tests(self, tmp_path: Path) -> None:
        """Collapse the lefthook test jobs to the single package."""
        self._write(tmp_path)
        update_tests(tmp_path, "my_pkg")
        content = tmp_path.joinpath("lefthook.yml").read_text()
        assert "$PKG_SHAR" not in content
        assert "$PKG_SCAF" not in content
        assert "- name: my_pkg" in content
        assert "cd $PKG_MY_ && coverage run -m pytest" in content

    def test_collapses_ci_tests(self, tmp_path: Path) -> None:
        """Collapse the CI test steps to the single package."""
        self._write(tmp_path)
        update_tests(tmp_path, "my_pkg")
        content = tmp_path.joinpath(".github", "workflows", "main.yml").read_text()
        assert "packages/shared_utils" not in content
        assert "packages/scaffolder" not in content
        assert "- name: Run my_pkg tests" in content
        assert "working-directory: packages/my_pkg" in content


class TestUpdateCommitizenVersionFiles:
    """Tests for update_commitizen_version_files."""

    def test_retargets_and_removes_shared_utils(self, tmp_path: Path) -> None:
        """Drop shared_utils entries and rename scaffolder to new package."""
        p = tmp_path / "pyproject.toml"
        p.write_text(
            "[tool.commitizen]\nversion_files = [\n"
            '  "README.md:^\\\\[!\\\\[release:",\n'
            '  "packages/shared_utils/src/shared_utils/constants.py:^VERSION",\n'
            '  "package.json",\n'
            '  "pyproject.toml",\n'
            '  "packages/scaffolder/pyproject.toml",\n'
            '  "packages/shared_utils/pyproject.toml",\n'
            '  "packages/docs/package.json",\n'
            "]\n"
        )

        update_commitizen_version_files(tmp_path, "my_pkg")

        doc = tomlkit.parse(p.read_text())
        files = doc["tool"]["commitizen"]["version_files"]
        # README badge entry is kept unchanged
        assert files[0].startswith("README.md:")
        assert "packages/shared_utils" not in "\n".join(files)
        assert files == [
            files[0],
            "package.json",
            "pyproject.toml",
            "packages/my_pkg/pyproject.toml",
            "packages/docs/package.json",
        ]

    def test_no_op_when_missing(self, tmp_path: Path) -> None:
        """Do nothing when there is no pyproject.toml."""
        update_commitizen_version_files(tmp_path, "my_pkg")


class TestUpdateLicensesSh:
    """Tests for update_licenses_sh."""

    def test_adds_exit_on_failure(self, tmp_path: Path) -> None:
        """Insert an early error exit after the shebang."""
        sh = tmp_path / "bin" / "lint" / "licenses.sh"
        sh.parent.mkdir(parents=True)
        sh.write_text("#!/bin/bash\necho hello\n")
        update_licenses_sh(tmp_path)
        content = sh.read_text()
        assert "exit 1" in content
        assert content.startswith("#!/bin/bash")

    def test_raises_when_file_missing(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when licenses.sh is absent."""
        with pytest.raises(FileNotFoundError):
            update_licenses_sh(tmp_path)


class TestCleanRootMd:
    """Tests for clean_root_md."""

    def test_updates_readme(self, tmp_path: Path) -> None:
        """Reset the root README to a project header."""
        clean_root_md(tmp_path, "NewProject")
        assert (tmp_path / "README.md").read_text() == "# NewProject\n\n"

    def test_clears_changelog(self, tmp_path: Path) -> None:
        """Empty the CHANGELOG file."""
        clean_root_md(tmp_path, "Proj")
        assert (tmp_path / "CHANGELOG.md").read_text() == ""

    def test_removes_lock_files(self, tmp_path: Path) -> None:
        """Delete the uv and pnpm lockfiles."""
        (tmp_path / "uv.lock").write_text("x")
        (tmp_path / "pnpm-lock.yaml").write_text("y")
        clean_root_md(tmp_path, "Proj")
        assert not (tmp_path / "uv.lock").exists()
        assert not (tmp_path / "pnpm-lock.yaml").exists()


class TestCorrectCoreProject:
    """Tests for correct_core_project."""

    def test_updates_all_files(self, tmp_path: Path) -> None:
        """Apply project metadata to the root config files."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "old"\ndependencies = ["x"]\n')
        pkg_json = tmp_path / "package.json"
        pkg_json.write_text('{"name": "old"}\n')
        devcontainer = tmp_path / ".devcontainer" / "devcontainer.json"
        devcontainer.parent.mkdir(parents=True)
        devcontainer.write_text('{"name": "old"}\n')

        correct_core_project(tmp_path, "NewProject", "my_pkg", "my-pkg", "New desc")

        pydoc = tomlkit.parse(pyproject.read_text())
        assert pydoc["project"]["name"] == "NewProject"
        assert pydoc["project"]["description"] == "New desc"
        assert pydoc["tool"]["uv"]["sources"]["my_pkg"] == {"workspace": True}
        assert "mono" in pydoc["dependency-groups"]

        pkg_data = json.loads(pkg_json.read_text())
        assert pkg_data["name"] == "NewProject"

        dc_data = json.loads(devcontainer.read_text())
        assert dc_data["name"] == "NewProject"


class TestRemoveProdDocker:
    """Tests for remove_prod_docker."""

    @staticmethod
    def _write(tmp_path: Path) -> None:
        (tmp_path / "Dockerfile").write_text("# prod\n")
        (tmp_path / "docker-compose.yml").write_text("prod:\n")
        dev_dir = tmp_path / ".devcontainer"
        dev_dir.mkdir(parents=True)
        (dev_dir / "dev.docker-compose.yml").write_text("dev:\n")
        (dev_dir / "devcontainer.json").write_text(
            '{"name": "init", "dockerComposeFile": '
            '["../docker-compose.yml", "dev.docker-compose.yml"]}\n'
        )
        (tmp_path / "package.env").write_text(
            "BIN_DEPLOY_PREP=x\nBIN_DEPLOY_HEALTH=y\nBIN_DEPLOY_ENTRY_PROD=z\n"
        )
        deploy = tmp_path / "bin" / "deploy"
        deploy.mkdir(parents=True)
        (deploy / "entry_prod.sh").write_text("x")
        (deploy / "health.sh").write_text("y")
        (deploy / "entry_dev.sh").write_text("z")

    def test_removes_prod_docker_and_promotes_dev(self, tmp_path: Path) -> None:
        """Drop the prod Dockerfile and promote the dev compose to root."""
        self._write(tmp_path)
        remove_prod_docker(tmp_path)
        assert not (tmp_path / "Dockerfile").exists()
        assert (tmp_path / "docker-compose.yml").read_text() == "dev:\n"
        assert not (tmp_path / ".devcontainer" / "dev.docker-compose.yml").exists()

    def test_devcontainer_points_at_single_compose(self, tmp_path: Path) -> None:
        """Collapse dockerComposeFile to the root (dev) compose."""
        self._write(tmp_path)
        remove_prod_docker(tmp_path)
        data = json.loads((tmp_path / ".devcontainer" / "devcontainer.json").read_text())
        assert data["dockerComposeFile"] == ["../docker-compose.yml"]

    def test_drops_prod_only_env_and_scripts(self, tmp_path: Path) -> None:
        """Remove prod-only env vars and deploy scripts."""
        self._write(tmp_path)
        remove_prod_docker(tmp_path)
        env = (tmp_path / "package.env").read_text()
        assert "BIN_DEPLOY_HEALTH" not in env
        assert "BIN_DEPLOY_ENTRY_PROD" not in env
        assert "BIN_DEPLOY_PREP" in env
        assert not (tmp_path / "bin" / "deploy" / "entry_prod.sh").exists()
        assert not (tmp_path / "bin" / "deploy" / "health.sh").exists()
        assert (tmp_path / "bin" / "deploy" / "entry_dev.sh").exists()


class TestRemoveDocs:
    """Tests for remove_docs."""

    @staticmethod
    def _write(tmp_path: Path) -> None:
        """Create a minimal project with docs wiring."""
        (tmp_path / "packages" / "docs" / "src").mkdir(parents=True)
        (tmp_path / "packages" / "docs" / "src" / "index.md").write_text("# docs\n")
        (tmp_path / "packages" / "my_pkg").mkdir(parents=True)

        (tmp_path / "pyproject.toml").write_text(
            "[tool.uv.workspace]\n"
            'members = ["packages/*"]\n'
            'exclude = ["packages/docs"]\n'
            "\n"
            "[dependency-groups]\n"
            'docs = ["griffe2md ==1.1.0"]\n'
            'test = ["pytest"]\n'
            "\n"
            "[tool.vulture]\n"
            'exclude = ["packages/docs/"]\n'
            "\n"
            "[tool.commitizen]\n"
            'version_files = [\n  "package.json",\n  "packages/docs/package.json",\n]\n'
        )
        (tmp_path / "pnpm-workspace.yaml").write_text('packages:\n  - "packages/docs"\n')
        (tmp_path / "Makefile").write_text(
            "docs: setup\n"
            "\t$(UVE) sync --group docs\n"
            "\n"
            "build-docs: docs-ref\n"
            "\tcd $(PKG_DOCS) && $(PNPME) run build\n"
            "\n"
            "run-docs: build-docs\n"
            "\t@echo hi\n"
            "\n"
            "serve-docs: build-docs\n"
            "\tcd $(PKG_DOCS) && $(PNPME) run preview\n"
            "\n"
            "docs-ref:\n"
            "\t$(UVE) run griffe2md -o $(DOCS_REF_DIR)/x.md\n"
            "\n"
            "exp-run-lock:\n"
            "\t$(UVE) lock\n"
            "\n"
            "real:\n"
            "\techo real\n"
        )
        (tmp_path / "package.env").write_text(
            "PKG_MY_=packages/my_pkg\n"
            "CONFIG_DOCS=packages/docs/.vitepress/config.toml\n"
            "PKG_DOCS=packages/docs\n"
            "DOCS_ENV=packages/docs/.env\n"
        )
        (tmp_path / "lefthook.yml").write_text(
            "tests:\n"
            "    jobs:\n"
            "        - name: docs\n"
            "          run: bin/install/wrap.sh 'cd $PKG_DOCS && $PNPME test'\n"
            "        - name: my_pkg\n"
            "          run: bin/install/wrap.sh 'cd $PKG_MY_ && pytest'\n"
        )
        lint_env = tmp_path / "bin" / "lint" / "lint_env.sh"
        lint_env.parent.mkdir(parents=True)
        lint_env.write_text('ENV_FILES=( "$ROOT_ENV" "$MY__ENV" "$DOCS_ENV")\n')
        clean = tmp_path / "bin" / "install" / "clean.sh"
        clean.parent.mkdir(parents=True, exist_ok=True)
        clean.write_text(
            "# package manager install trees\n"
            'if [[ -e "$ROOT/node_modules" ]]; then\n'
            '    rm -rf -- "$ROOT/node_modules"\n'
            "fi\n"
            "# ===== DOCS:START =====\n"
            'if [[ -e "$ROOT/$PKG_DOCS/node_modules" ]]; then\n'
            '    rm -rf -- "$ROOT/$PKG_DOCS/node_modules"\n'
            "fi\n"
            "# docs build output and VitePress workdir (cache/dist only; "
            ".vitepress source is tracked)\n"
            'if [[ -e "$ROOT/$PKG_DOCS/.vitepress/.vitepress" ]]; then\n'
            '    rm -rf -- "$ROOT/$PKG_DOCS/.vitepress/.vitepress"\n'
            "fi\n"
            "# ===== DOCS:END =====\n"
            "# build output\n"
            'if [[ -e "$ROOT/public" ]]; then\n'
            '    rm -rf -- "$ROOT/public"\n'
            "fi\n"
        )
        licenses = tmp_path / "bin" / "lint" / "licenses.sh"
        licenses.parent.mkdir(parents=True, exist_ok=True)
        licenses.write_text(
            'LICENSE_FILES=(\n    "$CONFIG_DOCS"\n)\n\n'
            "IGNORE=(\n"
            "    '^packages/docs/REUSE\\.toml$'\n"
            "    '^packages/docs/src/.+\\.md$'\n"
            "    '^bin/lint/licenses\\.sh$'\n"
            ")\n"
        )
        (tmp_path / ".gitignore").write_text(
            "# Sphinx documentation\ndocs/_build/\n"
            "\n"
            "# VitePress\n.vitepress/.cache/\n.vitepress/dist/\n"
        )
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "docs.yml").write_text("name: docs\n")
        (wf / "main.yml").write_text("name: main\n")

    def test_removes_docs_package_dir(self, tmp_path: Path) -> None:
        """Delete the packages/docs directory."""
        self._write(tmp_path)
        remove_docs(tmp_path)
        assert not (tmp_path / "packages" / "docs").exists()
        assert (tmp_path / "packages" / "my_pkg").exists()

    def test_cleans_pyproject(self, tmp_path: Path) -> None:
        """Strip docs from workspace exclude, dep groups, vulture and commitizen."""
        self._write(tmp_path)
        remove_docs(tmp_path)
        doc = tomlkit.parse((tmp_path / "pyproject.toml").read_text())
        ws = doc["tool"]["uv"]["workspace"]
        assert "exclude" not in ws
        assert "docs" not in doc["dependency-groups"]
        assert "packages/docs" not in "".join(doc["tool"]["vulture"]["exclude"])
        assert "packages/docs/package.json" not in [
            str(e) for e in doc["tool"]["commitizen"]["version_files"]
        ]

    def test_cleans_pnpm_workspace(self, tmp_path: Path) -> None:
        """Remove the docs package from the pnpm workspace."""
        self._write(tmp_path)
        remove_docs(tmp_path)
        assert "packages/docs" not in (tmp_path / "pnpm-workspace.yaml").read_text()

    def test_cleans_makefile(self, tmp_path: Path) -> None:
        """Drop docs targets and PKG_DOCS recipe lines from the Makefile."""
        self._write(tmp_path)
        remove_docs(tmp_path)
        makefile = (tmp_path / "Makefile").read_text()
        for frag in (
            "docs:",
            "build-docs:",
            "run-docs:",
            "serve-docs:",
            "docs-ref:",
            "PKG_DOCS",
        ):
            assert frag not in makefile
        assert not makefile.startswith("\n")
        assert "exp-run-lock:" in makefile
        assert "real:" in makefile

    def test_strips_docs_targets_robustly(self, tmp_path: Path) -> None:
        """Drop docs blocks (with and without recipes) and PKG_DOCS lines."""
        makefile = tmp_path / "Makefile"
        makefile.write_text(
            "docs: setup\n"
            "\t$(UVE) sync --group docs\n"
            "\n"
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
            "\n"
            "RAN := $(shell echo hi)\n"
            "run-bump: DISABLE_GIT_ADD = 0\n"
            "\techo bump\n"
        )
        _drop_docs_make_targets(makefile)
        makefile_text = makefile.read_text()
        for frag in (
            "docs:",
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
            "docs: setup\n"
            "\t$(UVE) sync --group docs\n"
            "\n"
            "docs-ref:\n"
            "\t$(UVE) run griffe2md -o $(DOCS_REF_DIR)/x.md\n"
        )
        with pytest.raises(ValueError, match="missing docs target"):
            _drop_docs_make_targets(makefile)

    def test_strips_docs_raises_on_pkg_docs_leftover(self, tmp_path: Path) -> None:
        """Fail loudly when PKG_DOCS survives outside a docs target block."""
        makefile = tmp_path / "Makefile"
        makefile.write_text(
            "docs: setup\n"
            "\t$(UVE) sync --group docs\n"
            "\n"
            "build-docs: docs-ref\n"
            "\tcd $(PKG_DOCS) && $(PNPME) run build\n"
            "\n"
            "run-docs: build-docs\n"
            "\t@echo hi\n"
            "\n"
            "serve-docs: build-docs\n"
            "\tcd $(PKG_DOCS) && $(PNPME) run preview\n"
            "\n"
            "docs-ref:\n"
            "\t$(UVE) run griffe2md -o $(DOCS_REF_DIR)/x.md\n"
            "\n"
            "exp-run-lock:\n"
            "\t$(UVE) lock\n"
            "\tcd $(PKG_DOCS) && $(PNPME) install --lockfile-only\n"
        )
        with pytest.raises(ValueError, match="PKG_DOCS"):
            _drop_docs_make_targets(makefile)

    def test_cleans_env_and_lint_scripts(self, tmp_path: Path) -> None:
        """Drop docs vars from package.env, lint_env.sh and licenses.sh."""
        self._write(tmp_path)
        remove_docs(tmp_path)
        env = (tmp_path / "package.env").read_text()
        assert "DOCS" not in env
        assert "PKG_MY_" in env
        lint_env = (tmp_path / "bin" / "lint" / "lint_env.sh").read_text()
        assert "DOCS_ENV" not in lint_env
        clean = (tmp_path / "bin" / "install" / "clean.sh").read_text()
        assert "PKG_DOCS" not in clean
        assert "DOCS:START" not in clean
        assert "vitepress" not in clean.lower()
        assert 'if [[ -e "$ROOT/node_modules" ]]; then' in clean
        assert 'if [[ -e "$ROOT/public" ]]; then' in clean
        licenses = (tmp_path / "bin" / "lint" / "licenses.sh").read_text()
        assert "CONFIG_DOCS" not in licenses
        assert "packages/docs" not in licenses

    def test_cleans_lefthook(self, tmp_path: Path) -> None:
        """Remove the docs test job from lefthook.yml."""
        self._write(tmp_path)
        remove_docs(tmp_path)
        text = (tmp_path / "lefthook.yml").read_text()
        assert "name: docs" not in text
        assert "PKG_DOCS" not in text
        assert "my_pkg" in text

    def test_removes_gitignore_and_workflow(self, tmp_path: Path) -> None:
        """Drop the VitePress ignore blocks and the docs workflow."""
        self._write(tmp_path)
        remove_docs(tmp_path)
        gitignore = (tmp_path / ".gitignore").read_text()
        assert ".vitepress" not in gitignore
        assert "docs/_build" not in gitignore
        assert not (tmp_path / ".github" / "workflows" / "docs.yml").exists()
        assert (tmp_path / ".github" / "workflows" / "main.yml").exists()


class TestUpdatePyprojectDepGroups:
    """Tests for update_pyproject_dep_groups."""

    def test_adds_mono_group(self, tmp_path: Path) -> None:
        """Add the package to the mono dependency group."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        update_pyproject_dep_groups(p, "my_pkg")
        doc = tomlkit.parse(p.read_text())
        assert doc["dependency-groups"]["mono"] == ["my_pkg"]


class TestClearLicensesDir:
    """Tests for clear_licenses_dir."""

    def test_removes_files_from_licenses_dir(self, tmp_path: Path) -> None:
        """Delete every file inside the LICENSES directory."""
        lic = tmp_path / "LICENSES"
        lic.mkdir()
        (lic / "MIT.txt").write_text("license")
        (lic / "APACHE.txt").write_text("license")
        clear_licenses_dir(tmp_path)
        assert not any(lic.iterdir())

    def test_noop_when_no_licenses_dir(self, tmp_path: Path) -> None:
        """Do nothing when the LICENSES directory is absent."""
        clear_licenses_dir(tmp_path)  # should not raise


class TestSetLicensePyproject:
    """Tests for set_license_pyproject."""

    def test_sets_license(self, tmp_path: Path) -> None:
        """Set the license field in an existing pyproject.toml."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[project]\nname = "x"\n')
        set_license_pyproject(p, "MIT")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["license"] == "MIT"

    def test_creates_project_when_missing(self, tmp_path: Path) -> None:
        """Create the project section when it is missing."""
        p = tmp_path / "pyproject.toml"
        p.write_text('[build-system]\nrequires = ["setuptools"]\n')
        set_license_pyproject(p, "MIT")
        doc = tomlkit.parse(p.read_text())
        assert doc["project"]["license"] == "MIT"


class TestSetLicensePackageJson:
    """Tests for set_license_package_json."""

    def test_sets_license(self, tmp_path: Path) -> None:
        """Set the license field in a package.json file."""
        p = tmp_path / "package.json"
        p.write_text('{"name": "x"}\n')
        set_license_package_json(p, "MIT")
        data = json.loads(p.read_text())
        assert data["license"] == "MIT"


class TestValidateLicense:
    """Tests for _validate_license."""

    def test_known_license_passes(self) -> None:
        """Accept a known SPDX license identifier."""
        _validate_license("MIT")  # should not raise

    def test_unknown_license_raises(self) -> None:
        """Raise ValueError for an unknown SPDX license identifier."""
        with pytest.raises(ValueError, match="Unknown SPDX license"):
            _validate_license("NONEXISTENT_LICENSE_XYZ")


class TestConfigureLicenses:
    """Tests for configure_licenses."""

    def test_configures_licenses(self, tmp_path: Path) -> None:
        """Clear, download, and set the license in all config files."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text('[project]\nname = "x"\n')
        pkg_json = tmp_path / "package.json"
        pkg_json.write_text('{"name": "x"}\n')
        licenses_dir = tmp_path / "LICENSES"
        licenses_dir.mkdir()
        (licenses_dir / "MIT.txt").write_text("x")
        # LICENSE file must exist (it gets unlinked first by write_license)
        (tmp_path / "LICENSE").write_text("old")

        with (
            patch("scaffolder.scaffold.files._validate_license"),
            patch("scaffolder.scaffold.files.write_license"),
            patch("scaffolder.scaffold.files.clear_licenses_dir") as mock_clear,
        ):
            configure_licenses(tmp_path, "MIT")
            mock_clear.assert_called_once()

        pydoc = tomlkit.parse(pyproject.read_text())
        assert pydoc["project"]["license"] == "MIT"

        pkg_data = json.loads(pkg_json.read_text())
        assert pkg_data["license"] == "MIT"


class TestRemoveReuse:
    """Tests for remove_reuse."""

    def test_removes_reuse_structure(self, tmp_path: Path) -> None:
        """Delete reuse dirs, REUSE.toml, dep, and script section."""
        # reuse directories + files
        (tmp_path / "LICENSES").mkdir()
        (tmp_path / "LICENSES" / "Unlicense.txt").write_text("x")
        (tmp_path / "package.json.license").write_text("x")
        reuse_toml = tmp_path / "packages" / "docs" / "REUSE.toml"
        reuse_toml.parent.mkdir(parents=True)
        reuse_toml.write_text("x")

        # keep LICENSE file
        (tmp_path / "LICENSE").write_text("keep me")

        # pyproject with a reuse dependency in the dev dependency group
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "x"\ndependencies = ["requests"]\n'
            "[dependency-groups]\n"
            'dev = ["pytest", "reuse ==6.2.0"]\n'
        )

        # licenses.sh with marked reuse section
        licenses_sh = tmp_path / "bin" / "lint" / "licenses.sh"
        licenses_sh.parent.mkdir(parents=True)
        licenses_sh.write_text(
            "#!/bin/bash\n"
            "echo non-reuse\n"
            "# ===== REUSE:START =====\n"
            "reuse lint\n"
            "# ===== REUSE:END =====\n"
            "echo tail\n"
        )

        remove_reuse(tmp_path)

        assert not (tmp_path / "LICENSES").exists()
        assert not (tmp_path / "packages" / "docs" / "REUSE.toml").exists()
        # .license companions are owned by strip_spdx_headers, not remove_reuse
        assert (tmp_path / "package.json.license").exists()
        assert (tmp_path / "LICENSE").read_text() == "keep me"

        pydoc = tomlkit.parse(pyproject.read_text())
        assert "reuse ==6.2.0" not in pydoc["project"]["dependencies"]
        assert "requests" in pydoc["project"]["dependencies"]
        dev_deps = pydoc["dependency-groups"]["dev"]
        assert "reuse ==6.2.0" not in dev_deps
        assert "pytest" in dev_deps

        script = licenses_sh.read_text()
        assert "reuse lint" not in script
        assert "REUSE:START" not in script
        assert "echo non-reuse" in script
        assert "echo tail" in script
