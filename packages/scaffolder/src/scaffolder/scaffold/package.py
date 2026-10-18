# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Package creation and file generation for scaffolding."""

import shutil

from pathlib import Path

from shared_utils.files import update_pyproject_authors


def create(
    path: Path,
    package_name: str,
    author_name: str,
    author_email: str,
) -> None:
    """Steps 3-5: create new package, copy pyproject.toml, clean packages/."""
    pkg_dir = path / "packages" / package_name
    (pkg_dir / "src" / package_name).mkdir(parents=True, exist_ok=True)
    shutil.copy2(
        Path(__file__).resolve().parent.parent.parent / "shared_utils" / "pyproject.toml",
        pkg_dir / "pyproject.toml",
    )
    for item in (path / "packages").iterdir():
        if item.name not in ("docs", package_name):
            shutil.rmtree(item) if item.is_dir() else item.unlink()

    # Update author info in pyproject.toml
    update_pyproject_authors(pkg_dir / "pyproject.toml", author_name, author_email)


def write_files(path: Path, package_name: str) -> None:
    """Steps 6-8: create main.py, py.typed, .env, README, test."""
    pkg_dir = path / "packages" / package_name
    src = pkg_dir / "src" / package_name

    (src / "main.py").write_text(
        f'"""{package_name} package."""\n\ndef main() -> None:\n'
        f'    """TODO: Implement {package_name} entry point."""\n    pass\n'
    )
    (src / "py.typed").touch()
    (src / "__init__.py").write_text("")
    (pkg_dir / ".env").write_text("")
    (pkg_dir / "README.md").write_text(f"# {package_name}\n\n")

    # Step 8 - template test
    tests = pkg_dir / "tests"
    tests.mkdir(exist_ok=True)
    (tests / "__init__.py").write_text("")
    (tests / f"test_{package_name}.py").write_text(
        f'"""TODO: Write unit tests for {package_name}."""\nimport pytest\n'
    )
