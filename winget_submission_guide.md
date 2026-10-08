# winget Submission Guide

Distilled from the PrettyReMark v1.13 submission (Sept 17 - Oct 6, 2026).
Part 1 covers a program that has never been on winget. Part 2 covers a new
version of a program that is already listed. The Addendum covers whether an
installer is always needed.

Items marked **(untested)** are things I believe are true but did not
actually run during the PRM submission.

Flow in one line (Part 1): build and test in the **staging** folder in the
project repo (1.2 - 1.4), then branch, **copy the folder into `winget-pkgs`**,
commit, push and open the PR (1.5).

## Reference: where things live

| What | Path |
|---|---|
| Staging manifests (scratch, in project repo) | `D:\SourceCode\Git\PrettyReMark\winget\d\DerellLicht\PrettyReMark\<ver>\` |
| winget-pkgs clone (my fork) | `D:\SourceCode\Git.others\winget-pkgs` |
| Submission folder (the only copy GitHub sees) | `...\winget-pkgs\manifests\d\DerellLicht\PrettyReMark\<ver>\` |
| Package ID | `DerellLicht.PrettyReMark` |

Two copies exist on purpose: build and test in staging, then copy the finished
folder into the clone for the PR.

---

# Part 1 - New program

## 1.0 One-time setup (done for PRM; skip next time)

```
winget settings --enable LocalManifestFiles
```
Admin window, once. Allows `winget ... --manifest <local folder>`.

- Enable **Windows Sandbox** (Windows Features, then reboot). Needed for the
  clean-machine test in 1.4.
- Fork `microsoft/winget-pkgs` on GitHub, then clone **your fork**:
  ```
  git clone --depth 1 https://github.com/DerellLicht/winget-pkgs.git
  ```
  Still about 4 GB: the bulk is the current manifest tree, not history.
- CLA: on your **first** PR only, post a normal comment
  `@microsoft-github-policy-service agree`. It is one-time across all
  Microsoft repos.

## 1.1 Pre-flight on the program

1. **Public, stable, versioned download URL**, reachable while logged out.
   Publish the `.zip` (many sites reject bare `.exe`) as a release asset.
2. **Hosting matters.** A GitLab URL triggered `Validation-Domain`, which
   meant manual moderator approval and weeks of waiting. A GitHub release URL
   probably avoids this **(untested)**.
3. **Silent install works** (the installer is run unattended by winget):
   ```
   Setup.exe /SILENT /SUPPRESSMSGBOXES /NORESTART
   ```
   No clicks, no restart prompt.
4. **List every runtime dependency** the app needs (PRM: WebView2). Your dev
   machine already has them, so it will not warn you. See the Dependencies
   section.

## 1.2 Build the three manifest files

Folder: `manifests\<first-letter>\<Publisher>\<PackageName>\<Version>\`

- `<Publisher>.<Package>.yaml` (version)
- `<Publisher>.<Package>.installer.yaml`
- `<Publisher>.<Package>.locale.en-US.yaml`

Every file starts with a schema comment matching its own type. Missing it is
only a warning in `winget validate` but a **hard error** in winget-pkgs CI:
```
# yaml-language-server: $schema=https://aka.ms/winget-manifest.installer.<ManifestVersion>.schema.json
```
(`version` and `defaultLocale` in place of `installer` for the other two.)

`ManifestVersion` should be the current schema, not whatever an old template
says. Copy it from the last merged PRM manifest, or look at a recent
winget-pkgs manifest.

Installer manifest, zip-wrapped Inno installer (the PRM pattern):
```yaml
PackageIdentifier: DerellLicht.PrettyReMark
PackageVersion: 1.20
Platform:
- Windows.Desktop
MinimumOSVersion: 10.0.17763.0
InstallerType: zip
NestedInstallerType: inno
NestedInstallerFiles:
- RelativeFilePath: PrettyReMarkV1.20.setup.exe
Scope: user
InstallModes:
- interactive
- silent
- silentWithProgress
UpgradeBehavior: install
Dependencies:
  PackageDependencies:
  - PackageIdentifier: Microsoft.EdgeWebView2Runtime
Installers:
- Architecture: x64
  InstallerUrl: https://gitlab.com/DerellLicht/pretty-mark/-/releases/v1.20/downloads/PrettyReMarkV1.20.setup.zip
  InstallerSha256: <hash of the .zip>
