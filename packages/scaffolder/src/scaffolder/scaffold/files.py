# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""File transformation functions for scaffolding."""

from tomlkit import TOMLDocument
import json
import re
import shutil
import tomlkit

from ruamel.yaml import YAML
from reuse.project import LICENSE_MAP
from shared_utils.files import update_pyproject_workspace
from shared_utils.files import update_pyproject_description
from shared_utils.files import update_package_devcon_name
from shared_utils.files import update_pyproject_name
from shared_utils.files import write_license
from shared_utils.names import package_env_file
from shared_utils.names import package_env_var
from pathlib import Path


def write_package_files(path: Path, package_name: str, /) -> None:
    """Create empty files, add TODOs, and a placeholder test.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
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
    """Update the docs index, module reference, and VitePress config.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
        project_name: The new project name.
    """
    index = path / "packages" / "docs" / "src" / "index.md"
    text = index.read_text()
    # The template home hero uses `name: INITpy` in its frontmatter.
    text = text.replace("name: INITpy", f"name: {project_name}", 1)
    index.write_text(text)

    ref_index = path / "packages" / "docs" / "src" / "ref" / "index.md"
    ref_index.write_text(f"# Reference\n\n- [{package_name}]({package_name})\n")

    config = path / "packages" / "docs" / ".vitepress" / "config.toml"
    doc = tomlkit.parse(config.read_text())
    doc["site"]["title"] = project_name
    theme = doc.get("vitepress", {}).get("themeConfig")
    if theme is not None and "socialLinks" in theme:
        links = theme["socialLinks"]
        for link in list(links):
            if str(link.get("link", "")).startswith("https://github.com/artdotlis"):
                links.remove(link)
    config.write_text(tomlkit.dumps(doc))


def update_copyright(path: Path, copyright: str, /) -> None:
    """Set COPYRIGHT in the project's ``package.env``.

    Args:
        path: Root of the generated project.
        copyright: Copyright holder of the new project.
    """
    package_env = path / "package.env"
    content = package_env.read_text()
    content = re.sub(r"^COPYRIGHT=.*$", f'COPYRIGHT="{copyright}"', content, flags=re.M)
    package_env.write_text(content)


def update_envs(path: Path, package_name: str, /) -> None:
    """Point package env variables at the new package.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
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
    content = content.replace("SCAF_ENV", package_env_file(package_name))
    lint_env.write_text(content)


def _round_trip_yaml() -> YAML:
    yaml = YAML()
    yaml.preserve_quotes = True  # noqa: Vulture
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 2**31  # noqa: Vulture
    return yaml


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


def update_commitizen_version_files(path: Path, package_name: str, /) -> None:
    """Scope :ref:`[tool.commitizen] version_files` to the new package.

    Removes entries referencing shared_utils and renames the scaffolder
    entry to the scaffolded package's pyproject.toml.

    Args:
        path: Root of the generated project.
        package_name: The package being scaffolded.
    """
    root_pyproject = path / "pyproject.toml"
    doc = tomlkit.parse(root_pyproject.read_text())
    tool = doc.get("tool")
    if tool is None:
        return
    commitizen = tool.get("commitizen")
    if commitizen is None:
        return

    version_files = commitizen.get("version_files")
    if not isinstance(version_files, list):
        return

    # Drop shared_utils entries; retarget scaffolder to the new package.
    cleaned = [
        (
            f"packages/{package_name}/pyproject.toml"
            if entry == "packages/scaffolder/pyproject.toml"
            else entry
        )
        for entry in version_files
        if "shared_utils" not in entry
    ]
    commitizen["version_files"] = cleaned

    root_pyproject.write_text(tomlkit.dumps(doc))


def update_licenses_sh(path: Path, /) -> None:
    """Add a leading error exit to ``licenses.sh``.

    Args:
        path: Root of the generated project.

    Raises:
        FileNotFoundError: If ``bin/lint/licenses.sh`` is missing.
    """
    licenses_sh = path / "bin" / "lint" / "licenses.sh"
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


def remove_prod_docker(path: Path, /) -> None:
    """Remove the production Docker setup and promote the dev compose.

    Deletes the root production ``Dockerfile`` and compose file, moves the
    dev compose up to the repo root, points the devcontainer at the single
    (dev) compose, and drops prod-only env vars and deploy scripts.

    Args:
        path: Root of the generated project.
    """
    dockerfile = path / "Dockerfile"
    if dockerfile.exists():
        dockerfile.unlink()

    dev_compose = path / ".devcontainer" / "dev.docker-compose.yml"
    root_compose = path / "docker-compose.yml"
    shutil.move(str(dev_compose), str(root_compose))

    devcontainer = path / ".devcontainer" / "devcontainer.json"
    data = json.loads(devcontainer.read_text())
    data["dockerComposeFile"] = ["../docker-compose.yml"]
    devcontainer.write_text(json.dumps(data, indent=2) + "\n")

    # prod-only env vars would trip the lint_env occurrence check
    package_env = path / "package.env"
    content = package_env.read_text()
    for var in ("BIN_DEPLOY_HEALTH", "BIN_DEPLOY_ENTRY_PROD"):
        content = re.sub(rf"^{var}=.*$", "", content, flags=re.M)
    content = re.sub(r"\n{2,}", "\n", content)
    package_env.write_text(content)

    # prod-only deploy scripts
    for name in ("entry_prod.sh", "health.sh"):
        script = path / "bin" / "deploy" / name
        if script.exists():
            script.unlink()


