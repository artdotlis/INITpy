<!--
SPDX-FileCopyrightText: 2026 Artur Lissin

SPDX-License-Identifier: CC0-1.0
-->

# 🛠️ INITpy

### A Bare-Bone Python Monorepo Template

[![release: 0.8.0](https://img.shields.io/badge/rel-0.8.0-blue.svg?style=flat-square)](https://github.com/artdotlis/INITpy)
[![The Unlicense](https://img.shields.io/badge/License-Unlicense-brightgreen.svg?style=flat-square)](https://choosealicense.com/licenses/unlicense/)
[![Documentation Status](https://img.shields.io/badge/docs-GitHub-blue.svg?style=flat-square)](https://artdotlis.github.io/INITpy/)

[![main](https://github.com/artdotlis/INITpy/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/artdotlis/INITpy/actions/workflows/main.yml)


**INITpy** is a minimal, opinionated project layout designed for modern Python development. It leverages `uv` for lightning-fast environment management, `tox` for testing, and `zensical` for documentation.

-----

## ✨ Key Features

  * **Single-Source Truth:** Tooling and dependencies are declared in one `pyproject.toml`.
  * **Native Monorepo Support:** Built-in logic for managing multiple packages (`pkg1`, `shared_utils`).
  * **AI-Powered Commits:** Integration with **Ollama** to generate Conventional Commit messages based on your staged changes.
  * **Strict Consistency:** A Docker-based Dev Container ensures every contributor uses the exact same tool versions.
  * **Robust CI/CD:** Ready-to-go workflows for testing, linting (`ruff`), and static analysis (`pyrefly`).

-----

## 🚀 Quick Start

If you are using **VS Code** and have the **Dev Containers** extension, simply open the folder and click **"Reopen in Container"**.

Alternatively, via CLI:

```bash
# 1. Clone the template
git clone https://github.com/artdotlis/INITpy.git && cd INITpy

# 2. Spin up the environment (Requires Docker)
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . bash

# 3. Bootstrap the project (Inside the container)
make dev
make runAct
```

-----

## 🏗️ Project Structure

```text
INITpy/
├── bin/                # Tooling shell scripts
├── configs/            # Tooling & Linting configurations
├── docs/               # Documentation configuration
├── packages/           # Your Python packages (Monorepo)
│   ├── pkg1/
│   └── shared_utils/
├── pyproject.toml      # The heart of the project
└── Makefile            # Command automation (requires CONTAINER=container)
```

-----

## 🛠️ Development Workflow

### Makefile Command Reference

All commands must be run within the Dev Container or by passing `CONTAINER=container`.

| Category | Command | Action |
| :--- | :--- | :--- |
| **Setup** | `make dev` | Installs `uv`, Python, and git hooks. |
| **Active** | `make runAct` | Enters the virtual environment shell. |
| **Quality** | `make runChecks` | Runs `ruff`, `pyrefly`, and other pre-commit hooks. |
| **Test** | `make runTests` | Runs the test suite via `tox`. |
| **Docs** | `make serveDocs` | Previews documentation at `localhost:$DOC_PORT`. |
| **Release** | `make runBump` | Bumps version and updates CHANGELOG. |
| **Git** | `make commit` | Generates AI commit message (via Ollama) or opens `cz`. |

### 🧠 Smart Commits

The `make commit` target checks if an Ollama server is reachable.

  - **If Ollama is up:** It sends your `git diff` to the model, generates a message, and opens `vim` for you to edit.
  - **If Ollama is down:** It falls back to standard `commitizen` prompts.

-----

## 📚 Documentation

The API documentation is built with **Zensical**.

  - **Build:** `make runDocs`
  - **Serve:** `make serveDocs`

-----

## 📜 License

Released into the public domain via the [Unlicense](https://choosealicense.com/licenses/unlicense/). No strings attached.

-----

### Why the `CONTAINER=container` guard?

To prevent accidental execution on your host, this `Makefile` uses a mandatory `CONTAINER` constraint. This safety gate ensures the code runs exclusively in the intended containerized environment.