ManifestType: installer
ManifestVersion: <current>
```

Fields that bit me:

- `InstallerType` must match the real installer tech: `inno` for Inno Setup
  (`nullsoft` is NSIS; it was copied by mistake from eagle1's template).
- `Scope` must match the script: `user` for `PrivilegesRequired=lowest`.
- Zip-wrapped means all three of `InstallerType: zip`, `NestedInstallerType`,
  `NestedInstallerFiles`. `RelativeFilePath` is the exe's name at the zip
  root (the Makefile uses `zip -j`) and **contains the version number**.
- `InstallerSha256` is the hash of the **zip**, not the exe inside it.
- `Dependencies` is how winget installs a missing runtime first. See the
  Dependencies section.
- Locale file: `License` and `LicenseUrl` must match the repo's real license
  (the first draft used MIT as a placeholder, so check it). Credit eagle1's
  PrettyMark as the origin in the description for PRM.

## 1.3 Hash the published asset

Download the zip from the **live release link**, not from `Output\`:
```
certutil -hashfile PrettyReMarkV1.20.setup.zip SHA256
```
Compare with `InstallerSha256` character for character. This proves the
uploaded asset is the one you tested.

## 1.4 Validate and test

Both commands below run on the **staging** folder in the project repo (built
in 1.2). `<version folder>` means that staging folder, for example
`D:\SourceCode\Git\PrettyReMark\winget\d\DerellLicht\PrettyReMark\<ver>`.
The copy into `winget-pkgs` comes later, in 1.5.

```
winget validate --manifest <version folder>
```
Schema and YAML only; no network. For a manifest with `Dependencies`, it
prints a notice that the dependency was "not validated" and then
`Manifest validation succeeded.` That is a pass, not a failure.

```
cd D:\SourceCode\Git.others\winget-pkgs
.\Tools\SandboxTest.ps1 D:\SourceCode\Git\PrettyReMark\winget\d\DerellLicht\PrettyReMark\<ver>
```
The `cd` is only to reach the script, which lives in the `winget-pkgs` clone.
The argument is the **staging** folder in the project repo, as an absolute
path; the manifests do not have to be inside the clone yet.

**Run this from an elevated PowerShell console** (right-click Windows
PowerShell, Run as administrator), not from TCC. In TCC the `.ps1` just opens
in Notepad, and from a non-elevated prompt the script wrongly reports
"Windows Sandbox does not seem to be available".

Expected and harmless on Windows 10: a red `CiTool.exe : The term 'CiTool.exe'
is not recognized` error at the start of "Installing WinGet". That tool only
exists on Windows 11. What matters is WebView2 installing, then PrettyReMark
installing, then the app starting.
Runs the real winget flow in a clean Windows Sandbox: dependency first, then
your installer. Confirm the app **starts**. This is the test that would have
caught the missing WebView2 before the reviewer did. The release must already
be live.

Avoid `winget install --manifest` on your own machine as a test. It can
install an older version over your working copy, and your machine hides
missing dependencies anyway.

## 1.5 Branch, copy, commit, push, PR

This is the one place the manifests move from the project repo (staging) into
`winget-pkgs`. Order matters: branch first, then copy, so the copied files
land on the submission branch.

1. Branch from an up-to-date `master`. If the clone is not brand new, first
   sync the fork on GitHub (**Sync fork**, then **Update branch**). Then in the
   clone:
   ```
   cd D:\SourceCode\Git.others\winget-pkgs
   git checkout master
   git pull
   git checkout -b add-prettyremark-<ver>
   ```
2. **Copy the tested staging folder into the clone.** The destination is the
   submission folder from the Reference table. Create it first (a first
   submission has no `PrettyReMark` folder yet), then copy the three `.yaml`
   files:
   ```
   mkdir D:\SourceCode\Git.others\winget-pkgs\manifests\d\DerellLicht\PrettyReMark\<ver>
   copy D:\SourceCode\Git\PrettyReMark\winget\d\DerellLicht\PrettyReMark\<ver>\*.yaml D:\SourceCode\Git.others\winget-pkgs\manifests\d\DerellLicht\PrettyReMark\<ver>\
   ```
   Check that the destination holds exactly three files, and that the staging
   copy is the one you validated and sandbox-tested in 1.4. Do not edit the
   copy afterwards; fix staging and copy again.
3. Commit and push:
   ```
   git add manifests\d\DerellLicht\PrettyReMark\<ver>\
   git commit -m "New package: DerellLicht.PrettyReMark version <ver>"
   git push -u origin HEAD
   ```
   `HEAD` is the branch you are on, so the branch name is never retyped. (A
   typed `git push origin <name>` once failed with `src refspec ... does not
   match any` even though `git branch` listed the branch; the push by `HEAD`
   worked.)
4. Open the PR with the "Compare & pull request" banner, or
`gh pr create --repo microsoft/winget-pkgs`. Keep the pre-filled title (from
the commit message). In the checklist, tick only boxes that are true: the
validate box is covered by `winget validate` and the `winget install
--manifest` box by `SandboxTest.ps1` (1.4). Leave the CLA box alone; post the
CLA comment (1.0) instead.

## 1.6 After the PR is open

- A bot pipeline runs: validation, download and hash check, sandbox install,
  domain check. When it is green, a human moderator still has to approve.
  "Review required" persisting is normal.
- **`Validation-Domain` label** (shared hosting like GitLab/GitHub): post one
  comment with evidence tying the URL to you:
  - the PackageUrl and the version-specific release page
  - the hosting namespace matches the publisher name
  - `curl.exe -sIL <InstallerUrl>` showing a direct link or one same-domain
    redirect
  - the `certutil` hash matching the manifest
- **Never use "Close with Comment".** Use plain **Comment**. Closing makes the
  bot strip `Needs-Attention` and unassign the reviewer, and reopening does
  not restore either.
- `@wingetbot run` is moderators only; it fails for authors.
- Expect a long wait: two active moderators, 600+ PRs a day. PRM's first PR
  took about three weeks. Do not ask "when". A polite post in the repo's
  Discussions got a moderator response.
- If a reviewer asks for a manifest fix, edit the file on the PR branch
  (GitHub's web editor works) and commit. PRM's fix merged within 15 minutes.

## 1.7 After it merges

The bot posts "Publish pipeline succeeded... refresh your index". That means
winget's package catalog, not git:
```
winget source update
winget show --id DerellLicht.PrettyReMark
```
Check the version and the dependency list. If not found, wait and retry; the
delay length is unknown.

Cleanup: click **Delete branch** on the merged PR page (removes only the
branch on your fork). Keep the fork itself; every later update needs it.

---

# Part 2 - Upgrade an existing program

Assumes the package is already merged. All files for the new version live
next to the old one; old version folders are never touched.

## 2.1 Release first, then hash

1. Build and test the release (installer, silent install, Sandbox run).
2. `make release`; confirm the zip is live on the release page.
3. Download the zip from the **live release link** (not from `Output\`) and
   hash it:
   ```
   certutil -hashfile PrettyReMarkV<newver>.setup.zip SHA256
   ```
   This is the value for `InstallerSha256` in 2.3. It proves the uploaded
   asset is the one you tested. Do not rebuild after hashing: every rebuild
   changes the hash.

## 2.2 Sync the fork and start a fresh branch

winget-pkgs moves quickly; a stale clone causes conflicts. Sync **before**
branching.

1. On GitHub: your fork, then **Sync fork**, then **Update branch**.
2. In the clone:
   ```
   cd D:\SourceCode\Git.others\winget-pkgs
   git checkout master
   git pull
   git checkout -b update-prettyremark-<ver>
   ```
   Check `git remote -v` if `pull` does something unexpected. `origin`
   should be your fork.

Never reuse an old PR branch. Do not hand-paste into the local clone anything
that was merged through GitHub's web editor; the pull will bring it.

## 2.3 Create the new version folder

Steps 1-4 happen in the **staging copy in the PRM repo** (no `manifests\`
prefix). Only step 5 touches `winget-pkgs`.

1. In the PRM repo, copy the previous version's three files from
   `D:\SourceCode\Git\PrettyReMark\winget\d\DerellLicht\PrettyReMark\<oldver>\`
   to `...\<newver>\` (same parent folder). Keep every version's staging
   folder in the repo.
2. In all three files change `PackageVersion`.
3. In the installer file change `InstallerUrl`, `InstallerSha256`, and the
   version inside `NestedInstallerFiles` `RelativeFilePath`. Keep the
   `Dependencies` block (see the Dependencies section) and `ManifestVersion`
   unless the schema changed.
4. Catch leftovers: from the folder run
   ```
   findstr /s /n /c:"1.13" *.yaml
   ```
   (substitute the old version). It should find nothing.
5. Only now, in `winget-pkgs`: copy the finished `<newver>` folder into the
   clone at
   `D:\SourceCode\Git.others\winget-pkgs\manifests\d\DerellLicht\PrettyReMark\<newver>\`.

## 2.4 Validate and test

Run from the `winget-pkgs` clone, with `<folder>` being
`manifests\d\DerellLicht\PrettyReMark\<newver>`. The release must already be
live. Do not use `winget install --manifest` on your own machine as the test:
it can install an older version over your working copy, and your machine
already has WebView2, so it hides missing dependencies.

```
cd D:\SourceCode\Git.others\winget-pkgs
winget validate --manifest <folder>
.\Tools\SandboxTest.ps1 <folder>
```

`SandboxTest.ps1` must be run from an **elevated PowerShell console** (right-click
Windows PowerShell, Run as administrator), not from TCC. In TCC the `.ps1` just
opens in Notepad, and from a non-elevated prompt the script wrongly reports
"Windows Sandbox does not seem to be available". Close any open Sandbox window
first.

- `validate`: the line `Manifest validation succeeded.` is the result. The
  notice above it ("dependencies that were not validated ... Microsoft.EdgeWebView2Runtime")
  is expected, not a failure; validate does not resolve dependencies.
- `SandboxTest.ps1`: in the sandbox, watch for WebView2 installing first and
  then PrettyReMark, and confirm the app starts. A red `CiTool.exe is not
  recognized` error at the start of "Installing WinGet" is expected and
  harmless on Windows 10 (that tool only exists on Windows 11).

## 2.5 Commit, push, PR

```
git add manifests\d\DerellLicht\PrettyReMark\<newver>\
git commit -m "New version: DerellLicht.PrettyReMark version <newver>"
git push -u origin HEAD
```
Open the PR with the "Compare & pull request" banner GitHub shows after the
push, or `gh pr create --repo microsoft/winget-pkgs`.

- Title: keep the pre-filled one, which comes from the commit message:
  `New version: DerellLicht.PrettyReMark version <newver>`
- In the checklist, tick only boxes that are true. The validate box is covered
  by `winget validate` (2.4). The `winget install --manifest` box is covered
  by `SandboxTest.ps1`, which runs that install inside the sandbox; there is
  no need to run it on your own machine.
- No CLA comment needed this time (it is one-time across all Microsoft repos).

## 2.6 Watch and finish

After the PR is open:

- A bot pipeline runs: validation, download and hash check, sandbox install,
  domain check. When it is green, a human moderator still has to approve.
  "Review required" persisting is normal.
- **`Validation-Domain` label:** may appear again (shared hosting). If it does,
  post one comment with evidence tying the URL to you: the PackageUrl and the
  version-specific release page; the hosting namespace matches the publisher
  name; `curl.exe -sIL <InstallerUrl>` showing a direct link or one same-domain
  redirect; and the `certutil` hash matching the manifest.
- **Never use "Close with Comment".** Use plain **Comment**. Closing makes the
  bot strip `Needs-Attention` and unassign the reviewer, and reopening does
  not restore either.
- `@wingetbot run` is moderators only; it fails for authors.
- Expect a wait: two active moderators, 600+ PRs a day. Do not ask "when". A
  polite post in the repo's Discussions got a moderator response once.
- If a reviewer asks for a manifest fix, edit the file on the PR branch
  (GitHub's web editor works) and commit. PRM's last fix merged within 15
  minutes.

After it merges, the bot posts "Publish pipeline succeeded... refresh your
index". That means winget's package catalog, not git:
```
winget source update
winget show --id DerellLicht.PrettyReMark
```
Check the new version and the dependency list. If not found, wait and retry;
the delay length is unknown.

Cleanup after the merge: click **Delete branch** on the PR page. It removes
only the branch on your fork; the merged PR and manifests stay. Do **not**
delete the fork itself: the next update needs it. The local branch in the
clone can be left alone or deleted; either is harmless.

Update PRs are likely lighter than a first submission **(untested)**, but the
review queue is the same one.

**Not used, untested - a shortcut that would replace 2.2 through 2.5
entirely:** Microsoft's `wingetcreate` tool can build the new version folder
from the previous one and open the PR itself:
```
wingetcreate update DerellLicht.PrettyReMark --version <newver> --urls <zip-url> --submit
```
It needs a GitHub token with repo scope, and **I do not currently have one
set up** (that is why some token-dependent commands gave errors during the
1.20 work). The manual route above needs no token. I have not confirmed how it handles
the zip-wrapped nested installer or the `Dependencies` block, and as far as I
know it does not run the Sandbox test. If you ever try it, compare its output
with 2.3, and run the 2.4 tests on the generated folder before the PR is
opened. The manual route above is the proven one.

---

# Dependencies - runtime requirements

Applies to both parts. A dependency is something the program needs installed
that is itself a winget package (PRM: the WebView2 runtime). winget installs
it before your installer runs. PRM is the example throughout.

## D.1 Find out whether you have one

Your dev machine already has everything, so it will not tell you. Run the
Sandbox test (1.4) **without** a `Dependencies` block: if the app fails or
misbehaves in the clean sandbox, something is missing. PRM's was found by a
reviewer on a clean machine; installing WebView2 by hand fixed it. Typical
candidates **(untested)**: WebView2, the Visual C++ redistributable, a .NET
runtime when the program is not self-contained.

A reviewer will test on a clean machine, so a missing dependency can hold up
approval. Better to find it first.

## D.2 Find the package ID

The ID must be an existing winget package. Look it up, then copy it exactly:
```
winget search <name>
winget show --id <PackageIdentifier>
```
PRM's ID, given by the reviewer: `Microsoft.EdgeWebView2Runtime`.

## D.3 Add it to the installer yaml

In `<Publisher>.<Package>.installer.yaml`, at the top level (between
`UpgradeBehavior` and `Installers`, not inside the `Installers` entry):
```yaml
Dependencies:
  PackageDependencies:
  - PackageIdentifier: Microsoft.EdgeWebView2Runtime
