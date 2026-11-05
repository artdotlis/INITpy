# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Test wiring (lefthook + CI) for a generated project."""

from pathlib import Path

from shared_utils.config.lefthook import prune_lefthook_hooks
from shared_utils.config.lefthook import round_trip_yaml
from shared_utils.core.names import package_env_var


def update_tests(path: Path, package_name: str, /) -> None:
    """Wire the scaffolded package into lefthook and CI test config.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
    _update_lefthook_tests(path, package_name)
    _update_ci_tests(path, package_name)


def _update_lefthook_tests(path: Path, package_name: str, /) -> None:
    """Replace lefthook.yml test jobs with the single scaffolded package."""
    abbr = package_env_var(package_name)
    run_cmd = f"bin/install/wrap.sh 'cd ${abbr} && coverage run -m pytest'"
    lefthook = path / "lefthook.yml"
    yaml = round_trip_yaml()
    doc = yaml.load(lefthook.read_text())
    doc["tests"]["jobs"] = [{"name": package_name, "run": run_cmd}]
    prune_lefthook_hooks(doc)
    with lefthook.open("w") as stream:
        yaml.dump(doc, stream)


def _update_ci_tests(path: Path, package_name: str, /) -> None:
    """Collapse CI test steps to the single scaffolded package."""
    main = path / ".github" / "workflows" / "main.yml"
    yaml = round_trip_yaml()
    doc = yaml.load(main.read_text())
    for job in doc.get("jobs", {}).values():
        steps = job.get("steps")
        if not isinstance(steps, list):
            continue
        # Drop any step that runs pytest (from a prior scaffold)
        steps[:] = [
            step
            for step in steps
            if isinstance(step, dict) and "pytest" not in step.get("run", "")
        ]
        steps.append(
            {
                "name": f"Run {package_name} tests",
                "working-directory": f"packages/{package_name}",
                "run": "uv run coverage run -m pytest",
            }
        )
    with main.open("w") as stream:
        yaml.dump(doc, stream)
