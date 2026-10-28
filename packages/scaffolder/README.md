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

## 📚 Installation & Build

The package is automatically built when you run:

```bash
# From the repository root
make run-build
```

There is no separate `pip install` step for consuming `scaffolder` from
outside this repo; it is included in the repository’s wheel
distribution.

If you add external dependencies, declare them in the root
`pyproject.toml` or in this sub‑module’s `[project.dependencies]`.

---

## ⚙️ Usage

### Console script

```bash
# From the repository root (or any virtual‑env that has the repo’s
# packages on `sys.path`):
scaffolder
```

Running the script will execute `scaffolder.main:run`.

### Importing in code

```python
from scaffolder.main import run
```

---

## 📚 Modules

| Module            | Description                                                                                                                     |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `scaffolder.main` | The application's main entry point; it coordinates the work performed by `scaffolder` and pulls in helpers from `shared_utils`. |
