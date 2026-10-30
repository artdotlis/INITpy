# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""File transformation functions for scaffolding."""

import tomlkit
from ruamel.yaml import YAML
from shared_utils.files import update_pyproject_dep_groups
from shared_utils.files import update_pyproject_workspace
from shared_utils.files import update_pyproject_description
from shared_utils.files import update_package_devcon_name
from shared_utils.files import update_pyproject_name
from shared_utils.names import package_env_file
from shared_utils.names import package_env_var
from pathlib import Path
from shared_utils.constants import VERSION


def write_package_files(path: Path, package_name: str, /) -> None:
    """Create empty files, add TODOs, and template test."""
    pkg_dir = path / "packages" / package_name
    src = pkg_dir / "src" / package_name

    src.mkdir(parents=True, exist_ok=True)
    # create empty files
    (src / "main.py").write_text("")
    (src / "py.typed").touch()
    (src / "__init__.py").write_text("__all__: list[str] = []")

    # empty README.md and .env
    (pkg_dir / "README.md").write_text("")
    (pkg_dir / ".env").write_text("")

    # main.py: add TODO comment
    (src / "main.py").write_text(f"# TODO: Implement {package_name}\n")

    # README.md: add package name header
    (pkg_dir / "README.md").write_text(f"# {package_name}\n")

    # template unit test with TODO
    tests = pkg_dir / "tests" / "unit"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / f"test_{package_name}.py").write_text(
        """
def test_placeholder() -> None:
    # TODO finish tests
    assert False
"""
    )


def amend_docs(path: Path, package_name: str, project_name: str, /) -> None:
    """Update docs/README.md and .zensical.toml."""
    index = path / "packages" / "docs" / "src" / "index.md"
    text = index.read_text()
    text = text.replace("# INIT - Python", f"# {project_name}", 1)
    index.write_text(text)

    ref_m = path / "packages" / "docs" / "src" / "ref" / "ref_m.md"
    if ref_m.exists():
        ref_m.write_text(
            f"# {project_name} - {package_name}\n\n::: {package_name}\n    options:"
            + "\n        show_submodules: true\n"
        )

    zensical = path / ".zensical.toml"
    doc = tomlkit.parse(zensical.read_text())
    doc["site_name"] = project_name
    if "repo_name" in doc:
        del doc["repo_name"]
    if "repo_url" in doc:
        del doc["repo_url"]
    zensical.write_text(tomlkit.dumps(doc))


def update_envs(path: Path, package_name: str, /) -> None:
    """Update PKG_SCAF / PKG_SHAR in env files."""
    package_env = path / "package.env"
    content = package_env.read_text()
    content = content.replace(
        "PKG_SCAF=packages/scaffolder",
        f"{package_env_var(package_name)}=packages/{package_name}",
    )
    content = content.replace("PKG_SHAR=packages/shared_utils", "")
    content = content.replace(
        "SCAF_ENV=packages/scaffolder/.env",
        f"{package_env_file(package_name)}=packages/{package_name}",
    )
    package_env.write_text(content)
    lint_env = path / "bin" / "lint" / "lint_env.sh"
    content = lint_env.read_text()
    content = content.replace("$SCAF_ENV", package_env_file(package_name))
    lint_env.write_text(content)


def _round_trip_yaml() -> YAML:
    yaml = YAML()
    yaml.preserve_quotes = True  # noqa: Vulture
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 2**31  # noqa: Vulture
    return yaml


def update_tests(path: Path, package_name: str, /) -> None:
    _update_lefthook_tests(path, package_name)
    _update_ci_tests(path, package_name)


def _update_lefthook_tests(path: Path, package_name: str, /) -> None:
    """Replace lefthook.yml test jobs with the single scaffolded package."""
    abbr = package_env_var(package_name)
    run_cmd = f"bin/install/wrap.sh 'cd ${abbr} && coverage run -m pytest'"
    lefthook = path / "lefthook.yml"
    yaml = _round_trip_yaml()
    doc = yaml.load(lefthook.read_text())
    doc["tests"]["jobs"] = [{"name": package_name, "run": run_cmd}]
    with lefthook.open("w") as stream:
        yaml.dump(doc, stream)


def _update_ci_tests(path: Path, package_name: str, /) -> None:
    """Collapse CI test steps to the single scaffolded package."""
    main = path / ".github" / "workflows" / "main.yml"
    yaml = _round_trip_yaml()
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


def set_version(path: Path, /) -> None:
    """Set version to 0.1.0 in pyproject.toml and package.json files."""
    for fpath in path.rglob("*"):
        if fpath.is_file() and fpath.name in ("pyproject.toml", "package.json"):
            text = fpath.read_text()
            text = text.replace(VERSION, "0.1.0")
            fpath.write_text(text)


def update_licenses_sh(path: Path, /) -> None:
    """Add leading error exit to licenses.sh."""
    licenses_sh = path / "bin" / "lint" / "licenses.sh"
    if not licenses_sh.exists():
        raise FileNotFoundError(f"Missing required file: {licenses_sh}")
    text = licenses_sh.read_text()
    # Insert exit after shebang
    exit_block = """# TODO: Complete license implementation before use.
# This script should fail until licenses are properly configured.
echo "Licenses are not configured. Complete license implementation before use." >&2
exit 1\n\n"""
    # Insert after the shebang line
    if text.startswith("#!"):
        first_newline = text.index("\n")
        text = text[: first_newline + 1] + exit_block + text[first_newline + 1 :]
    licenses_sh.write_text(text)


def set_entry_prod(path: Path, /) -> None:
    """Write entry_prod.sh."""
    entry = path / "bin" / "deploy" / "entry_prod.sh"
    entry.parent.mkdir(parents=True, exist_ok=True)
    entry.write_text("#!/bin/bash\n\nset -euo pipefail\n\nsleep infinity\n")


def clean_root_md(path: Path, project_name: str, /) -> None:
    (path / "README.md").write_text(f"# {project_name}\n\n")
    (path / "CHANGELOG.md").write_text("")
    (path / "uv.lock").unlink(True)
    (path / "pnpm-lock.yaml").unlink(True)


def correct_core_project(
    path: Path,
    project_name: str,
    package_name: str,
    dep_name: str,
    description: str,
    /,
) -> None:
    update_pyproject_name(path / "pyproject.toml", project_name)
    update_pyproject_workspace(path / "pyproject.toml", package_name)
    update_pyproject_dep_groups(path / "pyproject.toml", dep_name)
    update_pyproject_description(path / "pyproject.toml", description)
    update_package_devcon_name(path / "package.json", project_name)
    update_package_devcon_name(path / ".devcontainer" / "devcontainer.json", project_name)
