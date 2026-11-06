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

pytest_plugins = ("tests.fixture.env",)

# Canonical prompt answers, in prompt order: name, description, output dir,
# author, email, copyright, license, use reuse, use docs.
_PROJECT, _DESCRIPTION, _OUTPUT = "proj", "desc", "/tmp/out"
_ANSWERS = [
    _PROJECT,
    _DESCRIPTION,
    _OUTPUT,
    "Author",
    "a@b.com",
    "Copyright",
    "MIT",
    "",
    "",
]
NAME, DESCRIPTION, OUTPUT, AUTHOR, EMAIL, COPYRIGHT, LICENSE, REUSE, DOCS = range(9)


def _inputs(
    *,
    retried: dict[int, list[str]] | None = None,
    accepted: dict[int, str] | None = None,
    skipped: tuple[int, ...] = (),
    output: str = _OUTPUT,
) -> str:
    """Build run_cli stdin lines from the canonical answers.

    Args:
        retried: Rejected answers to try before the accepted answer index.
        accepted: Answers replacing the canonical value at that index.
        skipped: Prompt indexes not asked (for example a preset output dir).
        output: Answer used for the output-dir prompt.
    """
    answers = list(_ANSWERS)
    answers[OUTPUT] = output
    for index, value in (accepted or {}).items():
        answers[index] = value
    seq: list[str] = []
    for index, answer in enumerate(answers):
        if index in skipped:
            continue
        seq.extend((retried or {}).get(index, []))
        seq.append(answer)
    return "\n".join(seq) + "\n"


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

    def test_successful_flow(self) -> None:
        """Test the happy-path interactive CLI flow."""
        mock = _drive(_inputs(accepted={REUSE: "n"}), return_value=Path("/tmp/x"))
        mock.assert_called_once()
        args = mock.call_args[0][0]
        assert args.project_name == _PROJECT
        assert args.output_dir == _OUTPUT
        assert args.description == _DESCRIPTION
        assert args.license_name == "MIT"
        assert args.copyright == "Copyright"
        assert args.use_reuse is False
        assert args.use_docs is True

    def test_scaf_output_prefix_skips_prompt(self) -> None:
        """When SCAF_OUTPUT_DIR is set it is used as the output prefix."""
        mock = _drive(
            _inputs(skipped=(OUTPUT,)),
            scaf_output_dir="/scaf",
            return_value=Path("/scaf/proj"),
        )
        assert mock.call_args[0][0].output_dir == "/scaf"

    @pytest.mark.parametrize(
        ("index", "rejected_values"),
        [
            pytest.param(NAME, ["ab"], id="short-name"),
            pytest.param(NAME, ["", "x"], id="three-char-name"),
            pytest.param(DESCRIPTION, [""], id="empty-description"),
            pytest.param(OUTPUT, [""], id="empty-output"),
            pytest.param(AUTHOR, [""], id="empty-author"),
            pytest.param(EMAIL, [""], id="empty-email"),
            pytest.param(LICENSE, ["INVALID"], id="invalid-license"),
            pytest.param(REUSE, ["maybe"], id="invalid-reuse"),
            pytest.param(DOCS, ["maybe"], id="invalid-docs"),
        ],
    )
    def test_rejected_answer_is_retried(
        self, index: int, rejected_values: list[str]
    ) -> None:
        """Re-prompt after a rejected answer, then accept the retried value."""
        mock = _drive(_inputs(retried={index: rejected_values}), return_value=Path("/x"))
        mock.assert_called_once()
        args = mock.call_args[0][0]
        assert args.project_name == _PROJECT
        assert args.description == _DESCRIPTION
        assert args.output_dir == _OUTPUT
        assert args.author_name == "Author"
        assert args.author_email == "a@b.com"
        assert args.license_name == "MIT"

    @pytest.mark.parametrize("answer", ["y", "yes", "YES"])
    def test_explicit_yes_answers_keep_both(self, answer: str) -> None:
        """Explicit y/yes answers keep reuse tooling and the docs subpackage."""
        mock = _drive(
            _inputs(accepted={REUSE: answer, DOCS: answer}),
            return_value=Path("/x"),
        )
        args = mock.call_args[0][0]
        assert args.use_reuse is True
        assert args.use_docs is True

    def test_no_answers_drop_both(self) -> None:
        """Explicit 'n' answers drop the reuse tooling and the docs subpackage."""
        mock = _drive(_inputs(accepted={REUSE: "n", DOCS: "n"}), return_value=Path("/x"))
        args = mock.call_args[0][0]
        assert args.use_reuse is False
        assert args.use_docs is False

    def test_run_exception_handled(self) -> None:
        """Test that exceptions from run() are re-raised."""
        with pytest.raises(RuntimeError, match="test error"):
            _drive(_inputs(), exc=RuntimeError("test error"))

    def test_failure_removes_partial_output_dir(self, tmp_path: Path) -> None:
        """A failed run deletes the partially scaffolded output directory."""
        partial = tmp_path / _PROJECT
        partial.mkdir()
        (partial / "leftover.txt").write_text("x")
        with pytest.raises(RuntimeError, match="test error"):
            _drive(_inputs(output=str(tmp_path)), exc=RuntimeError("test error"))
        assert not partial.exists()

    def test_failure_removes_partial_output_file(self, tmp_path: Path) -> None:
        """A failed run unlinks a partial output path that is a file."""
        partial = tmp_path / _PROJECT
        partial.write_text("x")
        with pytest.raises(RuntimeError, match="test error"):
            _drive(_inputs(output=str(tmp_path)), exc=RuntimeError("test error"))
        assert not partial.exists()

    def test_failure_without_partial_output_keeps_tree(self, tmp_path: Path) -> None:
        """Leave unrelated files in place when nothing was scaffolded."""
        keep = tmp_path / "keep.txt"
        keep.write_text("x")
        with pytest.raises(RuntimeError, match="test error"):
            _drive(_inputs(output=str(tmp_path)), exc=RuntimeError("test error"))
        assert keep.exists()
