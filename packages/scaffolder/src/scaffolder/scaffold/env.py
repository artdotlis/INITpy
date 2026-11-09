# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Environment variable updates for a generated project."""

from pathlib import Path
from typing import Any

from scaffolder.template import render_template


def update_envs(path: Path, package_name: str, context: dict[str, Any], /) -> None:
    """Render the root ``package.env`` and ``bin/lint/lint_env.sh``.

    Both files are whole-file templates keyed on the package name and the
    ``use_docs`` flag, so the docs-conditional wiring is produced in one
    pass instead of string edits.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
        context: Template variables (``package_env_var``,
            ``package_env_file``, ``copyright_holder``, ``year``,
            ``use_docs``).
    """
    (path / "package.env").write_text(render_template("root/package.env.jinja", context))
    (path / "bin" / "lint" / "lint_env.sh").write_text(
        render_template("lint/lint_env.sh.jinja", context)
    )
