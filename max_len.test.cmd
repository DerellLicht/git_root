rem for %v in (binclock_redux, cdtimer, derbar, fidelity_calcs, FranklinFW_data, images_gdip, LedScroll, media_list, ndir32, plus42_image_mgr, qualify, read_tree, terminal, uni_file_mgr, wbigcalc, wdparse, wFontList, winagrams, winwiz, wmetar) do call :update_der_libs %v
for %v in (binclock_redux, cdtimer, derbar, fidelity_calcs, FranklinFW_data, images_gdip, LedScroll, media_list, ndir32, plus42_image_mgr, qualify, read_tree, terminal, uni_file_mgr, wbigcalc, wdparse, wFontList, winagrams, winwiz, wmetar) do call :update_der_libs %v
goto :eof

rem __Function update_der_libs
rem Arguments: %1
:update_der_libs
setlocal
max_len %1\*
@echo _
endlocal

