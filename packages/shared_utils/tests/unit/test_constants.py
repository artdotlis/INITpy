# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.core.constants."""

from pathlib import Path

import tomlkit

from shared_utils.core.constants import VERSION

PYPROJECT = Path(__file__).parents[2] / "pyproject.toml"


def test_version_matches_pyproject() -> None:
    """Keep the advertised template version in sync with pyproject.toml."""
    doc = tomlkit.parse(PYPROJECT.read_text())
    assert doc["project"]["version"] == VERSION
