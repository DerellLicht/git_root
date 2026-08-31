@echo off
setlocal enabledelayedexpansion

:: deprecate-repo.cmd
::
:: Marks a single GitHub repo as obsolete/superseded, then archives it.
:: Requires: gh CLI and git, both on PATH, gh already authenticated.
:: Operates on your EXISTING local clone -- does not clone a fresh copy.
::
:: Runs, in order (order matters -- once archived, a repo rejects pushes,
:: so archiving must happen last):
::   1. Prefix the repo description with "[DEPRECATED]" and add the
::      "deprecated" topic
::   2. In the existing local clone: prepend a deprecation notice to
::      README.md (linking the successor repo, if given), commit, push
::   3. Archive the repository (gh repo archive) -- reversible later
::      via `gh repo unarchive`
::
:: If the local clone has uncommitted changes sitting in it, steps 2 and 3
:: are skipped (flagged in the output) so the script never commits,
:: pushes, or archives on top of unrelated in-progress work.
::
:: Usage:
::   deprecate-repo.cmd <owner/repo> <successor-owner/repo-or-none> <local-path> [/DRYRUN]
::
:: Examples:
::   deprecate-repo.cmd yourusername/old-project yourusername/new-project C:\dev\old-project
::   deprecate-repo.cmd yourusername/old-project none C:\dev\old-project
::   deprecate-repo.cmd yourusername/old-project none C:\dev\old-project /DRYRUN

if "%~3"=="" (
    echo Usage: %~nx0 ^<owner/repo^> ^<successor-owner/repo-or-none^> ^<local-path^> [/DRYRUN]
    exit /b 1
)

set "REPO=%~1"
set "SUCCESSOR=%~2"
set "LOCALPATH=%~3"
if /I "%SUCCESSOR%"=="none" set "SUCCESSOR="

set "DRYRUN=0"
if /I "%~4"=="/DRYRUN" (
    set "DRYRUN=1"
    echo Running in DRY RUN mode -- no changes will be made.
)

echo ----------------------------------------------------
echo Processing %REPO% ...

call :UpdateDescription
call :UpdateReadme
if "%SKIP_ARCHIVE%"=="1" (
    echo   Skipping archive due to earlier warning.
) else (
    call :ArchiveRepo
)

echo Done with %REPO%.
goto :EOF


:: UpdateDescription
:: Prepends "[DEPRECATED]" to the current repo description and adds the
:: "deprecated" topic.
:UpdateDescription
for /f "delims=" %%D in ('gh repo view %REPO% --json description -q ".description"') do set "CURDESC=%%D"
set "NEWDESC=[DEPRECATED] %CURDESC%"

if "%DRYRUN%"=="1" (
    echo   [DRY RUN] description -^> "%NEWDESC%", topic -^> deprecated
) else (
    echo   Setting description: %NEWDESC%
    gh repo edit %REPO% --description "%NEWDESC%" --add-topic deprecated
)
goto :EOF


:: UpdateReadme
:: Edits README.md in the existing local clone at %LOCALPATH%: prepends a
:: deprecation notice, commits, and pushes. Sets SKIP_ARCHIVE=1 (and skips
:: its own edits) if the folder is missing, isn't a git repo, or has
:: uncommitted changes.
:UpdateReadme
set "SKIP_ARCHIVE=0"

if not exist "%LOCALPATH%\.git" (
    echo   WARNING: "%LOCALPATH%" not found or not a git repo -- skipping README update and archive.
    set "SKIP_ARCHIVE=1"
    goto :EOF
)

if "%DRYRUN%"=="1" (
    echo   [DRY RUN] would update README.md, commit, and push in %LOCALPATH%
    goto :EOF
)

pushd "%LOCALPATH%"

set "DIRTY="
for /f "delims=" %%S in ('git status --porcelain') do set "DIRTY=1"
if defined DIRTY (
    echo   WARNING: %LOCALPATH% has uncommitted changes -- skipping README update and archive.
    set "SKIP_ARCHIVE=1"
    popd
    goto :EOF
)

git pull --quiet

if not exist "README.md" (
    echo   No README.md found -- skipping README update.
    popd
    goto :EOF
)

findstr /b /c:"# DEPRECATED" "README.md" >nul
if not errorlevel 1 (
    echo   README already marked deprecated -- skipping.
    popd
    goto :EOF
)

set "NOTICE=_notice.tmp"
> "%NOTICE%" echo # DEPRECATED
>> "%NOTICE%" echo.
if not "%SUCCESSOR%"=="" (
    >> "%NOTICE%" echo This repository is no longer maintained. It has been superseded by [%SUCCESSOR%]^(https://github.com/%SUCCESSOR%^).
) else (
    >> "%NOTICE%" echo This repository is no longer maintained.
)
>> "%NOTICE%" echo.
>> "%NOTICE%" echo ---
>> "%NOTICE%" echo.

copy /b "%NOTICE%"+"README.md" "README_new.md" >nul
move /y "README_new.md" "README.md" >nul
del "%NOTICE%"

git add README.md
git commit -m "Mark repository as deprecated" --quiet
git push --quiet

popd
goto :EOF


:: ArchiveRepo
:: Final step -- makes the repo read-only.
:ArchiveRepo
if "%DRYRUN%"=="1" (
    echo   [DRY RUN] would archive %REPO%
) else (
    echo   Archiving %REPO%
    gh repo archive %REPO% --yes
)
goto :EOF
