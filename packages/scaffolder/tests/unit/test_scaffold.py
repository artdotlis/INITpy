# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.files."""

from pathlib import Path

from scaffolder.scaffold.files import write_package_files


class TestWritePackageFiles:
    def test_creates_package_dir(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        assert (tmp_path / "packages" / "my_pkg").is_dir()

    def test_creates_src_dir(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        assert (tmp_path / "packages" / "my_pkg" / "src" / "my_pkg").is_dir()

    def test_creates_main_with_todo(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        main = tmp_path / "packages" / "my_pkg" / "src" / "my_pkg" / "main.py"
        assert main.read_text() == "# TODO: Implement my_pkg\n"

    def test_creates_py_typed(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        assert (tmp_path / "packages" / "my_pkg" / "src" / "my_pkg" / "py.typed").exists()

    def test_creates_init_with_all(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        init = tmp_path / "packages" / "my_pkg" / "src" / "my_pkg" / "__init__.py"
        assert init.read_text() == "__all__: list[str] = []"

    def test_creates_readme_with_name(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        readme = tmp_path / "packages" / "my_pkg" / "README.md"
        assert readme.read_text() == "# my_pkg\n"

    def test_creates_dotenv(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        assert (tmp_path / "packages" / "my_pkg" / ".env").exists()

    def test_creates_tests_directory(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        assert (tmp_path / "packages" / "my_pkg" / "tests" / "unit").is_dir()

    def test_creates_placeholder_test(self, tmp_path: Path) -> None:
        write_package_files(tmp_path, "my_pkg")
        test_file = tmp_path / "packages" / "my_pkg" / "tests" / "unit" / "test_my_pkg.py"
        text = test_file.read_text()
        assert "test_placeholder" in text
        assert "assert False" in text
        assert "TODO" in text
