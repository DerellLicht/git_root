# Release procedure (CubicAdventurer)

Before step 1: add a `## [x.yy] - YYYY-MM-DD` section to `CHANGELOG.md`.
The newest such header is the only place the version lives.

1. `make sync-version`
   Copies the changelog version into `Source/CubicAdventurer.dproj`
   (both `VerInfo_Keys` lines, plus MajorVer and MinorVer).
2. Rebuild in the Delphi IDE (File > Close All, `git pull`, Shift-F9).
   Delphi Community Edition has no command-line compiler, so the exe
   cannot be built from make.
3. `make check`
   Verifies that both the .dproj and `CubicAdventurer.exe` carry the
   changelog version. Aborts with REBUILD REQUIRED if the exe is stale.
4. Commit and push everything (including the .dproj change from step 1),

5. `make release`  
   NOTE: It refuses to run on a dirty tree (`check-clean`). It then builds the
   zipped installer (`dist`, which re-runs `check`, stops the running app
   and cleans `installer/output`), writes the release notes from the
   changelog, tags `ca-<version>`, pushes the tag, and creates the GitHub
   release with the zip attached. Needs the `gh` CLI signed in.

### Afterwards
- `make update`: refresh the notes and zip of an existing release.  
- `make retag`: move the tag to HEAD (solo repo only).  
  `make re-release` = retag + update.  
- `make sha256`: SHA-256 of the zip, for download-site submissions.

### Local testing, not part of a release
- `make installer` then `make install` (or `make do_inst`, which does both).

Step 4 hides a dependency: sync-version changes the .dproj, so it has to be committed before make release. Otherwise check-clean stops you. The tag push is also why you run make release yourself, since my sessions can’t push tags.

---

#  How to handle `git pull` when I have pending commit(s)

## You

Okay, clue me in on how to handle this, because it probably is going to happen frequently...

I'm ready to `git pull` your changes, *but* I have a changed file in the `docs` folder... not the spec doc, but another reference doc.

If I (try to) commit and push my change, it'll fail because the remote copy has been updated.  But if I `git pull` now, I'll over-write my changed file...  

How to I deal with this??  I needs something like `git pull except what I have changed` ...

## Claude

You're fine. `git pull` never overwrites a file you've changed unless the incoming commits also change that same file. In that case it stops with an error and touches nothing. So `git pull` can't silently clobber your edit.

I've only changed `docs/dngrep-sar-before-after-spec.md` and `docs/phase0-spike-findings.md` so far. If your edited reference doc is neither of those, a plain `git pull` will apply my commits and leave your edit alone as an uncommitted change.

To check before pulling:

```
git fetch
git diff --name-only HEAD origin/sar-log
```

That lists the files my commits touch. If your file isn't in the list, pull away. If it is, use the stash steps below.

**If we ever do touch the same file** (the pull refuses with "local changes would be overwritten"):

```
git stash
git pull
git stash pop
```

This sets your edit aside, pulls, then puts your edit back on top. If we both changed the same lines, git marks a conflict in the file for you to sort out. Nothing is lost either way.

**Your commit-and-push failing** is a separate thing: the remote has newer commits than your copy. The fix is to commit locally, then:

```
git pull --rebase
git push
```

`--rebase` puts your commit after mine in a straight line, instead of creating an extra "merge" commit each time. You can make it the default with `git config --global pull.rebase true`.

Your usual routine, when you've edited a file and I've pushed:

1. `git add <your file>` and `git commit -m "..."`
2. `git pull --rebase`
3. `git push`

This is why I'll keep my changes to different files from yours where I can, and why you should tell me before you push, so I fetch first.

---

# How to enable `Issues` and `Discussions` tabs on GitHub project page

Open `Settings`, `General` tab, go to `Features` section,  
then set up desired feature

---

# Showing an HTML file as a rendered page from a GitHub README

Problem: a link to `github.com/<user>/<repo>/blob/.../file.html` shows the
source, not the rendered page. GitHub serves HTML as plain text on
github.com and raw.githubusercontent.com on purpose, and `?raw=true`
(which works for images) does not change that.

Solution: GitHub Pages.
1. Repo -> Settings -> Pages.
2. Build and deployment: Source = "Deploy from a branch",
   Branch = master, Folder = /docs. Save.
3. Wait a minute or so. Files in /docs are then served at:
   https://<user>.github.io/<repo>/<file>.html
4. Link to that URL from README.md.

Example (dlGrep):
  docs/replace-log.html -> https://derelllicht.github.io/dlGrep/replace-log.html

Notes:
- Works for standalone HTML (inline CSS, no external resources).
- Quick alternative with no setup: htmlpreview.github.io, which depends on
  a third-party service.
- Another alternative: a PNG screenshot embedded in the README.