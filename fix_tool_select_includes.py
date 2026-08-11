#!/usr/bin/env python3
"""
Update Makefiles under each repo subfolder so their
`include ..\\tool_select.mak` line points at the right copy of
tool_select.mak:

  - der_libs\\tool_select.mak  if the repo has a der_libs subfolder
  - .\\tool_select.mak         if it doesn't (and prints a reminder
                                to copy tool_select.mak in by hand)

Run this from the Git parent folder (the one containing all the repo
subfolders), or pass that folder's path as an argument.
"""

import sys
from pathlib import Path

OLD_LINE = "include ..\\tool_select.mak"
NEW_LINE_WITH_DER_LIBS = "include der_libs\\tool_select.mak"
NEW_LINE_NO_DER_LIBS = "include .\\tool_select.mak"


def process_repo(repo_dir: Path) -> None:
    """
    Look at a single repo subfolder. If it has a Makefile, find the line
    that includes tool_select.mak from the parent folder and rewrite it
    to point at der_libs\\ (if that subfolder exists) or .\\ (if not).
    When der_libs is missing, also print a reminder to copy
    tool_select.mak into the repo folder by hand. Does nothing if no
    Makefile is present.
    """
    makefile_path = repo_dir / "Makefile"
    if not makefile_path.is_file():
        return

    der_libs_present = (repo_dir / "der_libs").is_dir()
    new_line = NEW_LINE_WITH_DER_LIBS if der_libs_present else NEW_LINE_NO_DER_LIBS

    lines = makefile_path.read_text(encoding="utf-8").splitlines(keepends=True)

    # Walk every line, matching on content only (ignoring the line
    # ending), so we can preserve whatever line ending (\n or \r\n)
    # the file already used.
    changed = False
    for i, line in enumerate(lines):
        stripped = line.rstrip("\r\n")
        if stripped.strip() == OLD_LINE:
            eol = line[len(stripped):]
            lines[i] = new_line + eol
            changed = True

    if not changed:
        print(f"[skip]   {repo_dir.name}: no '{OLD_LINE}' line found in Makefile")
        return

    makefile_path.write_text("".join(lines), encoding="utf-8")

    if der_libs_present:
        print(f"[ok]     {repo_dir.name}: updated to use der_libs\\tool_select.mak")
    else:
        print(f"[ACTION] {repo_dir.name}: updated to use .\\tool_select.mak "
              f"-- copy tool_select.mak into this folder!")


def main() -> None:
    """
    Entry point: figure out the Git parent folder (current directory,
    or a path passed as the first command-line argument), then process
    every immediate subfolder as a repo.
    """
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    root = root.resolve()

    if not root.is_dir():
        print(f"Error: {root} is not a folder")
        sys.exit(1)

    print(f"Scanning repos under: {root}\n")

    for entry in sorted(root.iterdir()):
        if entry.is_dir():
            process_repo(entry)


if __name__ == "__main__":
    main()
