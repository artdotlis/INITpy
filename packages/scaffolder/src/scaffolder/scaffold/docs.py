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
        context: Template variables (``project_name``, ``package_name``,
            ``copyright_holder``, ``year``).
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

    Deletes ``packages/docs`` and the docs GitHub Actions workflow. The
    docs-conditional wiring in ``package.env``, ``lint_env.sh``,
    ``licenses.sh``, the ``Makefile``, and ``.gitignore`` is already absent
    because those files are rendered from their ``use_docs``-aware templates.

    Args:
        path: Root of the generated project.
    """
    shutil.rmtree(path / "packages" / "docs")
    (path / ".github" / "workflows" / "docs.yml").unlink()
