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

$(shell $(ROOT_MAKEFILE)/bin/install/env.sh $(ROOT_MAKEFILE)/package.env > .env.mk 2>/dev/null)
-include .env.mk

export
export PATH := $(PATH):$(ROOT_MAKEFILE)/$(UV_INSTALL_DIR)/:$(ROOT_MAKEFILE)/$(PNPM_HOME)/bin


$(eval UVEL := $(shell which uv && echo "true" || echo ""))
$(eval PNPMEL := $(shell which pnpm && echo "true" || echo ""))
UVE = $(if $(UVEL),uv,$(ROOT_MAKEFILE)/$(UV_INSTALL_DIR)/uv)
PNPME = $(if $(PNPMEL),pnpm,$(ROOT_MAKEFILE)/$(PNPM_HOME)/bin/pnpm)

dev: setupUv setupPnpm
	$(UVE) sync --frozen --all-groups
	find .git/hooks -name "*.old" -delete
	$(UVE) run lefthook uninstall 2>&1 || echo "not installed"
	$(UVE) run lefthook install

tests: setupUv
	$(UVE) sync --frozen --group test

build: setupUv
	$(UVE) sync --frozen

docs: setupUv setupPnpm
	$(UVE) sync --frozen --group docs

setupUv:
	bash $(ROOT_MAKEFILE)/$(BIN_INSTALL_UV)

setupPnpm:
	bash $(ROOT_MAKEFILE)/$(BIN_INSTALL_PNMP)

unstaged:
	@if ! git diff --quiet --exit-code; then \
		echo "ERROR: Unstaged changes found!"; \
		git diff; \
		exit 1; \
	fi
	@echo "No unstaged changes. Proceeding..."

setupLicense: unstaged
	bash $(BIN_RUN_LICENSE_LINT)
	git add .

RAN := $(shell awk 'BEGIN{srand();printf("%d", 65536*rand())}')

runAct:
	@echo "source .venv/bin/activate; rm /tmp/$(RAN)" > /tmp/$(RAN)
	bash --init-file /tmp/$(RAN)

runChecks:
	$(UVE) run lefthook run pre-commit --all-files -f

buildDocs:
	cd $(ROOT_MAKEFILE)/$(PKG_DOCS) && $(PNPME) run build

runDocs: buildDocs
	$(UVE) run zensical build -f $(CONFIG_DOCS)

serveDocs: buildDocs
	$(UVE) run zensical serve -f $(CONFIG_DOCS) -a 0.0.0.0:8000

runTests:
	$(UVE) run tox

runBuild:
	$(UVE) build --package shared-utils
	$(UVE) build --package pkg1

runBump: unstaged
	$(UVE) run cz bump --files-only --yes --changelog
	git add .
	$(UVE) run cz version --project | xargs -i git commit -am "bump: release {}"

runLock runUpdate: %: export_%

export_runLock:
	$(UVE) lock
	cd $(PKG_DOCS) && $(PNPME) install --lockfile-only

export_runUpdate:
	$(UVE) lock -U
	cd $(PKG_DOCS) && $(PNPME) update

com commit:
	@if [ -f .commit_msg ] && [ -s .commit_msg ]; then \
		$$EDITOR .commit_msg; \
		git commit -F .commit_msg && rm -f .commit_msg; \
	else \
		$(UVE) run cz commit --write-message-to-file .commit_msg && rm -f .commit_msg; \
	fi