def clean_root_md(path: Path, project_name: str, /) -> None:
    """Reset root README, CHANGELOG, and lockfiles for the new project.

    Args:
        path: Root of the generated project.
        project_name: The new project name.
    """
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
    """Apply project metadata to root config files.

    Updates the root ``pyproject.toml`` and ``package.json`` files with
    the project name, workspace dependency, description, and the
    ``mono`` dependency group.

    Args:
        path: Root of the generated project.
        project_name: The new project name.
        package_name: The workspace package name.
        dep_name: Name used for the ``mono`` dependency group.
        description: Short description of the new project.
    """
    update_pyproject_name(path / "pyproject.toml", project_name)
    update_pyproject_workspace(path / "pyproject.toml", package_name)
    update_pyproject_dep_groups(path / "pyproject.toml", dep_name)
    update_pyproject_description(path / "pyproject.toml", description)
    update_package_devcon_name(path / "package.json", project_name)
    update_package_devcon_name(path / ".devcontainer" / "devcontainer.json", project_name)


def remove_projects_output_folder(path: Path, /) -> None:
    """Remove the template PROJECTS output folder from a generated project.

    Args:
        path: Root of the generated project.
    """
    output_path = path / "PROJECTS"
    if output_path.exists():
        shutil.rmtree(output_path) if output_path.is_dir() else output_path.unlink()


def remove_docs(path: Path, /) -> None:
    """Remove the ``docs`` subpackage and every VitePress/docs mention.

    Deletes ``packages/docs`` and strips docs references from the workspace
    config, pyproject.toml, Makefile, CI workflows, lint scripts, package.env
    and .gitignore so no dangling docs wiring remains.

    Args:
        path: Root of the generated project.
    """
    docs_dir = path / "packages" / "docs"
    if docs_dir.exists():
        shutil.rmtree(docs_dir) if docs_dir.is_dir() else docs_dir.unlink()

    _remove_docs_pyproject(path / "pyproject.toml")
    _remove_docs_pnpm_workspace(path / "pnpm-workspace.yaml")
    _drop_docs_make_targets(path / "Makefile")
    _drop_docs_lefthook(path / "lefthook.yml")
    _drop_docs_env(path / "package.env")
    _drop_docs_env_script(path / "bin" / "lint" / "lint_env.sh")
    _drop_docs_clean_script(path / "bin" / "install" / "clean.sh")
    _drop_docs_licenses(path / "bin" / "lint" / "licenses.sh")
    _drop_docs_gitignore(path / ".gitignore")
    _drop_docs_workflow(path)


def _remove_docs_pyproject(pyproject: Path, /) -> None:
    """Drop docs references from the root pyproject.toml."""
    doc = tomlkit.parse(pyproject.read_text())
    _drop_docs_uv_workspace(doc)
    _drop_docs_dependency_group(doc)
    _drop_docs_commitizen(doc)
    _drop_docs_vulture(doc)
    pyproject.write_text(tomlkit.dumps(doc))


def _drop_docs_uv_workspace(doc: TOMLDocument) -> None:
    """Remove the docs package from the uv workspace exclude list."""
    workspace = doc.get("tool", {}).get("uv", {}).get("workspace")
    if isinstance(workspace, dict) and isinstance(workspace.get("exclude"), list):
        workspace["exclude"] = [
            entry for entry in workspace["exclude"] if str(entry) != "packages/docs"
        ]
        if not workspace["exclude"]:
            del workspace["exclude"]


def _drop_docs_dependency_group(doc: TOMLDocument) -> None:
    """Remove the docs dependency group."""
    groups = doc.get("dependency-groups")
    if isinstance(groups, dict) and "docs" in groups:
        del groups["docs"]


def _drop_docs_commitizen(doc: TOMLDocument) -> None:
    """Drop the docs package from commitizen version_files."""
    commitizen = doc.get("tool", {}).get("commitizen")
    if isinstance(commitizen, dict) and isinstance(commitizen.get("version_files"), list):
        commitizen["version_files"] = [
            entry
            for entry in commitizen["version_files"]
            if str(entry) != "packages/docs/package.json"
        ]


