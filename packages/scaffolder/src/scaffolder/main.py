# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Scaffolder CLI - generate INITpy-based projects."""

from scaffolder.scaffold.core import run
import random
import sys

from reuse.project import LICENSE_MAP


def run_cli() -> None:
    """Interactive CLI entry point."""
    print("📦 INITpy Project Scaffolder")
    print("─" * 40)

    while True:
        project_name = input("Project name: ").strip()
        if len(project_name) >= 3:
            break
        print("❌ Must be at least 3 characters", file=sys.stderr)

    while True:
        project_description = input("Project description: ").strip()
        if project_description:
            break
        print("❌ Cannot be empty", file=sys.stderr)

    while True:
        output_dir = input("Output directory: ").strip()
        if output_dir:
            break
        print("❌ Cannot be empty", file=sys.stderr)

    while True:
        author_name = input("Author name: ").strip()
        if author_name:
            break
        print("❌ Cannot be empty", file=sys.stderr)

    while True:
        author_email = input("Author email: ").strip()
        if author_email:
            break
        print("❌ Cannot be empty", file=sys.stderr)

    examples = random.sample(list(LICENSE_MAP.keys()), 6)
    print(f"\nAvailable licenses: {', '.join(examples)}, and more")
    while True:
        license_name = input("License: ").strip()
        if license_name in LICENSE_MAP:
            break
        new_examples = random.sample(list(LICENSE_MAP.keys()), 6)
        print(f"❌ Invalid. Examples: {', '.join(new_examples)}", file=sys.stderr)

    try:
        result = run(
            project_name,
            output_dir,
            author_name,
            author_email,
            license_name,
            project_description,
        )
        print(f"\n✅ '{project_name}' → {result.absolute()}")
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run_cli()
