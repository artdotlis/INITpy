# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.spdx."""

from pathlib import Path

from unittest.mock import patch


from reuse.comment import PythonCommentStyle

from shared_utils.spdx import _find_spdx_block

from shared_utils.spdx import strip_spdx_headers

from shared_utils.spdx import write_license


class TestFindSpdxBlock:
    """Tests for _find_spdx_block."""

    def test_returns_none_when_no_spdx(self) -> None:
        """Return None for text with no SPDX block."""
        result = _find_spdx_block("# hello world", PythonCommentStyle)
        assert result is None

    def test_returns_block_when_spdx_exists(self) -> None:
        """Return the offset and content of an SPDX comment block."""
        # REUSE-IgnoreStart
        text = "# SPDX-License-Identifier: MIT"
        # REUSE-IgnoreEnd
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is not None
        start, block = result
        assert start == 0
        assert "SPDX" in block

    def test_skips_lines_without_spdx(self) -> None:
        """Find the block even when preceding lines lack SPDX markers."""
        # REUSE-IgnoreStart
        text = "# no spdx\n# SPDX-License-Identifier: CC0-1.0"
        # REUSE-IgnoreEnd
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is not None
        start, block = result
        assert "SPDX" in block

    def test_iterates_when_no_spdx_found(self) -> None:
        """Return None after exhausting the comment block."""
        text = "# line1\n# line2\n# line3\n" * 10 + "end"
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is None

    def test_handles_first_line_only(self) -> None:
        """Return None for a single line with no SPDX."""
        # Single line with no newline triggers the `nxt == -1` break
        text = "# no SPDX here"
        result = _find_spdx_block(text, PythonCommentStyle)
        assert result is None


class TestStripSpdxHeaders:
    """Tests for strip_spdx_headers."""

    def test_removes_spdx_from_file(self, tmp_path: Path) -> None:
        """Remove SPDX headers from a file."""
        f = tmp_path / "file.py"
        f.write_text("# SPDX-License-Identifier: MIT\n# Copyright 2024\n\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        text = f.read_text()
        assert "SPDX" not in text
        assert "print('hi')" in text

    def test_removes_license_file(self, tmp_path: Path) -> None:
        """Delete the companion .license file."""
        (tmp_path / "MIT.license").write_text("license text")
        strip_spdx_headers(tmp_path)
        assert not (tmp_path / "MIT.license").exists()

    def test_skips_files_without_spdx(self, tmp_path: Path) -> None:
        """Leave files that contain no SPDX block unchanged."""
        f = tmp_path / "no_spdx.py"
        f.write_text("print('hello')\n")
        strip_spdx_headers(tmp_path)
        assert f.read_text() == "print('hello')\n"

    def test_handles_none_comment_style(self, tmp_path: Path) -> None:
        """Leave the file unchanged when no comment style is detected."""
        f = tmp_path / "file.py"
        f.write_text("# Contains SPDX somewhere\nprint('hi')\n")
        with patch("shared_utils.spdx.get_comment_style", return_value=None):
            strip_spdx_headers(tmp_path)
        # File should be unchanged since get_comment_style returned None
        assert f.read_text() == "# Contains SPDX somewhere\nprint('hi')\n"

    def test_handles_no_spdx_found(self, tmp_path: Path) -> None:
        """Leave a comment-only file unchanged."""
        f = tmp_path / "file.py"
        f.write_text("# just a comment\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        assert f.read_text() == "# just a comment\nprint('hi')\n"

    def test_handles_spdx_but_not_valid_block(self, tmp_path: Path) -> None:
        """Keep the text when SPDX is not part of a valid comment block."""
        f = tmp_path / "file.py"
        f.write_text("# SPDX not valid here\nprint('hi')\n")
        strip_spdx_headers(tmp_path)
        assert "SPDX" in f.read_text()


class TestWriteLicense:
    """Tests for write_license."""

    def test_writes_license_file(self, tmp_path: Path) -> None:
        """Download the license text into the target file."""
        lic_file = tmp_path / "LICENSE"
        lic_file.write_text("old content")
        with patch("shared_utils.spdx.put_license_in_file") as mock_put:
            write_license(lic_file, "MIT")
            mock_put.assert_called_once_with("MIT", lic_file)
