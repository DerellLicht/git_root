##  Github release procedure  
This file will document the initial Github release procedure for repositories
which do not yet have a Release present.

1. Generate `CHANGELOG.md` file from either existing version file or copied from other repos.  
The document should be in standard Github changelog format:
```text
# MediaList Changelog

## [1.03] - 2025-06-03
- Converted files linked list to vector/unique_ptr

## [1.02] - 2025-05-31
- Add support for SVG files
```
If the existing changelog is in a file (version.h or other), and is in ascending order by version or date,
use `revlog2md` script to generate `CHANGELOG.md` :  
`python ..\revlog2md.py version.h --title "project_name Changelog" -o CHANGELOG.md`  

2. make sure BASE is defined, as base-name of project 

3. copy-and-paste the `VERSION`, `DIST_ZIP`, `.PHONY` lines over  

4. change the `dist:` target to use `DIST_ZIP`  

5. copy-and-paste the `release:` target over  

---
##  How to update distribution without rolling version number

## Path A: Re-create the Release from Scratch (Cleanest)
If no one has downloaded your release yet, the cleanest approach is to delete the faulty release and publish the updated zip package.

Run these commands in your console:  

1. Delete the existing release from GitHub:  
`gh release delete v2.71 --yes`

2. Re-run your automated target:  
`make release`

*Why this works:* Your `make release` rule automatically triggers `dist` first. The `dist` target wipes your old zip file, builds the fresh one with your missing file (once you update the `dist:` recipe), and pushes the brand-new package up to GitHub seamlessly.  

## Path B: Just Upload the Missing File Natively
If you don't want to delete the release and regenerate the zip, you can upload the missing file directly to the existing release page as a standalone asset.  

Run this command in your console:

`gh release upload v2.71 ./path/to/your/missing_file.ext --clobber`

*Why this works:* The `gh release upload` command expects the tag to already exist and cleanly appends the new file to the current release assets page alongside your `$(DIST_ZIP)` and `CHANGELOG.md`.

---
##  Dealing with manual Release, not compatible with our new system

## Me  

Okay, now I have a repo where I manually did a Release, on the web site... I don't know whether I actually tagged it with a version or not, but probably not... now I would like to do our release or update process, but I'm not sure what to do about the latent history...??

## Gemini

Handling a repository that already has a manually created release on the website is a very common scenario. You don't have to worry about breaking the repository's history, as GitHub handles these situations gracefully.

When you create a release via the GitHub website, **GitHub forces you to type or select a version tag** before it allows you to hit publish. Therefore, a tag definitely exists on GitHub for that manual release.

The only reason you might not see it locally is that you haven't pulled down the tag metadata from GitHub to your local machine yet.

Here is how you handle this "latent history" safely based on what you want to achieve:

Step 1: Sync Your Local Git History

Before running any `make` targets, synchronize your local machine with whatever was done on the website. Run this command in your console:

```
git fetch --tags origin
```

-   **Why this is critical:** This pulls down the hidden tag metadata from GitHub. Once you run this, your local git history will perfectly match GitHub's release history, and commands like `git tag` will show the version tag created on the web.

---

Step 2: Choose Your Path Forward

Depending on whether the version inside your local `CHANGELOG.md` matches the version of that manual web release, choose one of these two options:

Option A: If `CHANGELOG.md` version MATCHES the web release version

If your local `CHANGELOG.md` 's top entry matches the tag used on the website, you can use your brand-new `update:` target to instantly sync everything up.

```
make update
```

-   **What happens:** Your `update` rule will trigger `make dist` to compile your binaries and build the fresh zip file. It then uses `gh release upload ... --clobber` to overwrite whatever zip files you manually uploaded to the website earlier, keeping the release text and history completely intact!

Option B: If you want to overwrite it completely and use your extracted notes

If you want to blow away the manual web release so your automated system can recreate it cleanly with your perfectly parsed `CHANGELOG.md` text snippet, simply delete the remote entry first:

```
# 1. Pull the version from your file variables
gh release delete v2.71 --yes

# 2. Re-release completely from scratch
make release
```

*(Note: Change `v2.71` to whatever the exact version tag was on the website).*

