# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.tests."""

from pathlib import Path

from scaffolder.scaffold.tests import update_tests

pytest_plugins = ("tests.fixture.template",)


class TestUpdateTests:
    """Tests for update_tests (renders lefthook + CI from whole-file templates)."""

    def test_renders_lefthook_and_ci(
        self, tmp_path: Path, context: dict[str, object]
    ) -> None:
        """Point the hook and CI at the single package."""
        (tmp_path / ".github" / "workflows").mkdir(parents=True)
        update_tests(tmp_path, context)

        hooks = (tmp_path / "lefthook.yml").read_text()
        assert f"name: {context['package_name']}" in hooks
        assert f"cd ${context['package_env_var']} && coverage run -m pytest" in hooks

        ci = (tmp_path / ".github" / "workflows" / "mac_win_test.yml").read_text()
        assert f"packages/{context['package_name']}" in ci
        assert "uv run coverage run -m pytest" in ci
        assert (tmp_path / ".github" / "workflows" / "lin_lint.yml").is_file()
