rem for %v in (binclock_redux, cdtimer, console_attr, derbar, fidelity_calcs, FranklinFW_data, gtstuff, images_gdip, LedScroll, media_list, ndir64, plus42_image_mgr, qualify, read_tree, terminal, uni_file_mgr, wbigcalc, wdparse, wFontList, winagrams, winwiz, wmetar) do call :update_der_libs %v
for %v in (binclock_redux, cdtimer, console_attr, derbar, fidelity_calcs, FranklinFW_data, gtstuff, images_gdip, LedScroll, media_list, ndir64, plus42_image_mgr, qualify, read_tree, terminal, uni_file_mgr, wbigcalc, wdparse, wFontList, winagrams, winwiz, wmetar) do call :update_der_libs %v
goto :eof

rem __Function update_der_libs
rem Arguments: %1
:update_der_libs
setlocal
cd %1\der_libs
git pull
cd ..
git commit -am "der_libs - integrate changes"
git push
cd..
@echo _
endlocal

