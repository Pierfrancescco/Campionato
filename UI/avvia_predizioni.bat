@echo off
echo.
echo ========================================
echo    🏆 LAUNCHER PREDIZIONI CALCISTICHE
echo ========================================
echo.
echo Avvio dell'interfaccia predizioni...
echo.

cd /d "G:\Campionato\UI"
"G:\Campionato\venv3.13.1\Scripts\python.exe" launcher_predizioni.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Errore nell'avvio dell'applicazione
    echo Controlla che:
    echo - PyQt5 sia installato
    echo - Il file Predizioni.py sia stato generato
    echo - L'ambiente virtuale sia configurato correttamente
    echo.
    pause
) else (
    echo.
    echo ✅ Applicazione avviata con successo
)