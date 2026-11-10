# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Verify the current project recreates from the whole-file templates.

The templates are the source of truth for the config files the scaffolder
writes. The ``template`` fixture yields one template at a time (parametrized
over every shipped template), so these tests check the catalogue file by file:
each template file exists, its target file (the original) exists, and the
template recreates its original.
"""

from pathlib import Path
from typing import Any

import pytest

from scaffolder.template import TEMPLATES_DIR

pytest_plugins = ("tests.fixture.template",)

# Every shipped whole-file template, resolved from the template directory so the
# catalogue cannot drift from what the scaffolder actually ships.
TEMPLATE_NAMES = sorted(
    entry.relative_to(TEMPLATES_DIR).as_posix()
    for entry in TEMPLATES_DIR.rglob("*.jinja")
)


class TestRecreatesProject:
    """The current project is reproducible from its templates."""

    @pytest.mark.parametrize("template", TEMPLATE_NAMES, indirect=["template"])
    def test_template_and_target_exist(self, template: Any) -> None:
        """The template file exists and its target file exists in the project."""
        assert template.path.is_file(), f"missing template: {template.name}"
        assert template.target_path.is_file(), f"missing target: {template.target}"

    @pytest.mark.parametrize("template", TEMPLATE_NAMES, indirect=["template"])
    def test_template_recreates_target(
        self, template: Any, context: dict[str, object], tmp_path: Path
    ) -> None:
        """Rendering the template materializes its original target file."""
        out = tmp_path / template.target
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(template.render(context))
        assert out.is_file(), f"not recreated: {template.name}"
        assert out.read_text(), f"empty render: {template.name}"
