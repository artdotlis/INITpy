# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.env."""

from pathlib import Path

from scaffolder.scaffold.env import update_copyright, update_envs

pytest_plugins = ("tests.fixture.template",)


class TestUpdateCopyright:
    """Tests for update_copyright."""

    def test_updates_package_env(self, tmp_path: Path, package_env: Path) -> None:
        """Replace the COPYRIGHT value in package.env."""
        update_copyright(tmp_path, "New Owner")
        content = package_env.read_text()
        assert 'COPYRIGHT="New Owner"' in content
        assert "Artur Lissin" not in content
        assert "PYV=" in content


class TestUpdateEnvs:
    """Tests for update_envs (run against live template files)."""

    def test_repoints_env_files(
        self, tmp_path: Path, package_env: Path, lint_env_sh: Path
    ) -> None:
        """Repoint package.env and the lint script at the new package."""
        update_envs(tmp_path, "my_pkg")

        content = package_env.read_text()
        assert "PKG_MY_" in content  # first 3 chars of "MY_PKG" are "MY_"
        assert "PKG_SHAR" not in content

        lint_env = lint_env_sh.read_text()
        assert "$SCAF_ENV" not in lint_env
        assert "MY__ENV" in lint_env
