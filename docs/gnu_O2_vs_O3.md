# g++ /O2 vs /O3 optimization

*2026-09-26*

## You

g++ optimization switches... /O2 vs /O3 ??

Could you comment on the two options??  
I've never used any level higher than 3, because of warnings (years ago, possibly obsolete ??) that the higher levels used aggressive techniques that were not stable in all cases, but supposedly 2 and 3 are both pretty reliable??

I *did* have one situation, many years ago, where I had a program that worked with /O2, but would crash with /O3 ... don't recall any details, it was 10 or 15 years back, with a *much* earlier version of mingw...

## Claude

Your instinct is mostly right, and the warnings you remember are largely outdated folklore. One correction first: `/O2` and `/O3` are MSVC-style spellings. g++ uses `-O2` and `-O3`, and MinGW accepts only the dash form.

**What each level does**

- **-O2** turns on nearly all optimizations that don't trade code size for speed: inlining of small functions, common subexpression elimination, instruction scheduling, strict-aliasing-based optimizations, and so on. It's the level most distributions use for whole systems, so it's the most heavily tested.
- **-O3** adds more aggressive transformations on top of that: loop vectorization (in recent GCC versions, `-O2` also enables some of this with a cheaper cost model), loop unswitching, function cloning, more aggressive inlining and unrolling, and loop interchange.

**Is -O3 less stable?**

Not in the sense the old warnings implied. Compiler bugs in -O3 passes do occur, but they are rare, and they occur at -O2 too. In practice, when a program works at -O2 and breaks at -O3, the cause is usually one of these:

1. **Undefined behavior in your code** (by far the most common). Examples are signed integer overflow, strict-aliasing violations, out-of-bounds access, uninitialized variables, and reading through misaligned or type-punned pointers. Higher optimization levels exploit UB more aggressively, so latent bugs that "happened to work" surface.
2. **Floating-point differences.** -O3 vectorization can reorder operations, and on x87 (32-bit) it can change intermediate precision. Results differ slightly, and code that compares floats for exact equality can change behavior. Note that `-ffast-math` is separate and is *not* part of any -O level. That one really is risky.
3. **Stack alignment problems on 32-bit Windows.** Vectorized code assumes 16-byte stack alignment for SSE spills, and old MinGW builds had a well-known problem here, especially with threads or callbacks from the Windows API. Your crash from 10 to 15 years ago fits this pattern well, because MinGW/GCC 4.x on Win32 had exactly this issue. It would be crashing in a way that looked random and disappeared at -O2. Modern MinGW-w64 handles it much better.
4. **Genuine compiler bugs**, which exist but are the least likely explanation.

**Practical advice**

- For embedded work, -O2 (or -Os when size matters) is the conventional choice. The speed gain from -O3 is often small and sometimes negative, because bigger code means worse instruction-cache behavior.
- Try -O3 only where you can measure a benefit, such as a tight numeric loop. Then benchmark, since it often shows no difference.
- If you want a safety net, build with `-fsanitize=undefined,address` (available in MinGW-w64 GCC with some limitations) or run under clang's sanitizers at both levels. A program that behaves differently at -O2 and -O3 almost always has a real bug, and those tools will usually find it.
- `-Ofast` is the one to avoid unless you know why you want it, since it enables `-ffast-math` and breaks strict IEEE and standards conformance.

Your caution was reasonable at the time, but on a current toolchain -O3 is safe for correct code. The bigger question is usually whether it's worth using, and for most programs -O2 is the sweet spot.

## You

Thank you, that is a very clear overview!!!!

## Claude

You're welcome, Derell! Glad it helped. If you ever want to test the -O2 vs -O3 question on one of your own projects, the quickest check is to build both ways, compare timings on a representative workload, and run the UB sanitizer on the -O3 build. Happy to help set that up if it comes up.

## You

wait... "UB sanitizer"  ???

## Claude

UB is short for undefined behavior, the C/C++ term for code the standard gives no defined meaning to: signed integer overflow, out-of-bounds array access, shifting by too many bits, dereferencing a null pointer, and so on. The "UB sanitizer" (UBSan) is a compiler feature, not a separate tool. You turn it on with a flag, and the compiler inserts runtime checks that report these problems when they actually happen:

```
g++ -O2 -g -fsanitize=undefined -fno-sanitize-recover=undefined foo.cpp -o foo
```

- `-fsanitize=undefined` enables the checks (overflow, bad shifts, misaligned access, null dereference, and so on).
- `-fno-sanitize-recover=undefined` makes the program abort at the first problem instead of printing a message and continuing.
- `-g` gives you file and line numbers in the report.

