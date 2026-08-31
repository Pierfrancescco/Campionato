import time
_T_INIZIO_AVVIO = time.perf_counter()

import os
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import signal

import subprocess
import sys
import webbrowser

# I miei moduli
from aggiornaCampionato import main as aggiornaCampionatoMain
from appStatistiche import AppStatistiche
from appClassifica import AppClassifica
from appPredizioni import RunPredizioni
from ErrorManager import catturaEccezione
from EstrazioneDati import EstrazioneDati
from myPath import myPath, myFile
from UI.Window import Ui_MainWindow  # il file generato da pyuic5

_T_FINE_IMPORT = time.perf_counter()


class MainWindow(QtWidgets.QMainWindow):
    @catturaEccezione
    def __init__(self, **kwargs):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.processiFigli = []  # Lista per tenere traccia dei processi figli
        self.setPath(**kwargs)
        self.sitiSquadre = self.popolaSitiSquadre(self.urlSquadre) # Carica i dati all'inizio
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

        # Imposta dimensioni e flag - usando valori di default
        # self.setWindowFlags(QtCore.Qt.Window)  # Commentato per evitare errori
        self.setMinimumSize(800, 600)
        self.setMaximumSize(16777215, 16777215)
        self.resize(1920, 1000)
        
        # Imposta icona dell'applicazione
        icon_path = os.path.join(myPath.icone, "iconaApp.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        
        # 🔗 Collegamenti ai pulsanti
        self.connettiPulsantiDelleSquadre()
        # Puoi aggiungere altri pulsanti qui...

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
        sitiSquadre = {}
        target = file_path or self.urlSquadre or myFile.urlSquadre
        if target and os.path.exists(target):
            df = pd.read_csv(target, sep=';')
            for index, row in df.iterrows():
                if 'Squadre' in row and 'Url' in row:
                    sitiSquadre[str(row['Squadre']).strip()] = str(row['Url']).strip()
        return sitiSquadre
    # end of popolaSitiSquadre()
    
    @catturaEccezione
    def connettiPulsantiDelleSquadre(self):
        # Associo il sito della squadra al pulsante corrispondente
        if not self.sitiSquadre or not isinstance(self.sitiSquadre, dict):
            self.sitiSquadre = self.popolaSitiSquadre(self.urlSquadre) or {}
            
        squadre_list = list(self.sitiSquadre.keys())
        for btn in range(1, min(21, len(squadre_list) + 1)):  # Evita errori se ci sono meno di 20 squadre
            toolButton = getattr(self.ui, f'toolButton_{btn}', None)
            if toolButton and (btn - 1) < len(squadre_list):
                squadra_nome = squadre_list[btn - 1]
                url = self.sitiSquadre.get(squadra_nome, "")
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
        # if hasattr(self.ui, 'pushButton_Statistiche'):
        self.ui.pushButton_Statistiche.clicked.connect(lambda: self.apri_appStatistiche())
        self.ui.pushButtonPredizioni.clicked.connect(lambda: self.apri_appPredizioni())
        # else:
        #     print("Warning: pushButton_Statistiche not found in UI.")
        self.ui.pushButton_closeApp.clicked.connect(self.close_application)
    # end of connettiPulsantiApp()
    
    @catturaEccezione
    def close_application(self, event = None):
        """Chiude l'applicazione"""
        self.close()
    # end close_application()
    
    @catturaEccezione
    def apri_appClassifica(self):
        """Apre un'applicazione come processo figlio"""
        
        tempo_inizio = time.time()
        appClassifica = AppClassifica()
        self.processiFigli.append(appClassifica)
        appClassifica.show()
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di esecuzione dell'app Classifica (righe 292-296): {tempo_esecuzione:.4f} secondi")
        print(f"⏱️  Tempo di esecuzione dell'app Classifica (righe 292-296): {tempo_esecuzione*1000:.2f} millisecondi")
    # end apri_appClassifica()
    
    @catturaEccezione
    def apri_appStatistiche(self):
        """Apre un'applicazione come processo figlio"""
        tempo_inizio = time.time()
        
        # app = QtWidgets.QApplication(sys.argv)
        window = AppStatistiche()
        self.processiFigli.append(window)
        window.show()
        # sys.exit(app.exec_())
        
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di esecuzione dell'app Statistiche (righe 292-296): {tempo_esecuzione:.4f} secondi")
        print(f"⏱️  Tempo di esecuzione dell'app Statistiche (righe 292-296): {tempo_esecuzione*1000:.2f} millisecondi")
    # end apri_appStatistiche()
    
    @catturaEccezione
    def chiudi_tutte_le_app(self):
        """Chiude tutti i processi figli attivi"""
        for processo in self.processiFigli[:]:  # Copia la lista per iterare sicuramente
            processo.close()  # Chiude la finestra dell'applicazione figlia
            processo.deleteLater()  # Assicura la deallocazione della memoria
        self.processiFigli.clear()  # Pulisce la lista
    # end of chiudi_tutte_le_app()
    
    @catturaEccezione
    def apri_appPredizioni(self):
        """Apre l'app delle predizioni come processo figlio"""
        # Implementa l'apertura dell'app delle predizioni qui
        tempo_inizio = time.time()
        appPredizioni = RunPredizioni()
        self.processiFigli.append(appPredizioni)
        appPredizioni.show()
        tempo_fine = time.time()
        tempo_esecuzione = tempo_fine - tempo_inizio
        print(f"⏱️  Tempo di esecuzione dell'app Classifica (righe 292-296): {tempo_esecuzione:.4f} secondi")
        print(f"⏱️  Tempo di esecuzione dell'app Classifica (righe 292-296): {tempo_esecuzione*1000:.2f} millisecondi")
    # end apri_appPredizioni() 
    
    @catturaEccezione
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione principale"""
        print("Chiusura app principale - terminando tutti i processi figli...")
        self.chiudi_tutte_le_app()
        event.accept()
    # end of closeEvent()
# end of MainWindow class

# TODO: continua
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
        # end if 
        
        if myFile.campionatiPrecedentiExcel in missing_files:
            estrazioneDati = EstrazioneDati(myFile.campionatiPrecedentiExcel)
            QMessageBox.critical(None, "Errore Critico", f"Il file Excel {myFile.campionatiPrecedentiExcel} è mancante. File generato automaticamente.")
            sys.exit(1)
            
        if myFile.urlSquadre in missing_files:
            QMessageBox.critical(None, "Errore Critico", f"Il file CSV {myFile.urlSquadre} è mancante. Impossibile continuare.")
            sys.exit(1)
        
        if myFile.campionatiPrecedenti in missing_files:
            estrazioneDati = EstrazioneDati(myFile.campionatiPrecedentiExcel)
            
        # end if
        
        # if missing_files:
        #     QMessageBox.critical(self, "Errore Critico",)
        #     print("Errore: I seguenti file critici sono mancanti:")
        #     for f in missing_files:
        #         print(f" - {f}")
        #     sys.exit(1)  # Esce dall'applicazione con codice di errore

if __name__ == "__main__":
    
    # Necessario per i file .exe compilati
    # import multiprocessing
    # multiprocessing.freeze_support()
    
    # # Aggiorna il campionato prima di avviare il programma principale
    # subprocess.run([sys.executable, "AggiornaCampionato.py"])
    # aggiornaCampionatoMain()
    # pathUrl = myFile.urlSquadre
    # print(f"\nPath URL Squadre: {pathUrl}")
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
        utente=myPath.utente,   # Non è più usato direttamente, ma lo passo comunque per coerenza e per eventuali usi futuri
        radice=myPath.radice,   # Non è più usato direttamente, ma lo passo comunque per coerenza e per eventuali usi futuri
        urlSquadre=myFile.urlSquadre,   # Passo il path del file CSV con le URL delle squadre
        campionatoCorrente=myFile.campionatoCorrente,   # Passo il path del file CSV del campionato corrente
        campionatiPrecedenti=myFile.campionatiPrecedenti,   # Passo il path del file CSV dei campionati precedenti
        classifica=myFile.classifica,   # Passo il path del file CSV della classifica
        metadati=myFile.metadati,   # Passo il path del file CSV dei metadati
        # campionatoCorrenteExcel=myFile.campionatoCorrenteExcel,
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
