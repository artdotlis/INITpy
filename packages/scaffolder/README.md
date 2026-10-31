<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: CC0-1.0
-->

# scaffolder

**An example package that lives inside the INITpy monorepo.**

---

## 📦 About

`scaffolder` is one of the first‑level projects bundled in the repository.  
It demonstrates how a standalone application can depend on the
internal `shared_utils` library and expose a console script entry
point (`scaffolder`).

Because it is part of a monorepo, the package is **private** - it
should not be published to PyPI - and is built along with the other
packages via the `uv` build system.

---

## 📚 Installation

The package is built alongside the rest of the repository when you run `make run-build` from the root; there is no separate installation step. Add any external dependencies to this module’s `[project.dependencies]`.

---

## ⚙️ Usage

The package exposes a console script named `scaffolder`. Its entry point is `scaffolder.main:run_cli`, which launches an interactive CLI.
