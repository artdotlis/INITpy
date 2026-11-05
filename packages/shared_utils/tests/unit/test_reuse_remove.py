# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for shared_utils.reuse_remove."""

from pathlib import Path


import tomlkit

from shared_utils.reuse_remove import remove_reuse


class TestRemoveReuse:
    """Tests for remove_reuse."""

    def test_removes_reuse_structure(self, tmp_path: Path) -> None:
        """Delete reuse dirs, REUSE.toml, dep, and script section."""
        # reuse directories + files
        (tmp_path / "LICENSES").mkdir()
        (tmp_path / "LICENSES" / "Unlicense.txt").write_text("x")
        (tmp_path / "package.json.license").write_text("x")
        reuse_toml = tmp_path / "packages" / "docs" / "REUSE.toml"
        reuse_toml.parent.mkdir(parents=True)
        reuse_toml.write_text("x")

        # keep LICENSE file
        (tmp_path / "LICENSE").write_text("keep me")

        # pyproject with a reuse dependency in the dev dependency group
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text(
            '[project]\nname = "x"\ndependencies = ["requests"]\n'
            "[dependency-groups]\n"
            'dev = ["pytest", "reuse ==6.2.0"]\n'
        )

        # licenses.sh with marked reuse section
        licenses_sh = tmp_path / "bin" / "lint" / "licenses.sh"
        licenses_sh.parent.mkdir(parents=True)
        licenses_sh.write_text(
            "#!/bin/bash\n"
            "echo non-reuse\n"
            "# ===== REUSE:START =====\n"
            "reuse lint\n"
            "# ===== REUSE:END =====\n"
            "echo tail\n"
        )
        # lefthook.yml (always present in the template)
        (tmp_path / "lefthook.yml").write_text("pre-commit:\n  jobs: []\n")

        remove_reuse(tmp_path)

        assert not (tmp_path / "LICENSES").exists()
        assert not (tmp_path / "packages" / "docs" / "REUSE.toml").exists()
        # .license companions are owned by strip_spdx_headers, not remove_reuse
        assert (tmp_path / "package.json.license").exists()
        assert (tmp_path / "LICENSE").read_text() == "keep me"

        pydoc = tomlkit.parse(pyproject.read_text())
        assert "reuse ==6.2.0" not in pydoc["project"]["dependencies"]
        assert "requests" in pydoc["project"]["dependencies"]
        dev_deps = pydoc["dependency-groups"]["dev"]
        assert "reuse ==6.2.0" not in dev_deps
        assert "pytest" in dev_deps

        script = licenses_sh.read_text()
        assert "reuse lint" not in script
        assert "REUSE:START" not in script
        assert "echo non-reuse" in script
        assert "echo tail" in script

    def test_removes_reuse_lefthook_job(self, tmp_path: Path) -> None:
        """Drop the *.license fixing job from lefthook.yml."""
        (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
        licenses_sh = tmp_path / "bin" / "lint" / "licenses.sh"
        licenses_sh.parent.mkdir(parents=True)
        licenses_sh.write_text("#!/bin/bash\necho x\n")
        lefthook = tmp_path / "lefthook.yml"
        lefthook.write_text(
            "pre-commit:\n"
            "  jobs:\n"
            "    - name: license\n"
            "    - name: fix-all-addable-files\n"
            "      env:\n"
            "        ALL_FILES: $(find . -name '*.license' -type f)\n"
        )
        remove_reuse(tmp_path)
        text = lefthook.read_text()
        assert "fix-all-addable-files" not in text
        assert "license" in text