def _drop_docs_vulture(doc: TOMLDocument) -> None:
    """Drop the docs path from vulture excludes."""
    vulture = doc.get("tool", {}).get("vulture")
    if isinstance(vulture, dict) and isinstance(vulture.get("exclude"), list):
        vulture["exclude"] = [
            entry for entry in vulture["exclude"] if "packages/docs" not in str(entry)
        ]


def _remove_docs_pnpm_workspace(workspace_yaml: Path, /) -> None:
    """Remove the docs package from the pnpm workspace packages list."""
    yaml = _round_trip_yaml()
    doc = yaml.load(workspace_yaml.read_text())
    packages = doc.get("packages")
    if isinstance(packages, list):
        doc["packages"] = [entry for entry in packages if str(entry) != "packages/docs"]
        if not doc["packages"]:
            del doc["packages"]
    with workspace_yaml.open("w") as stream:
        yaml.dump(doc, stream)


_DOCS_MAKE_TARGETS = ("docs", "build-docs", "run-docs", "serve-docs", "docs-ref")
_DOCS_TARGET_BLOCK_RE = re.compile(
    rf"^(?:{'|'.join(re.escape(t) for t in _DOCS_MAKE_TARGETS)}):.*?$\n"
    rf"(?:\t[^\n]*$\n?)*\n?",
    re.M,
)


def _drop_docs_make_targets(makefile: Path, /) -> None:
    """Remove docs build/dev targets from a Makefile, failing on leftovers.

    Verifies every docs target is present, drops each target block (header,
    recipe lines and one trailing blank), then fails loudly if the PKG_DOCS
    variable survives anywhere else — no silent stripping.
    """
    text = makefile.read_text()
    missing = [
        t for t in _DOCS_MAKE_TARGETS if not re.search(rf"(?m)^{re.escape(t)}:", text)
    ]
    if missing:
        raise ValueError("Makefile missing docs target(s): " + ", ".join(missing))
    text = _DOCS_TARGET_BLOCK_RE.sub("", text)
    if re.search(r"\$\(PKG_DOCS\)", text):
        raise ValueError(
            "Makefile still references $(PKG_DOCS) after dropping docs targets"
        )
    makefile.write_text(text)


def _drop_docs_lefthook(lefthook: Path, /) -> None:
    """Remove the docs test job from lefthook.yml."""
    yaml = _round_trip_yaml()
    doc = yaml.load(lefthook.read_text())
    for hook in doc.values():
        jobs = hook.get("jobs") if isinstance(hook, dict) else None
        if isinstance(jobs, list):
            jobs[:] = [
                job
                for job in jobs
                if not (isinstance(job, dict) and job.get("name") == "docs")
            ]
    with lefthook.open("w") as stream:
        yaml.dump(doc, stream)


def _drop_docs_env(package_env: Path, /) -> None:
    """Drop docs-related variable declarations from package.env."""
    content = package_env.read_text()
    for var in ("CONFIG_DOCS", "PKG_DOCS", "DOCS_ENV"):
        content = re.sub(rf"(?m)^{var}=.*$\n?", "", content)
    content = re.sub(r"\n{2,}", "\n", content)
    package_env.write_text(content)


def _drop_docs_env_script(script: Path, /) -> None:
    """Remove the DOCS_ENV entry from lint_env.sh ENV_FILES."""
    text = script.read_text()
    text = text.replace('"$DOCS_ENV"', "")
    script.write_text(text)


_DOCS_START = "# ===== DOCS:START ====="
_DOCS_END = "# ===== DOCS:END ====="


def _drop_docs_clean_script(script: Path, /) -> None:
    """Remove the marked DOCS block from clean.sh."""
    text = script.read_text()
    border = r"[ \t]*#[ \t-]*\n"
    text = re.sub(
        rf"(?ms)(?:{border})?{re.escape(_DOCS_START)}.*?{re.escape(_DOCS_END)}\n?(?:{border})?",
        "",
        text,
    )
    text = re.sub(r"\n\n\n+", "\n\n", text)
    script.write_text(text)


def _drop_docs_licenses(licenses_sh: Path, /) -> None:
    """Remove docs config and ignore entries from licenses.sh."""
    text = licenses_sh.read_text()
    text = text.replace('"$CONFIG_DOCS"', "")
    lines = [
        line for line in text.splitlines(keepends=True) if "packages/docs" not in line
    ]
    licenses_sh.write_text("".join(lines))


def _drop_docs_gitignore(gitignore: Path, /) -> None:
    """Remove Sphinx/VitePress ignore blocks from .gitignore."""
    text = gitignore.read_text()
    text = text.replace("# Sphinx documentation\ndocs/_build/\n", "")
    text = re.sub(
        r"(?m)^# VitePress\n\.vitepress/\.cache/\n\.vitepress/dist/\n", "", text
    )
    gitignore.write_text(text)


