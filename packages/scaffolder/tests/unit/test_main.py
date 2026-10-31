# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.main."""

from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch
import io

import pytest

from scaffolder.main import run_cli


def _drive(
    inputs: str,
    *,
    scaf_output_dir: str | None = None,
    return_value: Path | None = None,
    exc: Exception | None = None,
):
    """Drive run_cli with mocked io; return the run() mock."""
    env = nullcontext()
    if scaf_output_dir is not None:
        env = patch.dict("os.environ", {"SCAF_OUTPUT_DIR": scaf_output_dir})
    with (
        patch("builtins.input", side_effect=inputs.splitlines()),
        patch("scaffolder.main.run") as mock_run,
        patch("sys.stdout", new=io.StringIO()),
        env,
    ):
        mock_run.return_value = return_value
        mock_run.side_effect = exc
        run_cli()
        return mock_run


class TestRunCli:
    """Tests for the interactive run_cli entry point."""

    @pytest.fixture(autouse=True)
    def clear_scaf_output_dir(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Unset SCAF_OUTPUT_DIR so the output prompt is always shown."""
        monkeypatch.delenv("SCAF_OUTPUT_DIR", raising=False)

    def test_successful_flow(self) -> None:
        """Test the happy-path interactive CLI flow."""
        inputs = (
            "test_proj\n"  # project name (≥3 chars)
            "A description\n"  # description (non-empty)
            "/tmp/output\n"  # output dir (non-empty)
            "Test Author\n"  # author name
            "test@example.com\n"  # author email
            "MIT\n"  # valid license
        )
        mock = _drive(inputs, return_value=Path("/tmp/output/test_proj"))
        mock.assert_called_once()
        call_kwargs = mock.call_args[0]
        assert call_kwargs[0] == "test_proj"
        assert call_kwargs[1] == "/tmp/output"
        assert call_kwargs[4] == "MIT"

    def test_scaf_output_prefix_skips_prompt(self) -> None:
        """When SCAF_OUTPUT_DIR is set it is used as the output prefix."""
        inputs = (
            "test_proj\n"  # project name
            "A description\n"  # description
            "Test Author\n"  # author name
            "test@example.com\n"  # author email
            "MIT\n"  # valid license
        )
        mock = _drive(
            inputs,
            scaf_output_dir="/scaf",
            return_value=Path("/scaf/test_proj"),
        )
        assert mock.call_args[0][1] == "/scaf"

    def test_short_name_rejected(self) -> None:
        """Test that project names <3 chars are rejected."""
        inputs = (
            "ab\n"  # too short, rejected
            "valid_name\n"  # ≥3 chars, accepted
            "A desc\n"
            "/tmp/out\n"
            "Author\n"
            "a@b.com\n"
            "MIT\n"
        )
        assert _drive(inputs, return_value=Path("/tmp/out/valid_name")).call_count == 1

    def test_invalid_license_retries(self) -> None:
        """Test that invalid license prompts again."""
        inputs = (
            "proj\n"
            "desc\n"
            "/tmp/out\n"
            "Author\n"
            "a@b.com\n"
            "INVALID\n"  # invalid
            "MIT\n"  # valid, accepted
        )
        assert _drive(inputs, return_value=Path("/tmp/out/proj")).call_count == 1

    def test_empty_description_rejected(self) -> None:
        """Test that empty description is rejected."""
        inputs = (
            "proj\n"
            "\n"  # empty, rejected
            "desc\n"  # non-empty, accepted
            "/tmp/out\n"
            "Author\n"
            "a@b.com\n"
            "MIT\n"
        )
        assert _drive(inputs, return_value=Path("/tmp/out/proj")).call_count == 1

    def test_empty_output_rejected(self) -> None:
        """Test that empty output dir is rejected."""
        inputs = (
            "proj\n"
            "desc\n"
            "\n"  # empty, rejected
            "/tmp/out\n"  # non-empty, accepted
            "Author\n"
            "a@b.com\n"
            "MIT\n"
        )
        assert _drive(inputs, return_value=Path("/tmp/out/proj")).call_count == 1

    def test_empty_author_rejected(self) -> None:
        """Test that empty author name is rejected."""
        inputs = (
            "proj\n"
            "desc\n"
            "/tmp/out\n"
            "\n"  # empty, rejected
            "Author\n"  # non-empty, accepted
            "a@b.com\n"
            "MIT\n"
        )
        assert _drive(inputs, return_value=Path("/tmp/out/proj")).call_count == 1

    def test_empty_email_rejected(self) -> None:
        """Test that empty author email is rejected."""
        inputs = (
            "proj\n"
            "desc\n"
            "/tmp/out\n"
            "Author\n"
            "\n"  # empty, rejected
            "a@b.com\n"  # non-empty, accepted
            "MIT\n"
        )
        assert _drive(inputs, return_value=Path("/tmp/out/proj")).call_count == 1

    def test_run_exception_handled(self) -> None:
        """Test that exceptions from run() are re-raised."""
        inputs = "proj\ndesc\n/tmp/out\nAuthor\na@b.com\nMIT\n"
        with pytest.raises(RuntimeError, match="test error"):
            _drive(inputs, exc=RuntimeError("test error"))
