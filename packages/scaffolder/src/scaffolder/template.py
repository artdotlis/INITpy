# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Jinja template rendering for scaffolded config files."""

from pathlib import Path
from typing import Any

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import StrictUndefined

# templates/ lives next to the scaffolder package (src/scaffolder/templates)
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def render_template(
    template_name: str,
    context: dict[str, Any],
    /,
    variable_start_string: str = "{{",
    variable_end_string: str = "}}",
) -> str:
    """Render a scaffolded config template to its full target content.

    Args:
        template_name: Name of the template relative to ``templates/``,
            e.g. ``pyproject/root.toml.jinja``.
        context: Variables passed to the template. Undefined variables
            raise (StrictUndefined) so missing context fails loudly.
        variable_start_string: Jinja variable open delimiter. Defaults to
            ``{{``; use a non-colliding pair (e.g. ``[[`` / ``]]``) for
            files that already contain ``{{ }}`` (GitHub Actions).
        variable_end_string: Jinja variable close delimiter.

    Returns:
        The fully rendered file content.
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        undefined=StrictUndefined,
        variable_start_string=variable_start_string,
        variable_end_string=variable_end_string,
    )
    return env.get_template(template_name).render(**context)
