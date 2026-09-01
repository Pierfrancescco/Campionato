import time
_T_INIZIO_AVVIO = time.perf_counter()

import os
import sys
import csv
import webbrowser
import signal
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

# Moduli base locali
from ErrorManager import catturaEccezione
from myPath import myPath, myFile
from UI.Window import Ui_MainWindow

_T_FINE_IMPORT = time.perf_counter()


class WarmupThread(QtCore.QThread):
    """Thread in background per precaricare silenziosamente in RAM le librerie pesanti e i dataset"""
    def run(self):
        try:
            # 1. Precarica librerie scientifiche e sottomoduli in memoria
            import pandas as pd
            import matplotlib.pyplot as plt
            from appClassifica import AppClassifica
            from appStatistiche import AppStatistiche
            from appPredizioni import RunPredizioni
            from EstrazioneDati import ottieni_dataframe_cache
            
            # 2. Pre-riscalda la cache in RAM dei file CSV principali
            if os.path.exists(myFile.campionatoCorrente):
                ottieni_dataframe_cache(myFile.campionatoCorrente)
            if os.path.exists(myFile.campionatiPrecedenti):
                ottieni_dataframe_cache(myFile.campionatiPrecedenti)
            if os.path.exists(myFile.classifica):
                ottieni_dataframe_cache(myFile.classifica)
        except Exception:
            pass


