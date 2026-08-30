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
If the existing changelog is in a file (version.h or other), use `revlog2md` script to generate `CHANGELOG.md` :  
`python ..\revlog2md.py version.h --title "project_name Changelog" -o CHANGELOG.md`  

2. make sure BASE is defined, as base-name of project 

3. copy-and-paste the `VERSION` and `DIST_ZIP` lines over  

4. change the `dist:` target to use `DIST_ZIP`  

5. copy-and-paste the `release:` target over  


