@echo off
setlocal

:: Define the fixed Mediafire URL
set mediafire_url=https://www.mediafire.com/file/r9v1f68wz5zltuy/SpineViewer.zip/file

:: Define the output folder path relative to the location of the bat file
set output_folder=%~dp0SpineViewer-anosu

:: Ensure the "SpineViewer-anosu" folder exists
if not exist "%output_folder%" (
    mkdir "%output_folder%"
)

:: Run the Python command with the fixed URL and output folder
python mediafire.py "%mediafire_url%" -o "%output_folder%" -t 20

:: Pause to show the result
echo Download completed to: %output_folder%
exit /b
