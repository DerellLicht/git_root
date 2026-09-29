#!/usr/bin/env python3
"""
fix_compile_commands.py

compiledb (run against whatever the active build toolchain is -- Cygwin,
TDM, etc.) stamps every entry's compiler field with that build's actual
compiler (e.g. Cygwin's x86_64-w64-mingw32-g++). clang-tidy / ClaudeLint
need to see an LLVM clang++ invocation instead, so this rewrites the
compiler field of every entry in compile_commands.json to point at the
correct LLVM clang++ (x86_64 or i686), leaving every other flag, define
and include path untouched.

Usage:
    python fix_compile_commands.py --64      (default if no flag given)
    python fix_compile_commands.py --32
    python fix_compile_commands.py --64 --file path\\to\\compile_commands.json
"""

import argparse
import json
import sys
from pathlib import Path

CLANG_64 = "d:/llvm/bin/x86_64-w64-mingw32-clang++"
CLANG_32 = "d:/llvm/bin/i686-w64-mingw32-clang++"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--64", dest="use64", action="store_true",
                        help="point compile_commands.json at the x86_64 LLVM clang++")
    group.add_argument("--32", dest="use64", action="store_false",
                        help="point compile_commands.json at the i686 LLVM clang++")
    parser.set_defaults(use64=True)
    parser.add_argument("--file", default="compile_commands.json",
                         help="path to compile_commands.json (default: ./compile_commands.json)")
    args = parser.parse_args()

    clang_path = CLANG_64 if args.use64 else CLANG_32

    ccpath = Path(args.file)
    if not ccpath.is_file():
        sys.exit(f"error: {ccpath} not found")

    with ccpath.open("r", encoding="utf-8") as f:
        entries = json.load(f)

    changed = 0
    for entry in entries:
        # current compiledb format: a list under "arguments", argv[0] is the compiler
        if "arguments" in entry and entry["arguments"]:
            if entry["arguments"][0] != clang_path:
                entry["arguments"][0] = clang_path
                changed += 1
        # older compiledb format: a single "command" string
        elif "command" in entry:
            parts = entry["command"].split(None, 1)
            rest = parts[1] if len(parts) > 1 else ""
            new_command = f"{clang_path} {rest}" if rest else clang_path
            if entry["command"] != new_command:
                entry["command"] = new_command
                changed += 1

    with ccpath.open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=1)
        f.write("\n")

    arch = "x86_64" if args.use64 else "i686"
    print(f"fix_compile_commands: pointed {changed}/{len(entries)} entries "
          f"in {ccpath} at the {arch} LLVM clang++")


if __name__ == "__main__":
    main()
