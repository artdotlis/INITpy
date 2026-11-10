# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Template fixtures: one fixture function per whole-file template."""

import json
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from jinja2.environment import Template as JinjaTemplate

from scaffolder.template import TEMPLATES_DIR, load_template
from shared_utils.core.names import (
    package_env_file,
    package_env_var,
    sanitize_package_name,
    sanitize_package_name_dep_group,
)

# tests/fixture/template.py -> repo root
# (fixture -> tests -> scaffolder -> packages -> root)
_REPO_ROOT = Path(__file__).resolve().parents[4]

# A template is only rendered with the non-default [[ ]] delimiters when its
# target already contains {{ }} (GitHub Actions).
_ALTERNATE_DELIMITERS = {
    "github/mac_win_test.yml.jinja",
    "github/lin_lint.yml.jinja",
}

# template (relative to templates/) -> file the scaffolder writes in the project
TEMPLATE_TARGETS: dict[str, str] = {
    "root/root.toml.jinja": "pyproject.toml",
    "root/package.json.jinja": "package.json",
    "root/lefthook.yml.jinja": "lefthook.yml",
    "root/pnpm-workspace.yaml.jinja": "pnpm-workspace.yaml",
    "root/Makefile.jinja": "Makefile",
    "root/gitignore.jinja": ".gitignore",
    "root/dockerignore.jinja": ".dockerignore",
    "root/package.env.jinja": "package.env",
    "root/README.md.jinja": "README.md",
    "root/package.toml.jinja": "packages/scaffolder/pyproject.toml",
    "devcontainer/devcontainer.json.jinja": ".devcontainer/devcontainer.json",
    "github/mac_win_test.yml.jinja": ".github/workflows/mac_win_test.yml",
    "github/lin_lint.yml.jinja": ".github/workflows/lin_lint.yml",
    "lint/lint_env.sh.jinja": "bin/lint/lint_env.sh",
    "lint/licenses.sh.jinja": "bin/lint/licenses.sh",
    "docs/index.md.jinja": "packages/docs/src/index.md",
    "docs/ref_index.md.jinja": "packages/docs/src/ref/index.md",
    "docs/vitepress_config.toml.jinja": "packages/docs/.vitepress/config.toml",
    "docs/package.json.jinja": "packages/docs/package.json",
}


@dataclass(frozen=True, slots=True)
class Template:
    """A single whole-file template and the project file it produces."""

    name: str
    """Template path relative to ``templates/`` (e.g. ``root/root.toml.jinja``)."""
    target: str
    """Project-relative path the scaffolder writes this template to."""

    @property
    def path(self) -> Path:
        return TEMPLATES_DIR / self.name

    @property
    def target_path(self) -> Path:
        return _REPO_ROOT / self.target

    def load(self) -> JinjaTemplate:
        """Load (read + compile) this template from the templates directory.

        Returns the compiled Jinja template. Raises ``TemplateNotFound`` if the
        file is missing and ``TemplateSyntaxError`` if the source is malformed.
        """
        start, end = self._delimiters()
        return load_template(self.name, start, end)

    def render(self, context: dict[str, object]) -> str:
        """Render this template with the given context."""
        return self.load().render(**context)

    def _delimiters(self) -> tuple[str, str]:
        if self.name in _ALTERNATE_DELIMITERS:
            return "[[", "]]"
        return "{{", "}}"


# ---------------------------------------------------------------------------
# One fixture function per shipped template.
# ---------------------------------------------------------------------------


@pytest.fixture
def root_root_toml_jinja() -> Template:
    """``root/root.toml.jinja`` -> ``pyproject.toml``."""
    return Template("root/root.toml.jinja", TEMPLATE_TARGETS["root/root.toml.jinja"])


@pytest.fixture
def root_package_json_jinja() -> Template:
    """``root/package.json.jinja`` -> ``package.json``."""
    return Template(
        "root/package.json.jinja", TEMPLATE_TARGETS["root/package.json.jinja"]
    )


@pytest.fixture
def root_lefthook_yml_jinja() -> Template:
    """``root/lefthook.yml.jinja`` -> ``lefthook.yml``."""
    return Template(
        "root/lefthook.yml.jinja", TEMPLATE_TARGETS["root/lefthook.yml.jinja"]
    )


@pytest.fixture(name="root_pnpm-workspace_yaml_jinja")
def root_pnpm_workspace_yaml_jinja() -> Template:
    """``root/pnpm-workspace.yaml.jinja`` -> ``pnpm-workspace.yaml``."""
    return Template(
        "root/pnpm-workspace.yaml.jinja",
        TEMPLATE_TARGETS["root/pnpm-workspace.yaml.jinja"],
    )


