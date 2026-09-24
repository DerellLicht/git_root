#!/usr/bin/env python3
"""
migrate_release_mak.py -- rewrite a project's Makefile to pull its release
plumbing from the shared der_libs\\release.mak include, instead of carrying
its own copy of check-clean/notes/release/update/retag/re-release/sha256.

What it does, in order:
  1. Removes the local "VERSION := $(shell grep ... CHANGELOG.md ...)"
     assignment (and its one-line comment, if present) -- VERSION now comes
     from release.mak. DIST_ZIP and everything else that references
     $(VERSION) is left untouched.
  2. Removes the target blocks (comment + recipe) for any of: release,
     update, check-clean, retag, re-release, sha256 -- these now live in
     release.mak. Any OTHER target (dist, clean, wc, cppc, check, clint,
     depend, etc.) is left exactly as-is.
  3. Only if step 1 or 2 actually found something to remove: inserts
     "include der_libs\\release.mak" right after the existing
     "include der_libs\\tool_select.mak" line (skipped if already there).
     If NEITHER step found anything -- i.e. this Makefile never had its
     own release/update/etc. targets to begin with -- the include is
     deliberately NOT inserted, and nothing else in the file is touched.
     This is what protects a personal-use repo (no CHANGELOG.md, never
     released) from getting release.mak wired in for no reason, which
     would otherwise break plain "make" there.
  4. Strips those same names back out of any ".PHONY:" line, leaving the
     rest of that line untouched.

Safe to re-run: steps that find nothing to do (include already present,
target already gone) are silent no-ops.

Usage:
    python migrate_release_mak.py [path-to-Makefile]

With no argument, edits ".\\Makefile" in the current directory, in place.
Preserves the file's original line-ending style (CRLF vs LF) and prints a
short summary of what actually changed.
"""

import re
import sys
from pathlib import Path

# Target names now supplied by der_libs\release.mak -- their blocks (and
# their .PHONY entries) get stripped out of the project Makefile.
SHARED_TARGETS = ["release", "update", "check-clean", "retag", "re-release", "sha256"]

TOOL_SELECT_INCLUDE = r"include der_libs\tool_select.mak"
RELEASE_MAK_INCLUDE = r"include der_libs\release.mak"

# Comment line + VERSION assignment, e.g.:
#   # Automatically parse the latest version block
#   VERSION := $(shell grep -oE '\[[0-9]+\.[0-9]+\]' CHANGELOG.md | head -n 1 | tr -d '[]')
VERSION_BLOCK_RE = re.compile(
    r"(?:^#[^\n]*\n)?"
    r"^VERSION\s*:=\s*\$\(shell\s+grep.*?CHANGELOG\.md.*?\)\s*\n",
    re.MULTILINE,
)


def target_block_re(name):
    """
    Matches one target's full block: any comment lines immediately above it
    (no blank line in between), the "name:" line itself, all its recipe
    lines (tab-indented), and a single trailing blank line if there is one.
    """
    return re.compile(
        r"(?:^#[^\n]*\n)*"
        r"^" + re.escape(name) + r"\s*:[^\n]*\n"
        r"(?:\t[^\n]*\n)*"
        r"\n?",
        re.MULTILINE,
    )


def strip_phony_names(text, names):
    """Remove the given target names from any .PHONY: line, word by word."""
    def repl(m):
        prefix, rest = m.group(1), m.group(2)
        words = [w for w in rest.split() if w not in names]
        return prefix + (" " + " ".join(words) if words else "")

    return re.sub(r"^(\.PHONY:)(.*)$", repl, text, flags=re.MULTILINE)


def migrate(text):
    """Apply all edits to normalized (LF-only) text; returns (new_text, changes)."""
    changes = []

    # 1. Drop the local VERSION parse.
    new_text, n = VERSION_BLOCK_RE.subn("", text)
    version_found = bool(n)
    if n:
        changes.append("removed local VERSION := $(shell grep ...) block")
    text = new_text

    # 2. Drop each shared target's block, tracking whether we found any.
    #    This doubles as the signal for step 3: no target blocks found means
    #    this Makefile never had its own release/update/etc. -- e.g. a
    #    personal-use repo with no CHANGELOG.md that was never meant to get
    #    der_libs\release.mak in the first place. Inserting the include
    #    there would just break "make" for no reason (release.mak's
    #    VERSION/.DEFAULT_GOAL logic assumes a project that does releases).
    targets_found = False
    for name in SHARED_TARGETS:
        new_text, n = target_block_re(name).subn("", text)
        if n:
            changes.append(f"removed '{name}:' target block")
            targets_found = True
        text = new_text

    # 3. Insert the release.mak include after tool_select.mak's -- but only
    #    if this repo actually had release plumbing to strip (see above).
    if not (version_found or targets_found):
        changes.append(
            "no release/update/check-clean/etc. targets found -- treating "
            "this as a repo that never did releases; NOT inserting include "
            "der_libs\\release.mak (nothing else changed)"
        )
        return text, changes

    if RELEASE_MAK_INCLUDE not in text:
        if TOOL_SELECT_INCLUDE in text:
            text = text.replace(
                TOOL_SELECT_INCLUDE,
                TOOL_SELECT_INCLUDE + "\n" + RELEASE_MAK_INCLUDE,
                1,
            )
            changes.append("inserted include der_libs\\release.mak")
        else:
            changes.append(
                "WARNING: 'include der_libs\\tool_select.mak' not found -- "
                "release.mak include NOT inserted, please add it by hand"
            )
    else:
        changes.append("include der_libs\\release.mak already present -- left as-is")

    # 4. Strip those names out of .PHONY:.
    before = text
    text = strip_phony_names(text, SHARED_TARGETS)
    if text != before:
        changes.append("trimmed .PHONY: line")

    return text, changes


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Makefile")
    if not path.is_file():
        print(f"error: {path} not found", file=sys.stderr)
        sys.exit(1)

    raw = path.read_bytes().decode("utf-8")
    uses_crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")

    new_text, changes = migrate(text)

    if uses_crlf:
        new_text = new_text.replace("\n", "\r\n")

    if new_text == raw:
        print(f"{path}: no changes needed")
        return

    path.write_bytes(new_text.encode("utf-8"))

    print(f"{path}: updated")
    for c in changes:
        print(f"  - {c}")


if __name__ == "__main__":
    main()
