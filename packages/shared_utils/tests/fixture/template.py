# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Live shared_utils template fixtures: root files, reuse files, docs package."""

from pathlib import Path

import pytest

from shared_utils.template import load_template

# packages/shared_utils/tests -> repo root
_TEMPLATE_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def pyproject_toml(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "pyproject.toml")


@pytest.fixture
def lefthook_yml(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "lefthook.yml")


@pytest.fixture
def docs_pkg(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "packages/docs")


@pytest.fixture
def licenses_sh(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "bin/lint/licenses.sh")


@pytest.fixture
def licenses_dir(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "LICENSES")


@pytest.fixture
def license_file(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "LICENSE")


@pytest.fixture
def package_json_license(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, "package.json.license")


@pytest.fixture
def dockerignore(tmp_path: Path) -> Path:
    return load_template(_TEMPLATE_ROOT, tmp_path, ".dockerignore")
