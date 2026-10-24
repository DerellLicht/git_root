## Commands for interacting with winget  

### see if program is available
```
D:\SourceCode\Git\PrettyReMark Yes, Master?? > winget search PrettyReMark
Name         Id                       Version Source
-----------------------------------------------------
PrettyReMark DerellLicht.PrettyReMark 1.13    winget
```

### see if local copy is installed
```
D:\SourceCode\Git\PrettyReMark Yes, Master?? > winget list DerellLicht.prettyremark
Name              Id                       Version Source
----------------------------------------------------------
PrettyReMark 1.20 DerellLicht.PrettyReMark 1.20    winget
```

### "refresh your index"
i.e., update winget's record of projects
```
C:\Users\dan7m\Downloads Yes, Master?? > winget source update
Updating all sources...
Updating source: msstore...
Done
Updating source: winget...
  ██████████████████████████████  100%
Done
Updating source: winget-font...
Done
```

### get information about a project
```
C:\Users\dan7m\Downloads Yes, Master?? > winget show DerellLicht.PrettyReMark
Found PrettyReMark [DerellLicht.PrettyReMark]
Version: 1.13
Publisher: DerellLicht
Publisher Url: https://gitlab.com/DerellLicht
Description:
  PrettyReMark is a native, tabbed Markdown viewer for
  Windows built with .NET 8 and WebView2. This fork adds a JSON-based user
  color-override config, an Options dialog, window position/size persistence,
  per-file scroll-position memory, and fixes for local file/image links and
  mailto: links. PrettyReMark is a fork of eagle1's PrettyMark.
  Features carried over from upstream include GitHub-flavored
  Markdown rendering, syntax highlighting, live reload on file save, dark
  mode, multi-tab support, drag and drop, find bar, print support, and
  multi-language UI.
Homepage: https://gitlab.com/DerellLicht/pretty-mark
License: MIT
License Url: https://gitlab.com/DerellLicht/pretty-mark/-/blob/main/LICENSE.MIT.txt
Tags:
  markdown
  viewer
  markdown-viewer
Installer:
  Installer Type: inno (zip)
  Installer Url: https://gitlab.com/DerellLicht/pretty-mark/-/releases/v1.13/downloads/PrettyReMarkV1.13.setup.zip
  Installer SHA256: 47e4f5425c54624b7dbece0add4f32effe6b779f9d7289a5f9dc81d9dd03a2ef
  Offline Distribution Supported: true
  Dependencies:
    - Package Dependencies:
        Microsoft.EdgeWebView2Runtime
```
