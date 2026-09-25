# When `D:\clang-22.1.8` finally breaks — what to do

Background: this engine only exists to back **ClaudeLint's** own Python
`libclang` bindings (`--libclang-path`). It has nothing to do with
`clang-tidy` or the actual build — those come from `d:\llvm` and can be
upgraded independently, no issue.

## What the failure will look like

- Surfaces in **`ClaudeLint.py` / `phase0_spike.py`**, not in `make all`
  or `clang-tidy`.
- Symptom: parse diagnostics like `static_assert failed ... requires
  Clang 20 or later` (or similar — the exact number moves over time),
  because the real toolchain's `libc++` headers refuse to compile under
  an engine that's now too old.
- The 2026 upgrade (22.1.7→23.1.2) did **not** trigger this — libc++'s
  minimum-supported-compiler floor trails the newest release by about
  one version, so a same-or-newer-by-1 engine stays safe for a while.
  Eventually a `d:\llvm` version will outrun it.

## How to confirm it's this, not something else

Run `phase0_spike.py --file <name> --target <triple>` against one file.
Clean parse = not this issue. The specific `static_assert`/version
message = it's this.

## Fix, in order of preference

1. **Check `libclang-ng` on PyPI first.** As of 2026 it looked actively
   maintained and tracked recent Clang releases. If it now covers a
   version past whatever floor broke you, `pip install libclang-ng` and
   point `--libclang-path` at its bundled `.dll` — no manual LLVM
   install needed.
2. **If not actively maintained anymore (or not new enough):** download
   an official `clang+llvm-XX.Y.Z-<platform>.tar.xz` from
   github.com/llvm/llvm-project/releases (the archive, not the plain
   installer — it's the one documented to include libclang), install it
   as a new `D:\clang-XX.Y.Z`, and repoint `--libclang-path`. It does
   **not** need to exactly match `d:\llvm`'s version — just be recent
   enough to clear whatever floor is failing.
3. **Either way, spike-test before rolling out**: one small file, one
   heavier STL-using file, across the toolchains you actually use
   (64-bit and 32-bit both, if relevant at that time).
4. **Keep the old engine folder around** until confirmed — same
   low-regret rollback posture as the `d:\llvm` rename trick.

## If none of this is enough

Perfectly fine to just come back and discuss it — upload this file plus
`phase0_spike.py` and `ClaudeLint.py` to start the conversation where we
left off. `ClaudeLint.readme.txt` also has the fuller original story if
memory of *why* any of this exists has faded by then.

## Other things worth remembering

- This is a **separate failure mode from clang-tidy issues** (e.g. new
  warning categories like `bugprone-signed-bitwise` showing up after a
  `d:\llvm` upgrade) — different tool, different fix, don't conflate them.
- `--libclang-path`'s default is hardcoded in both `ClaudeLint.py` and
  `phase0_spike.py` — update both.