def _drop_docs_workflow(path: Path, /) -> None:
    """Remove the docs GitHub Actions workflow."""
    workflow = path / ".github" / "workflows" / "docs.yml"
    workflow.unlink()


def update_pyproject_dep_groups(
    path: Path,
    package_name: str,
    /,
) -> None:
    """Add `package_name` to the ``mono`` dependency group.

    Args:
        path: Path to pyproject.toml.
        package_name: The package to add.
    """
    doc = tomlkit.parse(path.read_text())
    if "dependency-groups" not in doc:
        doc["dependency-groups"] = {}
    doc["dependency-groups"]["mono"] = [package_name]
    path.write_text(tomlkit.dumps(doc))


def clear_licenses_dir(path: Path, /) -> None:
    """Remove all files from the ``LICENSES/`` directory.

    Args:
        path: Repository root that contains the ``LICENSES/`` directory.
    """
    lic_dir = path / "LICENSES"
    if lic_dir.is_dir():
        for file in lic_dir.iterdir():
            if file.is_file():
                file.unlink()


def _validate_license(license_name: str, /) -> None:
    """Validate that `license_name` is a known SPDX license identifier.

    Args:
        license_name: SPDX license identifier to validate.

    Raises:
        ValueError: If the identifier is not present in the license map.
    """
    if license_name not in LICENSE_MAP:
        raise ValueError(
            f"Unknown SPDX license: {license_name!r}. "
            f"Run `reuse fetch` to see supported licenses."
        )


def set_license_pyproject(path: Path, license_name: str, /) -> None:
    """Set the license field in pyproject.toml.

    Args:
        path: Path to pyproject.toml.
        license_name: SPDX license identifier to set.
    """
    doc = tomlkit.parse(path.read_text())
    if "project" not in doc:
        doc["project"] = {}
    doc["project"]["license"] = license_name
    path.write_text(tomlkit.dumps(doc))


def set_license_package_json(path: Path, license_name: str, /) -> None:
    """Set the license field in package.json.

    Args:
        path: Path to package.json.
        license_name: SPDX license identifier to set.
    """
    data = json.loads(path.read_text())
    data["license"] = license_name
    path.write_text(json.dumps(data, indent=2) + "\n")


def configure_licenses(path: Path, license_name: str, /) -> None:
    """Clear ``LICENSES/``, download ``LICENSE``, and set the license fields.

    Args:
        path: Repository root.
        license_name: SPDX license identifier to configure.
    """
    _validate_license(license_name)
    clear_licenses_dir(path)
    write_license(path / "LICENSE", license_name)
    set_license_pyproject(path / "pyproject.toml", license_name)
    set_license_package_json(path / "package.json", license_name)


_REUSE_START = "# ===== REUSE:START ====="
_REUSE_END = "# ===== REUSE:END ====="


def remove_reuse(path: Path, /) -> None:
    """Remove reuse tooling, keeping the LICENSE file.

    Args:
        path: Repository root of the project.
    """
    target = path / "LICENSES"
    if target.is_dir():
        shutil.rmtree(target)
    _remove_reuse_files(path)
    _remove_reuse_dependency(path / "pyproject.toml")
    _strip_reuse_script(path / "bin" / "lint" / "licenses.sh")


def _remove_reuse_files(path: Path, /) -> None:
    """Delete ``REUSE.toml`` configs."""
    for fpath in list(path.rglob("*")):
        if fpath.is_file() and fpath.name.lower() == "reuse.toml":
            fpath.unlink()


def _remove_reuse_dependency(pyproject: Path, /) -> None:
    """Drop the ``reuse`` dependency from ``pyproject.toml``."""
    doc = tomlkit.parse(pyproject.read_text())
    project = doc.get("project")
    if project is not None and project.get("dependencies") is not None:
        doc["project"]["dependencies"] = [
            dep
            for dep in project["dependencies"]
            if not (isinstance(dep, str) and dep.strip().lower().startswith("reuse"))
        ]
    groups = doc.get("dependency-groups")
    if groups is not None:
        for group_name, deps in list(groups.items()):
            groups[group_name] = [
                dep
                for dep in deps
                if not (isinstance(dep, str) and dep.strip().lower().startswith("reuse"))
            ]
    pyproject.write_text(tomlkit.dumps(doc))


def _strip_reuse_script(licenses_sh: Path, /) -> None:
    """Remove the marked reuse section from ``licenses.sh``."""
    text = licenses_sh.read_text()
    border = r"[ \t]*#[ \t-]*\n"
    text = re.sub(
        rf"(?ms)(?:{border})?{re.escape(_REUSE_START)}.*?{re.escape(_REUSE_END)}\n?(?:{border})?",
        "",
        text,
    )
    text = re.sub(r"\n\n\n+", "\n\n", text)
    licenses_sh.write_text(text)
