# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Docs (VitePress) amendment and removal for a generated project."""

import re
import shutil
from pathlib import Path

import tomlkit
from tomlkit import TOMLDocument

from shared_utils.lefthook import remove_lefthook_jobs
from shared_utils.lefthook import round_trip_yaml
from shared_utils.scripts import strip_marked_script_block


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


def remove_docs(path: Path, /) -> None:
    """Remove the ``docs`` subpackage and every VitePress/docs mention.

    Deletes ``packages/docs`` and strips docs references from the workspace
    config, pyproject.toml, Makefile, CI workflows, lint scripts, package.env
    and .gitignore so no dangling docs wiring remains.

    Args:
        path: Root of the generated project.
    """
    docs_dir = path / "packages" / "docs"
    shutil.rmtree(docs_dir) if docs_dir.is_dir() else docs_dir.unlink()

    _remove_docs_pyproject(path / "pyproject.toml")
    _remove_docs_pnpm_workspace(path / "pnpm-workspace.yaml")
    _drop_docs_make_targets(path / "Makefile")
    remove_lefthook_jobs(path / "lefthook.yml", "docs")
    _drop_docs_env(path / "package.env")
    _drop_docs_env_script(path / "bin" / "lint" / "lint_env.sh")
    strip_marked_script_block(
        path / "bin" / "install" / "clean.sh", _DOCS_START, _DOCS_END
    )
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
    yaml = round_trip_yaml()
    doc = yaml.load(workspace_yaml.read_text())
    packages = doc.get("packages")
    if isinstance(packages, list):
        doc["packages"] = [entry for entry in packages if str(entry) != "packages/docs"]
        if not doc["packages"]:
            del doc["packages"]
    with workspace_yaml.open("w") as stream:
        yaml.dump(doc, stream)


_DOCS_MAKE_TARGETS = ("build-docs", "run-docs", "serve-docs", "docs-ref")
_DOCS_TARGET_BLOCK_RE = re.compile(
    rf"^(?:{'|'.join(re.escape(t) for t in _DOCS_MAKE_TARGETS)}):.*?$\n"
    rf"(?:\t[^\n]*$\n?)*\n?",
    re.M,
)


def _drop_docs_make_targets(makefile: Path, /) -> None:
    """Remove docs build targets from a Makefile.

    Verifies every remaining docs target is present, drops each target block
    (header, recipe lines and one trailing blank), then strips any recipe line
    in kept targets (e.g. ``exp-run-lock`` / ``exp-run-update``) that still
    maintains the removed ``packages/docs`` lockfile. ``docs:`` itself is not
    required — the template has no bare ``docs``/``tests`` targets (replaced by
    ``dev``).
    """
    text = makefile.read_text()
    missing = [
        t for t in _DOCS_MAKE_TARGETS if not re.search(rf"(?m)^{re.escape(t)}:", text)
    ]
    if missing:
        raise ValueError("Makefile missing docs target(s): " + ", ".join(missing))
    text = _DOCS_TARGET_BLOCK_RE.sub("", text)
    # Drop recipe lines in kept targets that maintain the removed docs lockfile.
    text = re.sub(r"(?m)^\t[^\n]*\$\(PKG_DOCS\)[^\n]*\n", "", text)
    makefile.write_text(text)


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
