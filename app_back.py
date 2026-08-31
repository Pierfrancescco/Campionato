import os
import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import signal

import sys
import time
import webbrowser

# I miei moduli
from appStatistiche import AppStatistiche
from appClassifica import AppClassifica
from appPredizioni import RunPredizioni
from ErrorManager import catturaEccezione
from EstrazioneDati import EstrazioneDati
from myPath import myPath, myFile
from UI.Window import Ui_MainWindow  # il file generato da pyuic5


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
        QToolButton {   # Stile per i pulsanti delle squadre
            background-color: transparent;
            border: none;
            color: white;
        }
        QToolButton:hover { # Stile al passaggio del mouse
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }
        QToolButton:pressed {   # Stile quando il pulsante è premuto
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 5px;
        }
        """)

        # Imposta dimensioni e flag
        self.setWindowFlags(QtCore.Qt.Window |
                            QtCore.Qt.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowMaximizeButtonHint |
                            QtCore.Qt.WindowCloseButtonHint |
                            QtCore.Qt.WindowSystemMenuHint)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(16777215, 16777215)
        self.resize(1920, 1000)

        
        
        # 🔗 Collegamenti ai pulsanti
        self.connettiPulsantiDelleSquadre()
        # Puoi aggiungere altri pulsanti qui...

        self.connettiPulsantiApp()
    # end __init__()
    
    @catturaEccezione
    def setPath(self, **kwargs):
        self.utente = kwargs.get('utente')
        self.pathRadice = kwargs.get('radice')
        self.urlSquadre = kwargs.get('urlSquadre')
        self.campionatoCorrente = kwargs.get('campionatoCorrente')
        self.campionatiPrecedenti = kwargs.get('campionatiPrecedenti')
        self.classifica = kwargs.get('classifica')
        self.metadati = kwargs.get('metadati')
        self.campionatoCorrenteExcel = kwargs.get('campionatoCorrenteExcel')
        self.campionatiPrecedentiExcel = kwargs.get('campionatiPrecedentiExcel')
        # # todo: aggiungi gli altri path come attributi
        # for key, value in kwargs.items():
        #     print(f"Path impostato: {key} = {value}")    
    # end of setPath()
    
    @catturaEccezione
    def popolaSitiSquadre(self, file_path):
        sitiSquadre = {}
        df = pd.read_csv(file_path, sep=';')
        # sitiSquadre = df[['Squadre', 'Url']].to_dict(orient='records')
        for index, row in df.iterrows():
            sitiSquadre[row['Squadre']] = row['Url']
            # print(sitiSquadre[row['Squadre']])

        return sitiSquadre
    # end of popolaSitiSquadre()
    
    @catturaEccezione
    def connettiPulsantiDelleSquadre(self):
        # Associo il sito della squadra al pulsante corrispondente
        squadre_list = list(self.sitiSquadre.keys())
        for btn in range(1, min(21, len(squadre_list) + 1)):  # Evita errori se ci sono meno di 20 squadre
            toolButton = getattr(self.ui, f'toolButton_{btn}', None)
            if toolButton and (btn - 1) < len(squadre_list):
                squadra_nome = squadre_list[btn - 1]
                url = self.sitiSquadre[squadra_nome]
                toolButton.clicked.connect(lambda checked, url=url: webbrowser.open(url))

    # end of connettiPulsantiDelleSquadre()
    
    @catturaEccezione
    def connettiPulsantiApp(self):
        
        self.ui.pushButton_Classifica.clicked.connect(lambda: self.apri_appClassifica())
        # if hasattr(self.ui, 'pushButton_Statistiche'):
        self.ui.pushButton_Statistiche.clicked.connect(lambda: self.apri_appStatistiche())
        self.ui.pushButtonPredizioni.clicked.connect(lambda: self.apri_appPredizioni())
        # else:
        #     print("Warning: pushButton_Statistiche not found in UI.")
        self.ui.pushButton_closeApp.clicked.connect(self.close)
    # end of connettiPulsantiApp()
    
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
            QMessageBox.critical(None, "Errore Critico", f"Il file Excel {myFile.campionatiPrecedentiExcel} è mancante mancante. Impossibile fare predizioni e statistiche..")
            sys.exit(1)
            
        if myFile.urlSquadre in missing_files:
            QMessageBox.critical(None, "Errore Critico", f"Il file CSV {myFile.urlSquadre} è mancante. Impossibile continuare.")
            sys.exit(1)
        
        if myFile.campionatiPrecedentiExcel in missing_files:
            estrazioneDati = EstrazioneDati(myFile.campionatiPrecedentiExcel)
            
        # end if
        
        # if missing_files:
        #     QMessageBox.critical(self, "Errore Critico",)
        #     print("Errore: I seguenti file critici sono mancanti:")
        #     for f in missing_files:
        #         print(f" - {f}")
        #     sys.exit(1)  # Esce dall'applicazione con codice di errore

if __name__ == "__main__":
    
   
    
    # pathUrl = myFile.urlSquadre
    # print(f"\nPath URL Squadre: {pathUrl}")
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(
        utente=myPath.utente,
        radice=myPath.radice,
        urlSquadre=myFile.urlSquadre,
        campionatoCorrente=myFile.campionatoCorrente,
        campionatiPrecedenti=myFile.campionatiPrecedenti,
        classifica=myFile.classifica,
        metadati=myFile.metadati,
        campionatoCorrenteExcel=myFile.campionatoCorrenteExcel,
        campionatiPrecedentiExcel=myFile.campionatiPrecedentiExcel
    )
    CheckFile.checkFilesExistence()
    
    
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
