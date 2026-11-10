# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for the per-template fixtures.

Every shipped ``.jinja`` template is exposed as its own fixture function
(``a/b.toml.jinja`` -> ``a_b_toml_jinja``). Each of those fixtures is resolved
by name and the ``Template`` it yields is loaded (read + compiled from the
templates directory) to prove the template file is present and well-formed.
"""

import pytest
from jinja2 import Template as JinjaTemplate

pytest_plugins = ("tests.fixture.template",)

# Every shipped template, listed by the path the fixtures are named after.
TEMPLATE_PATHS = [
    "root/root.toml.jinja",
    "root/package.json.jinja",
    "root/lefthook.yml.jinja",
    "root/pnpm-workspace.yaml.jinja",
    "root/Makefile.jinja",
    "root/gitignore.jinja",
    "root/dockerignore.jinja",
    "root/package.env.jinja",
    "root/README.md.jinja",
    "root/package.toml.jinja",
    "devcontainer/devcontainer.json.jinja",
    "github/mac_win_test.yml.jinja",
    "github/lin_lint.yml.jinja",
    "lint/lint_env.sh.jinja",
    "lint/licenses.sh.jinja",
    "docs/index.md.jinja",
    "docs/ref_index.md.jinja",
    "docs/vitepress_config.toml.jinja",
    "docs/package.json.jinja",
]


def _fixture_name(path: str) -> str:
    """Fixture function name for a template path (same mapping the module uses)."""
    return path.replace("/", "_").replace(".", "_")


@pytest.mark.parametrize("path", TEMPLATE_PATHS)
def test_template_fixture_loads(request: pytest.FixtureRequest, path: str) -> None:
    """The per-template fixture resolves and its template file loads."""
    template = request.getfixturevalue(_fixture_name(path))
    # Load reads + compiles the source; raises if the file is missing or malformed.
    jinja_template = template.load()
    assert template.path.is_file()
    assert isinstance(jinja_template, JinjaTemplate)
    assert jinja_template.name == template.name
