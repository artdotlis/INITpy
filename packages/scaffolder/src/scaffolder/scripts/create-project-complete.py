#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Template Project Creator
Creates new Python projects from the INITpy template with full automation.
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
    update_package_imports,
    update_readme as common_update_readme,
)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Create new Python project from INITpy template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my-api
  %(prog)s my-api --author "John Doe" --email "john@example.com"
  %(prog)s my-api --output ./projects --no-git
        """,
    )

    parser.add_argument("name", help="Project name")
    parser.add_argument(
        "--author",
        "-a",
        default="Default Author",
        help="Author name (default: 'Default Author')",
    )
    parser.add_argument(
        "--email",
        "-e",
        default="author@example.com",
        help="Author email (default: 'author@example.com')",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument("--no-git", action="store_true", help="Skip git initialization")
    parser.add_argument(
        "--no-tests", action="store_true", help="Skip test directory creation"
    )

    return parser.parse_args()


def update_pyproject_toml(
    path: Path, project_name: str, package_name: str, author_name: str, author_email: str
) -> None:
    """Update pyproject.toml with project-specific values."""
    content = path.read_text()

    # Update basic project info
    content = re.sub(r'name = "initpy"', f'name = "{package_name}"', content)
    content = re.sub(r'version = "[^"]+"', 'version = "0.1.0"', content)
    content = re.sub(r'email = "[^"]+"', f'email = "{author_email}"', content)
    content = re.sub(
        r'name = "[^"]+", email = "', f'name = "{author_name}", email = "', content
    )

    # Update package references in workspace
    content = re.sub(
        r'"scaffolder" = \{ workspace = true \}',
        f'"{package_name}" = {{ workspace = true }}',
        content,
    )
    content = re.sub(
        r'"shared_utils" = \{ workspace = true \}',
        f'"{package_name}_utils" = {{ workspace = true }}',
        content,
    )

    # Update commitizen version_files
    content = re.sub(
        r'"packages/scaffolder/pyproject\.toml"',
        f'"packages/{package_name}/pyproject.toml"',
        content,
    )
    content = re.sub(
        r'"packages/shared_utils/pyproject\.toml"',
        f'"packages/{package_name}_utils/pyproject.toml"',
        content,
    )

    # Update project-includes in pyrefly
    content = re.sub(
        r'"packages/scaffolder/src"', f'"packages/{package_name}/src"', content
    )
    content = re.sub(
        r'"packages/shared_utils/src"', f'"packages/{package_name}_utils/src"', content
    )

    # Update source paths in coverage
    content = re.sub(
        r'"packages/scaffolder/src/scaffolder"',
        f'"packages/{package_name}/src/{package_name}"',
        content,
    )
    content = re.sub(
        r'"packages/shared_utils/src/shared_utils"',
        f'"packages/{package_name}_utils/src/{package_name}_utils"',
        content,
    )

    path.write_text(content)


def create_project(
    project_name: str,
    output_dir: str = ".",
    author_name: str = "Default Author",
    author_email: str = "author@example.com",
    skip_git: bool = False,
    skip_tests: bool = False,
) -> Path:
    """Create a new project from the template."""
    # Validate inputs
    if not project_name:
        raise ValueError("Project name cannot be empty")

    package_name = sanitize_package_name(project_name)
    output_path = Path(output_dir) / project_name

    if output_path.exists():
        raise FileExistsError(f"Project directory already exists: {output_path}")

    print(f"Creating project '{project_name}' (package: '{package_name}')...")

    # Clone template
    temp_dir = Path("/tmp/initpy_template")
    clone_template("https://github.com/artdotlis/INITpy.git", temp_dir)

    # Create project directory
    output_path.mkdir(parents=True, exist_ok=True)

    # Copy template files (excluding .git)
    for item in temp_dir.iterdir():
        if item.name == ".git":
            continue

        dest = output_path / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Update configuration files
    update_pyproject_toml(
        output_path / "pyproject.toml",
        project_name,
        package_name,
        author_name,
        author_email,
    )

    common_update_readme(output_path / "README.md", project_name)

    # Rename package directories
    (output_path / "packages" / "scaffolder").rename(
        output_path / "packages" / package_name
    )
    (output_path / "packages" / "shared_utils").rename(
        output_path / "packages" / f"{package_name}_utils"
    )

    # Update imports in package files
    update_package_imports(output_path / "packages" / package_name, package_name)
    update_package_imports(
        output_path / "packages" / f"{package_name}_utils",
        f"{package_name}_utils",
        "shared_utils",
    )

    # Initialize git repository
    if not skip_git:
        subprocess.run(["git", "init"], cwd=output_path, check=True, capture_output=True)

        # Initial commit
        subprocess.run(
            ["git", "add", "."], cwd=output_path, check=True, capture_output=True
        )

        subprocess.run(
            ["git", "commit", "-m", "chore: initial commit from INITpy template"],
            cwd=output_path,
            check=True,
            capture_output=True,
        )

    # Clean up temp directory
    shutil.rmtree(temp_dir)

    return output_path


def main():
    """Main entry point."""
    args = parse_args()

    try:
        project_path = create_project(
            args.name,
            output_dir=args.output,
            author_name=args.author,
            author_email=args.email,
            skip_git=args.no_git,
            skip_tests=args.no_tests,
        )

        print(f"\n✅ Project '{args.name}' created successfully!")
        print(f"📁 Location: {project_path.absolute()}")
        print("\nNext steps:")
        print(f"  cd {project_path.name}")
        print("  devcontainer up --workspace-folder .")
        print("  devcontainer exec --workspace-folder . make dev")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
