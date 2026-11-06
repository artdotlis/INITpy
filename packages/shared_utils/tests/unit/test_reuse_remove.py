# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.licenses.reuse_remove."""

import re
from pathlib import Path

import tomlkit

from shared_utils.licenses.reuse_remove import (
    _prune_dockerignore,
    _remove_reuse_dependency,
    remove_reuse,
)
from shared_utils.core.versions import is_version_at_least

pytest_plugins = ("tests.fixture.template",)

# Minimum accepted pins for deps left in pyproject.toml after remove_reuse.
# Kept as min-version baselines only, so a routine dependency bump in the
# template does not force a test edit.
MIN_PYTEST = "9.2.0"
MIN_GRIFFE2MD = "1.5.1"


def _pinned_at_least(dependency: str, package: str, minimum: str) -> bool:
    """Return True when ``dependency`` pins ``package == <v>`` with v >= minimum."""
    match = re.match(rf"{re.escape(package)} ==([0-9]+(?:\.[0-9]+)+)", dependency)
    return match is not None and is_version_at_least(match.group(1), minimum)


class TestRemoveReuse:
    """Tests for remove_reuse against the live template tree."""

    def test_removes_reuse_tooling(
        self,
        tmp_path: Path,
        licenses_dir: Path,
        package_json_license: Path,
        docs_pkg: Path,
        pyproject_toml: Path,
        licenses_sh: Path,
        lefthook_yml: Path,
        license_file: Path,
        dockerignore: Path,
    ) -> None:
        """Drop reuse dirs, configs, dep, script section, lefthook job, ignore entry."""
        remove_reuse(tmp_path)

        # the LICENSES dir and the docs REUSE.toml are deleted
        assert not licenses_dir.exists()
        assert not (docs_pkg / "REUSE.toml").exists()
        # .license companions are owned by strip_spdx_headers, not remove_reuse
        assert package_json_license.exists()
        # the LICENSE file itself is kept
        assert license_file.read_text().strip()

        pydoc = tomlkit.parse(pyproject_toml.read_text())
        # project has no dependencies at all; reuse lives only in the dev group
        assert pydoc["project"].get("dependencies") is None
        dev_deps = pydoc["dependency-groups"]["dev"]
        assert not any(str(dep).startswith("reuse") for dep in dev_deps)
        # pinned dep versions must stay at/above the minimum template baseline
        assert any(
            _pinned_at_least(str(dep), "pytest", MIN_PYTEST)
            for dep in pydoc["dependency-groups"]["test"]
        )
        # unrelated groups are untouched
        assert any(
            _pinned_at_least(str(dep), "griffe2md", MIN_GRIFFE2MD)
            for dep in pydoc["dependency-groups"]["docs"]
        )

        script = licenses_sh.read_text()
        assert "reuse lint" not in script
        assert "REUSE:START" not in script
        # non-reuse license checks stay
        assert "LICENSE file not found" in script

        # the reuse *.license fixing job is dropped from lefthook too
        text = lefthook_yml.read_text()
        assert "fix-all-addable-files" not in text
        assert "license" in text

        # the dead !LICENSES negation is pruned, the kept LICENSE one stays
        entries = [line.strip() for line in dockerignore.read_text().splitlines()]
        assert "!LICENSES" not in entries
        assert "!LICENSE" in entries


class TestRemoveReuseHelpers:
    """Tests for the individual remove_reuse helpers."""

    def test_prune_dockerignore_without_file(self, tmp_path: Path) -> None:
        """Do nothing when the repository has no .dockerignore."""
        _prune_dockerignore(tmp_path / ".dockerignore")

    def test_prune_dockerignore_drops_negation(self, dockerignore: Path) -> None:
        """Drop the dead !LICENSES negation from the live .dockerignore."""
        assert "!LICENSES" in dockerignore.read_text()
        _prune_dockerignore(dockerignore)
        entries = [line.strip() for line in dockerignore.read_text().splitlines()]
        assert "!LICENSES" not in entries
        assert "!LICENSE" in entries

    def test_remove_reuse_dependency_strips_project_deps(
        self, pyproject_toml: Path
    ) -> None:
        """Strip reuse from the project deps and the dev group alike."""
        doc = tomlkit.parse(pyproject_toml.read_text())
        doc["project"]["dependencies"] = ["reuse ==6.0.0", "tomlkit"]
        doc["dependency-groups"]["dev"].append("reuse ==6.0.0")
        pyproject_toml.write_text(tomlkit.dumps(doc))

        _remove_reuse_dependency(pyproject_toml)

        result = tomlkit.parse(pyproject_toml.read_text())
        assert result["project"]["dependencies"] == ["tomlkit"]
        assert not any(
            str(dep).startswith("reuse") for dep in result["dependency-groups"]["dev"]
        )

    def test_remove_reuse_dependency_without_project_deps(
        self, pyproject_toml: Path
    ) -> None:
        """Keep a pyproject that has no project dependencies valid."""
        _remove_reuse_dependency(pyproject_toml)
        result = tomlkit.parse(pyproject_toml.read_text())
        assert result["project"].get("dependencies") is None
