# Script PowerShell per avviare l'interfaccia Predizioni
# Gestisce automaticamente l'ambiente virtuale e l'avvio dell'applicazione

Write-Host ""
Write-Host "========================================"
Write-Host "   🏆 LAUNCHER PREDIZIONI CALCISTICHE"
Write-Host "========================================"
Write-Host ""

# Cambia directory
Set-Location "G:\Campionato\UI"

# Verifica che il file Python esista
if (-not (Test-Path "launcher_predizioni.py")) {
    Write-Host "❌ Errore: File launcher_predizioni.py non trovato" -ForegroundColor Red
    Write-Host "Esegui prima la conversione del file .ui in .py" -ForegroundColor Yellow
    pause
    exit 1
}

# Verifica che l'ambiente virtuale esista
if (-not (Test-Path "G:\Campionato\venv3.13.1\Scripts\python.exe")) {
    Write-Host "❌ Errore: Ambiente virtuale non trovato" -ForegroundColor Red
    Write-Host "Controlla il percorso dell'ambiente virtuale" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "🚀 Avvio dell'interfaccia predizioni..." -ForegroundColor Green
Write-Host ""

try {
    # Avvia l'applicazione
    & "G:\Campionato\venv3.13.1\Scripts\python.exe" launcher_predizioni.py
    
    Write-Host ""
    Write-Host "✅ Applicazione chiusa correttamente" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "❌ Errore nell'avvio dell'applicazione:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Suggerimenti per la risoluzione:" -ForegroundColor Yellow
    Write-Host "- Verifica che PyQt5 sia installato nell'ambiente virtuale" -ForegroundColor Yellow
    Write-Host "- Controlla che il file Predizioni.py sia stato generato correttamente" -ForegroundColor Yellow
    Write-Host "- Esegui: pip install PyQt5" -ForegroundColor Yellow
    Write-Host ""
    pause
}