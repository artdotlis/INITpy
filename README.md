<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: CC0-1.0
-->

# 🛠️ INITpy

### A Bare-Bone Python Monorepo Template

[![release: 0.11.0](https://img.shields.io/badge/rel-0.11.0-blue.svg?style=flat-square)](https://github.com/artdotlis/INITpy)
[![License: Unlicense](https://img.shields.io/badge/License-Unlicense-green.svg?style=flat-square)](https://unlicense.org)
[![Documentation Status](https://img.shields.io/badge/docs-GitHub-blue.svg?style=flat-square)](https://artdotlis.github.io/INITpy/)

[![lin_lint](https://github.com/artdotlis/INITpy/actions/workflows/lin_lint.yml/badge.svg?branch=main)](https://github.com/artdotlis/INITpy/actions/workflows/lin_lint.yml)

**INITpy** is a minimal, opinionated project layout designed for modern Python development. It leverages `uv` for environment management, `pytest` for testing, and `vitepress` for documentation.

---

## ⭐ Key Features

- **Single-Source Truth:** Python dependencies managed via `uv` in `pyproject.toml`.
- **Native Monorepo Support:** Built-in logic for managing multiple packages (`scaffolder`, `shared_utils`).
- **Conventional Commits:** Uses `commitizen` with `vim` for editing commit messages.
- **Strict Consistency:** A Docker-based Dev Container ensures every contributor uses the exact same tool versions.
- **Robust CI/CD:** Ready-to-go workflows for testing, linting (`ruff`), and static analysis (`pyrefly`).
- **Documentation:** Built with `vitepress` and deployed via GitHub Pages.

---

## ▶️ Quick Start

If you are using **VS Code** and have the **Dev Containers** extension, simply open the folder and click **"Reopen in Container"**.

Alternatively, via CLI:

```bash
# 1. Clone the template
git clone https://github.com/artdotlis/INITpy.git && cd INITpy

# 2. Spin up the environment (Requires Docker)
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . bash

# 3. Bootstrap the project (Inside the container)
just dev
just run-act
```

---

## 🏗️ Project Structure

```text
INITpy/
├-- .devcontainer/      # Dev Container definition
├-- .github/            # CI workflows
├-- bin/                # Tooling shell scripts
├-- configs/            # Tooling, Linting & Docker configurations
│   └-- docker/         # dev.Dockerfile & prod.Dockerfile
├-- packages/           # Your Python packages (Monorepo)
│   ├-- docs/
│   ├-- scaffolder/
│   └-- shared_utils/
├-- PROJECTS/           # Default scaffolder output (kept via inner .gitignore)
├-- LICENSES/           # REUSE license texts
├-- docker-compose.yml  # Scaffolder service definition
├-- lefthook.yml        # Git hook definitions
├-- pyproject.toml      # The heart of the project
└-- justfile            # Command runner (requires CONTAINER=container)
```

---

## 🛠️ Development Workflow

### Justfile Command Reference

All commands must be run within the Dev Container or by passing `CONTAINER=container`.

| Category    | Command                                   | Action                                                                               |
| :---------- | :---------------------------------------- | :----------------------------------------------------------------------------------- |
| **Setup**   | `just setup`, `just dev`                  | Installs tooling; `dev` also syncs all dependencies and installs lefthook hooks.     |
| **Active**  | `just run-act`                            | Enters the virtual environment shell.                                                |
| **Build**   | `just run-build`                          | Builds all packages as wheels via `uv`.                                              |
| **Quality** | `just run-checks`                         | Runs `lefthook` pre-commit hooks (lint + static analysis)                            |
| **Test**    | `just run-tests`                          | Runs the pytest suite and enforces the coverage floor for all packages.              |
| **Docs**    | `just run-docs`, `serve-docs`             | Builds and serves the VitePress site, with API reference partials regenerated.       |
| **Deps**    | `just lock`, `update`             | Locks or updates the `uv` and `pnpm` lockfiles.                                      |
| **Release** | `just bump`                               | Bumps the version and updates the CHANGELOG.                                         |
| **Git**     | `just commit`, `just com`                 | Generates commit message with `commitizen` or opens `vim` for editing, then commits. |
| **Clean**   | `just clean`                              | Removes build artifacts and caches via `bin/install/clean.sh`.                       |

### ✍️ Commit Messages

The `just commit`/`just com` recipe:

- If `.commit_msg` exists and is non-empty: opens it in `vim` for editing, then commits
- Else: runs `cz commit --write-message-to-file` to generate a commit message, commits using that message

> **Note**: The Makefile removes `.commit_msg` after committing (temp file cleanup).

---

## 🪄 Running the Scaffolder (Production)

The `scaffolder` service provides a **production** container with the interactive `scaffolder` CLI, and mounts a host folder at `/scaf` (exposed to the CLI as `SCAF_OUTPUT_DIR`).

- **Host folder:** `SCAF_OUTPUT_DIR`, set at `docker compose up` time (default `./PROJECTS`).
- **Mount:** `${SCAF_OUTPUT_DIR}:/scaf`; inside the container `SCAF_OUTPUT_DIR=/scaf`.
- The CLI treats `SCAF_OUTPUT_DIR` as a fixed prefix: the output-directory prompt is skipped and the project name is appended to it.

```bash
USER_UID=$(id -u) USER_GID=$(id -g) SCAF_OUTPUT_DIR=/some/host/folder docker compose up -d

docker compose exec -it scaffolder scaffolder
```

Projects land at `SCAF_OUTPUT_DIR/<project-name>` on the host (default `./PROJECTS/<project-name>`).

---

## 📚 Documentation

The API documentation is generated with **griffe2md** and served with **VitePress**.

- **Build only:** `just run-docs` (also used in CI)
- **Build + local preview:** `just serve-docs`

---

## ⚖️ License

Released into the public domain via the [Unlicense](https://choosealicense.com/licenses/unlicense/). No strings attached.

---

### Why the `CONTAINER=container` guard?

To prevent accidental execution on your host, `Makefile` uses a mandatory `CONTAINER` constraint. This safety gate ensures the code runs exclusively in the intended containerized environment.

---

> ✏️ **Note**:
> This project uses AI tools for code generation, review, and documentation.
> All AI-generated content is human-reviewed.
