# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Git-related utilities."""

import shutil
import subprocess
from pathlib import Path


def clone_template(template_url: str, temp_dir: Path) -> None:
    """Clone a template repository.

    Args:
        template_url: URL of the template repository
        temp_dir: Path where the template should be cloned

    Raises:
        subprocess.CalledProcessError: If git clone fails
    """
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    subprocess.run(
        ["git", "clone", template_url, str(temp_dir)], check=True, capture_output=True
    )
