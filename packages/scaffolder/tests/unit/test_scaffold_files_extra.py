# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.files (remaining functions)."""

from pathlib import Path
import tomlkit
import json

from scaffolder.scaffold.files import (
    amend_docs,
    update_envs,
    set_version,
    update_licenses_sh,
    set_entry_prod,
    clean_root_md,
    correct_core_project,
)


class TestAmendDocs:
    def test_updates_index_title(self, tmp_path: Path) -> None:
        zensical = tmp_path / ".zensical.toml"
        zensical.write_text('site_name = "old"\n')
        index = tmp_path / "packages" / "docs" / "src" / "index.md"
        index.parent.mkdir(parents=True)
        index.write_text("# INIT - Python\n\ncontent")
        amend_docs(tmp_path, "my_pkg", "NewProject")
        assert index.read_text().startswith("# NewProject")

    def test_updates_zensical_site_name(self, tmp_path: Path) -> None:
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
    def test_updates_package_env(self, tmp_path: Path) -> None:
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


class TestSetVersion:
    def test_replaces_version_in_pyproject(self, tmp_path: Path) -> None:
        p = tmp_path / "pyproject.toml"
        from shared_utils.constants import VERSION

        p.write_text(f'[project]\nversion = "{VERSION}"\n')
        set_version(tmp_path)
        assert VERSION not in p.read_text()
        assert "0.1.0" in p.read_text()

    def test_replaces_version_in_package_json(self, tmp_path: Path) -> None:
        p = tmp_path / "package.json"
        from shared_utils.constants import VERSION

        p.write_text(f'{{"version": "{VERSION}"}}\n')
        set_version(tmp_path)
        assert VERSION not in p.read_text()


class TestUpdateLicensesSh:
    def test_adds_exit_on_failure(self, tmp_path: Path) -> None:
        sh = tmp_path / "bin" / "lint" / "licenses.sh"
        sh.parent.mkdir(parents=True)
        sh.write_text("#!/bin/bash\necho hello\n")
        update_licenses_sh(tmp_path)
        content = sh.read_text()
        assert "exit 1" in content
        assert content.startswith("#!/bin/bash")

    def test_raises_when_file_missing(self, tmp_path: Path) -> None:
        import pytest

        with pytest.raises(FileNotFoundError):
            update_licenses_sh(tmp_path)


class TestSetEntryProd:
    def test_creates_entry_prod_sh(self, tmp_path: Path) -> None:
        set_entry_prod(tmp_path)
        entry = tmp_path / "bin" / "deploy" / "entry_prod.sh"
        assert entry.read_text() == "#!/bin/bash\n\nset -euo pipefail\n\nsleep infinity\n"


class TestCleanRootMd:
    def test_updates_readme(self, tmp_path: Path) -> None:
        clean_root_md(tmp_path, "NewProject")
        assert (tmp_path / "README.md").read_text() == "# NewProject\n\n"

    def test_clears_changelog(self, tmp_path: Path) -> None:
        clean_root_md(tmp_path, "Proj")
        assert (tmp_path / "CHANGELOG.md").read_text() == ""

    def test_removes_lock_files(self, tmp_path: Path) -> None:
        (tmp_path / "uv.lock").write_text("x")
        (tmp_path / "pnpm-lock.yaml").write_text("y")
        clean_root_md(tmp_path, "Proj")
        assert not (tmp_path / "uv.lock").exists()
        assert not (tmp_path / "pnpm-lock.yaml").exists()


class TestCorrectCoreProject:
    def test_updates_all_files(self, tmp_path: Path) -> None:
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
