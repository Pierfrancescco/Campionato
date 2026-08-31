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


class MainWindow(QtWidgets.QMainWindow):
    @catturaEccezione
    def __init__(self, **kwargs):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.processiFigli = []  # Lista per tenere traccia dei processi figli
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
        
        # 🔗 Collegamenti ai pulsanti
        self.connettiPulsantiDelleSquadre()
        self.connettiPulsantiApp()
    # end __init__()

    def showEvent(self, event):
        super().showEvent(event)
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
    def apri_appClassifica(self):
        """Apre l'app Classifica come processo figlio con caricamento on-demand (lazy)"""
        tempo_inizio = time.time()
        from appClassifica import AppClassifica
        appClassifica = AppClassifica()
        self.processiFigli.append(appClassifica)
        appClassifica.show()
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di apertura Classifica: {tempo_esecuzione:.4f} secondi ({tempo_esecuzione*1000:.2f} ms)")
    # end apri_appClassifica()
    
    @catturaEccezione
    def apri_appStatistiche(self):
        """Apre l'app Statistiche come processo figlio con caricamento on-demand (lazy)"""
        tempo_inizio = time.time()
        from appStatistiche import AppStatistiche
        window = AppStatistiche()
        self.processiFigli.append(window)
        window.show()
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di apertura Statistiche: {tempo_esecuzione:.4f} secondi ({tempo_esecuzione*1000:.2f} ms)")
    # end apri_appStatistiche()
    
    @catturaEccezione
    def apri_appPredizioni(self):
        """Apre l'app Predizioni come processo figlio con caricamento on-demand (lazy)"""
        tempo_inizio = time.time()
        from appPredizioni import RunPredizioni
        appPredizioni = RunPredizioni()
        self.processiFigli.append(appPredizioni)
        appPredizioni.show()
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
