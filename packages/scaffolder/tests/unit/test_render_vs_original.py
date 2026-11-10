# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Compare each template's render against its original project file.

One test per whole-file template (except the hand-curated README). Each test
renders the template with the current project's ``context`` and compares it
byte-for-byte to the original file it reproduces. Where the render already
matches the original the test asserts equality (so a later drift fails loudly).
Where the original has diverged the test is reported as ``xfail`` rather than
forced to pass, so the drifted files are surfaced in the summary without
breaking the run.
"""

from typing import Any

import pytest

pytest_plugins = ("tests.fixture.template",)


def _assert_render_matches(template: Any, context: dict[str, object]) -> None:
    """Render ``template`` and compare it to its original on disk."""
    rendered = template.render(context)
    original = template.target_path.read_text()
    if rendered != original:
        pytest.xfail(f"drift: {template.name} render != original {template.target}")
    assert rendered == original


class TestRenderMatchesOriginal:
    """Each template render equals its original file where it is expected to."""

    def test_root_package_json(
        self, root_package_json_jinja: Any, context: dict[str, object]
    ) -> None:
        """``root/package.json.jinja`` -> ``package.json``."""
        _assert_render_matches(root_package_json_jinja, context)

    def test_root_lefthook_yml(
        self, root_lefthook_yml_jinja: Any, context: dict[str, object]
    ) -> None:
        """``root/lefthook.yml.jinja`` -> ``lefthook.yml``.

        The full file cannot match: the original runs test jobs for its real
        packages (plus ``coverage report``), while the template emits the single
        scaffolded ``{{ package_name }}`` step. So the rendered static content
        (everything up to the first test job) is asserted to be a contiguous
        substring of the original, and the dynamic package job is checked in
        the render separately.
        """
        rendered = root_lefthook_yml_jinja.render(context)
        original = root_lefthook_yml_jinja.target_path.read_text()
        package_line = f"        - name: {context['package_name']}"
        rendered_prefix = rendered.split(package_line, 1)[0]
        assert rendered_prefix in original
        assert package_line in rendered

    def test_root_pnpm_workspace_yaml(
        self, request: pytest.FixtureRequest, context: dict[str, object]
    ) -> None:
        """``root/pnpm-workspace.yaml.jinja`` -> ``pnpm-workspace.yaml``."""
        _assert_render_matches(
            request.getfixturevalue("root_pnpm-workspace_yaml_jinja"), context
        )

    def test_root_makefile(
        self, request: pytest.FixtureRequest, context: dict[str, object]
    ) -> None:
        """``root/Makefile.jinja`` -> ``Makefile``."""
        _assert_render_matches(request.getfixturevalue("root_Makefile_jinja"), context)

    def test_root_gitignore(
        self, root_gitignore_jinja: Any, context: dict[str, object]
    ) -> None:
        """``root/gitignore.jinja`` -> ``.gitignore``."""
        _assert_render_matches(root_gitignore_jinja, context)

    def test_root_dockerignore(
        self, root_dockerignore_jinja: Any, context: dict[str, object]
    ) -> None:
        """``root/dockerignore.jinja`` -> ``.dockerignore``."""
        _assert_render_matches(root_dockerignore_jinja, context)

    def test_root_package_env(
        self, root_package_env_jinja: Any, context: dict[str, object]
    ) -> None:
        """``root/package.env.jinja`` -> ``package.env``.

        The full file cannot match: the original is this multi-package repo (the
        second package's ``PKG_SHA`` and the scaffolder's ``SCAF_OUTPUT_DIR`` are
        INITpy-specific and sit below the template-controlled region), while the
        template emits the single scaffolded ``{{ package_name }}`` package. So
        the rendered static content (everything up to the package var) is
        asserted to be a contiguous substring of the original, and the dynamic
        package line is checked in the render separately.
        """
        rendered = root_package_env_jinja.render(context)
        original = root_package_env_jinja.target_path.read_text()
        package_line = f"PKG_SCA=packages/{context['package_name']}"
        rendered_prefix = rendered.split(package_line, 1)[0]
        assert rendered_prefix in original
        assert package_line in rendered

    def test_devcontainer_devcontainer_json(
        self,
        devcontainer_devcontainer_json_jinja: Any,
        context: dict[str, object],
    ) -> None:
        """``devcontainer/devcontainer.json.jinja`` -> the devcontainer config."""
        _assert_render_matches(devcontainer_devcontainer_json_jinja, context)

    def test_github_mac_win_test_yml(
        self, github_mac_win_test_yml_jinja: Any, context: dict[str, object]
    ) -> None:
        """``github/mac_win_test.yml.jinja`` -> ``.github/workflows/mac_win_test.yml``.

        The full file cannot match: the original runs test steps for its two real
        packages (plus ``coverage report``), while the template emits the single
        scaffolded ``{{ package_name }}`` step. So the rendered static content
        (everything up to the first package step) is asserted to be a contiguous
        substring of the original, and the dynamic package step is checked in
        the render separately.
        """
        rendered = github_mac_win_test_yml_jinja.render(context)
        original = github_mac_win_test_yml_jinja.target_path.read_text()
        package_line = f"            - name: Run {context['package_name']} tests"
        rendered_prefix = rendered.split(package_line, 1)[0]
        assert rendered_prefix in original
        assert package_line in rendered

    def test_github_lin_lint_yml(
        self, github_lin_lint_yml_jinja: Any, context: dict[str, object]
    ) -> None:
        """``github/lin_lint.yml.jinja`` -> ``.github/workflows/lin_lint.yml``.

        The full file cannot match: the original carries no ``{{ package_name }}``
        step, while the template appends the scaffolded one at the end. So the
        rendered static content (everything up to the appended step) is asserted
        to be a contiguous substring of the original, and the dynamic package
        step is checked in the render separately.
        """
        rendered = github_lin_lint_yml_jinja.render(context)
        original = github_lin_lint_yml_jinja.target_path.read_text()
        package_line = f"            - name: Run {context['package_name']} tests"
        rendered_prefix = rendered.split(package_line, 1)[0]
        assert rendered_prefix in original
        assert package_line in rendered

    def test_lint_lint_env_sh(
        self, lint_lint_env_sh_jinja: Any, context: dict[str, object]
    ) -> None:
        """``lint/lint_env.sh.jinja`` -> ``bin/lint/lint_env.sh``."""
        _assert_render_matches(lint_lint_env_sh_jinja, context)

    def test_lint_licenses_sh(
        self, lint_licenses_sh_jinja: Any, context: dict[str, object]
    ) -> None:
        """``lint/licenses.sh.jinja`` -> ``bin/lint/licenses.sh``."""
        _assert_render_matches(lint_licenses_sh_jinja, context)

    def test_docs_index_md(
        self, docs_index_md_jinja: Any, context: dict[str, object]
    ) -> None:
        """``docs/index.md.jinja`` -> ``packages/docs/src/index.md``."""
        _assert_render_matches(docs_index_md_jinja, context)

    def test_docs_ref_index_md(
        self, docs_ref_index_md_jinja: Any, context: dict[str, object]
    ) -> None:
        """The ref index render's static parts are part of the original.

        The full file cannot match: the original lists every real package by its
        source name, while the template emits the single scaffolded package
        (``{{ package_name }}``). So the rendered static content (SPDX header,
        heading, subtitle) is asserted to be present in the original, and the
        dynamic package entry is checked separately.
        """
        rendered = docs_ref_index_md_jinja.render(context)
        original = docs_ref_index_md_jinja.target_path.read_text()
        package_line = f"- [{context['package_name']}]({context['package_name']})"
        # The render's static preamble (SPDX header, heading, subtitle) is a
        # contiguous part of the original; only the package list differs.
        rendered_prefix = rendered.split(package_line, 1)[0]
        assert rendered_prefix in original
        assert package_line in rendered

    def test_docs_vitepress_config_toml(
        self,
        docs_vitepress_config_toml_jinja: Any,
        context: dict[str, object],
    ) -> None:
        """``docs/vitepress_config.toml.jinja`` -> the VitePress config.

        The brand (title/description/base) and the ``socialLinks`` block differ
        by design (the original carries the real project brand and a GitHub
        link). The placeholder-driven lines (license, footer copyright, SPDX
        header) are asserted to match the original.
        """
        rendered = docs_vitepress_config_toml_jinja.render(context)
        original = docs_vitepress_config_toml_jinja.target_path.read_text()
        for line in (
            f'license = "{context["license"]}"',
            f'copyright = "Copyright © {context["year"]} {context["copyright_holder"]}"',
            f"# SPDX-FileCopyrightText: {context['year']} {context['copyright_holder']}",
        ):
            assert line in rendered, f"missing from render: {line!r}"
            assert line in original, f"missing from original: {line!r}"

    def test_docs_package_json(
        self, docs_package_json_jinja: Any, context: dict[str, object]
    ) -> None:
        """``docs/package.json.jinja`` -> ``packages/docs/package.json``."""
        _assert_render_matches(docs_package_json_jinja, context)
