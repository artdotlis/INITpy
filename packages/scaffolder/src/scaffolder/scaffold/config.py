# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Root project configuration for a generated project."""

from pathlib import Path
from typing import Any

from scaffolder.template import render_template


def correct_core_project(path: Path, root_ctx: dict[str, Any], /) -> None:
    """Render the root config files and JSON metadata from whole-file templates.

    Args:
        path: Root of the generated project.
        root_ctx: Template variables for the root files.
    """
    (path / "pyproject.toml").write_text(
        render_template("root/root.toml.jinja", root_ctx)
    )
    (path / "pnpm-workspace.yaml").write_text(
        render_template("root/pnpm-workspace.yaml.jinja", root_ctx)
    )
    (path / "package.json").write_text(
        render_template("root/package.json.jinja", root_ctx)
    )
    if root_ctx["use_docs"]:
        (path / "packages" / "docs" / "package.json").write_text(
            render_template("docs/package.json.jinja", root_ctx)
        )
    (path / ".devcontainer" / "devcontainer.json").write_text(
        render_template("devcontainer/devcontainer.json.jinja", root_ctx)
    )
    (path / "Makefile").write_text(render_template("root/Makefile.jinja", root_ctx))
    (path / ".gitignore").write_text(render_template("root/gitignore.jinja", root_ctx))
    (path / ".dockerignore").write_text(
        render_template("root/dockerignore.jinja", root_ctx)
    )
    (path / "bin" / "lint" / "licenses.sh").write_text(
        render_template("lint/licenses.sh.jinja", root_ctx)
    )
