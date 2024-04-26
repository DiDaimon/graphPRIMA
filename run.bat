@echo off

set TMP=.tmp
set VENV_DIR=.venv
rem set MAIN_DIR="D:\Python\graphPRIMA"

rem cd /d %MAIN_DIR%
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
echo venv %PYTHON%
%PYTHON% -c "" >%TMP%/stdout.txt 2>%TMP%/stderr.txt
%PYTHON% graphPRIMA.py %*