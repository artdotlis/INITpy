# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for the scaffolder grouped scaffold modules."""

import json
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

import pytest
import tomlkit
from scaffolder.scaffold.config import correct_core_project
from scaffolder.scaffold.config import update_commitizen_version_files
from scaffolder.scaffold.config import update_pyproject_dep_groups
from scaffolder.scaffold.docs import _drop_docs_make_targets, amend_docs, remove_docs
from scaffolder.scaffold.env import update_copyright, update_envs
from scaffolder.scaffold.licenses import _validate_license
from scaffolder.scaffold.licenses import clear_licenses_dir
from scaffolder.scaffold.licenses import configure_licenses
from scaffolder.scaffold.licenses import set_license_licenses_sh
from scaffolder.scaffold.licenses import set_license_package_json
from scaffolder.scaffold.licenses import set_license_pyproject
from scaffolder.scaffold.licenses import update_licenses_sh
from scaffolder.scaffold.skeleton import clean_root_md, remove_prod_docker
from scaffolder.scaffold.skeleton import remove_projects_output_folder
from scaffolder.scaffold.tests import update_tests

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


class TestUpdateCopyright:
    """Tests for update_copyright."""

    def test_updates_package_env(self, tmp_path: Path, package_env: Path) -> None:
        """Replace the COPYRIGHT value in package.env."""
        update_copyright(tmp_path, "New Owner")
        content = package_env.read_text()
        assert 'COPYRIGHT="New Owner"' in content
        assert "Artur Lissin" not in content
        assert "PYV=" in content


class TestUpdateEnvs:
    """Tests for update_envs (run against live template files)."""

    def test_repoints_env_files(
        self, tmp_path: Path, package_env: Path, lint_env_sh: Path
    ) -> None:
        """Repoint package.env and the lint script at the new package."""
        update_envs(tmp_path, "my_pkg")

        content = package_env.read_text()
        assert "PKG_MY_" in content  # first 3 chars of "MY_PKG" are "MY_"
        assert "PKG_SHAR" not in content

        lint_env = lint_env_sh.read_text()
        assert "$SCAF_ENV" not in lint_env
        assert "MY__ENV" in lint_env


class TestUpdateTests:
    """Tests for update_tests (run against live template files)."""

    def test_collapses_tests_to_single_package(
        self, tmp_path: Path, lefthook_yml: Path, main_workflow: Path
    ) -> None:
        """Collapse the lefthook jobs and the CI steps to the one package."""
        update_tests(tmp_path, "my_pkg")

        hooks = lefthook_yml.read_text()
        assert "$PKG_SHAR" not in hooks
        assert "$PKG_SCAF" not in hooks
        assert "- name: my_pkg" in hooks
        assert "cd $PKG_MY_ && coverage run -m pytest" in hooks

        ci = main_workflow.read_text()
        assert "packages/shared_utils" not in ci
        assert "packages/scaffolder" not in ci
        assert "working-directory: packages/my_pkg" in ci
        # The real template runs tests from several jobs, so the appended
        # step appears once per job — count generously, never "exactly".
        assert ci.count("- name: Run my_pkg tests") >= 1

    def test_skips_jobs_without_step_list(self, tmp_path: Path) -> None:
        """Leave jobs whose steps are not a list untouched."""
        (tmp_path / "lefthook.yml").write_text("tests: {jobs: [{name: x, run: y}]}\n")
        workflow = tmp_path / ".github" / "workflows" / "main.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            "jobs:\n"
            "  reusable:\n"
            "    uses: ./.github/workflows/other.yml\n"
            "  real:\n"
            "    steps:\n"
            "      - run: uv run pytest\n"
        )
        update_tests(tmp_path, "my_pkg")
        content = workflow.read_text()
        assert "uses: ./.github/workflows/other.yml" in content
        assert "uv run pytest" not in content
        assert content.count("Run my_pkg tests") == 1


def _drop_tool_table(doc: Any) -> None:
    """Remove the whole [tool] table."""
    _ = doc.pop("tool")


def _drop_commitizen_table(doc: Any) -> None:
    """Remove the [tool.commitizen] table."""
    _ = doc["tool"].pop("commitizen")


def _make_version_files_a_string(doc: Any) -> None:
    """Replace the version_files list with a bare string."""
    doc["tool"]["commitizen"]["version_files"] = "pyproject.toml"


def _drop_version_files(doc: Any) -> None:
    """Remove version_files from the [tool.commitizen] table."""
    _ = doc["tool"]["commitizen"].pop("version_files")


