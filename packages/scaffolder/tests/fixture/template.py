# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Live single-package template fixtures: root files, hooks, and workflows."""

from pathlib import Path

import pytest

from shared_utils.repo.template import load_template

# packages/scaffolder/tests/fixture -> repo root
_TEMPLATE_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def pyproject_toml(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "pyproject.toml")


@pytest.fixture
def shared_utils_pyproject(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "packages/shared_utils/pyproject.toml")


@pytest.fixture
def pnpm_workspace_yaml(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "pnpm-workspace.yaml")


@pytest.fixture
def makefile(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "Makefile")


@pytest.fixture
def gitignore(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, ".gitignore")


@pytest.fixture
def lefthook_yml(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "lefthook.yml")


@pytest.fixture
def package_env(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "package.env")


@pytest.fixture
def lint_env_sh(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "bin/lint/lint_env.sh")


@pytest.fixture
def licenses_sh(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "bin/lint/licenses.sh")


@pytest.fixture
def clean_sh(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "bin/install/clean.sh")


@pytest.fixture
def package_json(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "package.json")


@pytest.fixture
def devcontainer_json(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, ".devcontainer/devcontainer.json")


@pytest.fixture
def dev_compose(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, ".devcontainer/dev.docker-compose.yml")


@pytest.fixture
def dockerfile(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "Dockerfile")


@pytest.fixture
def main_workflow(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, ".github/workflows/main.yml")


@pytest.fixture
def docs_workflow(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, ".github/workflows/docs.yml")


@pytest.fixture
def docs_pkg(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "packages/docs")


@pytest.fixture
def scaffolder_pkg(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "packages/scaffolder")


@pytest.fixture
def docs_template(tmp_path: Path) -> Path:
    """Materialize the live template pieces used by docs removal."""
    for rel in (
        "pyproject.toml",
        "pnpm-workspace.yaml",
        "Makefile",
        ".gitignore",
        "lefthook.yml",
        "package.env",
        "bin/lint/lint_env.sh",
        "bin/lint/licenses.sh",
        "bin/install/clean.sh",
        ".github/workflows/docs.yml",
        ".github/workflows/main.yml",
        "packages/docs",
        "packages/scaffolder",
    ):
        load_template(_TEMPLATE_ROOT, tmp_path, rel)
    return tmp_path
