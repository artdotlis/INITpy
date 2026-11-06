# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.git and shared_utils.repo.make."""

from pathlib import Path
from unittest.mock import patch, MagicMock

from shared_utils.repo.git import reset_git, init_and_commit, clone_git
from shared_utils.repo.make import _tools_available, lock_project


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
        # Mock subprocess to avoid real git
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


class TestLockProject:
    """Tests for lock_project."""

    def test_runs_make_cmd(self) -> None:
        """Run ``make run-lock`` inheriting CONTAINER from the env."""
        with (
            patch("subprocess.run") as mock_run,
            patch("shared_utils.repo.make._tools_available", return_value=True),
            patch.dict("os.environ", {"CONTAINER": "container"}),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            lock_project(Path("/tmp"))
            mock_run.assert_called_once()
            kwargs = mock_run.call_args.kwargs
            assert mock_run.call_args[0][0] == ["make", "run-lock"]
            assert kwargs["env"]["CONTAINER"] == "container"

    def test_runs_setup_before_lock(self) -> None:
        """Run ``make setup`` first when uv or pnpm are missing."""
        with (
            patch("subprocess.run") as mock_run,
            patch("shared_utils.repo.make._tools_available", return_value=False),
        ):
            mock_run.return_value = MagicMock(returncode=0)
            lock_project(Path("/tmp"))
            args = [call[0][0] for call in mock_run.call_args_list]
            assert args == [["make", "setup"], ["make", "run-lock"]]


class TestCloneGit:
    """Tests for clone_git."""

    def test_creates_and_clones(self, tmp_path: Path) -> None:
        """Create the target directory and clone the dev branch."""
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


class TestToolsAvailable:
    """Tests for _tools_available."""

    def test_true_when_both_tools_present(self) -> None:
        """Return True when uv and pnpm resolve on PATH."""
        with patch("shutil.which", return_value="/usr/bin/tool"):
            assert _tools_available() is True

    def test_false_when_a_tool_is_missing(self) -> None:
        """Return False when either tool is missing."""
        with patch("shutil.which", side_effect=[None, "/usr/bin/pnpm"]):
            assert _tools_available() is False
