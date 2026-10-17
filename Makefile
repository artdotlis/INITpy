# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

ifeq ($(CONTAINER),container)
$(info Makefile enabled, proceeding ...)
else
$(error Error: Makefile disabled, exiting ...)
endif

RAN := $(shell awk 'BEGIN{srand();printf("%d", 65536*rand())}')
ROOT_MAKEFILE := $(abspath $(patsubst %/, %, $(dir $(abspath $(lastword $(MAKEFILE_LIST))))))
$(shell $(ROOT_MAKEFILE)/bin/install/env.sh 2>/dev/null || true)
-include .env.mk

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
	$(UVE) run lefthook run tests

run-build:
	$(UVE) build --package shared-utils
	$(UVE) build --package scaffolder

run-bump: DISABLE_GIT_ADD = 0
run-bump:
	bash $(BIN_RUN_UNSTAGED)
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
