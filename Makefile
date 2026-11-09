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
# Env comes straight from package.env (+ nested *.env), no generated file.
define NL


endef
$(eval $(subst |,$(NL),$(shell $(ROOT_MAKEFILE)/bin/install/env.sh | tr '\n' '|')))

.EXPORT_ALL_VARIABLES:

DISABLE_GIT_ADD ?= 0
export DISABLE_GIT_ADD

setup:
	bash $(ROOT_MAKEFILE)/$(BIN_INSTALL_UV)
	bash $(ROOT_MAKEFILE)/$(BIN_INSTALL_PNPM)

dev: setup
	$(UVE) sync --frozen --all-groups
	$(PNPME) install --frozen-lockfile
	@if [ "$(DISABLE_GIT_ADD)" = "1" ]; then \
		echo "Skipping git operations (DISABLE_GIT_ADD=1)"; \
	else \
		find .git/hooks -name "*.old" -delete; \
		$(UVE) run lefthook uninstall 2>&1 || echo "not installed"; \
		$(UVE) run lefthook install; \
	fi

build: setup
	$(UVE) sync --frozen
	$(PNPME) install --frozen-lockfile --prod

run-act:
	@echo "source .venv/bin/activate; rm /tmp/$(RAN)" > /tmp/$(RAN)
	bash --init-file /tmp/$(RAN)

run-checks:
	@if [ "${DISABLE_GIT_ADD}" = "1" ]; then \
		$(UVE) run lefthook run pre-commit --all-files -f --no-stage-fixed; \
	else \
		$(UVE) run lefthook run pre-commit --all-files -f; \
	fi

build-docs: docs-ref
	cd $(ROOT_MAKEFILE)/$(PKG_DOCS) && $(PNPME) run build

run-docs: build-docs
	@echo "docs build complete (CI)"

serve-docs: build-docs
	cd $(PKG_DOCS) && $(PNPME) run preview

docs-ref:
	$(UVE) run griffe2md scaffolder -o $(DOCS_REF_DIR)/scaffolder.md
	$(UVE) run griffe2md shared_utils -o $(DOCS_REF_DIR)/shared_utils.md
	mkdir -p $(DOCS_PARTIALS_DIR)
	cp $(ROOT_MAKEFILE)/README.md $(DOCS_PARTIALS_DIR)/readme.md
	cp $(ROOT_MAKEFILE)/LICENSE $(DOCS_PARTIALS_DIR)/license.md

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

clean:
	bash $(ROOT_MAKEFILE)/bin/install/clean.sh