@pytest.fixture(name="root_Makefile_jinja")
def root_makefile_jinja() -> Template:
    """``root/Makefile.jinja`` -> ``Makefile``."""
    return Template("root/Makefile.jinja", TEMPLATE_TARGETS["root/Makefile.jinja"])


@pytest.fixture
def root_gitignore_jinja() -> Template:
    """``root/gitignore.jinja`` -> ``.gitignore``."""
    return Template("root/gitignore.jinja", TEMPLATE_TARGETS["root/gitignore.jinja"])


@pytest.fixture
def root_dockerignore_jinja() -> Template:
    """``root/dockerignore.jinja`` -> ``.dockerignore``."""
    return Template(
        "root/dockerignore.jinja", TEMPLATE_TARGETS["root/dockerignore.jinja"]
    )


@pytest.fixture
def root_package_env_jinja() -> Template:
    """``root/package.env.jinja`` -> ``package.env``."""
    return Template("root/package.env.jinja", TEMPLATE_TARGETS["root/package.env.jinja"])


@pytest.fixture(name="root_README_md_jinja")
def root_readme_md_jinja() -> Template:
    """``root/README.md.jinja`` -> ``README.md``."""
    return Template("root/README.md.jinja", TEMPLATE_TARGETS["root/README.md.jinja"])


@pytest.fixture
def root_package_toml_jinja() -> Template:
    """``root/package.toml.jinja`` -> ``packages/scaffolder/pyproject.toml``."""
    return Template(
        "root/package.toml.jinja", TEMPLATE_TARGETS["root/package.toml.jinja"]
    )


@pytest.fixture
def devcontainer_devcontainer_json_jinja() -> Template:
    """``devcontainer/devcontainer.json.jinja`` -> ``.devcontainer/devcontainer.json``."""
    return Template(
        "devcontainer/devcontainer.json.jinja",
        TEMPLATE_TARGETS["devcontainer/devcontainer.json.jinja"],
    )


@pytest.fixture
def github_mac_win_test_yml_jinja() -> Template:
    """``github/mac_win_test.yml.jinja`` -> ``.github/workflows/mac_win_test.yml``."""
    return Template(
        "github/mac_win_test.yml.jinja",
        TEMPLATE_TARGETS["github/mac_win_test.yml.jinja"],
    )


@pytest.fixture
def github_lin_lint_yml_jinja() -> Template:
    """``github/lin_lint.yml.jinja`` -> ``.github/workflows/lin_lint.yml``."""
    return Template(
        "github/lin_lint.yml.jinja", TEMPLATE_TARGETS["github/lin_lint.yml.jinja"]
    )


@pytest.fixture
def lint_lint_env_sh_jinja() -> Template:
    """``lint/lint_env.sh.jinja`` -> ``bin/lint/lint_env.sh``."""
    return Template("lint/lint_env.sh.jinja", TEMPLATE_TARGETS["lint/lint_env.sh.jinja"])


@pytest.fixture
def lint_licenses_sh_jinja() -> Template:
    """``lint/licenses.sh.jinja`` -> ``bin/lint/licenses.sh``."""
    return Template("lint/licenses.sh.jinja", TEMPLATE_TARGETS["lint/licenses.sh.jinja"])


@pytest.fixture
def docs_index_md_jinja() -> Template:
    """``docs/index.md.jinja`` -> ``packages/docs/src/index.md``."""
    return Template("docs/index.md.jinja", TEMPLATE_TARGETS["docs/index.md.jinja"])


@pytest.fixture
def docs_ref_index_md_jinja() -> Template:
    """``docs/ref_index.md.jinja`` -> ``packages/docs/src/ref/index.md``."""
    return Template(
        "docs/ref_index.md.jinja", TEMPLATE_TARGETS["docs/ref_index.md.jinja"]
    )


@pytest.fixture
def docs_vitepress_config_toml_jinja() -> Template:
    """``docs/vitepress_config.toml.jinja`` -> ``packages/docs/.vitepress`` config."""
    return Template(
        "docs/vitepress_config.toml.jinja",
        TEMPLATE_TARGETS["docs/vitepress_config.toml.jinja"],
    )


@pytest.fixture
def docs_package_json_jinja() -> Template:
    """``docs/package.json.jinja`` -> ``packages/docs/package.json``."""
    return Template(
        "docs/package.json.jinja", TEMPLATE_TARGETS["docs/package.json.jinja"]
    )


# ---------------------------------------------------------------------------
# One fixture function per original project file (the target each template
# produces). These mirror the per-template fixtures but yield the *original*
# file on disk that each template recreates, so tests can compare a rendered
# template against its source-of-truth original.
# ---------------------------------------------------------------------------


