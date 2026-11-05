# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""License configuration for a generated project."""

import json
import re
from pathlib import Path

import tomlkit
from reuse.project import LICENSE_MAP

from shared_utils.spdx import write_license


def update_licenses_sh(path: Path, /) -> None:
    """Add a leading error exit to ``licenses.sh``.

    Args:
        path: Root of the generated project.

    Raises:
        FileNotFoundError: If ``bin/lint/licenses.sh`` is missing.
    """
    licenses_sh = path / "bin" / "lint" / "licenses.sh"
    text = licenses_sh.read_text()
    # Insert exit after shebang
    exit_block = """# TODO: Complete license implementation before use.
# This script should fail until licenses are properly configured.
echo "Licenses are not configured. Complete license implementation before use." >&2
exit 1\n\n"""
    # Insert after the shebang line
    if text.startswith("#!"):
        first_newline = text.index("\n")
        text = text[: first_newline + 1] + exit_block + text[first_newline + 1 :]
    licenses_sh.write_text(text)


def clear_licenses_dir(path: Path, /) -> None:
    """Remove all files from the ``LICENSES/`` directory.

    Args:
        path: Repository root that contains the ``LICENSES/`` directory.
    """
    lic_dir = path / "LICENSES"
    if lic_dir.is_dir():
        for file in lic_dir.iterdir():
            if file.is_file():
                file.unlink()


def _validate_license(license_name: str, /) -> None:
    """Validate that `license_name` is a known SPDX license identifier.

    Args:
        license_name: SPDX license identifier to validate.

    Raises:
        ValueError: If the identifier is not present in the license map.
    """
    if license_name not in LICENSE_MAP:
        raise ValueError(
            f"Unknown SPDX license: {license_name!r}. "
            f"Run `reuse fetch` to see supported licenses."
        )


def set_license_pyproject(path: Path, license_name: str, /) -> None:
    """Set the license field in pyproject.toml.

    Args:
        path: Path to pyproject.toml.
        license_name: SPDX license identifier to set.
    """
    doc = tomlkit.parse(path.read_text())
    if "project" not in doc:
        doc["project"] = {}
    doc["project"]["license"] = license_name
    path.write_text(tomlkit.dumps(doc))


def set_license_package_json(path: Path, license_name: str, /) -> None:
    """Set the license field in package.json.

    Args:
        path: Path to package.json.
        license_name: SPDX license identifier to set.
    """
    data = json.loads(path.read_text())
    data["license"] = license_name
    path.write_text(json.dumps(data, indent=2) + "\n")


def set_license_licenses_sh(licenses_sh: Path, license_name: str, /) -> None:
    """Set the software license in ``licenses.sh``.

    The license is chosen by the user at scaffold time; it replaces the
    default ``SOFTWARE_LIC`` assignment so the license-check tooling annotates
    files with the selected SPDX identifier.

    Args:
        licenses_sh: Path to ``bin/lint/licenses.sh``.
        license_name: SPDX license identifier to set.

    Raises:
        ValueError: If the ``SOFTWARE_LIC`` assignment is not found.
    """
    text = licenses_sh.read_text()
    text, count = re.subn(
        r'^SOFTWARE_LIC="[^"]*"$',
        f'SOFTWARE_LIC="{license_name}"',
        text,
        count=1,
        flags=re.M,
    )
    if count != 1:
        raise ValueError("SOFTWARE_LIC assignment not found in licenses.sh")
    licenses_sh.write_text(text)


def configure_licenses(path: Path, license_name: str, /) -> None:
    """Clear ``LICENSES/``, download ``LICENSE``, and set the license fields.

    Args:
        path: Repository root.
        license_name: SPDX license identifier to configure.
    """
    _validate_license(license_name)
    clear_licenses_dir(path)
    write_license(path / "LICENSE", license_name)
    set_license_pyproject(path / "pyproject.toml", license_name)
    set_license_package_json(path / "package.json", license_name)
    set_license_licenses_sh(path / "bin" / "lint" / "licenses.sh", license_name)
