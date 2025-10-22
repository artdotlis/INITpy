# INITpy – A Bare‑Bone Python Project Template

[![release: 0.7.0](https://img.shields.io/badge/rel-0.7.0-blue.svg?style=flat-square)](https://github.com/artdotlis/INITpy)
[![The Unlicense](https://img.shields.io/badge/License-Unlicense-brightgreen.svg?style=flat-square)](https://choosealicense.com/licenses/unlicense/)
[![Documentation Status](https://img.shields.io/badge/docs-GitHub-blue.svg?style=flat-square)](https://artdotlis.github.io/INITpy/)

[![main](https://github.com/artdotlis/INITpy/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/artdotlis/INITpy/actions/workflows/main.yml)

> **A minimal, opinionated, and fully‑automated Python project layout.**

---

## 🛠️ Development Workflow

### 1. Dev Container (Optional)

The project ships with a Docker‑Compose powered dev container. It automatically installs all dev dependencies - ideal for a consistent and sandboxed development environment.

Inside the container you can use the `make` targets as below.

#### Prerequisites

- **GNU/Linux**
- **Docker**
- **Docker Compose**
- **Dev Container CLI**

#### Steps

1. Clone the repository:
   ```sh
   git clone https://github.com/artdotlis/INITpy.git
   cd INITpy
   ```

2. If using Docker, start the development container manually or use VSCode:
   ```sh
   devcontainer up --workspace-folder .
   devcontainer exec --workspace-folder . bash
   ```

3. Create and activate a virtual environment (inside docker the container):
   ```sh
   make dev
   make runAct
   ```

### 2. Makefile Targets

| Target            | Purpose |
|-------------------|---------|
| `dev`             | Sets up the development environment, installs the frozen dependency set, and installs the git hooks. |
| `tests`           | Synchronises the test‑only dependency set. |
| `build`           | Synchronises the build‑time dependency set. |
| `docs`            | Synchronises the docs‑only dependency set. |
| `setup`           | Installs **uv**, the specified Python version, creates a relocatable virtual environment, and upgrades pip. |
| `runAct`          | Activates the `.venv` and cleans a temporary file. |
| `runChecks`       | Runs the pre‑commit hook suite (`lefthook run pre-commit`). |
| `runDocs`         | Builds the MkDocs site (using the dev configuration). |
| `serveDocs`       | Serves the MkDocs site locally. |
| `runTests`        | Executes the test suite via **tox**. |
| `runBuild`        | Builds the declared packages (`pkg1`, `shared_utils`). |
| `runBump`         | Bumps the version with **cz** and commits the change. |
| `runUV`           | Executes an arbitrary `uv` command passed in `CMD`. |
| `runLock / runUpdate` | Exports the frozen dependency set to `requirements.txt` files for each package/group and locks the environment. Also updates the dependencies in `runUpdate`. |
| `com commit`      | Generates a Conventional Commit message (via ollama or `cz`), validates it, and commits. |
| `recom recommit`  | Commits the previously generated message (again validating with `cz`). |

> **Important** – the Makefile is guarded by `ifeq ($(CONTAINER),container)`; if `CONTAINER` is not set to `container` the make process aborts with an error.  
> To run the targets, set the variable on the command line, e.g. `make CONTAINER=container dev`, or run it from inside the dev container.

---

## 📚 Documentation

The full API documentation is built with **MkDocs** and automatically deployed to GitHub Pages.

```bash
# Build the site into the `public/` folder
make runDocs
```

You can preview the documentation locally while you work:

```bash
# Start a lightweight development server
make serveDocs
```

Open `http://localhost:8000` to explore.

---

## 🚀 Features

- **Zero‑configuration** – All tooling, dependencies, and build settings are declared in a single `pyproject.toml` file.
- **Monorepo‑friendly** – The layout supports multiple packages in a single repository, making it ideal for mono‑repo workflows.
- **Modern tooling** – Linting, formatting, static analysis, and security checks are handled by `black`, `ruff`, and `mypy`.
- **Testing** – Automated tests run with `tox`, and coverage reports are generated automatically.
- **Packaging** – Distribution follows PEP 621; the project can be built and published via `uv` or `pip`.
- **Documentation** – MkDocs generates a fully‑static site from Markdown; it can be previewed locally or published to GitHub Pages.
- **Containerised development** – A Docker‑Compose dev container replicates the CI environment, ensuring consistent tool versions.
- **License** – The project is released into the public domain under the Unlicense.

---

## 📜 License

This project is licensed under the [Unlicense](https://choosealicense.com/licenses/unlicense/).  
Feel free to use, modify, and distribute it without any restrictions.
