# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""File transformation functions for scaffolding."""

from pathlib import Path

from shared_utils.files import strip_spdx_headers


def amend_docs(path: Path, package_name: str, project_name: str) -> None:
    """Step 9: update docs/README.md and .zensical.toml."""
    (path / "packages" / "docs" / "README.md").write_text(
        f'--8<-- "README.md"\n\n--8<-- "packages/{package_name}/README.md"\n'
    )
    index = path / "packages" / "docs" / "src" / "index.md"
    index.write_text(f"# {project_name}\n\nBlank init project\n")
    zensical = path / ".zensical.toml"
    text = zensical.read_text()
    text = text.replace("INIT PY", project_name)
    text = text.replace("artdotlis/INITpy", f"artdotlis/{project_name}")
    zensical.write_text(text)


def update_envs(path: Path, package_name: str) -> None:
    """Step 10: update PKG_SCAF / PKG_SHAR in env files."""
    _update_pkg_vars(path / "package.env", package_name)
    lint_env = path / "bin" / "lint" / "lint_env.sh"
    content = lint_env.read_text()
    content = content.replace(
        "PKG_SCAF=packages/scaffolder", f"PKG_SCAF=packages/{package_name}"
    )
    content = content.replace(
        "PKG_SHAR=packages/shared_utils", f"PKG_SHAR=packages/{package_name}"
    )
    lint_env.write_text(content)


def replace_authors(path: Path, email: str) -> None:
    """Step 12: replace author email in config files."""
    for fpath in (path / "pyproject.toml", path / "package.env"):
        if fpath.exists():
            fpath.write_text(fpath.read_text().replace("artdotlis@pm.me", email))


def replace_project_name(path: Path, name: str) -> None:
    """Step 13: replace all INITpy references."""
    for root, dirs, files in path.walk():
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__")]
        for fname in files:
            if fname.endswith((".py", ".sh", ".toml", ".env", ".md", ".yml")):
                fpath = root / fname
                try:
                    text = fpath.read_text().replace("INITpy", name)
                    fpath.write_text(text)
                except Exception:
                    pass


def strip_spdx(path: Path) -> None:
    """Step 14: remove SPDX headers and .license files."""
    strip_spdx_headers(path)


def set_version(path: Path) -> None:
    """Step 17: set version to 0.1.0 everywhere."""
    for fpath in path.rglob("*"):
        if fpath.is_file() and fpath.suffix in (".py", ".sh", ".toml", ".md"):
            text = fpath.read_text()
            if "0.11.0" in text or "0.9.4" in text:
                fpath.write_text(
                    text.replace("0.11.0", "0.1.0").replace("0.9.4", "0.1.0")
                )


def fix_licenses(path: Path, license_name: str) -> None:
    """Step 18: clear LICENSES/ and write LICENSE."""
    lic_dir = path / "LICENSES"
    if lic_dir.is_dir():
        for f in lic_dir.iterdir():
            if f.is_file():
                f.unlink()

    path.joinpath("LICENSE").write_text(f"# TODO finish: {license_name}\n\n")

    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text()
        text = "\n".join(
            f'license = "{license_name}"'
            if line.strip().startswith("license =")
            else line
            for line in text.splitlines()
        )
        pyproject.write_text(text)


def update_licenses_sh(path: Path) -> None:
    """Step 16: add leading error exit to licenses.sh."""
    licenses_sh = path / "bin" / "lint" / "licenses.sh"
    if not licenses_sh.exists():
        return
    text = licenses_sh.read_text()
    # Insert warning after shebang
    warning = """# TODO: Complete license implementation before use.
# This script will fail until licenses are properly configured.\n\n"""
    # Insert after the shebang line
    if text.startswith("#!"):
        first_newline = text.index("\n")
        text = text[: first_newline + 1] + warning + text[first_newline + 1 :]
    licenses_sh.write_text(text)


def _update_pkg_vars(path: Path, package_name: str) -> None:
    text = path.read_text()
    text = "\n".join(
        l
        for l in text.splitlines()
        if not l.startswith("PKG_SCAF=packages/scaffolder")
        and not l.startswith("PKG_SHAR=packages/shared_utils")
    )
    text += f"\nPKG_SCAF=packages/{package_name}\nPKG_SHAR=packages/{package_name}\n"
    path.write_text(text)
