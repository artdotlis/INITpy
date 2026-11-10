# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Live shared_utils template fixtures: the reuse tree remove_reuse operates on.

``remove_reuse`` only deletes the ``LICENSES/`` tree and the ``REUSE.toml``
configs (the ``.dockerignore`` ``!LICENSES`` line is template-owned, and the
``.license`` companions belong to ``strip_spdx_headers``). These fixtures
materialize the live repo pieces a realistic reuse tree needs.
"""

from pathlib import Path

import pytest

from shared_utils.repo.template import load_template

# packages/shared_utils/tests/fixture -> repo root
_REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.fixture
def licenses_dir(tmp_path: Path) -> Path:
    return load_template(_REPO_ROOT, tmp_path, "LICENSES")


@pytest.fixture
def license_file(tmp_path: Path) -> Path:
    return load_template(_REPO_ROOT, tmp_path, "LICENSE")


@pytest.fixture
def reuse_toml(tmp_path: Path) -> Path:
    return load_template(_REPO_ROOT, tmp_path, "packages/docs/REUSE.toml")


@pytest.fixture
def package_json_license(tmp_path: Path) -> Path:
    return load_template(_REPO_ROOT, tmp_path, "package.json.license")
