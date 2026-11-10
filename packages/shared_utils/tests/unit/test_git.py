# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.repo.git."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from shared_utils.repo.git import clone_git, init_and_commit, reset_git


class TestResetGit:
    """Tests for reset_git."""

    def test_removes_git_dir(self, tmp_path: Path) -> None:
        """Delete the .git directory in the target path."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("[core]")
        reset_git(tmp_path)
        assert not git_dir.exists()


class TestInitAndCommit:
    """Tests for init_and_commit."""

    def test_initializes_repo_and_commits(self, tmp_path: Path) -> None:
        """Initialize a repo, stage files, and create the initial commit."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            init_and_commit(tmp_path, "Author", "a@b.com")
            assert mock_run.call_count == 3
            args_list = [c[0][0] for c in mock_run.call_args_list]
            assert args_list[0] == ["git", "init"]
            assert args_list[1] == ["git", "add", "."]
            assert args_list[2][:5] == [
                "git",
                "-c",
                "user.name=Author",
                "-c",
                "user.email=a@b.com",
            ]
            assert args_list[2][5:] == ["commit", "-m", "init", "--no-verify"]


class TestCloneGit:
    """Tests for clone_git."""

    def test_creates_and_clones(self, tmp_path: Path) -> None:
        """Create the target directory and clone the ref."""
        target = tmp_path / "repo"
        with patch("subprocess.run") as mock_run, patch("shutil.rmtree") as mock_rmtree:
            mock_run.return_value = MagicMock(returncode=0)
            clone_git(target, "https://example.com/repo.git")
            assert target.exists()
            assert mock_rmtree.call_count == 0
            assert mock_run.call_count == 1
            args = mock_run.call_args[0][0]
            assert "clone" in args
            assert "--branch" in args
            assert "dev" in args

    def test_removes_existing_target_before_clone(self, tmp_path: Path) -> None:
        """Wipe a leftover existing target before cloning."""
        target = tmp_path / "repo"
        target.mkdir()
        (target / "leftover.txt").write_text("x")
        with patch("subprocess.run") as mock_run, patch("shutil.rmtree") as mock_rmtree:
            mock_run.return_value = MagicMock(returncode=0)
            clone_git(target, "https://example.com/repo.git")
            assert mock_rmtree.call_count == 1
            assert mock_run.call_count == 1
