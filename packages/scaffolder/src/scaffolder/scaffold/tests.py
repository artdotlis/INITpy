# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Test wiring (lefthook + CI) for a generated project."""

from pathlib import Path
from typing import Any

from scaffolder.template import render_template

# CI workflow templates; the target filename is the template stem.
_CI_WORKFLOWS = ("github/mac_win_test.yml.jinja", "github/lin_lint.yml.jinja")


def update_tests(path: Path, context: dict[str, Any], /) -> None:
    """Render the lefthook and CI workflows from whole-file templates.

    ``lefthook.yml`` and the two CI workflow files
    (``.github/workflows/mac_win_test.yml`` and
    ``.github/workflows/lin_lint.yml``) are produced from their templates in one
    pass (hook jobs, the reuse ``fix`` job, the single-package ``tests`` job,
    and the CI pytest steps).

    Args:
        path: Root of the generated project.
        context: Template variables (``package_name``, ``package_env_var``,
            ``use_reuse``, ``use_docs``, ``year``, ``copyright_holder``).
    """
    (path / "lefthook.yml").write_text(
        render_template("root/lefthook.yml.jinja", context)
    )
    for template in _CI_WORKFLOWS:
        name = template.rsplit("/", 1)[-1].removesuffix(".jinja")
        (path / ".github" / "workflows" / name).write_text(
            render_template(
                template,
                context,
                variable_start_string="[[",
                variable_end_string="]]",
            )
        )