```
Indentation matters: `PackageDependencies` is indented two spaces, and the
`- PackageIdentifier` line sits at the same two spaces.

For more than one dependency, repeat the `- PackageIdentifier:` line. An
optional `MinimumVersion:` can follow it **(untested)**. The schema also has
`WindowsFeatures`, `WindowsLibraries` and `ExternalDependencies` for things
that are not winget packages **(untested; check the schema docs)**.

## D.4 Carry it through every version

The block lives in each version's installer yaml. A new version folder gets
it only if you copy it forward (2.3 does: copy the previous version, keep the
block). Old versions are not changed by this. PRM's 1.13 was fixed by a
manifest-only edit to the open PR (three lines), which merged within 15
minutes; no new build or hash was needed.

## D.5 Verify it

- `winget validate`: prints a notice that the dependency was "not validated".
  Expected; see 1.4.
- `SandboxTest.ps1`: the dependency installs first, then your program. Confirm
  the program starts. This is the real test.
- After merge: `winget show --id <PackageIdentifier>` lists the dependency.

## D.6 Bundling in the installer is separate

A bootstrapper inside your own installer only helps people who download the
setup directly. winget users get the runtime from the manifest. Keep both;
the manifest entry is still needed even when the installer bundles it.

---

# Addendum - do I always need an installer?

**No**, as far as I know. winget accepts several package types:

- exe installers (Inno, NSIS, and others), MSI, MSIX
- a zip containing any of those (the PRM pattern)
- **portable**: a standalone `.exe`, or a zip containing one, declared with
  `InstallerType: portable` (or `NestedInstallerType: portable` for a zip).
  winget unpacks it to a per-user folder and links it onto PATH. No installer
  needed. **(untested; check the current manifest schema docs first)**

Portable suits console tools with no shortcuts, file associations, or
runtime dependencies. An installer is the right choice when the program needs
any of: Start Menu shortcuts, file associations, a runtime dependency, or
registry entries (PRM needs all of these).

When you do use Inno Setup, winget expects:

- `PrivilegesRequired=lowest` goes with `Scope: user` (otherwise `machine`)
- a **constant `AppId`** across versions, so winget can recognize an upgrade
- the displayed app version matches `PackageVersion`
  **(untested; I believe winget compares them)**
- installs silently with `/SILENT /SUPPRESSMSGBOXES /NORESTART`
- no restart prompt (`RestartIfNeededByRun=no` fixed one in PRM)
- no hard-coded drive paths; use `{autopf}` (PRM originally had `D:\`)
- no custom wizard pages that block unattended mode
