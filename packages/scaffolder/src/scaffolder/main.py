# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Scaffolder CLI - generate INITpy-based projects."""

import argparse
import sys

from .scaffold.core import run


def run_cli() -> None:
    """Parse args and delegate to scaffold.run()."""
    parser = argparse.ArgumentParser(description="Create a new INITpy-based project")
    parser.add_argument("name", help="Project name")
    parser.add_argument("-a", "--author", default="Default Author")
    parser.add_argument("-e", "--email", default="author@example.com")
    parser.add_argument("-o", "--output", default=".")
    parser.add_argument(
        "-l",
        "--license",
        default="Unlicense",
        choices=["Unlicense", "MIT", "Apache-2.0", "GPL-3.0", "CC0-1.0"],
    )
    parser.add_argument("--no-git", action="store_true")
    args = parser.parse_args()

    try:
        result = run(
            args.name,
            output_dir=args.output,
            author_name=args.author,
            author_email=args.email,
            license_name=args.license,
            skip_git=args.no_git,
        )
        print(f"\n✅ '{args.name}' → {result.absolute()}")
    except Exception as exc:
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
