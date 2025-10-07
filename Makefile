ifeq ($(CONTAINER),container)
$(info Makefile enabled, proceeding ...)
else
$(error Error: Makefile disabled, exiting ...)
endif

ROOT_MAKEFILE:=$(abspath $(patsubst %/, %, $(dir $(abspath $(lastword $(MAKEFILE_LIST))))))

include $(ROOT_MAKEFILE)/.env

export
export PATH := $(PATH):$(shell pwd)/$(UV_INSTALL_DIR)

$(eval UVEL := $(shell which uv && echo "true" || echo ""))
UVE = $(if ${UVEL},'uv',$(UV_INSTALL_DIR)/uv)

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
	$(UVE) run mkdocs build -f configs/dev/mkdocs.yml -d ../../public

serveDocs:
	$(UVE) run mkdocs serve -f configs/dev/mkdocs.yml

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

runUV:
	$(UVE) run $(CMD)

runLock runUpdate: %: export_%
# add all packages rquired to be build
	$(UVE) export --package pkg1 --frozen --format requirements.txt > packages/pkg1/requirements.txt
	$(UVE) export --package shared_utils --frozen --format requirements.txt > packages/shared_utils/requirements.txt
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
	else \
		$(UVE) run cz commit; \
	fi
	echo "" > .commit_msg

recom recommit:
	@if curl -sf http://ollama:11434; then \
		[ ! -s .commit_msg ] || (echo "Missing commit message!" && exit 1); \
		git commit -F .commit_msg; \
	else \
		$(UVE) run cz commit; \
	fi
	echo "" > .commit_msg

PROMPT=Generate a commit message in the Conventional Commits 1.0.0 format for the following git diff. \
The message must follow this structure: \
1. commit type (e.g., feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert) \
2. optional scope in parentheses (e.g., feat(auth):) \
3. description — a brief summary of the change in present tense \
4. optional body — a detailed explanation if needed \
5. optional footer(s) — include breaking changes (if they exist — do not mention “no breaking changes”), issue references (e.g., Closes \#123), or co-authors (e.g., Co-authored-by: Author Name) \
Important formatting rules: \
- the first line (type/scope: description) must be entirely in lowercase \
- the body and footer may use uppercase letters \
- the message must follow Conventional Commits 1.0.0 \
- return only the commit message and use only plain text, no extra formatting \
- do not mention *no breaking changes* explicitly \
Git diff:

message:
	git diff --staged |  paste -s -d ' ' | sed 's/\t/ /g; s/\n/ /g; s/\"//g' | \
		xargs -I {} curl -s -X POST http://ollama:11434/api/generate -H "Content-Type: application/json" \
            -d "{\"stream\": false, \"model\": \"$(OLLAMA_MODEL)\", \"prompt\": \"$(PROMPT) {}\"}" | \
		jq -r 'select(.done == true) | .response' > .commit_msg
	vim .commit_msg
	@if ! $(UVE) run cz check --commit-msg-file .commit_msg; then \
		echo "Commit message failed cz check. Aborting."; \
		echo "" > .commit_msg; \
		exit 1; \
	fi
	git commit -F .commit_msg
