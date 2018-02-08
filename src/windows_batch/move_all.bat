SET src_folder=%1
SET dest_folder=%2

for /f %%a IN ('dir "%src_folder%" /b') do move %src_folder%\%%a %dest_folder%