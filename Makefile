PYV = 3.13.2
UV_CACHE_DIR = .cache
export UV_CACHE_DIR


dev: setup
	uv sync --frozen --all-groups
	uv run lefthook uninstall 2>&1
	uv run lefthook install
	bash bin/deploy/post.sh

tests: setup
	uv sync --frozen --no-group docs --no-group dev

build: setup
	uv sync --frozen --no-group test --no-group docs --no-group dev

docs: setup
	uv sync --froze --no-group test --no-group dev

setup:
	git lfs install || echo '[FAIL] git-lfs could not be installed'
	uv python install $(PYV)
	rm -rf .venv
	uv venv --python $(PYV)
	uv pip install --upgrade pip

runAct:
	bash --init-file <(echo "source .venv/bin/activate")

runChecks:
	uv run lefthook run pre-commit --all-files -f

runDocs:
	uv run mkdocs build -f configs/dev/mkdocs.yml -d ../../public

serveDocs:
	uv run mkdocs serve -f configs/dev/mkdocs.yml

runTests:
	uv run tox

runBuild:
# add all packages rquired to be build
	uv build --package pkg1
	uv build --package utils

runBump:
	cz bump --files-only --yes --changelog
	git add .
	cz version --project | xargs -i git commit -am "bump: release {}"

runUV:
	uv run $(CMD)

runLock runUpdate: %: export_%
# add all packages rquired to be build
	uv export --package pkg1 --frozen --format requirements.txt > packages/pkg1/requirements.txt
	uv export --package utils --frozen --format requirements.txt > packages/utils/requirements.txt
	uv export --frozen --only-group dev --format requirements.txt > configs/dev/requirements.dev.txt
	uv export --frozen --only-group test --format requirements.txt > configs/dev/requirements.test.txt
	uv export --frozen --only-group docs --format requirements.txt > configs/dev/requirements.docs.txt

export_runLock:
	uv lock

export_runUpdate:
	uv lock -U

com commit:
	uv run cz commit

recom recommit:
	uv run cz commit --retry