Option C: If `CHANGELOG.md` is a HIGHER version (The web release is legacy)

If the web release was, say, version `2.70`, and your `CHANGELOG.md` is now at `2.71`, **you don't have to do anything special at all!**

```
make release
```

-   **What happens:** Your script will run flawlessly. GitHub will seamlessly place your new `2.71` release right on top of the old manual web release in your project's history timeline.

---

If you aren't sure what version tag was used on the website, type **`gh release list`** in your console. It will instantly spit out the exact version tag string GitHub has on record!

Did the `gh release list` show a matching version tag to what you have ready in your local files?


## Me  
Okay, here is the tags info... 
I *think* what this tells us, is the entire filename is the tag, right?? 
In that case, it *doesn't* match what is in CHANGELOG.md, 
which is `## \[6.11\] - 2026-08-27`  

```text
D:\\SourceCode\\Git\\wbigcalc Yes, Master?? > git fetch --tags origin
From https://github.com/DerellLicht/wbigcalc 
* [new tag] WBigCalc_V6.11 -> WBigCalc_V6.11
```
So I *think* I can just 'make update'?? or not??

## Gemini

No, running `make update` **will not work directly** because of the way the tag name is structured.

Your `git fetch` command revealed that the tag on GitHub is named **`WBigCalc_V6.11`**. However, your `Makefile` expects the tag to be strictly **`v6.11`** (parsed from `[6.11]` in your `CHANGELOG.md`). Because the names do not match identically, GitHub will treat `v6.11` as a brand-new release instead of updating the existing one.

To get this repository cleanly into your automated pipeline, you have two excellent choices depending on how you want to handle the historical tag name.

---

Since you are migrating this project to your new, standardized automated system, the cleanest route is to delete that custom `WBigCalc_V6.11` tag from the server and let your script rebuild a standard `v6.11` release from scratch.

Run these commands in your console:

1.  **Delete the manual web release and the old tag from GitHub:**

    ```
    gh release delete WBigCalc_V6.11 --yes
    ```

2.  **Delete the old tag from your local machine:**

    ```
    git tag -d WBigCalc_V6.11
    ```

3.  **Execute your new automated pipeline:**

    ```
    make release
    ```


-   **Why this is best:** This wipes the slate clean and lets your `Makefile` automatically create a standardized `v6.11` release tag. It updates your downloads and embeds your freshly extracted `CHANGELOG.md` notes perfectly into the GitHub page.

---

Option B: Update the Existing Release Manually One Last Time

If you explicitly want to keep the name `WBigCalc_V6.11` on GitHub for that specific release, you cannot use your `Makefile` targets directly without modifying the `VERSION` macro. Instead, you can run a manual one-time `gh` command in your console to push the updated archive up to the existing tag.

Run these commands in your console:

1.  **Generate the new zip archive locally:**

    ```
    make dist
    ```

2.  **Manually push it to the specific web tag using the `--clobber` flag:**

    ```
    gh release upload WBigCalc_V6.11 ./wbigcalcV6.11.zip ./CHANGELOG.md --clobber
    ```

    *(Note: Ensure the zip filename matches exactly what `make dist` built).*

---

For your long-term goal of unifying all 57 repositories into a copy-and-paste system, **Option A** is the best path forward because it ensures `wbigcalc` follows the exact same naming scheme as your other completed projects.

Let me know which option you choose to go with! If you choose Option A, did the deletion commands clear out the old tag smoothly?

## Me  

Okay, excellent!! Option A worked perfectly, and now this repo is consistent with the others, which is the most desirable option!! Thank you again!

## Gemini

That is absolutely wonderful news! Cleaning the slate with **Option A** was a brilliant strategic choice. Now `wbigcalc` stands perfectly in formation with your other repositories, using the exact same clean, automated naming conventions.

You have successfully navigated tags, complex Makefile variable nesting, tricky Windows console quoting bugs, and now legacy remote repository alignment. You are fully in the driver's seat of this portfolio modernization.

Have an excellent time moving through the rest of your priority list! It has been an absolute pleasure assisting you with this milestone project. Take care, and happy automated releasing!


