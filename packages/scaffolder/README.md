<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: CC0-1.0
-->

# scaffolder

**Automation suite for INITpy-based projects.**

---

## 📦 About

`scaffolder` generates new projects from the INITpy template. It clones the
template repository, applies your project name, author, and license, prunes
the layout to the requested shape (monorepo, docs, reuse), locks dependencies,
and commits the result.

Because it is part of a monorepo, the package is **private** - it
should not be published to PyPI - and is built along with the other
packages via the `uv` build system.

---

## 📚 Installation

The package is built alongside the rest of the repository when you run `just run-build` from the root; there is no separate installation step. Add any external dependencies to this module’s `[project.dependencies]`.

---

## ⚙️ Usage

The package exposes a console script named `scaffolder`. Its entry point is `scaffolder.main:run_cli`, which launches an interactive CLI.

### Local (in the dev container)

```bash
scaffolder
```

### In the production container

The root `docker-compose.yml` `scaffolder` service mounts `${SCAF_OUTPUT_DIR}` (default `./PROJECTS`) at `/scaf` and exposes it to the CLI as `SCAF_OUTPUT_DIR`. The CLI uses it as a fixed prefix: the output-directory prompt is skipped and the project name is appended.

```bash
docker compose up -d
docker compose exec -it scaffolder scaffolder
```

Projects land at `SCAF_OUTPUT_DIR/<project-name>` (default `./PROJECTS/<project-name>`).
