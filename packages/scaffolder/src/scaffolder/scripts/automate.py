#!/usr/bin/env python3
"""Comprehensive Project Automation Suite
Handles project creation, CI/CD setup, and lifecycle management.
"""

import argparse
import re
import sys
import shutil
from pathlib import Path
import subprocess

from shared_utils.common import (
    sanitize_package_name,
    clone_template,
    init_git,
    update_package_imports,
    update_readme as common_update_readme,
)


class ProjectCreator:
    """Handles project creation from template."""

    def __init__(self, template_url: str = "https://github.com/artdotlis/INITpy.git"):
        self.template_url = template_url
        self.temp_dir = Path("/tmp/initpy_template")

    def create(
        self,
        name: str,
        output_dir: Path = Path(),
        author: str = "Default Author",
        email: str = "author@example.com",
        no_git: bool = False,
        no_tests: bool = False,
    ) -> Path:
        """Create a new project from the template."""
        # Sanitize name
        package_name = sanitize_package_name(name)

        # Create paths
        project_path = output_dir / name

        if project_path.exists():
            raise FileExistsError(f"Project already exists: {project_path}")

        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"Creating '{name}' (package: '{package_name}')...")

        # Clone template
        clone_template(self.template_url, self.temp_dir)

        try:
            # Copy template
            self._copy_template(self.temp_dir, project_path)

            # Update configurations
            self._update_pyproject(
                project_path / "pyproject.toml", name, package_name, author, email
            )

            self._update_readme(project_path / "README.md", name)

            # Create package structure
            self._setup_packages(project_path, package_name, not no_tests)

            # Initialize git
            if not no_git:
                init_git(project_path)

            # Clean up
            shutil.rmtree(self.temp_dir)

            return project_path

        except Exception as e:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            raise e

    def _copy_template(self, source: Path, dest: Path) -> None:
        """Copy template files to project directory."""
        dest.mkdir(parents=True, exist_ok=True)

        for item in source.iterdir():
            if item.name == ".git":
                continue

            dest_item = dest / item.name
            if item.is_dir():
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)

    def _update_pyproject(
        self, path: Path, project_name: str, package_name: str, author: str, email: str
    ) -> None:
        """Update pyproject.toml with project-specific values."""
        content = path.read_text()

        # Update project info
        content = re.sub(r'name = "initpy"', f'name = "{package_name}"', content)
        content = re.sub(r'version = "[^"]+"', 'version = "0.1.0"', content)
        content = re.sub(r'(email = ")[^"]+(")', rf"\g<1>{email}\g<2>", content)
        content = re.sub(
            r'(name = ")[^"]+(", email = ")', rf"\g<1>{author}\g<2>", content
        )

        # Update package references
        content = re.sub(
            r'"pkg1" = \{ workspace = true \}',
            f'"{package_name}" = {{ workspace = true }}',
            content,
        )
        content = re.sub(
            r'"shared_utils" = \{ workspace = true \}',
            f'"{package_name}_utils" = {{ workspace = true }}',
            content,
        )

        # Update commitizen version files
        content = re.sub(
            r'"packages/pkg1/pyproject\.toml"',
            f'"packages/{package_name}/pyproject.toml"',
            content,
        )
        content = re.sub(
            r'"packages/shared_utils/pyproject\.toml"',
            f'"packages/{package_name}_utils/pyproject.toml"',
            content,
        )

        # Update pyrefly paths
        content = re.sub(
            r'"packages/pkg1/src"', f'"packages/{package_name}/src"', content
        )
        content = re.sub(
            r'"packages/shared_utils/src"',
            f'"packages/{package_name}_utils/src"',
            content,
        )

        # Update coverage paths
        content = re.sub(
            r'"packages/pkg1/src/pkg1"',
            f'"packages/{package_name}/src/{package_name}"',
            content,
        )
        content = re.sub(
            r'"packages/shared_utils/src/shared_utils"',
            f'"packages/{package_name}_utils/src/{package_name}_utils"',
            content,
        )

        path.write_text(content)

    def _update_readme(self, path: Path, project_name: str) -> None:
        """Update README.md with project-specific values."""
        common_update_readme(path, project_name)

    def _setup_packages(
        self, project_path: Path, package_name: str, create_tests: bool = True
    ) -> None:
        """Setup package directories and files."""
        packages_dir = project_path / "packages"

        # Rename packages
        (packages_dir / "pkg1").rename(packages_dir / package_name)
        (packages_dir / "shared_utils").rename(packages_dir / f"{package_name}_utils")

        # Update imports
        for pkg_dir in [
            packages_dir / package_name,
            packages_dir / f"{package_name}_utils",
        ]:
            update_package_imports(pkg_dir, package_name)

            # Create test directory if requested
            if create_tests:
                tests_dir = pkg_dir / "tests"
                tests_dir.mkdir(exist_ok=True)
                (tests_dir / "__init__.py").touch()


