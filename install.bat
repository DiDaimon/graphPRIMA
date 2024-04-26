@echo off

set PYTHON=python
set GIT=git
mkdir .venv 2>NUL
set VENV_DIR=.venv
mkdir .tmp 2>NUL
set TMP=.tmp

xcopy /y "graphPRIMA.lnk" "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\SendTo"

%PYTHON% -c "" >%TMP%/stdout.txt 2>%TMP%/stderr.txt
if %ERRORLEVEL% == 0 goto :check_pip
echo Couldn't launch python
goto :show_stdout_stderr
echo venv %PYTHON%

:check_pip
%PYTHON% -mpip --help >%TMP%/stdout.txt 2>%TMP%/stderr.txt
if %ERRORLEVEL% == 0 goto :start_venv
echo Install pip
goto :show_stdout_stderr

:start_venv
dir "%VENV_DIR%\Scripts\Python.exe" >%TMP%/stdout.txt 2>%TMP%/stderr.txt
if %ERRORLEVEL% == 0 goto :activate_venv

for /f "delims=" %%i in ('CALL %PYTHON% -c "import sys; print(sys.executable)"') do set PYTHON_FULLNAME="%%i"
echo Creating venv in directory %VENV_DIR% using python %PYTHON_FULLNAME%
%PYTHON_FULLNAME% -m venv "%VENV_DIR%" >%TMP%/stdout.txt 2>%TMP%/stderr.txt
if %ERRORLEVEL% == 0 goto :activate_venv
echo Unable to create venv in directory "%VENV_DIR%"
goto :show_stdout_stderr

:activate_venv
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
echo venv %PYTHON%
git pull origin
%PYTHON% -m pip install -r requirements.txt --no-warn-script-location | findstr /V "Requirement already satisfied"
echo All OK
goto :endofscript

:show_stdout_stderr
echo.
echo exit code: %errorlevel%
for /f %%i in (".tmp\stdout.txt") do set size=%%~zi
if %size% equ 0 goto :show_stderr
echo.
echo stdout:
type %TMP%\stdout.txt

:show_stderr
for /f %%i in (".tmp\stderr.txt") do set size=%%~zi
if %size% equ 0 goto :show_stderr
echo.
echo stderr:
type %TMP%\stderr.txt

:endofscript
echo.
echo Install successful. Exiting.
pause
