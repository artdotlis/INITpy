# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

"""Lefthook YAML helpers."""

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


def round_trip_yaml() -> YAML:
    """Return a YAML instance that preserves quotes and mapping indent.

    Returns:
        A round-trip ``YAML`` emitter configured for the template files.
    """
    yaml = YAML()
    yaml.preserve_quotes = True  # noqa: Vulture
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.width = 2**31  # noqa: Vulture
    return yaml


def _prune_jobs(jobs: list[Any], /) -> None:
    """Recursively drop empty group entries from a lefthook ``jobs`` list."""
    kept: list[Any] = []
    for job in jobs:
        if not isinstance(job, dict):
            kept.append(job)
            continue
        group = job.get("group")
        if isinstance(group, dict) and isinstance(group.get("jobs"), list):
            _prune_jobs(group["jobs"])
            if not group["jobs"]:
                continue
        kept.append(job)
    jobs[:] = kept


def prune_lefthook_hooks(doc: dict[str, Any], /) -> None:
    """Drop lefthook hooks and groups left without jobs.

    Args:
        doc: Parsed lefthook.yml document.
    """
    to_del: list[str] = []
    for hook, body in doc.items():
        if not isinstance(body, dict):
            continue
        jobs = body.get("jobs")
        if isinstance(jobs, list):
            _prune_jobs(jobs)
        commands = body.get("commands")
        has_jobs = isinstance(jobs, list) and len(jobs) > 0
        has_commands = isinstance(commands, dict) and len(commands) > 0
        if not has_jobs and not has_commands:
            to_del.append(hook)
    for hook in to_del:
        del doc[hook]


def _remove_named_jobs(jobs: list[object], name: str, /) -> None:
    """Recursively drop jobs named `name` from a lefthook ``jobs`` list."""
    kept: list[object] = []
    for job in jobs:
        if isinstance(job, dict) and job.get("name") == name:
            continue
        group = job.get("group") if isinstance(job, dict) else None
        if isinstance(group, dict) and isinstance(group.get("jobs"), list):
            _remove_named_jobs(group["jobs"], name)
        kept.append(job)
    jobs[:] = kept


def remove_lefthook_jobs(path: Path, name: str, /) -> None:
    """Remove every lefthook job named `name` from ``lefthook.yml``.

    Drops the job wherever it appears (top level or inside a group), prunes
    now-empty hooks and groups, and writes the file back.

    Args:
        path: Path to ``lefthook.yml``.
        name: Job name to remove.
    """
    yaml = round_trip_yaml()
    doc = yaml.load(path.read_text())
    for hook in doc.values():
        jobs = hook.get("jobs") if isinstance(hook, dict) else None
        if isinstance(jobs, list):
            _remove_named_jobs(jobs, name)
    prune_lefthook_hooks(doc)
    with path.open("w") as stream:
        yaml.dump(doc, stream)