class ProjectAutomator:
    """Handles project lifecycle automation."""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)

    def run_checks(self) -> bool:
        """Run all quality checks."""
        checks = [
            ("Ruff", ["uv", "run", "ruff", "check", "."]),
            ("Pyrefly", ["uv", "run", "pyrefly", "."]),
            ("Tox", ["uv", "run", "tox"]),
        ]

        for name, cmd in checks:
            print(f"Running {name}...")
            result = subprocess.run(
                cmd, cwd=self.project_path, capture_output=True, text=True
            )

            if result.returncode != 0:
                print(f"❌ {name} failed:")
                print(result.stderr)
                return False

            print(f"✅ {name} passed")

        return True

    def build_package(self) -> bool:
        """Build the package."""
        result = subprocess.run(
            ["uv", "build"], cwd=self.project_path, capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"❌ Build failed: {result.stderr}")
            return False

        print("✅ Build successful")
        return True

    def generate_docs(self) -> bool:
        """Generate documentation."""
        result = subprocess.run(
            ["uv", "run", "zensical", "build"],
            cwd=self.project_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ Documentation build failed: {result.stderr}")
            return False

        print("✅ Documentation generated")
        return True

    def setup_ci(self) -> None:
        """Set up CI/CD workflows."""
        workflows_dir = self.project_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Generate workflows
        self._write_workflow(workflows_dir / "main.yml", self._get_ci_workflow())

        self._write_workflow(workflows_dir / "docs.yml", self._get_docs_workflow())

        self._write_workflow(workflows_dir / "release.yml", self._get_release_workflow())

        print("✅ CI/CD workflows generated")

    def _write_workflow(self, path: Path, content: str) -> None:
        """Write workflow file."""
        path.write_text(content)

    def _get_ci_workflow(self) -> str:
        """Get CI workflow content."""
        return """# SPDX-FileCopyrightText: 2026 Artur Lissin

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: CC0-1.0
# SPDX-License-Identifier: Unlicense

name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: '3.13'
      - name: Install uv
        run: |
          python -m pip install --upgrade pip
          pip install uv
      - name: Install dependencies
        run: uv sync --frozen --group test
      - name: Run tests
        run: uv run tox -e py

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: '3.13'
      - name: Install uv
        run: |
          python -m pip install --upgrade pip
          pip install uv
      - name: Run linters
        run: |
          uv sync --frozen
          uv run ruff check .
          uv run pyrefly .
"""

    def _get_docs_workflow(self) -> str:
        """Get docs deployment workflow."""
        return """# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: CC0-1.0

name: Deploy Documentation

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: '3.13'
      - name: Install uv
        run: |
          python -m pip install --upgrade pip
          pip install uv
      - name: Build docs
        run: uv run zensical build
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v5
        with:
          path: ./public/docs

  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v5
"""

    def _get_release_workflow(self) -> str:
        """Get release workflow."""
        return """# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: CC0-1.0

name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0

      - name: Get version
        id: get_version
        run: |
          VERSION=$(grep '^version' pyproject.toml | cut -d '"' -f2)
          echo "version=$VERSION" >> $GITHUB_OUTPUT

      - name: Create tag
        run: |
          TAG="v${{ steps.get_version.outputs.version }}"
          git config user.name "github-actions[bot]"
          git tag "$TAG"
          git push origin "$TAG"
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Project automation suite for INITpy-based projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create a new project
  %(prog)s create my-api --author "John Doe" --email "john@example.com"

  # Run quality checks
  %(prog)s checks

  # Build package
  %(prog)s build

  # Setup CI/CD
  %(prog)s setup-ci
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--author", "-a", default="Default Author")
    create_parser.add_argument("--email", "-e", default="author@example.com")
    create_parser.add_argument("--output", "-o", default=".")
    create_parser.add_argument("--no-git", action="store_true")
    create_parser.add_argument("--no-tests", action="store_true")

    # Checks command
    subparsers.add_parser("checks", help="Run quality checks")

    # Build command
    subparsers.add_parser("build", help="Build package")

    # Docs command
    subparsers.add_parser("docs", help="Generate documentation")

    # Setup CI command
    subparsers.add_parser("setup-ci", help="Setup CI/CD workflows")

    # Setup release command
    subparsers.add_parser("setup-release", help="Setup release automation")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "create":
        creator = ProjectCreator()

        try:
            project_path = creator.create(
                args.name,
                Path(args.output),
                args.author,
                args.email,
                args.no_git,
                args.no_tests,
            )

            print("\n" + "=" * 50)
            print("✅ Project created successfully!")
            print("=" * 50)
            print(f"📁 Location: {project_path.absolute()}")
            print(f"📦 Package: {args.name.lower().replace(' ', '_')}")

        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

    elif args.command == "checks":
        automator = ProjectAutomator(Path())
        if not automator.run_checks():
            sys.exit(1)

    elif args.command == "build":
        automator = ProjectAutomator(Path())
        if not automator.build_package():
            sys.exit(1)

    elif args.command == "docs":
        automator = ProjectAutomator(Path())
        if not automator.generate_docs():
            sys.exit(1)

    elif args.command == "setup-ci":
        automator = ProjectAutomator(Path())
        automator.setup_ci()

    elif args.command == "setup-release":
        print("Release automation setup coming soon!")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