class TestUpdateCommitizenVersionFiles:
    """Tests for update_commitizen_version_files (live root pyproject.toml)."""

    def test_retargets_and_removes_shared_utils(
        self, tmp_path: Path, pyproject_toml: Path
    ) -> None:
        """Drop shared_utils entries and rename scaffolder to new package."""
        update_commitizen_version_files(tmp_path, "my_pkg")

        doc = tomlkit.parse(pyproject_toml.read_text())
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

    def test_raises_when_missing(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when there is no pyproject.toml."""
        with pytest.raises(FileNotFoundError):
            update_commitizen_version_files(tmp_path, "my_pkg")

    @pytest.mark.parametrize(
        "mutate",
        [
            pytest.param(_drop_tool_table, id="no-tool-table"),
            pytest.param(_drop_commitizen_table, id="no-commitizen"),
            pytest.param(_make_version_files_a_string, id="version-files-not-a-list"),
            pytest.param(_drop_version_files, id="no-version-files"),
        ],
    )
    def test_leaves_incomplete_pyproject_untouched(
        self, tmp_path: Path, pyproject_toml: Path, mutate: Callable[[Any], None]
    ) -> None:
        """Skip the rewrite when the commitizen version_files block is absent."""
        doc = tomlkit.parse(pyproject_toml.read_text())
        mutate(doc)
        pyproject_toml.write_text(tomlkit.dumps(doc))
        before = pyproject_toml.read_text()

        update_commitizen_version_files(tmp_path, "my_pkg")

        assert pyproject_toml.read_text() == before


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

    def test_updates_all_files(
        self,
        tmp_path: Path,
        pyproject_toml: Path,
        package_json: Path,
        devcontainer_json: Path,
    ) -> None:
        """Apply project metadata to the live root config files."""
        pyproject = pyproject_toml
        pkg_json = package_json
        devcontainer = devcontainer_json

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


class TestRemoveProjectsOutputFolder:
    """Tests for remove_projects_output_folder."""

    def test_removes_directory(self, tmp_path: Path) -> None:
        """Delete the PROJECTS directory and its contents."""
        projects = tmp_path / "PROJECTS"
        (projects / "demo").mkdir(parents=True)
        remove_projects_output_folder(tmp_path)
        assert not projects.exists()

    def test_removes_file_named_projects(self, tmp_path: Path) -> None:
        """Unlink a PROJECTS path that is a plain file."""
        (tmp_path / "PROJECTS").write_text("stale")
        remove_projects_output_folder(tmp_path)
        assert not (tmp_path / "PROJECTS").exists()

    def test_noop_without_projects(self, tmp_path: Path) -> None:
        """Do nothing when there is no PROJECTS path."""
        remove_projects_output_folder(tmp_path)
        assert list(tmp_path.iterdir()) == []


class TestRemoveProdDocker:
    """Tests for remove_prod_docker."""

    def test_removes_prod_docker_and_promotes_dev(
        self,
        tmp_path: Path,
        dockerfile: Path,
        dev_compose: Path,
        devcontainer_json: Path,
    ) -> None:
        """Drop the prod Dockerfile and promote the dev compose to root."""
        remove_prod_docker(tmp_path)

        assert not dockerfile.exists()
        promoted = tmp_path / "docker-compose.yml"
        assert promoted.exists()
        assert not dev_compose.exists()
        config = json.loads(devcontainer_json.read_text())
        assert config["dockerComposeFile"] == ["../docker-compose.yml"]


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
        """Drop docs targets and PKG_DOCS recipe lines from the Makefile."""
        remove_docs(docs_template)
        makefile = (docs_template / "Makefile").read_text()
        for frag in (
            "build-docs:",
            "run-docs:",
            "serve-docs:",
            "docs-ref:",
            "PKG_DOCS",
        ):
            assert frag not in makefile
        assert not makefile.startswith("\n")
        assert "exp-run-lock:\n\t$(UVE) lock\n" in makefile
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


class TestSetLicenseLicensesSh:
    """Tests for set_license_licenses_sh."""

    def test_sets_software_lic(self, licenses_sh: Path) -> None:
        """Replace the default SOFTWARE_LIC with the user's choice."""
        sh = licenses_sh
        set_license_licenses_sh(sh, "MIT")
        text = sh.read_text()
        assert 'SOFTWARE_LIC="MIT"' in text
        assert 'DATA_LIC="CC0-1.0"' in text

    def test_raises_when_assignment_missing(self, tmp_path: Path) -> None:
        """Fail loudly when SOFTWARE_LIC is not present."""
        sh = tmp_path / "licenses.sh"
        sh.write_text('DATA_LIC="CC0-1.0"\n')
        with pytest.raises(ValueError):
            set_license_licenses_sh(sh, "MIT")


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

    def test_configures_licenses(
        self,
        tmp_path: Path,
        pyproject_toml: Path,
        package_json: Path,
        licenses_sh: Path,
    ) -> None:
        """Clear, download, and set the license in all config files."""
        pyproject = pyproject_toml
        pkg_json = package_json

        with (
            patch("scaffolder.scaffold.licenses._validate_license"),
            patch("scaffolder.scaffold.licenses.write_license"),
            patch("scaffolder.scaffold.licenses.clear_licenses_dir") as mock_clear,
        ):
            configure_licenses(tmp_path, "MIT")
            mock_clear.assert_called_once()

        pydoc = tomlkit.parse(pyproject.read_text())
        assert pydoc["project"]["license"] == "MIT"

        pkg_data = json.loads(pkg_json.read_text())
        assert pkg_data["license"] == "MIT"
        assert 'SOFTWARE_LIC="MIT"' in licenses_sh.read_text()
