# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.files (remaining functions)."""

import json
from pathlib import Path

import pytest
import tomlkit
from scaffolder.scaffold.files import (
    amend_docs,
    clean_root_md,
    correct_core_project,
    remove_prod_docker,
    set_version,
    update_commitizen_version_files,
    update_copyright,
    update_envs,
    update_licenses_sh,
    update_tests,
)
from shared_utils.constants import VERSION


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


class TestSetVersion:
    """Tests for set_version."""

    def test_replaces_version_in_pyproject(self, tmp_path: Path) -> None:
        """Replace the template version in a pyproject.toml."""
        p = tmp_path / "pyproject.toml"

        p.write_text(f'[project]\nversion = "{VERSION}"\n')
        set_version(tmp_path)
        assert VERSION not in p.read_text()
        assert "0.1.0" in p.read_text()

    def test_replaces_version_in_package_json(self, tmp_path: Path) -> None:
        """Replace the template version in a package.json."""
        p = tmp_path / "package.json"

        p.write_text(f'{{"version": "{VERSION}"}}\n')
        set_version(tmp_path)
        assert VERSION not in p.read_text()

    def test_preserves_dependency_version_pins(self, tmp_path: Path) -> None:
        """Only the project version is replaced, not pinned dependency versions."""
        p = tmp_path / "pyproject.toml"

        p.write_text(
            f'[project]\nversion = "{VERSION}"\ndependencies = ["shellcheck-py=={VERSION}.1"]\n'
        )
        set_version(tmp_path)
        content = p.read_text()
        assert content.startswith('[project]\nversion = "0.1.0"')
        assert f"shellcheck-py=={VERSION}.1" in content


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
