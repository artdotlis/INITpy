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
    set_entry_prod,
    set_version,
    update_envs,
    update_licenses_sh,
    update_tests,
)
from shared_utils.constants import VERSION


class TestAmendDocs:
    """Tests for amend_docs."""

    def test_updates_index_title(self, tmp_path: Path) -> None:
        """Retitle the docs index with the project name."""
        zensical = tmp_path / ".zensical.toml"
        zensical.write_text('site_name = "old"\n')
        index = tmp_path / "packages" / "docs" / "src" / "index.md"
        index.parent.mkdir(parents=True)
        index.write_text("# INIT - Python\n\ncontent")
        amend_docs(tmp_path, "my_pkg", "NewProject")
        assert index.read_text().startswith("# NewProject")

    def test_updates_zensical_site_name(self, tmp_path: Path) -> None:
        """Update the site name and drop repo references in zensical."""
        zensical = tmp_path / ".zensical.toml"
        zensical.write_text('site_name = "old"\nrepo_name = "x"\nrepo_url = "y"\n')
        # Need index.md for amend_docs to not fail
        index = tmp_path / "packages" / "docs" / "src" / "index.md"
        index.parent.mkdir(parents=True)
        index.write_text("# INIT - Python\n")
        amend_docs(tmp_path, "my_pkg", "NewProject")
        doc = tomlkit.parse(zensical.read_text())
        assert doc["site_name"] == "NewProject"
        assert "repo_name" not in doc
        assert "repo_url" not in doc

    def test_updates_ref_m_when_exists(self, tmp_path: Path) -> None:
        """Rewrite the module reference doc when it exists."""
        ref_m = tmp_path / "packages" / "docs" / "src" / "ref" / "ref_m.md"
        ref_m.parent.mkdir(parents=True)
        ref_m.write_text("# old content\n")
        # Need index.md for amend_docs to not fail
        zensical = tmp_path / ".zensical.toml"
        zensical.write_text('site_name = "old"\n')
        index = tmp_path / "packages" / "docs" / "src" / "index.md"
        index.write_text("# INIT - Python\n")
        amend_docs(tmp_path, "my_pkg", "NewProject")
        assert "# NewProject - my_pkg" in ref_m.read_text()


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


class TestSetEntryProd:
    """Tests for set_entry_prod."""

    def test_creates_entry_prod_sh(self, tmp_path: Path) -> None:
        """Write the production entry script with a sleeping loop."""
        set_entry_prod(tmp_path)
        entry = tmp_path / "bin" / "deploy" / "entry_prod.sh"
        assert entry.read_text() == "#!/bin/bash\n\nset -euo pipefail\n\nsleep infinity\n"


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
