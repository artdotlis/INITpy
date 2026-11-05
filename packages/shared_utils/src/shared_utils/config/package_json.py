# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""package.json editing helpers."""

import json
from pathlib import Path


def update_package_authors(path: Path, author_name: str, author_email: str, /) -> None:
    """Replace author info in a package.json file.

    Args:
        path: Path to package.json
        author_name: New author name
        author_email: New author email
    """
    data = json.loads(path.read_text())
    data["author"] = {"email": author_email, "name": author_name}
    path.write_text(json.dumps(data, indent=2) + "\n")


def update_package_devcon_name(path: Path, name: str, /) -> None:
    """Set the ``name`` field in a package.json file.

    Args:
        path: Path to package.json.
        name: New name value.
    """
    data = json.loads(path.read_text())
    data["name"] = name
    path.write_text(json.dumps(data, indent=2) + "\n")
