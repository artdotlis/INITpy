# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.package_json."""

import json

from pathlib import Path


from shared_utils.package_json import update_package_authors

from shared_utils.package_json import update_package_devcon_name


class TestUpdatePackageAuthors:
    """Tests for update_package_authors."""

    def test_updates_author(self, tmp_path: Path) -> None:
        """Set the author object in a package.json file."""
        p = tmp_path / "package.json"
        p.write_text('{"name": "x"}\n')
        update_package_authors(p, "New Name", "new@mail.com")
        data = json.loads(p.read_text())
        assert data["author"] == {"email": "new@mail.com", "name": "New Name"}


class TestUpdatePackageDevconName:
    """Tests for update_package_devcon_name."""

    def test_updates_name(self, tmp_path: Path) -> None:
        """Replace the name field in a JSON file."""
        p = tmp_path / "package.json"
        p.write_text('{"name": "old"}\n')
        update_package_devcon_name(p, "new_name")
        data = json.loads(p.read_text())
        assert data["name"] == "new_name"
