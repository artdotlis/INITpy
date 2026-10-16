# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

ifeq ($(CONTAINER),container)
$(info Makefile enabled, proceeding ...)
else
$(error Error: Makefile disabled, exiting ...)
endif

SHELL := /bin/bash
ROOT_MAKEFILE := $(abspath $(patsubst %/, %, $(dir $(abspath $(lastword $(MAKEFILE_LIST))))))
DISABLE_GIT_ADD ?= 0

$(shell $(ROOT_MAKEFILE)/bin/install/env.sh $(ROOT_MAKEFILE)/package.env > .env.mk 2>/dev/null)
-include .env.mk

export
export PATH := $(PATH):$(ROOT_MAKEFILE)/$(UV_INSTALL_DIR)/:$(ROOT_MAKEFILE)/$(PNPM_HOME)/bin


$(eval UVEL := $(shell which uv && echo "true" || echo ""))
$(eval PNPMEL := $(shell which pnpm && echo "true" || echo ""))
UVE = $(if $(UVEL),uv,$(ROOT_MAKEFILE)/$(UV_INSTALL_DIR)/uv)
PNPME = $(if $(PNPMEL),pnpm,$(ROOT_MAKEFILE)/$(PNPM_HOME)/bin/pnpm)

dev: setup-uv setup-pnpm
	$(UVE) sync --frozen --all-groups
	$(PNPME) install --frozen-lockfile
	@if [ "$(DISABLE_GIT_ADD)" = "1" ]; then \
		echo "Skipping git operations (DISABLE_GIT_ADD=1)"; \
	else \
		find .git/hooks -name "*.old" -delete; \
		$(UVE) run lefthook uninstall 2>&1 || echo "not installed"; \
		$(UVE) run lefthook install; \
	fi

tests: setup-uv
	$(UVE) sync --frozen --group test
	$(PNPME) install --frozen-lockfile

build: setup-uv
	$(UVE) sync --frozen
	$(PNPME) install --frozen-lockfile --prod

docs: setup-uv setup-pnpm
	$(UVE) sync --frozen --group docs
	$(PNPME) install --frozen-lockfile

setup-uv:
	bash $(ROOT_MAKEFILE)/$(BIN_INSTALL_UV)

setup-pnpm:
	bash $(ROOT_MAKEFILE)/$(BIN_INSTALL_PNMP)

unstaged:
	@if [ "$(DISABLE_GIT_ADD)" = "1" ]; then \
		echo "Skipping unstaged check (DISABLE_GIT_ADD=1)"; \
	else \
		if ! git diff --quiet --exit-code; then \
			echo "ERROR: Unstaged changes found!"; \
			git diff; \
			exit 1; \
		fi; \
	fi
	@if [ "$(DISABLE_GIT_ADD)" != "1" ]; then \
		echo "No unstaged changes. Proceeding..."; \
	fi

setup-license: unstaged
	bash $(BIN_RUN_LICENSE_LINT)
	@if [ "$(DISABLE_GIT_ADD)" != "1" ]; then git add .; fi

RAN := $(shell awk 'BEGIN{srand();printf("%d", 65536*rand())}')

run-act:
	@echo "source .venv/bin/activate; rm /tmp/$(RAN)" > /tmp/$(RAN)
	bash --init-file /tmp/$(RAN)

run-checks:
	$(UVE) run lefthook run pre-commit --all-files -f

build-docs:
	cd $(ROOT_MAKEFILE)/$(PKG_DOCS) && $(PNPME) run build

run-docs: build-docs
	$(UVE) run zensical build -f $(CONFIG_DOCS)

serve-docs: build-docs
	$(UVE) run zensical serve -f $(CONFIG_DOCS) -a 0.0.0.0:8000

run-tests:
	cd $(PKG_SHAR) && pytest
	cd $(PKG_SCAF) && pytest

run-build:
	$(UVE) build --package shared-utils
	$(UVE) build --package scaffolder

run-bump: DISABLE_GIT_ADD = 0
run-bump: unstaged
	$(UVE) run cz bump --files-only --yes --changelog
	git add .
	$(UVE) run cz version --project | xargs -i git commit -am "bump: release {}"

run-lock run-update: %: exp-%

exp-run-lock:
	$(UVE) lock
	cd $(PKG_DOCS) && $(PNPME) install --lockfile-only

exp-run-update:
	$(UVE) lock -U
	cd $(PKG_DOCS) && $(PNPME) update

com commit:
	@if [ -f .commit_msg ] && [ -s .commit_msg ]; then \
		$$EDITOR .commit_msg; \
		git commit -F .commit_msg && rm -f .commit_msg; \
	else \
		$(UVE) run cz commit --write-message-to-file .commit_msg && rm -f .commit_msg; \
	fi
