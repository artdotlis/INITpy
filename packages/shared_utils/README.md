<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: CC0-1.0
-->

# shared_utils

**Shared utility library for all the packages in this repository.**

---

## 📦 About

`shared_utils` is a lightweight, internal library that provides a common set of helper functions, data‑structures, and utilities used across the various top‑level packages in the repository. It is **private** - not intended to be uploaded to PyPI - and is bundled with the main project via the `uv` monorepo build system.

---

## 📚 Installation

The library is automatically built and packaged when you run `make run-build` from the repository root. There is no separate installation step required for consuming code in this mono‑repo.

If you need to add dependencies to the shared library, add them under the `[project.dependencies]` section of the root `pyproject.toml` or in this sub‑module's `pyproject.toml`.

---

## ⚙️ Usage

Import functions directly from the package:

```python
from shared_utils import sanitize_package_name, clone_template
from shared_utils import init_git, update_package_imports, update_readme
```

### Modules

| Module  | Functions                                 |
| ------- | ----------------------------------------- |
| `names` | `sanitize_package_name`                   |
| `git`   | `clone_template`, `init_git`              |
| `files` | `update_package_imports`, `update_readme` |
