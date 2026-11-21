# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.repo.just."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from shared_utils.repo.just import _tools_available, lock_project


class TestLockProject:
    """Tests for lock_project."""

    def test_runs_lock_cmd(self, tmp_path: Path) -> None:
        """Run ``just lock`` inheriting CONTAINER from the env."""
        with (
            patch("subprocess.run") as mock_run,
            patch("shared_utils.repo.just._tools_available", return_value=True),
            patch.dict("os.environ", {"CONTAINER": "container"}),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            lock_project(tmp_path)
            mock_run.assert_called_once()
            kwargs = mock_run.call_args.kwargs
            assert mock_run.call_args[0][0][1:] == ["lock"]
            assert kwargs["env"]["CONTAINER"] == "container"

    def test_skips_when_tools_missing(self, tmp_path: Path) -> None:
        """Skip locking when uv, pnpm or just are missing."""
        with (
            patch("subprocess.run") as mock_run,
            patch("shared_utils.repo.just._tools_available", return_value=False),
        ):
            lock_project(tmp_path)
            mock_run.assert_not_called()


class TestToolsAvailable:
    """Tests for _tools_available."""

    def test_true_when_both_tools_present(self) -> None:
        """Return True when uv and pnpm resolve on PATH."""
        with patch("shutil.which", return_value="/usr/bin/tool"):
            assert _tools_available() is True

    def test_false_when_a_tool_is_missing(self) -> None:
        """Return False when any tool is missing."""
        with patch("shutil.which", side_effect=[None, "/usr/bin/pnpm", "/usr/bin/just"]):
            assert _tools_available() is False
