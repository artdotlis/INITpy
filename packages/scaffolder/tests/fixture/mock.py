# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Mocked run() collaborator fixtures for scaffolder tests."""

from collections.abc import Iterator
from contextlib import ExitStack
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

CORE = "scaffolder.scaffold.core"

_COLLABORATORS = (
    "clone_git",
    "reset_git",
    "remove_projects_output_folder",
    "create_package",
    "write_package_files",
    "amend_docs",
    "update_envs",
    "update_tests",
    "clean_root_md",
    "correct_core_project",
    "strip_spdx_headers",
    "configure_licenses",
    "remove_prod_docker",
    "remove_reuse",
    "remove_docs",
    "lock_project",
    "init_and_commit",
)


def _recorder(order: list[str], name: str):
    """Build a side effect that appends name to order."""

    def _side_effect(*args: object, **kwargs: object) -> None:
        del args, kwargs
        order.append(name)

    return _side_effect


@pytest.fixture
def pipeline() -> Iterator[tuple[dict[str, MagicMock], list[str]]]:
    """Patch every run() collaborator and record the call order."""
    with ExitStack() as stack:
        mocks = {
            name: stack.enter_context(patch(f"{CORE}.{name}")) for name in _COLLABORATORS
        }
        order: list[str] = []
        for name, mock in mocks.items():
            mock.side_effect = _recorder(order, name)
        yield mocks, order
