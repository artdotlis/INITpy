#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Project Template Generator
Automates the creation of new Python projects from the INITpy template.
"""

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


class ProjectGenerator:
    """Generate new projects from the INITpy template."""

    def __init__(self, template_path: str = "https://github.com/artdotlis/INITpy.git"):
        self.template_path = template_path
        self.temp_dir = Path("/tmp/initpy_template")

    def update_pyproject_toml(
        self,
        path: Path,
        project_name: str,
        package_name: str,
        author_name: str,
        author_email: str,
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
            r'"packages/shared_utils/src"',
            f'"packages/{package_name}_utils/src"',
            content,
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
        self,
        project_name: str,
        output_dir: str = ".",
        author_name: str = "Default Author",
        author_email: str = "author@example.com",
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
        clone_template(self.template_path, self.temp_dir)

        # Create project directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Copy template files (excluding .git)
        for item in self.temp_dir.iterdir():
            if item.name == ".git":
                continue

            dest = output_path / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        # Update configuration files
        self.update_pyproject_toml(
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

        return output_path

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(
            "Usage: python create-project.py <project-name> [author-name] [author-email]"
        )
        print("Example: python create-project.py my-app 'John Doe' 'john@example.com'")
        sys.exit(1)

    project_name = sys.argv[1]
    author_name = sys.argv[2] if len(sys.argv) > 2 else "Default Author"
    author_email = sys.argv[3] if len(sys.argv) > 3 else "author@example.com"

    generator = ProjectGenerator()

    try:
        project_path = generator.create_project(
            project_name, author_name=author_name, author_email=author_email
        )

        print(f"\n✅ Project '{project_name}' created successfully!")
        print(f"📁 Location: {project_path.absolute()}")
        print("\nNext steps:")
        print(f"  cd {project_path.name}")
        print("  devcontainer up --workspace-folder .")
        print("  devcontainer exec --workspace-folder . make dev")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        generator.cleanup()


if __name__ == "__main__":
    main()
