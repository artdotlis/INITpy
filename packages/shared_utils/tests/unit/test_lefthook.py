# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.config.lefthook."""

from pathlib import Path
from typing import Any

import yaml

from shared_utils.config.lefthook import remove_lefthook_jobs

pytest_plugins = ("tests.fixture.template",)


def _load(path: Path) -> dict[str, Any]:
    """Parse a lefthook file into plain data."""
    return yaml.safe_load(path.read_text())


class TestRemoveLefthookJobs:
    """Tests for remove_lefthook_jobs against the live lefthook.yml."""

    def test_removes_job_and_keeps_siblings(self, lefthook_yml: Path) -> None:
        """Drop the named job but keep the hook and its other jobs."""
        remove_lefthook_jobs(lefthook_yml, "docs")
        names = [job["name"] for job in _load(lefthook_yml)["tests"]["jobs"]]
        assert "docs" not in names
        assert "scaffolder" in names
        assert "shared-utils" in names

    def test_drops_emptied_group(self, lefthook_yml: Path) -> None:
        """Remove a group whose last job is gone, keeping its siblings."""
        remove_lefthook_jobs(lefthook_yml, "license")
        names = [job["name"] for job in _load(lefthook_yml)["pre-commit"]["jobs"]]
        assert "add" not in names
        assert "check" in names
        assert "fix" in names

    def test_drops_hook_when_all_jobs_gone(self, lefthook_yml: Path) -> None:
        """Remove the hook once its last job is removed."""
        for job in ("docs", "scaffolder", "shared-utils"):
            remove_lefthook_jobs(lefthook_yml, job)
        assert "tests" not in _load(lefthook_yml)

    def test_keeps_hook_with_commands(self, lefthook_yml: Path) -> None:
        """Leave command-only hooks such as commit-msg untouched."""
        remove_lefthook_jobs(lefthook_yml, "docs")
        assert "commitizen" in _load(lefthook_yml)["commit-msg"]["commands"]

    def test_keeps_non_dict_job_entries(self, tmp_path: Path) -> None:
        """Keep job entries that are not mappings instead of dropping them."""
        lefthook = tmp_path / "lefthook.yml"
        lefthook.write_text(
            "pre-commit:\n"
            "    jobs:\n"
            "        - just-a-string\n"
            "        - name: docs\n"
            "          run: x\n"
        )
        remove_lefthook_jobs(lefthook, "docs")
        assert _load(lefthook)["pre-commit"]["jobs"] == ["just-a-string"]
