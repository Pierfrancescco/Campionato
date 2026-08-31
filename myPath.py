import os
from pathlib import Path
from types import SimpleNamespace


import sys

def _trova_radice_progetto():
    """Trova la cartella principale del progetto cercando la presenza della cartella 'Csv'"""
    # 1. Prova cartella dell'eseguibile se congelato (frozen)
    if getattr(sys, 'frozen', False):
        p = Path(sys.executable).resolve().parent
    else:
        p = Path(__file__).resolve().parent

    # Se p contiene 'Csv', è la radice corretta
    if (p / 'Csv').exists():
        return p
    # Se p è una sottocartella (es. 'dist' o 'build') e il genitore contiene 'Csv'
    if (p.parent / 'Csv').exists():
        return p.parent
    # Fallback su directory di lavoro corrente o su genitore della directory di lavoro
    cwd = Path.cwd()
    if (cwd / 'Csv').exists():
        return cwd
    if (cwd.parent / 'Csv').exists():
        return cwd.parent
    return p

corrente = _trova_radice_progetto()

csv_dir = corrente / 'Csv'
excel_dir = corrente / 'Excel'
immagini_dir = corrente / 'Immagini'
ui_dir = corrente / 'UI'    

myPath = SimpleNamespace(
    utente = os.getlogin(),
    radice = str(corrente.drive + '\\') if os.name == 'nt' else '/',
    corrente = str(Path.cwd()),
    csv = str(corrente / 'Csv'),
    excel = str(excel_dir),
    immagini = str(immagini_dir),
    grafici = str(immagini_dir / 'Grafici'),
    icone = str(immagini_dir / 'Icone'),
    scudetti = str(immagini_dir / 'Scudetti'),
    sfondoPerApp = str(immagini_dir / 'Sfondo per App'),
    ui = str(ui_dir),
)
# end of myPath class

myFile = SimpleNamespace(
    urlSquadre = f'{myPath.csv}\\UrlSquadre.csv',
    squadre = f'{myPath.csv}\\UrlSquadre.csv',
    campionatoCorrente = f'{myPath.csv}\\Campionato.csv',
    campionatiPrecedenti = f'{myPath.csv}\\CampionatiPrecedenti.csv',
    classifica = f'{myPath.csv}\\Classifica.csv',
    metadati = f'{myPath.csv}\\Campionato_metadati.csv',
    campionatoCorrenteExcel = f'{myPath.excel}\\Campionato.xlsm',
    campionatiPrecedentiExcel = f'{myPath.excel}\\CampionatiPrecedenti.xlsm',
    graficoConfrontoSquadre = f'{myPath.grafici}\\confronto_squadre.png'
)