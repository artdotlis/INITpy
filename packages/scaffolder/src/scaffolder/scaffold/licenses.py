# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""License configuration for a generated project."""

from pathlib import Path

from reuse.project import LICENSE_MAP

from shared_utils.licenses.spdx import write_license


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


def configure_licenses(path: Path, license_name: str, /) -> None:
    """Clear ``LICENSES/`` and download the ``LICENSE`` file.

    The software license is rendered into the files that carry it (root
    ``pyproject.toml``, ``package.json`` and ``bin/lint/licenses.sh``) by the
    whole-file templates, so only the license document itself is written here.

    Args:
        path: Root of the generated project.
        license_name: SPDX license identifier to configure.
    """
    _validate_license(license_name)
    clear_licenses_dir(path)
    write_license(path / "LICENSE", license_name)
