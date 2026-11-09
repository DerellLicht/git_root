# Current help file formats

## You

So, we were working on one of my projects recently, and I mentioned maybe creating a helpfile for it.  For years, I've been using `HelpNDoc` to create `.chm` help files for my projects, which has been working fine under Windows 10.

However, you said that `.chm` was an obsolete format and might not be readable on some machines... honestly, I haven't had any problems yet, but I don't mind researching new options...

So what format is considered current, and are there any free (not adware) tools that will let me create helpfiles in such format?

## Claude

There isn't really a single successor to CHM. Microsoft's HTML Help engine has been frozen for a long time, and the modern approach is plain HTML. A help file is a folder of HTML/CSS/JS pages (a "WebHelp" site) that opens in any browser, and you can zip it up or host it online. PDF is the other common choice for a single-file manual.

**Why CHM is considered legacy**
- It still works on Windows 10 and 11, so you're not wrong that it hasn't bitten you yet.
- The usual failure is that Windows blocks a CHM that was downloaded from the internet. The viewer then shows blank pages or "Navigation canceled" until the user right-clicks the file, opens Properties and ticks **Unblock**. This matters if you distribute your programs through download sites.
- CHM also won't display properly from a network share, it's Windows-only, and Microsoft hasn't developed it in years.
- Third-party viewers exist for Linux and Mac, but they're a second-class experience.

**Free options**
- **HelpNDoc, which you already use.** Its free Personal Edition can generate CHM files, responsive HTML web-sites, PDF and Word documents, ePub and Kindle eBooks, Markdown documents, and Qt Help files. The restriction is that it can't be used for profit, and a discreet banner is added to the generated documentation. For your free software that's probably acceptable, though the banner will appear in the HTML output too. You could keep your current tool and just ship the HTML output alongside (or instead of) the CHM, with no new learning curve.
- **mdBook.** It's a single executable with no dependencies. You write Markdown and it produces a clean HTML site with a table of contents and search, and as far as I know the search works when you open the files straight from disk. It's open source, with no ads or banners.
- **MkDocs.** It's Python-based, so you already have what it needs. It gives you Markdown to a static site, and the Material theme looks good. The built-in search generally needs a web server unless you add an offline plugin, so it suits online docs better than a local help folder.
- **Pandoc.** It converts Markdown to a single self-contained HTML file or a PDF, which can work well for a small program that needs only a short manual.

For a Windows utility, I'd keep HelpNDoc and export responsive HTML, probably zipped with the program. If you'd rather have plain-text sources you can put under version control next to your code, mdBook is the best fit.

I only skimmed vendor and directory pages for this, so check the current HelpNDoc license terms on their site before relying on the banner and non-commercial details.

Sources:
- [HelpNDoc free version overview (TechSpot)](https://www.techspot.com/downloads/4882-helpndoc.html)
- [HelpNDoc pricing and edition differences](https://support.helpndoc.com/en/support/solutions/articles/43000504818-how-much-does-helpndoc-costs-)
- [HelpNDoc listing on SnapFiles](https://www.snapfiles.com/get/helpndoc.html)

## You

Oh, just to clarify... I have a registered copy of HelpNDoc v2.9.0.144 Standard Edition (2010)... so I don't even have to worry about the "discreet banner"... and commercial use is a non-issue, since all of my tools are CC0-1.0 ...

The thing I dislike about `.html` for a distributed application, is that you don't get a single help file, you get a spread-out file tree, which I feel is very sloppy... and every time I made a trivial change to the help file, I would have to make updates to the `.iss` file, to include all the correct items... a single `.chm` is soooo much cleaner !!!  *and* user doesn't have to open a full web browser to read it...

## Claude

Those are good reasons, and with an Inno Setup installer I'd say staying with CHM is a legitimate choice, not just stubbornness.

**The "blocked CHM" problem mostly doesn't apply to you.** It bites when someone downloads a bare `.chm` or extracts it from a zip with Explorer, because the file keeps its "downloaded from the internet" mark. As far as I know, files written out by an installer don't get that mark, so a CHM installed by your Inno Setup package should open normally. If you also offer a zip download, that's where an unblocked file could trip people up. A line in a readme about the Unblock checkbox covers it.

**If you ever do want HTML, the `.iss` maintenance problem is solvable.** Inno Setup can pull in a whole tree with one line, so you never edit the script when help pages change:

```
Source: "help\*"; DestDir: "{app}\help"; Flags: recursesubdirs createallsubdirs ignoreversion
```

The tree is still spread out on the user's disk, though, so it doesn't fix your sloppiness objection.

**If you want one file that isn't CHM,** the options are:
- **PDF.** It's a single file, but it needs a PDF reader and has no real navigation pane or search index.
- **Single-file HTML.** Pandoc can embed the CSS and images into one `.html` file. It opens in a browser, which you dislike.

Neither beats CHM for a single self-contained file with a built-in table of contents, index and search, opened by the viewer that ships with Windows.

The one real risk is that the CHM viewer (`hh.exe`) renders with Microsoft's old Internet Explorer engine. It still works on Windows 10 and 11, but Microsoft doesn't maintain it, so it could eventually break or lose features. Keep your HelpNDoc project files (`.hnd`), since they can export to other formats later if it comes to that.

My recommendation is to keep your current workflow, and I'd stop worrying about it until a real compatibility problem shows up.

## You

okay, cool ... thank you for all this input...

## Claude

You're welcome, Derell. Good luck with the helpfile when you get to it.
