# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.env."""

from pathlib import Path

from scaffolder.scaffold.env import update_envs

pytest_plugins = ("tests.fixture.template",)


class TestUpdateEnvs:
    """Tests for update_envs (renders the env files from whole-file templates)."""

    def test_renders_env_files(self, tmp_path: Path, context: dict[str, object]) -> None:
        """Write package.env and the lint script for the new package."""
        (tmp_path / "bin" / "lint").mkdir(parents=True)
        update_envs(tmp_path, str(context["package_name"]), context)

        env = (tmp_path / "package.env").read_text()
        assert f"{context['package_env_var']}=packages/{context['package_name']}" in env
        assert f"{context['package_env_file']}=packages/{context['package_name']}" in env
        assert f'COPYRIGHT="{context["copyright_holder"]}"' in env

        lint_env = (tmp_path / "bin" / "lint" / "lint_env.sh").read_text()
        assert f'"${context["package_env_file"]}"' in lint_env

    def test_no_docs_drops_docs_env(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Omit the docs env wiring when docs are dropped."""
        (tmp_path / "bin" / "lint").mkdir(parents=True)
        update_envs(tmp_path, str(context["package_name"]), dict(context, use_docs=False))
        assert "DOC_ENV" not in (tmp_path / "package.env").read_text()
