# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Scaffolder CLI - generate INITpy-based projects."""

from scaffolder.scaffold.core import ScaffoldArgs, run
import os
import random
import sys

from reuse.project import LICENSE_MAP


def _prompt_use_reuse() -> bool:
    """Ask whether to keep reuse tooling; default yes (empty = y)."""
    while True:
        raw = input("Use reuse tooling? [Y/n] ").strip()
        if raw == "":
            return True
        normalization = raw.lower()
        if normalization in ("y", "yes"):
            return True
        if normalization in ("n", "no"):
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
    use_reuse = _prompt_use_reuse()

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
            )
        )
        print(f"\n✅ '{project_name}' → {result.absolute()}")
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run_cli()
