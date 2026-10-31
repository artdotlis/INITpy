<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: CC0-1.0
-->

# shared_utils

**Shared utility library for all the packages in this repository.**

---

## 📦 About

`shared_utils` is a lightweight, internal library that provides common helper functions and utilities used across the repository's packages. It is **private** (not intended for PyPI) and is bundled with the repository through the `uv` monorepo build system.

---

## 📚 Installation

The library is built alongside the rest of the repository when you run `make run-build` from the root; there is no separate installation step. Add any dependencies to this module's `[project.dependencies]`.

---

## ⚙️ Usage

This is an internal library, so you import functions directly from its submodules, for example `from shared_utils.names import sanitize_package_name`.
