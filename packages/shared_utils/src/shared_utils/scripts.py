# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Shell script manipulation helpers."""

import re
from pathlib import Path


def strip_marked_script_block(path: Path, start_marker: str, end_marker: str, /) -> None:
    """Remove a ``# ==== MARKER:START ====`` block from a shell script.

    Drops the region between ``start_marker`` and ``end_marker`` inclusive,
    along with any surrounding comment/blank border, then collapses runs of
    blank lines left behind.

    Args:
        path: Path to the shell script.
        start_marker: First line of the block to remove.
        end_marker: Last line of the block to remove.
    """
    text = path.read_text()
    border = r"[ \t]*#[ \t-]*\n"
    text = re.sub(
        rf"(?ms)(?:{border})?{re.escape(start_marker)}.*?{re.escape(end_marker)}\n?(?:{border})?",
        "",
        text,
    )
    text = re.sub(r"\n\n\n+", "\n\n", text)
    path.write_text(text)
