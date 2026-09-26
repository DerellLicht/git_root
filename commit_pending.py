#!/usr/bin/env python3

# CC0 1.0 Universal (Public Domain Dedication)
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide.  This software is distributed without any warranty.
#
# See LICENSE.txt in this repository, or
# <https://creativecommons.org/publicdomain/zero/1.0/>.

"""
commit_pending.py

Walk the immediate subfolders of a directory; in each one that is a git repo,
commit any pending modifications to Makefile-type files.  Intended as the
follow-up to a "modify all the makefiles" pass.

Default is a DRY RUN: nothing is committed unless --apply is given.
Nothing is ever pushed.

Usage:
    python commit_pending.py .                       (dry run)
    python commit_pending.py . --apply               (commit)
    python commit_pending.py . --apply -m "My message"
    python commit_pending.py . --all --apply         (commit ALL tracked changes)

What gets committed:
  * By default ONLY modified/deleted TRACKED files whose names look like
    makefiles (Makefile, GNUmakefile, *.mak, *.mk).  Other pending changes in
    the same repo are left exactly as they are and reported, so unrelated
    work-in-progress never gets swept into a makefile commit.
  * --all widens that to every modified/deleted tracked file.
  * Untracked files are never added; they are only reported.
  * Each commit uses an explicit path list, so files you had staged for other
    reasons are not pulled in.
"""

import argparse
import fnmatch
import os
import subprocess
import sys

DEFAULT_MESSAGE = "Remove obsolete Cygwin/gdiplus warning comment from Makefile"

MAKEFILE_PATTERNS = ["Makefile", "GNUmakefile", "*.mak", "*.mk"]


def git(repo, *args):
    """
    Run a git command in 'repo'.  Returns (returncode, stdout, stderr) with
    stdout/stderr as text.  Never raises on a non-zero exit.
    """
    p = subprocess.run(["git", "-C", repo] + list(args),
                       capture_output=True, text=True, errors="replace")
    return p.returncode, p.stdout, p.stderr


def is_makefile_path(path):
    """Return True if the basename of 'path' matches a makefile pattern."""
    base = os.path.basename(path)
    return any(fnmatch.fnmatch(base.lower(), pat.lower())
               for pat in MAKEFILE_PATTERNS)


def parse_status(raw):
    """
    Parse `git status --porcelain -z` output.  Returns (tracked, untracked):
      tracked   - list of (xy, path) for entries that are tracked changes
      untracked - list of paths that are untracked ("??")
    Rename/copy entries carry an extra "original path" field, which is skipped.
    """
    tracked = []
    untracked = []
    fields = raw.split("\0")
    i = 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        xy, path = entry[:2], entry[3:]
        if xy == "??":
            untracked.append(path)
            continue
        if xy == "!!":
            continue
        if "R" in xy or "C" in xy:
            i += 1  # skip the original-path field
        tracked.append((xy, path))
    return tracked, untracked


def find_repos(root):
    """
    Return a sorted list of immediate subfolders of 'root' that contain a
    .git entry (a directory, or a file for worktrees/submodules).
    """
    repos = []
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isdir(full) and os.path.exists(os.path.join(full, ".git")):
            repos.append(full)
    return repos


def process_repo(repo, message, apply, everything):
    """
    Examine one repo and, if apply is True, commit the selected paths.
    Returns a status string: "committed", "would-commit", "clean",
    "nothing-selected" or "error".
    """
    rc, out, err = git(repo, "status", "--porcelain", "-z")
    if rc != 0:
        print(f"{repo}\n  ERROR running git status: {err.strip()}")
        return "error"

    tracked, untracked = parse_status(out)
    if not tracked and not untracked:
        return "clean"

    # Refuse to touch a repo that is mid-merge/rebase/etc.
    if any(xy in ("UU", "AA", "DD", "AU", "UA", "DU", "UD") for xy, _ in tracked):
        print(f"{repo}\n  SKIPPED: unresolved merge conflicts")
        return "error"

    selected = [p for xy, p in tracked if everything or is_makefile_path(p)]
    others = [p for xy, p in tracked if p not in selected]

    if not selected:
        if others or untracked:
            print(f"{repo}\n  no makefile changes; leaving "
                  f"{len(others)} other modified and {len(untracked)} "
                  f"untracked file(s) alone")
        return "nothing-selected"

    print(f"{repo}")
    for p in selected:
        print(f"  {'commit' if apply else 'would commit'}: {p}")
    for p in others:
        print(f"  left alone (modified, not a makefile): {p}")
    for p in untracked:
        print(f"  left alone (untracked): {p}")

    if not apply:
        return "would-commit"

    # 'commit -- paths' commits only those paths, regardless of what else is
    # staged.  A path that was deleted works the same way.
    rc, out, err = git(repo, "commit", "-m", message, "--", *selected)
    if rc != 0:
        print(f"  ERROR: git commit failed: {(err or out).strip()}")
        return "error"
    print(f"  committed ({out.strip().splitlines()[0] if out.strip() else 'ok'})")
    return "committed"


def main():
    """Parse arguments, process each repo under the given folder, summarize."""
    ap = argparse.ArgumentParser(
        description="Commit pending Makefile changes in each repo under a folder.")
    ap.add_argument("root", nargs="?", default=".",
                    help="folder whose immediate subfolders are repos (default .)")
    ap.add_argument("--apply", action="store_true",
                    help="actually commit (default is a dry run)")
    ap.add_argument("-m", "--message", default=DEFAULT_MESSAGE,
                    help="commit message (default: %(default)r)")
    ap.add_argument("--all", action="store_true", dest="everything",
                    help="commit ALL modified tracked files, not just makefiles")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(f"error: {args.root} is not a directory", file=sys.stderr)
        return 1

    repos = find_repos(args.root)
    counts = {}
    for repo in repos:
        status = process_repo(repo, args.message, args.apply, args.everything)
        counts[status] = counts.get(status, 0) + 1

    mode = "APPLIED" if args.apply else "DRY RUN (nothing committed)"
    print(f"\n{mode}: {len(repos)} repo(s) checked; "
          + "; ".join(f"{v} {k}" for k, v in sorted(counts.items())))
    if not args.apply and counts.get("would-commit"):
        print("Re-run with --apply to commit.")
    return 1 if counts.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
