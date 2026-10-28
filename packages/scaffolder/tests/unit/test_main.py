# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Unit tests for scaffolder.main."""

from pathlib import Path
from unittest.mock import patch
import io

from scaffolder.main import run_cli


class TestRunCli:
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
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
            patch("sys.stdout", new=io.StringIO()) as mock_stdout,
        ):
            mock_run.return_value = Path("/tmp/output/test_proj")
            run_cli()
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[0]
            assert call_kwargs[0] == "test_proj"
            assert call_kwargs[1] == "/tmp/output"
            assert call_kwargs[4] == "MIT"

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
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
        ):
            mock_run.return_value = Path("/tmp/out/valid_name")
            run_cli()
            assert mock_run.call_count == 1

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
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
        ):
            mock_run.return_value = Path("/tmp/out/proj")
            run_cli()
            assert mock_run.call_count == 1

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
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
        ):
            mock_run.return_value = Path("/tmp/out/proj")
            run_cli()
            assert mock_run.call_count == 1

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
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
        ):
            mock_run.return_value = Path("/tmp/out/proj")
            run_cli()
            assert mock_run.call_count == 1

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
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
        ):
            mock_run.return_value = Path("/tmp/out/proj")
            run_cli()
            assert mock_run.call_count == 1

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
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
        ):
            mock_run.return_value = Path("/tmp/out/proj")
            run_cli()
            assert mock_run.call_count == 1

    def test_run_exception_handled(self) -> None:
        """Test that exceptions from run() are re-raised."""
        inputs = "proj\ndesc\n/tmp/out\nAuthor\na@b.com\nMIT\n"
        with (
            patch("builtins.input", side_effect=inputs.splitlines()),
            patch("scaffolder.main.run") as mock_run,
        ):
            mock_run.side_effect = RuntimeError("test error")
            try:
                run_cli()
            except RuntimeError as exc:
                assert str(exc) == "test error"