When a check fires, you get a message like `foo.cpp:42:15: runtime error: signed integer overflow: 2147483647 + 1 cannot be represented in type 'int'`, which points right at the bug.

Two caveats:

- It only catches UB on code paths that actually execute, so it needs a run that exercises the code.
- It slows the program down and grows it, so it's a testing build, not something to ship.

I also need to correct something from my earlier answer. I lumped `address` in with `undefined` for MinGW-w64 GCC, and that was overstated. AddressSanitizer isn't supported by GCC on Windows. UBSan generally is, provided your MinGW distribution ships the `libubsan` runtime. MSYS2's GCC packages include it, but older standalone MinGW builds may not. If it isn't there, you'll get a linker error about `-lubsan`. Clang in MSYS2's clang64 environment supports both sanitizers, which makes it a handy second compiler for this kind of checking, and it pairs well with the clang-tidy work you've been doing.

For your embedded work, the sanitizers usually can't run on the target itself. The practical approach is to build the portable logic on your PC with UBSan enabled and run your tests there.

## You

interesting... I looked for ubsan in general filenames on my machine, and current `llvm` has these entries... but it's not clear how I would reference these with linker flags...


```
 NDIR 2.71 /64 D:\llvm\lib\clang\23\lib\windows\        Volume label is Bulker
         2,270 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_loop_detect-aarch64.a
         2,236 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_loop_detect-arm.a
         2,440 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_loop_detect-i386.a
         2,274 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_loop_detect-x86_64.a
     1,324,352 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone-aarch64.a
     1,122,622 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone-arm.a
     1,187,770 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone-i386.a
     1,264,564 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone-x86_64.a
        26,506 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone_cxx-aarch64.a
        22,946 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone_cxx-arm.a
        25,402 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone_cxx-i386.a
        26,106 a_____ Sep 22, 2026 09:41:20 libclang_rt.ubsan_standalone_cxx-x86_64.a
```

## Claude

You don't reference them yourself. When you compile and link with `clang++ -fsanitize=undefined`, the driver picks the right runtime from that directory and adds it to the link line based on your target architecture:

```
D:\llvm\bin\clang++ -O2 -g -fsanitize=undefined -fno-sanitize-recover=undefined foo.cpp -o foo.exe
```

**What the files are**

- `libclang_rt.ubsan_standalone-x86_64.a` is the main UBSan runtime for 64-bit x86. The `i386` one is used for 32-bit targets, and the `arm`/`aarch64` ones are for those targets.
- `libclang_rt.ubsan_standalone_cxx-x86_64.a` adds the C++-specific checks (`-fsanitize=vptr` and the dynamic-type checks). The driver adds it when you link with `clang++` and omits it for plain `clang`.
- `ubsan_loop_detect` is one I don't recognize. It's a tiny runtime, so it's presumably for a newer, narrow check in clang 23, and I'd rather not guess. You don't need it for normal UBSan use.

**Checking what the driver does**

To see the actual link line, add `-v`. You should see the `ubsan_standalone` archive(s) named there:

```
D:\llvm\bin\clang++ -v -fsanitize=undefined foo.cpp -o foo.exe
```

**If you ever need to do it manually**

Something like this should work, but it's normally unnecessary:

```
-LD:\llvm\lib\clang\23\lib\windows -lclang_rt.ubsan_standalone-x86_64 -lclang_rt.ubsan_standalone_cxx-x86_64
```

**If you're building with MinGW-style targets**

If you use `--target=x86_64-w64-mingw32`, the driver should find the same runtimes, though sanitizer support there has historically been less polished than for the MSVC-style target. If the link fails, `-v` will show which path the driver was searching.

**Getting readable reports**

For file and line numbers in reports, `llvm-symbolizer.exe` (in `D:\llvm\bin`) needs to be on your PATH. Setting `UBSAN_OPTIONS=print_stacktrace=1` in the environment gives you a stack trace with each report.

Since your LLVM install already ships these, clang's UBSan is probably the easier route for you than hunting for `libubsan` in a MinGW GCC install.

## You

This is so cool!!  new toys... I'll be experimenting with these in coming days...

## Claude

Enjoy the experimenting! A good first target is one of your bigger C++ projects, since large codebases are where latent UB tends to hide. If you want a quick sanity test of the setup itself, compile a tiny file that does `int x = INT_MAX; x++;` with `-fsanitize=undefined` and confirm you get the overflow report. Once that works, everything else is just pointing it at real code.

And if the link step misbehaves or a report looks puzzling, paste it here and I'll help sort it out.