class MainWindow(QtWidgets.QMainWindow):
    @catturaEccezione
    def __init__(self, **kwargs):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.processiFigli = []  # Lista per tenere traccia dei processi figli
        self.warmup_thread = None
        self.setPath(**kwargs)
        self.sitiSquadre = self.popolaSitiSquadre(self.urlSquadre) # Carica i siti con parser CSV nativo ultrarapido
        
        # Imposta stile globale
        self.setStyleSheet("""
        QToolTip {
            color: #ffffff;
            background-color: #1e293b;
            border: 1px solid #4b5563;
            border-radius: 4px;
            padding: 5px 8px;
            font-size: 11pt;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QToolButton {
            /* Stile per i pulsanti delle squadre */
            background-color: transparent;
            border: none;
            color: white;
        }
        QToolButton:hover {
            /* Stile al passaggio del mouse */
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }
        QToolButton:pressed {
            /* Stile quando il pulsante è premuto */
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
        }
        """)

        # Imposta dimensioni
        self.setMinimumSize(800, 600)
        self.setMaximumSize(16777215, 16777215)
        self.resize(1920, 1000)
        
        # Imposta icona dell'applicazione
        icon_path = os.path.join(myPath.icone, "iconaApp.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
            
        # 🌟 Frase ad effetto nel frontespizio (Gioco Responsabile) - Centrata sotto gli scudetti
        self.labelQuote = QtWidgets.QLabel(self.ui.centralwidget)
        self.labelQuote.setText("""
        <div style="text-align: center; line-height: 120%;">
            <span style="font-size: 23pt; color: #FFFFFF; font-weight: 800; font-style: italic; letter-spacing: 0.5px;">“ Giocare è bello,</span><br>
            <span style="font-size: 20pt; color: #CBD5E1; font-weight: 600; font-style: italic;">farlo in modo responsabile</span><br>
            <span style="font-size: 24pt; color: #FFD700; font-weight: 800; font-style: italic; letter-spacing: 0.5px;">è meglio! ”</span>
        </div>
        """)
        self.labelQuote.setAlignment(QtCore.Qt.AlignCenter)
        self.labelQuote.setStyleSheet("""
            QLabel {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                            stop:0 rgba(15, 23, 42, 230), 
                            stop:1 rgba(30, 58, 138, 210));
                border: 2px solid rgba(255, 215, 0, 0.75);
                border-radius: 18px;
                padding: 12px 24px;
                font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        # Ombra elegante sul banner
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QtGui.QColor(0, 0, 0, 190))
        shadow.setOffset(4, 6)
        self.labelQuote.setGraphicsEffect(shadow)
        self.labelQuote.raise_()
        
        self.aggiornaPosizioneQuote()
        
        # 🔗 Collegamenti ai pulsanti
        self.connettiPulsantiDelleSquadre()
        self.connettiPulsantiApp()
    # end __init__()

    def aggiornaPosizioneQuote(self):
        """Mantiene il banner della frase ad effetto perfettamente centrato e posizionato appena sotto gli scudetti"""
        if hasattr(self, 'labelQuote'):
            bw = 860
            bh = 195
            bx = max(20, (self.width() - bw) // 2)
            by = 150  # Posizionato appena sotto gli scudetti (y=130)
            self.labelQuote.setGeometry(bx, by, bw, bh)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.aggiornaPosizioneQuote()

    def showEvent(self, event):
        super().showEvent(event)
        self.aggiornaPosizioneQuote()
        if not getattr(self, '_misurato_tempo_avvio', False):
            self._misurato_tempo_avvio = True
            t_fine = time.perf_counter()
            tempo_totale = t_fine - _T_INIZIO_AVVIO
            tempo_import = _T_FINE_IMPORT - _T_INIZIO_AVVIO
            tempo_ui = t_fine - _T_FINE_IMPORT
            print("\n" + "=" * 60)
            print("🚀 STATISTICHE DI AVVIO APPLICAZIONE")
            print("=" * 60)
            print(f"⏱️  TEMPO TOTALE ALLA PRIMA VIDEATA:  {tempo_totale:.4f} s ({tempo_totale * 1000:.2f} ms)")
            print(f"   • Importazione moduli e librerie: {tempo_import:.4f} s ({tempo_import * 1000:.2f} ms)")
            print(f"   • Inizializzazione e rendering UI: {tempo_ui:.4f} s ({tempo_ui * 1000:.2f} ms)")
            print("=" * 60 + "\n")
            
            # Avvia riscaldamento in background a bassa priorità
            self.warmup_thread = WarmupThread()
            self.warmup_thread.start(QtCore.QThread.LowestPriority)
    
    @catturaEccezione
    def setPath(self, **kwargs):
        self.utente = kwargs.get('utente') or myPath.utente
        self.pathRadice = kwargs.get('radice') or myPath.radice
        self.urlSquadre = kwargs.get('urlSquadre') or myFile.urlSquadre
        self.campionatoCorrente = kwargs.get('campionatoCorrente') or myFile.campionatoCorrente
        self.campionatiPrecedenti = kwargs.get('campionatiPrecedenti') or myFile.campionatiPrecedenti
        self.classifica = kwargs.get('classifica') or myFile.classifica
        self.metadati = kwargs.get('metadati') or myFile.metadati
        self.campionatoCorrenteExcel = kwargs.get('campionatoCorrenteExcel') or myFile.campionatoCorrenteExcel
        self.campionatiPrecedentiExcel = kwargs.get('campionatiPrecedentiExcel') or myFile.campionatiPrecedentiExcel
    # end of setPath()
    
    @catturaEccezione
    def popolaSitiSquadre(self, file_path=None):
        """Legge il file CSV con il parser standard (ultrarapido, <1ms)"""
        sitiSquadre = {}
        target = file_path or self.urlSquadre or myFile.urlSquadre
        if target and os.path.exists(target):
            try:
                with open(target, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    for row in reader:
                        if 'Squadre' in row and 'Url' in row:
                            sitiSquadre[row['Squadre'].strip()] = row['Url'].strip()
            except Exception:
                with open(target, mode='r', encoding='latin1') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    for row in reader:
                        if 'Squadre' in row and 'Url' in row:
                            sitiSquadre[row['Squadre'].strip()] = row['Url'].strip()
        return sitiSquadre
    # end of popolaSitiSquadre()
    
    @catturaEccezione
    def connettiPulsantiDelleSquadre(self):
        """Collega i pulsanti ai siti ufficiali e imposta tooltip/icone"""
        if not self.sitiSquadre or not isinstance(self.sitiSquadre, dict):
            self.sitiSquadre = self.popolaSitiSquadre(self.urlSquadre) or {}
            
        squadre_list = list(self.sitiSquadre.keys())
        for btn in range(1, min(21, len(squadre_list) + 1)):
            toolButton = getattr(self.ui, f'toolButton_{btn}', None)
            if toolButton and (btn - 1) < len(squadre_list):
                squadra_nome = squadre_list[btn - 1]
                url = self.sitiSquadre.get(squadra_nome, "")
                
                # Se l'icona non è già stata caricata dalle risorse Qt
                if toolButton.icon().isNull():
                    path_icona = os.path.join(myPath.scudetti, f"{squadra_nome}.png")
                    if os.path.exists(path_icona):
                        toolButton.setIcon(QtGui.QIcon(path_icona))
                        toolButton.setIconSize(QtCore.QSize(90, 90))
                
                toolButton.setToolTip(f"{squadra_nome} - Sito Ufficiale")
                if url:
                    toolButton.clicked.connect(lambda checked, u=url: webbrowser.open(u))
    # end of connettiPulsantiDelleSquadre()
    
    @catturaEccezione
    def connettiPulsantiApp(self):
        if hasattr(self.ui, 'pushButton_Aggiorna'):
            self.ui.pushButton_Aggiorna.clicked.connect(lambda: self.apri_aggiornaCampionato())
        self.ui.pushButton_Classifica.clicked.connect(lambda: self.apri_appClassifica())
        self.ui.pushButton_Statistiche.clicked.connect(lambda: self.apri_appStatistiche())
        self.ui.pushButtonPredizioni.clicked.connect(lambda: self.apri_appPredizioni())
        self.ui.pushButton_closeApp.clicked.connect(self.close_application)
    # end of connettiPulsantiApp()
    
    @catturaEccezione
    def close_application(self, event=None):
        """Chiude l'applicazione"""
        self.close()
    # end close_application()
    
    @catturaEccezione
    def apri_aggiornaCampionato(self):
        """Apre la finestra di estrazione e aggiornamento dati da internet"""
        tempo_inizio = time.time()
        from aggiornaCampionato import AggiornaClassificaWindow
        self.win_aggiorna = AggiornaClassificaWindow(parent=self, standalone=False)
        self.processiFigli.append(self.win_aggiorna)
        
        # Alla conclusione dell'aggiornamento, invalidiamo le vecchie istanze e la cache in RAM
        def on_aggiornamento_finito(*args):
            try:
                from EstrazioneDati import _DF_CACHE
                _DF_CACHE.clear()
            except Exception:
                pass
            self._win_classifica = None
            self._win_statistiche = None
            self._win_predizioni = None

        if hasattr(self.win_aggiorna, 'worker') and self.win_aggiorna.worker:
            self.win_aggiorna.worker.finished_signal.connect(on_aggiornamento_finito)
            
        self.win_aggiorna.show()
        self.win_aggiorna.raise_()
        self.win_aggiorna.activateWindow()
        tempo_fine = time.time()
        print(f"⏱️  Finestra di aggiornamento aperta in: {(tempo_fine - tempo_inizio)*1000:.2f} ms")
    # end apri_aggiornaCampionato()

    @catturaEccezione
    def apri_appClassifica(self):
        """Apre l'app Classifica come processo figlio con apertura istantanea"""
        tempo_inizio = time.time()
        from appClassifica import AppClassifica
        if not hasattr(self, '_win_classifica') or self._win_classifica is None:
            self._win_classifica = AppClassifica()
            self.processiFigli.append(self._win_classifica)
        self._win_classifica.show()
        self._win_classifica.raise_()
        self._win_classifica.activateWindow()
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di apertura Classifica: {tempo_esecuzione:.4f} secondi ({tempo_esecuzione*1000:.2f} ms)")
    # end apri_appClassifica()
    
    @catturaEccezione
    def apri_appStatistiche(self):
        """Apre l'app Statistiche come processo figlio con apertura istantanea"""
        tempo_inizio = time.time()
        from appStatistiche import AppStatistiche
        if not hasattr(self, '_win_statistiche') or self._win_statistiche is None:
            self._win_statistiche = AppStatistiche()
            self.processiFigli.append(self._win_statistiche)
        self._win_statistiche.show()
        self._win_statistiche.raise_()
        self._win_statistiche.activateWindow()
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di apertura Statistiche: {tempo_esecuzione:.4f} secondi ({tempo_esecuzione*1000:.2f} ms)")
    # end apri_appStatistiche()
    
    @catturaEccezione
    def apri_appPredizioni(self):
        """Apre l'app Predizioni come processo figlio con apertura istantanea"""
        tempo_inizio = time.time()
        from appPredizioni import RunPredizioni
        if not hasattr(self, '_win_predizioni') or self._win_predizioni is None:
            self._win_predizioni = RunPredizioni()
            self.processiFigli.append(self._win_predizioni)
        self._win_predizioni.show()
        self._win_predizioni.raise_()
        self._win_predizioni.activateWindow()
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di apertura Predizioni: {tempo_esecuzione:.4f} secondi ({tempo_esecuzione*1000:.2f} ms)")
    # end apri_appPredizioni() 
    
    @catturaEccezione
    def chiudi_tutte_le_app(self):
        """Chiude tutti i processi figli attivi"""
        for processo in self.processiFigli[:]:
            try:
                processo.close()
                processo.deleteLater()
            except Exception:
                pass
        self.processiFigli.clear()
    # end of chiudi_tutte_le_app()
    
    @catturaEccezione
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione principale"""
        print("Chiusura app principale - terminando tutti i processi figli...")
        self.chiudi_tutte_le_app()
        event.accept()
    # end of closeEvent()
# end of MainWindow class


class CheckFile:
    @staticmethod
    @catturaEccezione
    def checkFilesExistence():
        """Controlla l'esistenza dei file critici all'avvio"""
        critical_files = [
            myFile.urlSquadre,
            myFile.campionatoCorrente,
            myFile.campionatiPrecedenti,
            myFile.campionatiPrecedentiExcel,
            myFile.campionatoCorrenteExcel
        ]
        missing_files = [f for f in critical_files if not os.path.isfile(f)]
        if myFile.campionatoCorrenteExcel in missing_files:
            QMessageBox.critical(None, "Errore Critico", f"Il file Excel --> {myFile.campionatoCorrenteExcel} è mancante. Impossibile fare predizioni e statistiche.")
            sys.exit(1)
        
        if myFile.campionatiPrecedentiExcel in missing_files:
            from EstrazioneDati import EstrazioneDati
            estrazioneDati = EstrazioneDati(myFile.campionatiPrecedentiExcel)
            QMessageBox.critical(None, "Errore Critico", f"Il file Excel {myFile.campionatiPrecedentiExcel} è mancante. File generato automaticamente.")
            sys.exit(1)
            
        if myFile.urlSquadre in missing_files:
            QMessageBox.critical(None, "Errore Critico", f"Il file CSV {myFile.urlSquadre} è mancante. Impossibile continuare.")
            sys.exit(1)
        
        if myFile.campionatiPrecedenti in missing_files:
            from EstrazioneDati import EstrazioneDati
            estrazioneDati = EstrazioneDati(myFile.campionatiPrecedentiExcel)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("""
        QToolTip {
            color: #ffffff;
            background-color: #1e293b;
            border: 1px solid #4b5563;
            border-radius: 4px;
            padding: 5px 8px;
            font-size: 10pt;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)
    window = MainWindow(
        utente=myPath.utente,
        radice=myPath.radice,
        urlSquadre=myFile.urlSquadre,
        campionatoCorrente=myFile.campionatoCorrente,
        campionatiPrecedenti=myFile.campionatiPrecedenti,
        classifica=myFile.classifica,
        metadati=myFile.metadati,
        campionatiPrecedentiExcel=myFile.campionatiPrecedentiExcel
    )
    
    # Gestione segnali per chiusura pulita
    def signal_handler(signum, frame):
        print(f"\nRicevuto segnale {signum}, chiusura in corso...")
        window.chiudi_tutte_le_app()
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    window.show()
    sys.exit(app.exec_())
