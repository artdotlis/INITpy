# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.repo.just."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from shared_utils.repo.just import _tools_available, lock_project


class TestLockProject:
    """Tests for lock_project."""

    def test_runs_make_cmd(self) -> None:
        """Run ``just lock`` inheriting CONTAINER from the env."""
        with (
            patch("subprocess.run") as mock_run,
            patch("shared_utils.repo.just._tools_available", return_value=True),
            patch.dict("os.environ", {"CONTAINER": "container"}),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            lock_project(Path("/tmp"))
            mock_run.assert_called_once()
            kwargs = mock_run.call_args.kwargs
            assert mock_run.call_args[0][0] == ["just", "lock"]
            assert kwargs["env"]["CONTAINER"] == "container"

    def test_runs_setup_before_lock(self) -> None:
        """Run ``just setup`` first when uv, pnpm or just are missing."""
        with (
            patch("subprocess.run") as mock_run,
            patch("shared_utils.repo.just._tools_available", return_value=False),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            lock_project(Path("/tmp"))
            args = [call[0][0] for call in mock_run.call_args_list]
            assert args == [["just", "setup"], ["just", "lock"]]


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
