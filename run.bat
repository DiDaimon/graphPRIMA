@echo off

set TMP=.tmp
set VENV_DIR=.venv
set PYTHON="%VENV_DIR%\Scripts\Python.exe"
%PYTHON% -c "" >%TMP%/stdout.txt 2>%TMP%/stderr.txt
%PYTHON% graphPRIMA.py %*