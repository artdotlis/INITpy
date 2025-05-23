ROOT_MAKEFILE:=$(abspath $(patsubst %/, %, $(dir $(abspath $(lastword $(MAKEFILE_LIST))))))

include $(ROOT_MAKEFILE)/.env

export

UVE := $(UV_INSTALL_DIR)/uv

dev: setup
	$(UVE) sync --frozen --all-groups
	$(UVE) run lefthook uninstall 2>&1
	$(UVE) run lefthook install

tests: setup
	$(UVE) sync --frozen --no-group docs --no-group dev

build: setup
	$(UVE) sync --frozen --no-group test --no-group docs --no-group dev

docs: setup
	$(UVE) sync --froze --no-group test --no-group dev

setup:
	git lfs install || echo '[FAIL] git-lfs could not be installed'
	[ -d "${$(UVE)_INSTALL_DIR}" ] || (curl -LsSf https://astral.sh/uv/install.sh | sh)
	$(UVE) python install $(PYV)
	rm -rf .venv
	$(UVE) venv --python $(PYV) --relocatable --link-mode clone
	$(UVE) pip install --upgrade pip

runAct:
	bash --init-file <(echo "source .venv/bin/activate")

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
	$(UVE) build --package utils

runBump:
	cz bump --files-only --yes --changelog
	git add .
	cz version --project | xargs -i git commit -am "bump: release {}"

run$(UVE):
	$(UVE) run $(CMD)

runLock runUpdate: %: export_%
# add all packages rquired to be build
	$(UVE) export --package pkg1 --frozen --format requirements.txt > packages/pkg1/requirements.txt
	$(UVE) export --package utils --frozen --format requirements.txt > packages/utils/requirements.txt
	$(UVE) export --frozen --only-group dev --format requirements.txt > configs/dev/requirements.dev.txt
	$(UVE) export --frozen --only-group test --format requirements.txt > configs/dev/requirements.test.txt
	$(UVE) export --frozen --only-group docs --format requirements.txt > configs/dev/requirements.docs.txt

export_runLock:
	$(UVE) lock

export_runUpdate:
	$(UVE) lock -U

com commit:
	$(UVE) run cz commit

recom recommit:
	$(UVE) run cz commit --retry