@pytest.fixture
def original_package_json() -> Path:
    """``package.json``."""
    return _REPO_ROOT / "package.json"


@pytest.fixture
def original_lefthook_yml() -> Path:
    """``lefthook.yml``."""
    return _REPO_ROOT / "lefthook.yml"


@pytest.fixture
def original_pnpm_workspace_yaml() -> Path:
    """``pnpm-workspace.yaml``."""
    return _REPO_ROOT / "pnpm-workspace.yaml"


@pytest.fixture
def original_makefile() -> Path:
    """``Makefile``."""
    return _REPO_ROOT / "Makefile"


@pytest.fixture
def original_gitignore() -> Path:
    """``.gitignore``."""
    return _REPO_ROOT / ".gitignore"


@pytest.fixture
def original_dockerignore() -> Path:
    """``.dockerignore``."""
    return _REPO_ROOT / ".dockerignore"


@pytest.fixture
def original_package_env() -> Path:
    """``package.env``."""
    return _REPO_ROOT / "package.env"


@pytest.fixture
def original_readme_md() -> Path:
    """``README.md``."""
    return _REPO_ROOT / "README.md"


@pytest.fixture
def original_devcontainer_json() -> Path:
    """``.devcontainer/devcontainer.json``."""
    return _REPO_ROOT / ".devcontainer/devcontainer.json"


@pytest.fixture
def original_github_mac_win_test_yml() -> Path:
    """``.github/workflows/mac_win_test.yml``."""
    return _REPO_ROOT / ".github/workflows/mac_win_test.yml"


@pytest.fixture
def original_github_lin_lint_yml() -> Path:
    """``.github/workflows/lin_lint.yml``."""
    return _REPO_ROOT / ".github/workflows/lin_lint.yml"


@pytest.fixture
def original_lint_env_sh() -> Path:
    """``bin/lint/lint_env.sh``."""
    return _REPO_ROOT / "bin/lint/lint_env.sh"


@pytest.fixture
def original_licenses_sh() -> Path:
    """``bin/lint/licenses.sh``."""
    return _REPO_ROOT / "bin/lint/licenses.sh"


@pytest.fixture
def original_docs_index_md() -> Path:
    """``packages/docs/src/index.md``."""
    return _REPO_ROOT / "packages/docs/src/index.md"


@pytest.fixture
def original_docs_ref_index_md() -> Path:
    """``packages/docs/src/ref/index.md``."""
    return _REPO_ROOT / "packages/docs/src/ref/index.md"


@pytest.fixture
def original_docs_vitepress_config_toml() -> Path:
    """``packages/docs/.vitepress/config.toml``."""
    return _REPO_ROOT / "packages/docs/.vitepress/config.toml"


@pytest.fixture
def original_docs_package_json() -> Path:
    """``packages/docs/package.json``."""
    return _REPO_ROOT / "packages/docs/package.json"


# ---------------------------------------------------------------------------
# Generic (parametrized) and render-context fixtures.
# ---------------------------------------------------------------------------


def _package_json() -> dict[str, Any]:
    return json.loads((_REPO_ROOT / "package.json").read_text())


def _pyproject() -> dict[str, Any]:
    with (_REPO_ROOT / "pyproject.toml").open("rb") as handle:
        return tomllib.load(handle)


@pytest.fixture
def template(request: pytest.FixtureRequest) -> Template:
    """Resolve a single template (parametrize over the shipped templates)."""
    name = request.param
    return Template(name, TEMPLATE_TARGETS[name])


@pytest.fixture
def context() -> dict[str, object]:
    """The current project's render context, rebuilt as ``core.run`` does.

    The package identity is derived the same way the scaffolder derives it for a
    generated project (``<sanitized>_pkg``), here from the repo's own package;
    the metadata comes from the current ``package.json`` / ``pyproject.toml``.
    """
    package_name = f"{sanitize_package_name('scaffolder')}_pkg"
    project = _package_json()
    pyproject = _pyproject()
    copyright_holder = str(project["author"]["name"])
    return {
        "package_name": package_name,
        "version": str(project["version"]),
        "description": str(pyproject["project"]["description"]),
        "author_name": copyright_holder,
        "author_email": str(project["author"]["email"]),
        "copyright_holder": copyright_holder,
        "year": datetime.now().year,
        "project_name": str(project["name"]),
        "dep_name": sanitize_package_name_dep_group(package_name),
        "license": str(pyproject["project"]["license"]),
        "package_env_var": package_env_var(package_name),
        "package_env_file": package_env_file(package_name),
        "use_reuse": True,
        "use_docs": True,
    }
