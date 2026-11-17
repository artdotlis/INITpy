# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""End-to-end tests: run the whole pipeline for every output variant.

The template clone is fed from this repository (``git archive``) and the two
network/install steps are stubbed, so every other step runs for real.
"""

import shutil
import subprocess
import tomllib
from collections.abc import Callable
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest
from scaffolder.scaffold.core import ScaffoldArgs
from scaffolder.scaffold.core import run

_REPO_ROOT = Path(__file__).resolve().parents[4]
_PROJECT = "My Project"
_PKG = "my_project_pkg"

# (use_monorepo, use_docs, use_reuse)
_VARIANTS = [
    (monorepo, docs, reuse)
    for monorepo in (True, False)
    for docs in (True, False)
    for reuse in (True, False)
]


def _fake_clone(path: Path, template_url: str, ref: str, /) -> None:
    """Unpack the repo tree instead of cloning it (no network)."""
    del template_url, ref
    path = Path(path)
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    archive = subprocess.run(
        ["git", "archive", "HEAD"],
        cwd=_REPO_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(path)], input=archive, check=True)
    (path / ".git").mkdir()


def _fake_license_file(path: Path, license_name: str, /) -> None:
    """Write a dummy license instead of downloading it (no network)."""
    Path(path).write_text(f"{license_name} license text\n")


def _fake_lock(path: Path, /) -> None:
    """Skip ``uv lock`` / ``pnpm install`` (no network, no installs)."""
    del path


@pytest.fixture
def scaffold(
    tmp_path: Path,
) -> Iterator[Callable[..., Path]]:
    """Return a callable that runs the full pipeline for one variant."""
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    def _make(
        *, use_monorepo: bool = True, use_docs: bool = True, use_reuse: bool = True
    ) -> Path:
        args = ScaffoldArgs(
            project_name=_PROJECT,
            output_dir=str(out_dir),
            author_name="Ann",
            author_email="ann@example.com",
            license_name="MIT",
            description="A demo",
            copyright="2026 Ann",
            use_reuse=use_reuse,
            use_docs=use_docs,
            use_monorepo=use_monorepo,
        )
        return run(args)

    with (
        patch("scaffolder.scaffold.core.clone_git", _fake_clone),
        patch("scaffolder.scaffold.core.lock_project", _fake_lock),
        patch("scaffolder.scaffold.licenses.write_license", _fake_license_file),
    ):
        yield _make


class TestAllVariants:
    """One test per (monorepo, docs, reuse) output variant."""

    @pytest.mark.parametrize(("use_monorepo", "use_docs", "use_reuse"), _VARIANTS)
    def test_output(
        self,
        scaffold: Callable[..., Path],
        use_monorepo: bool,
        use_docs: bool,
        use_reuse: bool,
    ) -> None:
        """Generate the project and check the simple output expectations."""
        path = scaffold(use_monorepo=use_monorepo, use_docs=use_docs, use_reuse=use_reuse)
        pkg_dir = path / "packages" / _PKG if use_monorepo else path

        assert path.is_dir()
        assert (path / ".git").is_dir()
        assert _PROJECT in (path / "README.md").read_text()
        assert (path / "LICENSE").is_file()
        assert (path / "LICENSE").read_text() != ""
        assert (path / "pyproject.toml").is_file()
        assert not (path / "PROJECTS").exists()
        assert (path / "docker-compose.yml").is_file()
        assert not (path / "configs" / "docker" / "prod.Dockerfile").exists()

        # package files
        assert (pkg_dir / "src" / _PKG / "main.py").is_file()
        assert (pkg_dir / "src" / _PKG / "py.typed").is_file()
        assert (pkg_dir / "tests" / "unit" / f"test_{_PKG}.py").is_file()

        # monorepo vs flat
        assert (path / "packages").is_dir() is use_monorepo
        assert (path / "package.json").is_file() is use_monorepo
        assert not (path / "packages" / "scaffolder").exists()
        assert not (path / "packages" / "shared_utils").exists()

        # docs kept only in a monorepo when requested
        assert (path / "packages" / "docs").is_dir() is (use_monorepo and use_docs)
        docs_yml = path / ".github" / "workflows" / "docs.yml"
        assert docs_yml.is_file() is (use_monorepo and use_docs)

        # reuse tooling only when requested
        assert (path / "LICENSES").is_dir() is use_reuse

    @pytest.mark.parametrize(("use_monorepo", "use_docs", "use_reuse"), _VARIANTS)
    def test_root_project_name(
        self,
        scaffold: Callable[..., Path],
        use_monorepo: bool,
        use_docs: bool,
        use_reuse: bool,
    ) -> None:
        """Name the root project after the package, or the project in a monorepo."""
        path = scaffold(use_monorepo=use_monorepo, use_docs=use_docs, use_reuse=use_reuse)
        text = (path / "pyproject.toml").read_text()
        pyproject = tomllib.loads(text)
        assert pyproject["project"]["name"] == (_PROJECT if use_monorepo else _PKG)
        assert pyproject["project"]["description"] == "A demo"
        assert pyproject["project"]["license"] == "MIT"
        # monorepo workspace layout vs single installable package
        assert ("[tool.uv.workspace]" in text) is use_monorepo
        assert f"package = {'false' if use_monorepo else 'true'}" in text

    @pytest.mark.parametrize(("use_monorepo", "use_docs", "use_reuse"), _VARIANTS)
    def test_package_file_matches_project(
        self,
        scaffold: Callable[..., Path],
        use_monorepo: bool,
        use_docs: bool,
        use_reuse: bool,
    ) -> None:
        """Point the package pyproject at the generated package."""
        path = scaffold(use_monorepo=use_monorepo, use_docs=use_docs, use_reuse=use_reuse)
        pkg_dir = path / "packages" / _PKG if use_monorepo else path
        pyproject = tomllib.loads((pkg_dir / "pyproject.toml").read_text())
        assert pyproject["project"]["name"] == _PKG
        assert pyproject["project"]["version"] == "0.1.0"
        assert pyproject["project"]["description"] == "A demo"


class TestFailingInput:
    """One test for the failure output."""

    def test_unknown_license_raises(
        self, tmp_path: Path, scaffold: Callable[..., Path]
    ) -> None:
        """Fail loudly instead of producing a project with an unknown license."""
        del scaffold
        out_dir = tmp_path / "bad"
        out_dir.mkdir()
        args = ScaffoldArgs(
            project_name=_PROJECT,
            output_dir=str(out_dir),
            author_name="Ann",
            author_email="ann@example.com",
            license_name="NotALicense",
            description="A demo",
            copyright="2026 Ann",
            use_reuse=True,
            use_docs=True,
            use_monorepo=True,
        )
        with (
            patch("scaffolder.scaffold.core.clone_git", _fake_clone),
            patch("scaffolder.scaffold.core.lock_project", _fake_lock),
            pytest.raises(ValueError, match="Unknown SPDX license"),
        ):
            run(args)
