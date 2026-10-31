# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.git and shared_utils.make."""

from pathlib import Path
from unittest.mock import patch, MagicMock

from shared_utils.git import reset_git, inti_and_commit, clone_git
from shared_utils.make import lock_project


class TestResetGit:
    """Tests for reset_git."""

    def test_removes_git_dir(self, tmp_path: Path) -> None:
        """Delete the .git directory in the target path."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("[core]")
        reset_git(tmp_path)
        assert not git_dir.exists()


class TestIntiAndCommit:
    """Tests for inti_and_commit."""

    def test_initializes_repo_and_commits(self, tmp_path: Path) -> None:
        """Initialize a repo, stage files, and create the initial commit."""
        # Mock subprocess to avoid real git
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            inti_and_commit(tmp_path)
            assert mock_run.call_count == 3
            args_list = [c[0][0] for c in mock_run.call_args_list]
            assert args_list[0] == ["git", "init"]
            assert args_list[1][0] == "git"
            assert args_list[2][0] == "git"


class TestLockProject:
    """Tests for lock_project."""

    def test_runs_make_cmd(self) -> None:
        """Invoke the make command that locks the project dependencies."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            lock_project(Path("/tmp"))
            mock_run.assert_called_once()
            assert mock_run.call_args[0][0] == ["make", "run-lock"]


class TestCloneGit:
    """Tests for clone_git."""

    def test_creates_and_clones(self, tmp_path: Path) -> None:
        """Create the target directory and clone the dev branch."""
        target = tmp_path / "repo"
        with patch("subprocess.run") as mock_run, patch("shutil.rmtree") as mock_rmtree:
            mock_run.return_value = MagicMock(returncode=0)
            clone_git(target, "https://example.com/repo.git")
            assert target.exists()
            assert mock_rmtree.call_count == 1
            assert mock_run.call_count == 1
            args = mock_run.call_args[0][0]
            assert "clone" in args
            assert "--branch" in args
            assert "dev" in args
