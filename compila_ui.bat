@echo off
setlocal
echo ========================================
echo   Compilazione file .ui e .qrc (PyQt5)
echo ========================================
echo.

set PYUIC="%~dp0venv3.13.1\Scripts\pyuic5.exe"
set PYRCC="%~dp0venv3.13.1\Scripts\pyrcc5.exe"

if not exist %PYUIC% set PYUIC=pyuic5
if not exist %PYRCC% set PYRCC=pyrcc5

echo [1/5] Compilazione Classifica.ui...
%PYUIC% "%~dp0UI\Classifica.ui" -o "%~dp0UI\Classifica.py"

echo [2/5] Compilazione Esiti.ui...
%PYUIC% "%~dp0UI\Esiti.ui" -o "%~dp0UI\Esiti.py"

echo [3/5] Compilazione Grafici.ui...
%PYUIC% "%~dp0UI\Grafici.ui" -o "%~dp0UI\Grafici.py"

echo [4/5] Compilazione Predizioni.ui...
%PYUIC% "%~dp0UI\Predizioni.ui" -o "%~dp0UI\Predizioni.py"

echo [5/5] Compilazione Window.ui...
%PYUIC% "%~dp0UI\Window.ui" -o "%~dp0UI\Window.py"

if exist "%~dp0resource.qrc" (
    echo Compilazione resource.qrc...
    %PYRCC% "%~dp0resource.qrc" -o "%~dp0resource_rc.py"
)

echo.
echo ========================================
echo   Compilazione completata con successo!
echo ========================================
pause
