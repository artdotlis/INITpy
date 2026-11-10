# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Environment fixtures for scaffolder CLI tests."""

import pytest


@pytest.fixture(autouse=True)
def clear_scaf_output_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unset SCAF_OUTPUT_DIR so the output prompt is always shown."""
    monkeypatch.delenv("SCAF_OUTPUT_DIR", raising=False)
