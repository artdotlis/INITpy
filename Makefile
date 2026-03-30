# SPDX-FileCopyrightText: 2026 Artur Lissin
#
# SPDX-License-Identifier: Unlicense

ifeq ($(CONTAINER),container)
$(info Makefile enabled, proceeding ...)
else
$(error Error: Makefile disabled, exiting ...)
endif

SHELL := /bin/bash
ROOT_MAKEFILE:=$(abspath $(patsubst %/, %, $(dir $(abspath $(lastword $(MAKEFILE_LIST))))))

$(shell $(ROOT_MAKEFILE)/bin/install/env.sh $(ROOT_MAKEFILE)/package.env > .env.mk 2>/dev/null)
-include .env.mk

export
export PATH := $(PATH):$(shell pwd)/$(UV_INSTALL_DIR)
OLLAMA_MODEL?=qwen3.5:9b

$(eval UVEL := $(shell which uv && echo "true" || echo ""))
UVE = $(if $(UVEL),uv,$(UV_INSTALL_DIR)/uv)

dev: setup
	$(UVE) sync --frozen --all-groups
	$(UVE) run lefthook uninstall 2>&1 || echo "not installed"
	$(UVE) run lefthook install
	@HOOK_FILE=.git/hooks/pre-push; \
	if ! grep -q "git lfs pre-push" $$HOOK_FILE; then \
		echo "command -v git-lfs >/dev/null && git lfs pre-push \"\$$@\"" >> $$HOOK_FILE; \
		echo "added 'git lfs pre-push' to pre-push hook."; \
	fi

tests: setup
	$(UVE) sync --frozen --group test

build: setup
	$(UVE) sync --frozen

docs: setup
	$(UVE) sync --frozen --group docs

setup:
	which uv || [ -d "${UV_INSTALL_DIR}" ] || (curl -LsSf https://astral.sh/uv/install.sh | sh -s - --quiet)
	$(UVE) python install $(PYV)
	rm -rf .venv
	$(UVE) venv --python=$(PYV) --relocatable --link-mode=copy --seed
	$(UVE) pip install --upgrade pip


RAN := $(shell awk 'BEGIN{srand();printf("%d", 65536*rand())}')

runAct:
	echo "source .venv/bin/activate; rm /tmp/$(RAN)" > /tmp/$(RAN)
	bash --init-file /tmp/$(RAN)

runChecks:
	$(UVE) run lefthook run pre-commit --all-files -f

runDocs:
	$(UVE) run mkdocs build -f configs/docs/mkdocs.yml -d ../../public

serveDocs:
	$(UVE) run mkdocs serve -f configs/docs/mkdocs.yml

runTests:
	$(UVE) run tox

runBuild:
# add all packages rquired to be build
	$(UVE) build --package pkg1
	$(UVE) build --package shared_utils

runBump:
	$(UVE) run cz bump --files-only --yes --changelog
	git add .
	$(UVE) run cz version --project | xargs -i git commit -am "bump: release {}"


runLock runUpdate: %: export_%
# add all packages rquired to be build
	$(UVE) export --package pkg1 --frozen --format requirements.txt > packages/pkg1/requirements.prod.txt
	$(UVE) export --package shared_utils --frozen --format requirements.txt > packages/shared_utils/requirements.prod.txt
	$(UVE) export --frozen --only-group dev --format requirements.txt > configs/dev/requirements.dev.txt
	$(UVE) export --frozen --only-group test --format requirements.txt > configs/dev/requirements.test.txt
	$(UVE) export --frozen --only-group docs --format requirements.txt > configs/dev/requirements.docs.txt

export_runLock:
	$(UVE) lock

export_runUpdate:
	$(UVE) lock -U

com commit:
	echo "" > .commit_msg
	@if curl -sf http://ollama:11434; then \
		$(MAKE) message; \
	else\
		$(UVE) run cz commit; \
	fi
	echo "" > .commit_msg

recom recommit:
	@if curl -sf http://ollama:11434; then \
		[ ! -s .commit_msg ] || (echo "Missing commit message!" && exit 1); \
		git commit -F .commit_msg; \
	else\
		$(UVE) run cz commit --retry; \
	fi
	echo "" > .commit_msg

define PROMPT
Generate a commit message in the Conventional Commits 1.0.0 format
based on the following git diff. The commit message must:
- Analyze the diff and summarize the changes accurately:
  1. Include added, removed, or modified functionality.
  2. Ignore cosmetic changes like whitespace or formatting if not relevant.
  3. Exclude changes in files matching 'requirements*.txt'.
- Follow this structure:
  1. Commit type (feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert)
  2. Optional scope in parentheses inferred from the changed file paths (e.g., feat(auth):)
  3. A brief, lowercase description in present tense on the first line
  4. Optional body with detailed explanation. Use uppercase letters to emphasize key points.
     Explain why the change was made and how it affects behavior.
  5. Optional footer(s) with issue references (e.g., Closes #123), co-authors (Co-authored-by: Name),
     or additional metadata if present in the diff.
- Formatting rules:
  1. The first line must be entirely lowercase.
  2. Body lines must be wrapped at 100 characters.
  3. Follow Conventional Commits 1.0.0 strictly.
  4. Return only the commit message as plain text (no markdown, no quotes).
  5. Do not invent breaking changes; only include if explicitly present in the diff.
- Prioritize:
  1. Functional or behavioral changes over formatting changes.
  2. Changes in core logic over trivial modifications.
- Example:
feat(auth): add user login API

Added support for user login via OAuth2. This allows users to authenticate
using their Google account.

Closes #42
endef

message:
	git diff --staged -- . ':(exclude)*requirements*.txt' | \
		jq -Rs --arg prompt "$(PROMPT)" \
			'{"stream": false, "model": "$(OLLAMA_MODEL)", "prompt": ("<GIT_DIFF>" + . + "</GIT_DIFF>" + $$prompt)}' | \
		curl -s -X POST http://ollama:11434/api/generate \
			-H "Content-Type: application/json" \
			-d @- | \
		jq -r 'select(.done == true) | .response' > .commit_msg
	vim .commit_msg
	@if ! $(UVE) run cz check --commit-msg-file .commit_msg; then \
		echo "Commit message failed cz check. Aborting."; \
		echo "" > .commit_msg; \
		exit 1; \
	fi
	git commit -F .commit_msg
