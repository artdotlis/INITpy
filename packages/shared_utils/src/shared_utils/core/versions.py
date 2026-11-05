# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Version comparison helpers."""

__all__ = ["is_version_at_least"]


def is_version_at_least(version: str, minimum: str, /) -> bool:
    """Return True when dotted ``version`` is at least ``minimum``.

    Compares numeric segments left-to-right; shorter versions pad with zero
    segments so ``1.5`` ranks below ``1.5.1``.

    Args:
        version: Actual dotted version, e.g. ``"9.2.0"``.
        minimum: Minimum accepted dotted version, e.g. ``"9.2.0"``.

    Returns:
        True when ``version`` >= ``minimum`` segment-wise.
    """
    v = [int(part) for part in version.split(".")]
    m = [int(part) for part in minimum.split(".")]
    size = max(len(v), len(m))
    v += [0] * (size - len(v))
    m += [0] * (size - len(m))
    return tuple(v) >= tuple(m)
