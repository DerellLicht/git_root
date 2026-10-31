# Distributing a program through Scoop

Scoop is a command-line installer for Windows. Users type `scoop install <name>` and it
downloads and installs the program. A **bucket** is a GitHub repository that holds one small
JSON file (a **manifest**) per program, telling Scoop where to download it and how to install it.
No one has to approve a bucket: you make the repository, and users add it as a source.

This document is the routine for adding a new program to a bucket and for updating it on each
release. It was worked out with CubicAdventurer (bucket repo `scoop-cubicadventurer`); the
Scoop installation itself is not covered here.

**Run every `scoop` command from a `cmd.exe` console, not from TCC.** Scoop's launcher
(`scoop.cmd`) prints `No closing quote` errors under TCC, and `powershell` may not be found
there. The same commands work normally in cmd.exe.

Note: only the manifest-generating script and the first install test were tested on the
CubicAdventurer release. The `scoop uninstall` step has NOT been tested yet (see "Known
limitations").

## What you need first

- A GitHub release of the program that contains a zip file. For CubicAdventurer this is
  `CubicAdventurerV0.99.setup.zip`, made by `make dist` and uploaded by `make release`.
  The zip holds the Inno Setup installer (`CubicAdventurerV0.99.setup.exe`).
- A bucket repository on GitHub (public), with a folder named `bucket` in it. One bucket can
  hold manifests for many programs; each program is one JSON file in that folder.
- Python, and the script `make_scoop_manifest.py` (kept next to the bucket).

## Adding a new program (one time per program)

1. **Adapt the script.** At the top of `make_scoop_manifest.py`, change `REPO` (the program's
   GitHub `owner/repo`) and, if the tag name differs, `TAG_PREFIX`. The zip-name pattern in
   `build_manifest` (`CubicAdventurerV<version>.setup.zip`) and the description text also name
   CubicAdventurer, so edit those. The uninstall path (`unins000.exe` under
   `Programs\CubicAdventurer`) is also specific to the program.
2. **Release the program first.** The release zip must already be on GitHub, because Scoop
   downloads it from there and checks its hash.
3. **Download the zip from the GitHub release page** and run the script on that downloaded
   file, not on your local build:
   ```
   python make_scoop_manifest.py CubicAdventurerV0.99.setup.zip
   ```
   The script reads the version from the file name, computes the SHA-256 hash (a fingerprint
   of the file) and writes `<name>.json`.
4. **Copy the JSON into the bucket's `bucket` folder.**
5. **Test it locally** (from cmd.exe, in the folder that holds the JSON):
   ```
   scoop install .\cubicadventurer.json
   ```
6. **Commit and push the bucket:**
   ```
   git add bucket/cubicadventurer.json
   git commit -m "Add cubicadventurer 0.99"
   git push
   ```
7. **Test it as a user would:**
   ```
   scoop bucket add cubicadventurer https://github.com/DerellLicht/scoop-cubicadventurer
   scoop install cubicadventurer
   ```
8. **Tell users.** Put the two commands from step 7 in the bucket's README and, if wanted, in
   the program's own README.

## Updating on every new release

1. Release the new version (`make release`), which uploads the new zip.
2. Download that zip from GitHub and run the script on it again.
3. Copy the new JSON over the old one in `bucket`, then commit and push.

**The hash must match the uploaded zip exactly.** `make dist` rebuilds the zip every time, and
a rebuilt zip has a different hash even when nothing changed. If you rebuild and re-upload the
zip, regenerate the JSON afterward. A "hash check failed" message from Scoop means the JSON
and the zip on GitHub do not match. After fixing it, clear any stale download with
`scoop cache rm <name>`.

## Behavior to expect

- Scoop unzips the download and runs the Inno Setup installer silently. A silent install
  reuses the folder and Start Menu group of an existing install of the same program, so on a
  machine that already has it Scoop upgrades in place. A fresh machine gets the installer's
  default folder and no choice of location.
- A leftover "isn't installed correctly" message after an earlier failed attempt is Scoop
  cleaning up; it is harmless.
- Scoop labels the install `[64bit]` when the manifest has no architecture block. That is only
  a label.

## Known limitations

- **Uninstall is untested, and the path is hardcoded.** The manifest's uninstall step assumes
  the default install folder. On a machine where the program was installed somewhere else, it
  would look in the wrong place. A more robust version would read the uninstaller's location
  from the registry entry that Inno Setup writes for the program's AppId. Do not run
  `scoop uninstall` on a machine with your everyday copy until this is checked.
- **No auto-update.** The manifest has no `checkver` / `autoupdate` section, so the script is
  rerun by hand for each release.
- **A program that is not an Inno Setup installer** (for example a plain zip of an
  executable) needs a different manifest: no `installer` block, and a `bin` entry naming the
  executable. That variant has not been tried here.
- Scoop's audience is mostly developers and power users, so this is an additional install
  route and a legitimate listing, not a major source of visibility.
