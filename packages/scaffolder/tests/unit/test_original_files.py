# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for the per-original-file fixtures.

Every original project file that a template recreates is exposed as its own
fixture function (``original_<file>``) yielding the file's ``Path``. Each fixture
is resolved by name and asserted to point at an existing, non-empty file so the
source-of-truth originals are present and readable.
"""

from pathlib import Path

import pytest

pytest_plugins = ("tests.fixture.template",)

# Every original-file fixture, listed by name.
ORIGINAL_FIXTURES = [
    "original_package_json",
    "original_lefthook_yml",
    "original_pnpm_workspace_yaml",
    "original_makefile",
    "original_gitignore",
    "original_dockerignore",
    "original_package_env",
    "original_readme_md",
    "original_devcontainer_json",
    "original_github_mac_win_test_yml",
    "original_github_lin_lint_yml",
    "original_lint_env_sh",
    "original_licenses_sh",
    "original_docs_index_md",
    "original_docs_ref_index_md",
    "original_docs_vitepress_config_toml",
    "original_docs_package_json",
]


@pytest.mark.parametrize("fixture_name", ORIGINAL_FIXTURES)
def test_original_file_fixture_resolves(
    request: pytest.FixtureRequest, fixture_name: str
) -> None:
    """The per-original-file fixture yields an existing, non-empty file."""
    path: Path = request.getfixturevalue(fixture_name)
    assert path.is_file(), f"missing original: {fixture_name} -> {path}"
    assert path.stat().st_size > 0, f"empty original: {path}"
