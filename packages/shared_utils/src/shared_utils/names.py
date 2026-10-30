# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Name sanitization utilities."""

import re


def sanitize_package_name(name: str, /) -> str:
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


def sanitize_package_name_dep_group(name: str, /) -> str:
    sanitized = name.lower().replace(" ", "-").replace("_", "-")
    sanitized = re.sub(r"[^a-z0-9-]", "", sanitized)
    if sanitized and sanitized[0].isdigit():
        sanitized = "-" + sanitized
    return sanitized or "project"


def package_abbrev(package_name: str, /) -> str:
    return package_name.upper()[0:3]


def package_env_var(package_name: str, /) -> str:
    return f"PKG_{package_abbrev(package_name)}"


def package_env_file(package_name: str, /) -> str:
    return f"{package_abbrev(package_name)}_ENV"
