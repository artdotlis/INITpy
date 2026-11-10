# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Docs (VitePress) amendment and removal for a generated project."""

import shutil
from pathlib import Path
from typing import Any

from scaffolder.template import render_template


def amend_docs(path: Path, context: dict[str, Any], /) -> None:
    """Render the docs index, module reference, and VitePress config.

    Args:
        path: Root of the generated project.
        context: Template variables.
    """
    (path / "packages" / "docs" / "src" / "index.md").write_text(
        render_template("docs/index.md.jinja", context)
    )
    (path / "packages" / "docs" / "src" / "ref" / "index.md").write_text(
        render_template("docs/ref_index.md.jinja", context)
    )
    (path / "packages" / "docs" / ".vitepress" / "config.toml").write_text(
        render_template("docs/vitepress_config.toml.jinja", context)
    )


def remove_docs(path: Path, /) -> None:
    """Remove the ``docs`` subpackage and its workflow.

    Args:
        path: Root of the generated project.

    Raises:
        FileNotFoundError: If the docs package or workflow file is absent.
    """
    docs_dir = path / "packages" / "docs"
    if not docs_dir.is_dir():
        raise FileNotFoundError(f"docs package missing: {docs_dir}")
    shutil.rmtree(docs_dir)

    docs_yml = path / ".github" / "workflows" / "docs.yml"
    if not docs_yml.is_file():
        raise FileNotFoundError(f"docs workflow missing: {docs_yml}")
    docs_yml.unlink()
