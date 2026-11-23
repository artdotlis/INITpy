set shell := [
    'bash',
    '-cu',
    '''
[ "${CONTAINER:-}" = container ] || { echo "Error: run just inside the dev container only, exiting ..." >&2; exit 1; }
source bin/install/env.sh
: "${DISABLE_GIT_ADD:=0}"
eval "$0"
''',
]

setup:
    bash "$BIN_INSTALL_UV"
    bash "$BIN_INSTALL_PNPM"

prepare: setup
    case "${COMPONENT:-all}" in \
        py) "$UVE" sync --frozen;; \
        docs) "$UVE" sync --frozen && "$PNPME" install --frozen-lockfile;; \
        all) "$UVE" sync --frozen --all-groups && "$PNPME" install --frozen-lockfile;; \
        *) echo "Error: unknown component '${COMPONENT:-}' (use py, docs or all)" >&2; exit 1;; \
    esac
    if [ "$DISABLE_GIT_ADD" = "1" ]; then \
        echo "Skipping git operations (DISABLE_GIT_ADD=1)"; \
    else \
        find .git/hooks -name "*.old" -delete; \
        "$UVE" run lefthook uninstall 2>&1 || echo "not installed"; \
        "$UVE" run lefthook install; \
    fi

run-act:
    RAN=$$ && \
    echo "source .venv/bin/activate; source bin/install/env.sh; rm /tmp/$RAN" > /tmp/$RAN && \
    bash --init-file /tmp/$RAN

run-checks:
    if [ "$DISABLE_GIT_ADD" = "1" ]; then \
        "$UVE" run lefthook run pre-commit --all-files -f --no-stage-fixed; \
    else \
        "$UVE" run lefthook run pre-commit --all-files -f; \
    fi

run-docs:
    "$UVE" run griffe2md scaffolder -o "$DOCS_REF_DIR/scaffolder.md"
    "$UVE" run griffe2md shared_utils -o "$DOCS_REF_DIR/shared_utils.md"
    mkdir -p "$DOCS_PARTIALS_DIR"
    sed -E '/^\[!\[/d' README.md > "$DOCS_PARTIALS_DIR/readme.md"
    cp LICENSE "$DOCS_PARTIALS_DIR/license.md"
    cd "$PKG_DOC" && "$PNPME" run build

serve-docs: run-docs
    cd "$PKG_DOC" && "$PNPME" run preview

run-tests:
    "$UVE" run lefthook run tests

run-build:
    "$UVE" build --package shared-utils && \
    "$UVE" build --package scaffolder

bump:
    NEW_VER=$("$UVE" run bash bin/install/bump.sh | tail -1) && \
    echo "bumped to $NEW_VER" && \
    just lock && \
    git add . && \
    git commit -am "bump: release $NEW_VER"

lock:
    "$UVE" lock
    cd "$PKG_DOC" && "$PNPME" install --lockfile-only

update:
    "$UVE" lock -U
    cd "$PKG_DOC" && "$PNPME" update

com:
    if [ -f .commit_msg ] && [ -s .commit_msg ]; then \
        "$EDITOR" .commit_msg; \
        git commit -F .commit_msg && rm -f .commit_msg; \
    else \
        "$UVE" run cz commit --write-message-to-file .commit_msg && rm -f .commit_msg; \
    fi

clean:
    bash bin/install/clean.sh
