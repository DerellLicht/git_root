#!/usr/bin/env python3
"""
fix_update_rule.py

Walks every folder under a root directory, finds Makefiles that contain
an `update:` target, and replaces that rule with the corrected version:

    # Your corrected, bulletproof update-in-place pipeline
    update: dist
        @cmd /C "@echo Updating assets for existing release v$(VERSION)..."
        gh release upload v$(VERSION) ./$(DIST_ZIP) ./CHANGELOG.md --clobber
        @cmd /C "@echo Release v$(VERSION) assets successfully updated on GitHub!"

By default this is a DRY RUN: it reports what it would change and shows
a diff, but touches nothing on disk and runs no git commands. Pass
--apply to actually write files and commit/push.

Usage:
    python fix_update_rule.py [--root PATH] [--apply]
                               [--skip-push] [--message MSG]

  --root PATH     Directory to start walking from (default: current dir)
  --apply         Actually write the file and run git commit/push
                   (omit this for a dry run / diff-only report)
  --skip-push     Commit locally but don't push
  --message MSG   Commit message (default: "fix Makefile upload rule")
"""

import argparse
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

# Matches an optional single comment line directly above `update:`,
# the `update:` target line itself (whatever its prerequisites are),
# and every tab-indented recipe line that follows it. Recipe lines are
# matched structurally (must start with a literal tab, per Make syntax)
# rather than by exact text, so minor wording differences between the
# 18 repos don't stop the match.
UPDATE_BLOCK_RE = re.compile(
    r'(?:^#[^\r\n]*\r?\n)?'
    r'^update:[^\r\n]*\r?\n'
    r'(?:^\t[^\r\n]*\r?\n?)*',
    re.MULTILINE,
)

NEW_BLOCK_LF = (
    "# Your corrected, bulletproof update-in-place pipeline\n"
    "update: dist\n"
    "\t@cmd /C \"@echo Updating assets for existing release v$(VERSION)...\"\n"
    "\tgh release upload v$(VERSION) ./$(DIST_ZIP) ./CHANGELOG.md --clobber\n"
    "\t@cmd /C \"@echo Release v$(VERSION) assets successfully updated on GitHub!\"\n"
)


def read_text(path):
    """
    Read a Makefile as text, tolerating non-UTF-8 bytes (some of these
    files may have accumulated stray characters over the years from
    editors on Windows). Falls back to latin-1, which never raises.
    """
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8')
    except UnicodeDecodeError:
        return raw.decode('latin-1')


def new_block_for(text):
    """Return the replacement block using the same newline convention (CRLF or LF) as `text`."""
    if '\r\n' in text:
        return NEW_BLOCK_LF.replace('\n', '\r\n')
    return NEW_BLOCK_LF


