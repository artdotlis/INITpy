# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.licenses.reuse_remove."""

from pathlib import Path

import pytest

from shared_utils.licenses.reuse_remove import remove_reuse

pytest_plugins = ("tests.fixture.template",)


class TestRemoveReuse:
    """Tests for remove_reuse against a realistic reuse tree."""

    def test_removes_reuse_tree_and_keeps_license(
        self,
        tmp_path: Path,
        licenses_dir: Path,
        license_file: Path,
        reuse_toml: Path,
        package_json_license: Path,
    ) -> None:
        """Drop the LICENSES tree and REUSE.toml, keep LICENSE and .license files."""
        remove_reuse(tmp_path)

        # the LICENSES tree is gone
        assert not licenses_dir.exists()
        # the REUSE.toml config is removed
        assert not reuse_toml.exists()
        # the LICENSE file itself is kept
        assert license_file.read_text().strip()
        # .license companions are owned by strip_spdx_headers, not remove_reuse
        assert package_json_license.exists()

    def test_noop_without_reuse_tree(self, tmp_path: Path, license_file: Path) -> None:
        """Keep an empty project (only a LICENSE) untouched."""
        remove_reuse(tmp_path)
        assert license_file.exists()
        assert not (tmp_path / "LICENSES").exists()

    def test_nested_reuse_toml_removed(self, tmp_path: Path) -> None:
        """Remove REUSE.toml files at any depth."""
        nested = tmp_path / "packages" / "docs"
        nested.mkdir(parents=True)
        (nested / "REUSE.toml").write_text("path = []\n")
        (nested / "keep.md").write_text("# keep\n")
        remove_reuse(tmp_path)
        assert not (nested / "REUSE.toml").exists()
        assert (nested / "keep.md").exists()
