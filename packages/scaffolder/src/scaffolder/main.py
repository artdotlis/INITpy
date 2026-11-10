# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Scaffolder CLI - generate INITpy-based projects."""

import os
import random
import shutil
import sys
from pathlib import Path

from reuse.project import LICENSE_MAP

from scaffolder.scaffold.core import ScaffoldArgs, run


def _prompt_yes_no(prompt: str, /) -> bool:
    """Prompt until y or n is entered; empty input counts as yes."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return True
        normalized = raw.lower()
        if normalized in ("y", "yes"):
            return True
        if normalized in ("n", "no"):
            return False
        print("❌ Please answer y or n", file=sys.stderr)


def _prompt_project_name() -> str:
    """Prompt for a project name of at least 3 characters."""
    while True:
        project_name = input("Project name: ").strip()
        if len(project_name) >= 3:
            return project_name
        print("❌ Must be at least 3 characters", file=sys.stderr)


def _prompt_non_empty(prompt: str, /) -> str:
    """Prompt until a non-empty value is entered."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("❌ Cannot be empty", file=sys.stderr)


def _prompt_output_dir() -> str:
    """Use SCAF_OUTPUT_DIR when set, else prompt for an output directory."""
    env_output = (os.environ.get("SCAF_OUTPUT_DIR") or "").strip()
    if env_output:
        return env_output
    return _prompt_non_empty("Output directory: ")


def _prompt_license() -> str:
    """Prompt until a valid SPDX license is selected."""
    examples = random.sample(list(LICENSE_MAP.keys()), 6)
    print(f"\nAvailable licenses: {', '.join(examples)}, and more")
    while True:
        license_name = input("License: ").strip()
        if license_name in LICENSE_MAP:
            return license_name
        new_examples = random.sample(list(LICENSE_MAP.keys()), 6)
        print(f"❌ Invalid. Examples: {', '.join(new_examples)}", file=sys.stderr)


def run_cli() -> None:
    """Interactive CLI entry point."""
    print("📦 INITpy Project Scaffolder")
    print("─" * 40)

    project_name = _prompt_project_name()
    project_description = _prompt_non_empty("Project description: ")
    output_dir = _prompt_output_dir()
    author_name = _prompt_non_empty("Author name: ")
    author_email = _prompt_non_empty("Author email: ")
    copyright = _prompt_non_empty("Copyright holder: ")
    license_name = _prompt_license()
    use_reuse = _prompt_yes_no("Use reuse tooling? [Y/n] ")
    use_docs = _prompt_yes_no("Keep docs subpackage? [Y/n] ")

    try:
        result = run(
            ScaffoldArgs(
                project_name=project_name,
                output_dir=output_dir,
                author_name=author_name,
                author_email=author_email,
                license_name=license_name,
                description=project_description,
                copyright=copyright,
                use_reuse=use_reuse,
                use_docs=use_docs,
            )
        )
        print(f"\n✅ '{project_name}' → {result.absolute()}")
    except Exception as exc:
        # clean up any partially scaffolded output, then re-raise
        partial = Path(output_dir) / project_name
        if partial.exists():
            shutil.rmtree(partial) if partial.is_dir() else partial.unlink()
        print(f"❌ {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run_cli()
