@if /I "%~2"!="" goto :usage
@if /I "%~1"=="dryrun" goto :dryrun
@if /I "%~1"=="apply" goto :apply

:usage
   @echo USAGE:
   @echo     fix_makefiles [dryrun] [apply]
   @echo.
   @echo ARGUMENTS
   @echo    dryrun - Execute a dry run of this script
   @echo    apply - make and commit the changes
   @echo.
   @echo    Either dryrun or check are required
   @echo.
   @goto :eof

:dryrun
   python fix_update_rule.py 
   @goto :eof

:apply
   python fix_update_rule.py --apply
   @goto :eof