def find_target_dirs(root):
    """
    Walk `root` recursively and yield the path to every Makefile that
    contains an `update:` target. `.git` directories are pruned from
    the walk so we don't waste time descending into repo internals.
    This only checks for presence of the target, not its content --
    process_makefile() decides whether a rewrite is actually needed.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != '.git']
        if 'Makefile' not in filenames:
            continue
        makefile_path = Path(dirpath) / 'Makefile'
        text = read_text(makefile_path)
        if re.search(r'^update:', text, re.MULTILINE):
            yield makefile_path


def process_makefile(path):
    """
    Compute the corrected contents for one Makefile.
    Returns a dict with keys: path, changed (bool), old_text, new_text.
    `changed` is False when the update: block already matches the
    corrected version (already fixed by hand, or by a prior run) --
    callers should treat that as a no-op, not an error.
    """
    old_text = read_text(path)
    replacement = new_block_for(old_text)
    new_text, count = UPDATE_BLOCK_RE.subn(replacement, old_text, count=1)
    return {
        'path': path,
        'changed': count == 1 and new_text != old_text,
        'old_text': old_text,
        'new_text': new_text,
    }


def git(args, cwd):
    """Run a git command in `cwd`. Returns (success, combined stdout+stderr)."""
    result = subprocess.run(
        ['git', *args], cwd=cwd, capture_output=True, text=True
    )
    output = (result.stdout or '') + (result.stderr or '')
    return result.returncode == 0, output.strip()


def repo_is_clean(repo_dir):
    """
    True only if `git status --porcelain` is empty in `repo_dir` --
    i.e. nothing staged, modified, or untracked. Required before we
    touch Makefile, so a `-am` commit can't sweep up unrelated pending
    work and a pre-existing local edit to Makefile can't get silently
    overwritten by our rewrite.
    """
    ok, output = git(['status', '--porcelain'], cwd=repo_dir)
    return ok and output == ''


def repo_push_readiness(repo_dir):
    """
    Return (ready, reason). Checks for detached HEAD and a configured
    upstream tracking branch, so we never attempt a blind push that
    would fail (or push to the wrong place).
    """
    ok, branch = git(['rev-parse', '--abbrev-ref', 'HEAD'], cwd=repo_dir)
    if not ok or branch == 'HEAD':
        return False, 'detached HEAD (no branch checked out)'
    ok, _ = git(['rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'], cwd=repo_dir)
    if not ok:
        return False, 'no upstream tracking branch configured'
    return True, ''


def commit_and_push(repo_dir, skip_push, message):
    """
    Commit the already-written Makefile change and (unless skip_push)
    push it. Uses `git commit -am` directly -- safe here because
    repo_is_clean() already gated on an empty `git status --porcelain`
    before this repo was touched, so the Makefile edit is the only
    change `-am` can possibly pick up. Returns (success, message).
    """
    ok, out = git(['commit', '-am', message], cwd=repo_dir)
    if not ok:
        return False, f'git commit -am failed: {out}'

    if skip_push:
        return True, 'committed (push skipped)'

    ok, out = git(['push'], cwd=repo_dir)
    if not ok:
        return False, f'commit succeeded locally, but git push failed: {out}'
    return True, 'committed and pushed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.', help='Directory to walk (default: current dir)')
    parser.add_argument('--apply', action='store_true', help='Actually write files and commit/push')
    parser.add_argument('--skip-push', action='store_true', help='Commit locally but do not push')
    parser.add_argument('--message', default='fix Makefile upload rule', help='Commit message')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    fixed, unchanged, dirty_skipped, push_not_ready, errors = [], [], [], [], []

    for makefile_path in find_target_dirs(root):
        repo_dir = makefile_path.parent
        result = process_makefile(makefile_path)

        if not result['changed']:
            unchanged.append(makefile_path)
            continue

        print(f'\n=== {makefile_path} ===')
        diff = difflib.unified_diff(
            result['old_text'].splitlines(keepends=True),
            result['new_text'].splitlines(keepends=True),
            fromfile='before', tofile='after',
        )
        sys.stdout.writelines(diff)

        if not args.apply:
            fixed.append(makefile_path)  # "would fix" in dry-run
            continue

        if not repo_is_clean(repo_dir):
            print(f'  SKIPPED: {repo_dir} has uncommitted changes elsewhere; resolve manually.')
            dirty_skipped.append(makefile_path)
            continue

        ready, reason = repo_push_readiness(repo_dir)
        if not ready and not args.skip_push:
            print(f'  SKIPPED: {repo_dir} not ready to push ({reason}).')
            push_not_ready.append(makefile_path)
            continue

        makefile_path.write_text(result['new_text'], encoding='utf-8', newline='')
        ok, msg = commit_and_push(repo_dir, args.skip_push, args.message)
        print(f'  {"OK" if ok else "ERROR"}: {msg}')
        (fixed if ok else errors).append(makefile_path)

    print('\n' + '=' * 60)
    print(f'{"Would fix" if not args.apply else "Fixed"}: {len(fixed)}')
    print(f'Already correct (skipped): {len(unchanged)}')
    print(f'Skipped, dirty tree: {len(dirty_skipped)}')
    print(f'Skipped, not push-ready: {len(push_not_ready)}')
    print(f'Errors: {len(errors)}')
    for p in dirty_skipped:
        print(f'  DIRTY: {p.parent}')
    for p in push_not_ready:
        print(f'  NOT PUSH-READY: {p.parent}')
    for p in errors:
        print(f'  ERROR: {p.parent}')

    if not args.apply and fixed:
        print('\nThis was a dry run -- nothing was written or committed. Re-run with --apply to make it real.')


if __name__ == '__main__':
    main()
