# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Common utilities for scaffolder and other automation tools."""

import re
import shutil
import subprocess
from pathlib import Path


def sanitize_package_name(name: str) -> str:
    """Convert project name to valid Python package name.

    Args:
        name: The project name to sanitize

    Returns:
        A valid Python package name (lowercase, underscore-separated,
        no special characters, doesn't start with digit)
    """
    sanitized = name.lower().replace(" ", "_").replace("-", "_")
    sanitized = re.sub(r"[^a-z0-9_]", "", sanitized)
    if sanitized and sanitized[0].isdigit():
        sanitized = "_" + sanitized
    return sanitized or "project"


def clone_template(template_url: str, temp_dir: Path) -> None:
    """Clone a template repository.

    Args:
        template_url: URL of the template repository
        temp_dir: Path where the template should be cloned

    Raises:
        subprocess.CalledProcessError: If git clone fails
    """
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    subprocess.run(
        ["git", "clone", template_url, str(temp_dir)], check=True, capture_output=True
    )


def init_git(project_path: Path) -> None:
    """Initialize git repository in project directory.

    Args:
        project_path: Path to the project directory
    """
    subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)

    subprocess.run(["git", "add", "."], cwd=project_path, check=True, capture_output=True)

    subprocess.run(
        ["git", "commit", "-m", "chore: initial commit from INITpy template"],
        cwd=project_path,
        check=True,
        capture_output=True,
    )


def update_package_imports(
    package_dir: Path, package_name: str, old_name: str = "pkg1"
) -> None:
    """Update import statements in package files.

    Args:
        package_dir: Path to the package directory
        package_name: New package name to use
        old_name: Old package name to replace (default: "pkg1")
    """
    if not package_dir.exists():
        return

    for py_file in package_dir.rglob("*.py"):
        content = py_file.read_text()
        content = content.replace(old_name, package_name)
        py_file.write_text(content)


def update_readme(path: Path, project_name: str) -> None:
    """Update README.md with project-specific values.

    Args:
        path: Path to README.md
        project_name: New project name
    """
    content = path.read_text()

    content = content.replace("INITpy", project_name)
    content = content.replace("artdotlis/INITpy", f"artdotlis/{project_name}")
    content = content.replace("# 🛠️ INITpy", f"# 🛠️ {project_name}")

    path.write_text(content)


# def run_command(
#     cmd: list[str],
#     cwd: Path,
#     capture_output: bool = True,
#     text: bool = True
# ) -> subprocess.CompletedProcess:
#     """Run a command with consistent error handling.
#
#     Args:
#         cmd: Command to run as list of arguments
#         cwd: Working directory
#         capture_output: Whether to capture stdout/stderr
#         text: Whether to return output as text
#
#     Returns:
#         CompletedProcess instance with returncode and output
#
#     Raises:
#         subprocess.CalledProcessError: If command fails
#     """
#     return subprocess.run(
#         cmd,
#         cwd=cwd,
#         capture_output=capture_output,
#         text=text,
#         check=True
#     )


# NOTE: Disabled to fix vulture false positive; re-enable when needed for future extensions
