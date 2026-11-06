# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.skeleton."""

from pathlib import Path

from scaffolder.scaffold.skeleton import write_package_files


class TestWritePackageFiles:
    """Tests for write_package_files."""

    def test_writes_package_skeleton(self, tmp_path: Path) -> None:
        """Write the package layout and its placeholder files."""
        write_package_files(tmp_path, "my_pkg")
        pkg = tmp_path / "packages" / "my_pkg"

        assert (pkg / "src" / "my_pkg").is_dir()
        assert (pkg / "src" / "my_pkg" / "main.py").read_text() == (
            "# TODO: Implement my_pkg\n"
        )
        assert (pkg / "src" / "my_pkg" / "py.typed").exists()
        assert (pkg / "src" / "my_pkg" / "__init__.py").read_text() == (
            "__all__: list[str] = []"
        )
        assert (pkg / "README.md").read_text() == "# my_pkg\n"
        assert (pkg / ".env").exists()
        assert (pkg / "tests" / "unit").is_dir()

        placeholder = (pkg / "tests" / "unit" / "test_my_pkg.py").read_text()
        assert "test_placeholder" in placeholder
        assert "assert False" in placeholder
        assert "TODO" in placeholder
