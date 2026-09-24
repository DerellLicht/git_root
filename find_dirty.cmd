for /d %%R in (*) do (
    pushd "%%R"
    git diff --quiet -- Makefile || echo DIRTY: %%R
    popd
)
