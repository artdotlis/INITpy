# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.lefthook."""

from pathlib import Path


from shared_utils.lefthook import remove_lefthook_jobs


class TestRemoveLefthookJobs:
    """Tests for remove_lefthook_jobs (pruning empty hooks and groups)."""

    def test_removes_hook_left_without_jobs(self, tmp_path: Path) -> None:
        """Drop a hook when removing its last job leaves it empty."""
        lefthook = tmp_path / "lefthook.yml"
        lefthook.write_text(
            "pre-push:\n"
            "    piped: true\n"
            "    jobs:\n"
            "        - name: docs\n"
            "          run: x\n"
        )
        remove_lefthook_jobs(lefthook, "docs")
        assert "pre-push" not in lefthook.read_text()

    def test_removes_empty_group_and_keeps_siblings(self, tmp_path: Path) -> None:
        """Drop an emptied group entry but keep the hook and its other jobs."""
        lefthook = tmp_path / "lefthook.yml"
        lefthook.write_text(
            "pre-commit:\n"
            "    jobs:\n"
            "        - name: check\n"
            "          group:\n"
            "              jobs:\n"
            "                  - name: docs\n"
            "                    run: x\n"
            "        - name: other\n"
            "          run: y\n"
        )
        remove_lefthook_jobs(lefthook, "docs")
        text = lefthook.read_text()
        assert "pre-commit" in text
        assert "check" not in text
        assert "name: other" in text

    def test_removes_hook_when_group_emptied(self, tmp_path: Path) -> None:
        """Drop the hook when its only group ends up empty."""
        lefthook = tmp_path / "lefthook.yml"
        lefthook.write_text(
            "pre-commit:\n"
            "    jobs:\n"
            "        - name: check\n"
            "          group:\n"
            "              jobs:\n"
            "                  - name: docs\n"
            "                    run: x\n"
        )
        remove_lefthook_jobs(lefthook, "docs")
        assert "pre-commit" not in lefthook.read_text()

    def test_keeps_hook_with_commands(self, tmp_path: Path) -> None:
        """Keep a hook that only has commands (no jobs) untouched."""
        lefthook = tmp_path / "lefthook.yml"
        lefthook.write_text(
            "commit-msg:\n    commands:\n        commitizen:\n            run: cz\n"
        )
        remove_lefthook_jobs(lefthook, "docs")
        assert "commitizen" in lefthook.read_text()
