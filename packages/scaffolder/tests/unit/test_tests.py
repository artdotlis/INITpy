# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.scaffold.tests."""

from pathlib import Path

from scaffolder.scaffold.tests import update_tests
from shared_utils.config.lefthook import round_trip_yaml

pytest_plugins = ("tests.fixture.template",)


class TestUpdateTests:
    """Tests for update_tests (run against live template files)."""

    def test_collapses_tests_to_single_package(
        self, tmp_path: Path, lefthook_yml: Path, main_workflow: Path
    ) -> None:
        """Collapse the lefthook jobs and the CI steps to the one package."""
        update_tests(tmp_path, "my_pkg")

        hooks = lefthook_yml.read_text()
        assert "$PKG_SHAR" not in hooks
        assert "$PKG_SCAF" not in hooks
        assert "run: bin/install/wrap.sh 'cd $PKG_MY_ && coverage run -m pytest'" in hooks

        ci = main_workflow.read_text()
        assert "packages/shared_utils" not in ci
        assert "packages/scaffolder" not in ci
        # The real template runs tests from several jobs, so the appended
        # step appears once per job.
        doc = round_trip_yaml().load(ci)
        steps = [step for job in doc["jobs"].values() for step in job.get("steps", [])]
        assert {
            "name": "Run my_pkg tests",
            "working-directory": "packages/my_pkg",
            "run": "uv run coverage run -m pytest",
        } in steps

    def test_skips_jobs_without_step_list(self, tmp_path: Path) -> None:
        """Leave jobs whose steps are not a list untouched."""
        (tmp_path / "lefthook.yml").write_text("tests: {jobs: [{name: x, run: y}]}\n")
        workflow = tmp_path / ".github" / "workflows" / "main.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            "jobs:\n"
            "  reusable:\n"
            "    uses: ./.github/workflows/other.yml\n"
            "  real:\n"
            "    steps:\n"
            "      - run: uv run pytest\n"
        )
        update_tests(tmp_path, "my_pkg")
        content = workflow.read_text()
        assert "uses: ./.github/workflows/other.yml" in content
        assert "uv run pytest" not in content
        assert content.count("Run my_pkg tests") == 1
