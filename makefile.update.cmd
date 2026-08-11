rem about_hlinks, binclock_redux, cdtimer, derbar, FranklinFW_data, gstuff, images_gdip, LedScroll, media_list, ndir32, plus42_image_mgr, snippets, svg_hacker, terminal, ToolTipTest, unicode_console, uni_file_mgr, wbigcalc, wdparse, winwiz

for %v in (about_hlinks, cdtimer, derbar, FranklinFW_data, gstuff, images_gdip, LedScroll, media_list, ndir32, plus42_image_mgr, snippets, svg_hacker, terminal, ToolTipTest, unicode_console, uni_file_mgr, wbigcalc, wdparse, winwiz) do call :git_commit %v
goto :eof

rem __Function git_commit
rem Arguments: %1
:git_commit
setlocal
cd %1
git commit -am "Makefile: change d:/clang to d:/llvm"
git push
@echo _
endlocal

