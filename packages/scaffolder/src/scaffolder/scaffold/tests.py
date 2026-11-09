# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Test wiring (lefthook + CI) for a generated project."""

from pathlib import Path
from typing import Any

from scaffolder.template import render_template


def update_tests(path: Path, context: dict[str, Any], /) -> None:
    """Render the lefthook and CI workflow from whole-file templates.

    Both ``lefthook.yml`` and ``.github/workflows/main.yml`` are produced
    from their templates in one pass (hook jobs, the reuse ``fix`` job, the
    single-package ``tests`` job, and the CI pytest steps).

    Args:
        path: Root of the generated project.
        context: Template variables (``package_name``, ``package_env_var``,
            ``use_reuse``, ``use_docs``, ``year``, ``copyright_holder``).
    """
    (path / "lefthook.yml").write_text(
        render_template("root/lefthook.yml.jinja", context)
    )
    (path / ".github" / "workflows" / "main.yml").write_text(
        render_template(
            "github/main.yml.jinja",
            context,
            variable_start_string="[[",
            variable_end_string="]]",
        )
    )
