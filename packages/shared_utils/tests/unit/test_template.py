# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.repo.template."""

from pathlib import Path

import pytest

from shared_utils.repo.template import load_template


class TestLoadTemplate:
    """Tests for load_template."""

    def test_copies_directory(self, tmp_path: Path) -> None:
        """Copy a template directory recursively."""
        root = tmp_path / "root"
        (root / "docs").mkdir(parents=True)
        (root / "docs" / "index.md").write_text("hi")
        target = tmp_path / "target"
        target.mkdir()
        assert load_template(root, target, "docs") == target / "docs"
        assert (target / "docs" / "index.md").read_text() == "hi"

    def test_creates_parent_dirs_for_file(self, tmp_path: Path) -> None:
        """Create missing parent dirs when copying a single file."""
        root = tmp_path / "root"
        root.mkdir()
        (root / "configs.toml").write_text("x = 1")
        target = tmp_path / "target"
        target.mkdir()
        assert load_template(root, target, "configs.toml") == target / "configs.toml"
        assert (target / "configs.toml").read_text() == "x = 1"

    def test_raises_when_template_missing(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when the template piece is absent."""
        target = tmp_path / "target"
        target.mkdir()
        with pytest.raises(FileNotFoundError, match="template file missing"):
            load_template(tmp_path, target, "nope")
