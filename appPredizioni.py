from os import read
import pandas as pd
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys

# I miei Moduli
from ErrorManager import catturaEccezione
from EsitoDalRanking import PredizionePartita
from EstrazioneDati import EstrazioneDati
from myPath import myPath, myFile
from UI.Predizioni import Ui_MainWindow
from ProgressBar import ProgressBar



class RunPredizioni(QMainWindow):
    @catturaEccezione
    def __init__(self,scudetti = 'Immagini/Scudetti', urlSquadre = 'Csv/urlSquadre.csv', campionatoCorrente='Csv/Campionato.csv', campionatiPrecedenti='Csv/CampionatiPrecedenti.csv'):
        super(RunPredizioni, self).__init__()
        self.campionatoCorrente = campionatoCorrente        # Percorso del file CSV del campionato corrente
        self.campionatiPrecedenti = campionatiPrecedenti    # Percorso del file CSV dei campionati precedenti
        self.urlSquadreFile = urlSquadre                    # Percorso del file CSV degli URL delle squadre per ricavare le squadre in campionato
        self.scudetti = scudetti  
        # Percorso della cartella delle immagini degli scudetti
        # loadUi('UI\\Predizioni.ui', self)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setStyleSheet("""
        QMainWindow {
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(14, 0, 255, 255), stop:1 rgba(76, 152, 228, 255));
            color: white;
            font: 12pt "Segoe UI";
        }
        QToolTip {
            color: #ffffff;
            background-color: #1e293b;
            border: 1px solid #4b5563;
            border-radius: 4px;
            padding: 5px 8px;
            font-size: 10pt;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        QComboBox {
            background-color: #1e293b;
            color: #ffffff;
            border: 2px solid #3b82f6;
            border-radius: 6px;
            padding: 4px 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12pt;
            font-weight: bold;
        }
        QComboBox:hover {
            border: 2px solid #60a5fa;
            background-color: #273549;
        }
        QComboBox QAbstractItemView {
            background-color: #1e293b;
            color: #ffffff;
            selection-background-color: #3b82f6;
            selection-color: #ffffff;
            border: 1px solid #4b5563;
            padding: 4px;
        }
        """)
        
        self.estrazioneDati = EstrazioneDati(myFile.campionatoCorrente)
        self.run()
    # end __init__()
    
    @catturaEccezione
    def run(self):
        self.popolaComboBox()
        
        # Connetto i bottoni
        self.ui.buttonEsci.clicked.connect(self.close_window)
        self.ui.buttonPredizione.clicked.connect(self.avviaPredizione)
        self.ui.buttonReset.clicked.connect(self.reset)
        self.connettiComboBox()
        self.reset()
        
    # end run()
    
    @catturaEccezione
    def avviaPredizione(self, event = None):
        # se l'indice corrente delle 2 combobox è maggiore di 0
        # e quindi sono selezionate 2 squadre valide e comunque diverse
        # esegue la predizione
        if self.ui.comboBoxCasa.currentIndex() > 0 and self.ui.comboBoxTrasferta.currentIndex() > 0:
            if self.ui.comboBoxCasa.currentText() == self.ui.comboBoxTrasferta.currentText():
                QMessageBox.warning(self, "Attenzione", "Le 2 squadre selezionate non possono essere uguali.")
                return
            self.prediciPartita()
        else:
            if self.ui.comboBoxCasa.currentIndex() == 0 :
                QMessageBox.warning(self, "Attenzione", "Squadra di casa non selezionata.")
                return
            elif self.ui.comboBoxTrasferta.currentIndex() == 0 :
                QMessageBox.warning(self, "Attenzione", "Squadra in trasferta non selezionata.")
                return
        # Alla fine resetta l'interfaccia
            self.reset()
    # end avviaPredizione()
    
    def inizializzaProgressBar(self):
        self.pb = ProgressBar("Sto generando le predizioni...")
        self.pb.mostra()
    
    @catturaEccezione
    def close_window(self, event = None):
        """Chiude la finestra"""
        self.close()
    
    @catturaEccezione
    def closeEvent(self, event = None):
        """Gestisce la chiusura della finestra tramite X o Alt+F4"""
        choice = QMessageBox.question(self, 'Esci', 
                                      "Sei sicuro di voler uscire?", 
                                      QMessageBox.Yes | QMessageBox.No)
        if choice == QMessageBox.Yes:
            print("Uscita dall'applicazione.")
            # Accetta l'evento di chiusura
            event.accept()  # type: ignore
        else:
            # Ignora l'evento di chiusura
            event.ignore()  #type: ignore
    # end closeEvent()
    
    @catturaEccezione
    def connettiComboBox(self):
        self.ui.comboBoxCasa.currentIndexChanged.connect(self.setLabelSquadraDiCasa)
        self.ui.comboBoxTrasferta.currentIndexChanged.connect(self.setLabelSquadraInTrasferta)
    # end connettiComboBox()
    
    @catturaEccezione
    def popolaComboBox(self):
        
        # Carica le squadre dal CSV
        
        squadre = self.estrazioneDati.squadre()
       
        
        # Popola le combobox
        self.ui.comboBoxCasa.addItem("Seleziona Squadra di Casa")  # Aggiungi un'opzione vuota all'inizio
        self.ui.comboBoxCasa.addItems(squadre)
        self.ui.comboBoxTrasferta.addItem("Seleziona Squadra in Trasferta")  # Aggiungi un'opzione vuota all'inizio
        self.ui.comboBoxTrasferta.addItems(squadre)
        
        # aggiorna le label delle squadre
        if self.ui.comboBoxCasa.currentText() != self.ui.comboBoxTrasferta.currentText():
            self.setLabelSquadraDiCasa()
            self.setLabelSquadraInTrasferta()
    # end popolaComboBox()
    
    @catturaEccezione
    def setLabelSquadraDiCasa(self, event = None):
        # Legge la squadra da  self.comboBoxCasa.currentText() e la imposta in self.labelSquadraDiCasa
        # Aggiorna la label con la squadra selezionata
        self.ui.labelSquadraDiCasa.setText(self.ui.comboBoxCasa.currentText())
        self.setLabelscudettoSquadraDiCasa()
    # end setLabelSquadraDiCasa()
    
    @catturaEccezione
    def setLabelSquadraInTrasferta(self, event = None):
        # Legge la squadra da  self.comboBoxTrasferta.currentText() e la imposta in self.labelSquadraDiTrasferta
        # Aggiorna la label con la squadra selezionata
        self.ui.labelSquadraInTrasferta.setText(self.ui.comboBoxTrasferta.currentText())
        self.setLabelscudettoSquadraInTrasferta()
    # end setLabelSquadraInTrasferta()
    
    
    
    @catturaEccezione
    def setLabelscudettoSquadraDiCasa(self):
        # Legge la squadra da  self.comboBoxCasa.currentText() e la imposta in self.labelSquadraDiCasa
        squadra_casa = self.ui.comboBoxCasa.currentText()
        
        # Controlla se la squadra è valida (non è il testo di default)
        if squadra_casa and not squadra_casa.startswith("Seleziona"):
            # recupera l'immagine dello scudetto dal percorso specificato
            pixmapCasa = QPixmap(f"{self.scudetti}/{squadra_casa}.png")
            if not pixmapCasa.isNull():
                scaled_pixmap = pixmapCasa.scaled(self.ui.labelScudettoSquadraDiCasa.size())
                self.ui.labelScudettoSquadraDiCasa.setPixmap(scaled_pixmap)
            else:
                print(f"Scudetto non trovato: {self.scudetti}/{squadra_casa}.png")
                self.ui.labelScudettoSquadraDiCasa.clear()  # Rimuovi immagine precedente
    # end setLabelscudettoSquadraDiCasa()
    
    @catturaEccezione
    def setLabelscudettoSquadraInTrasferta(self):
        # Legge la squadra da  self.comboBoxTrasferta.currentText() e la imposta in self.labelSquadraInTrasferta
        squadra_trasferta = self.ui.comboBoxTrasferta.currentText()
        
        # Controlla se la squadra è valida (non è il testo di default)
        if squadra_trasferta and not squadra_trasferta.startswith("Seleziona"):
            # recupera l'immagine dello scudetto dal percorso specificato
            pixmapTrasferta = QPixmap(f"{self.scudetti}/{squadra_trasferta}.png")
            if not pixmapTrasferta.isNull():
                scaled_pixmap = pixmapTrasferta.scaled(self.ui.labelScudettoSquadraInTrasferta.size())
                self.ui.labelScudettoSquadraInTrasferta.setPixmap(scaled_pixmap)
            else:
                print(f"Scudetto non trovato: {self.scudetti}/{squadra_trasferta}.png")
                self.ui.labelScudettoSquadraInTrasferta.clear()  # Rimuovi immagine precedente
    # end setLabelscudettoSquadraInTrasferta()
    
    
    
    def generaPredizioni(self):
        self.prediciPartita()
    
    @catturaEccezione
    def prediciPartita(self):
        squadraCasa = self.ui.comboBoxCasa.currentText()
        squadraTrasferta = self.ui.comboBoxTrasferta.currentText()
        
        # Non calcolare se le squadre sono uguali o vuote
        if not squadraCasa or not squadraTrasferta or squadraCasa == squadraTrasferta:
            return
            
        # Crea la predizione
        self.predizione = PredizionePartita(
            squadraCasa, squadraTrasferta,
            campionatoCorrente=self.campionatoCorrente,
            campionatiPrecedenti=self.campionatiPrecedenti,
            peso_attuale=0.6
        )
        
        # Calcola le predizioni
        self.predizione.prevedi()
        
        # Inizializza la progress bar
        # self.inizializzaProgressBar()
        
        self.pb = ProgressBar("Sto generando le predizioni...")
        self.pb.mostra()
        # Popola l'interfaccia
        
        self.popolaFramePredizioni()
        self.popolaFrameRankingCampionatiPrecedenti()
        self.popolaFrameRankingCampionatoAttuale()
        self.popolaFrameRankingUltime5Partite()
        self.popolaFrameScontriStoriciDiretti(self.checkScontriDiretti())
        self.popolaScommessaConsigliata()
        self.popolaComboSuggerita()
        self.popolaMotivazioneTecnica()
        self.popolaCommentoFinale()
        self.popolaAnalisiFormaCasa()
        self.popolaAnalisiFormaTrasferta()
        self.setGraficoConfrontoForma()
        
        # Chiudi la progress bar alla fine
        self.pb.close()
    # end prediciPartita()
    
    def checkScontriDiretti(self):
        squadraDiCasa = self.ui.comboBoxCasa.currentText()
        squadraInTrasferta = self.ui.comboBoxTrasferta.currentText()
        df = pd.read_csv(self.campionatiPrecedenti, sep=";")
        scontri_diretti = df[
                ((df['Casa'] == squadraDiCasa) & (df['Trasferta'] == squadraInTrasferta)) |
                ((df['Casa'] == squadraInTrasferta) & (df['Trasferta'] == squadraDiCasa))
        ]    
        
        if scontri_diretti.empty:
            return False
        return True
    # end checkScontriDiretti()
    
    @catturaEccezione
    def checkCampionatiPrecedentiSquadraDiCasa(self):
        squadraDiCasa = self.ui.comboBoxCasa.currentText()
        df = pd.read_csv(self.campionatiPrecedenti, sep=";")
        campionati_precedenti_casa = df[
                (df['Casa'] == squadraDiCasa) | (df['Trasferta'] == squadraDiCasa)
        ]    
        
        if campionati_precedenti_casa.empty:
            return False
        return True
    # end checkCampionatiPrecedentiSquadraDiCasa()
    
    @catturaEccezione
    def checkCampionatiPrecedentiSquadraInTrasferta(self):
        squadraInTrasferta = self.ui.comboBoxTrasferta.currentText()
        df = pd.read_csv(self.campionatiPrecedenti, sep=";")
        campionati_precedenti_trasferta = df[
                (df['Casa'] == squadraInTrasferta) | (df['Trasferta'] == squadraInTrasferta)
        ]    
        
        if campionati_precedenti_trasferta.empty:
            return False
        return True
    # end checkCampionatiPrecedentiSquadraInTrasferta()
    
    @catturaEccezione
    def popolaFramePredizioni(self):
        
        # --- Predizioni Goals ---
        
        # Goals Previsti
        self.ui.labelGoalPrevisti.setText(
            f"Goals Previsti: {self.predizione.squadra_casa} {self.predizione.predizioneGoals['goalPrevistiCasa']} - {self.predizione.predizioneGoals['goalPrevistiTrasferta']} {self.predizione.squadra_trasferta}"
        )
        self.pb.setProgressBar()
        
        # Esito Previsto
        self.ui.labelEsitoPrevisto.setText(
            f"Esito Previsto: {self.predizione.predizioneGoals['esitoPrevisto']}"
        )
        self.pb.setProgressBar()
        
        # Doppia Chance
        self.ui.labelDoppiaChanceSuggerita.setText(
            f"Doppia Chance Suggerita: {self.predizione.predizioneGoals['doppiaChance']}"
        )
        self.pb.setProgressBar()
        
        # ---Probalità Esito---
        
        # Vittoria Casa
        self.ui.labelProbabilitaVittoria.setText(f'1 (Vittoria {self.predizione.squadra_casa}): {self.predizione.probabilitaEsito["VittoriaCasa"]:.2f}%')
        self.pb.setProgressBar()
        
        # Pareggio
        self.ui.labelProbabilitaPareggio.setText(f'X (Pareggio): {self.predizione.probabilitaEsito["Pareggio"]:.2f}%')
        self.pb.setProgressBar()
        # Vittoria Trasferta
        self.ui.labelProbabilitaSconfitta.setText(f'2 (Vittoria {self.predizione.squadra_trasferta}): {self.predizione.probabilitaEsito["VittoriaTrasferta"]:.2f}%')
        self.pb.setProgressBar()
        # --- Under/Over ---
        # Under 1.5
        self.ui.labelUnder15.setText(f'Under 1.5: {self.predizione.underOver["Under1.5"]:.2f}%')
        self.pb.setProgressBar()
        # Over 1.5
        self.ui.labelOver15.setText(f'Over 1.5: {self.predizione.underOver["Over1.5"]:.2f}%')
        self.pb.setProgressBar()
        # Under 2.5
        self.ui.labelUnder25.setText(f'Under 2.5: {self.predizione.underOver["Under2.5"]:.2f}%')
        self.pb.setProgressBar()
        # Over 2.5
        self.ui.labelOver25.setText(f'Over 2.5: {self.predizione.underOver["Over2.5"]:.2f}%')
        self.pb.setProgressBar()
        # --- Forma Recente ---
        # Forma Casa
        self.ui.labelFormaRecenteSquadraDiCasa.setText(f'{self.predizione.squadra_casa}: {self.predizione.formaRecente["FormaCasa"]:.2f}/3.0 punti/partita')
        self.pb.setProgressBar()
        # Forma Trasferta
        self.ui.labelFormaRecenteSquadraInTrasferta.setText(f'{self.predizione.squadra_trasferta}: {self.predizione.formaRecente["FormaTrasferta"]:.2f}/3.0 punti/partita')
        self.pb.setProgressBar()
        
        
    # end popolaFramePredizioni()
    
    @catturaEccezione
    def popolaFrameRankingCampionatiPrecedenti(self):
        """Mostra il ranking delle squadre nei campionati precedenti"""
        squadraDiCasa = self.ui.comboBoxCasa.currentText()
        squadraInTrasferta = self.ui.comboBoxTrasferta.currentText()
        # se la squadra processata ha giocato in campionati precedenti
        # scriverà i dati altrimenti scriverà N/A
        
        squadraDiCasaCampionatiPrecedenti = self.checkCampionatiPrecedentiSquadraDiCasa()
        squadraInTrasfertaCampionatiPrecedenti = self.checkCampionatiPrecedentiSquadraInTrasferta()
        # --- Generale ---
        if not squadraDiCasaCampionatiPrecedenti:
            self.ui.labelRankingCampionatiPrecedentiGeneraleSquadraDiCasa.setText(f"{squadraDiCasa} N/A")
        else:
            self.ui.labelRankingCampionatiPrecedentiGeneraleSquadraDiCasa.setText(self.predizione.casaRankingStorico['generale'])
        # end if
        self.pb.setProgressBar()
        
        if not squadraInTrasfertaCampionatiPrecedenti:
            self.ui.labelRankingCampionatiPrecedentiGeneraleSquadraInTrasferta.setText(f"{squadraInTrasferta} N/A")
        else:
            self.ui.labelRankingCampionatiPrecedentiGeneraleSquadraInTrasferta.setText(self.predizione.trasfertaRankingStorico['generale'])
        # end if
        self.pb.setProgressBar()
        
        #  --- In Casa ---
        if not squadraDiCasaCampionatiPrecedenti:
            self.ui.labelRankingCampionatiPrecedentiInCasaSquadraDiCasa.setText(f"{squadraDiCasa} N/A")
        else:
            self.ui.labelRankingCampionatiPrecedentiInCasaSquadraDiCasa.setText(self.predizione.casaRankingStorico['casa'])
        # end if
        self.pb.setProgressBar()
        
        if not squadraInTrasfertaCampionatiPrecedenti:
            self.ui.labelRankingCampionatiPrecedentiInCasaSquadraInTrasferta.setText(f"{squadraInTrasferta} N/A")
        else:
            self.ui.labelRankingCampionatiPrecedentiInCasaSquadraInTrasferta.setText(self.predizione.trasfertaRankingStorico['casa'])
        # end if
        self.pb.setProgressBar()
        
        # --- In Trasferta ---
        if not squadraDiCasaCampionatiPrecedenti:
            self.ui.labelRankingCampionatiPrecedentiInTrafertaSquadraDiCasa.setText(f"{squadraDiCasa} N/A")
        else:
            self.ui.labelRankingCampionatiPrecedentiInTrafertaSquadraDiCasa.setText(self.predizione.casaRankingStorico['trasferta'])
        # end if
        self.pb.setProgressBar()
            
        if not squadraInTrasfertaCampionatiPrecedenti:
            self.ui.labelRankingCampionatiPrecedentiInTrafertaSquadraInTrasferta.setText(f"{squadraInTrasferta} N/A")
        else:
            self.ui.labelRankingCampionatiPrecedentiInTrafertaSquadraInTrasferta.setText(self.predizione.trasfertaRankingStorico['trasferta'])
            # end if
        self.pb.setProgressBar()
        
        # --- Statistiche storiche Aggegate ---
        if not squadraDiCasaCampionatiPrecedenti:
            self.ui.labelStatisticheStoricheAggregateSquadraDiCasa.setText(f"{squadraDiCasa} N/A")
        else:
            self.ui.labelStatisticheStoricheAggregateSquadraDiCasa.setText(self.predizione.casaRankingStorico['statisticheAggregate'])
            # end if
        self.pb.setProgressBar()
        
        if not squadraInTrasfertaCampionatiPrecedenti:
            self.ui.labelStatisticheStoricheAggregateSquadraInTrasferta.setText(f"{squadraInTrasferta} N/A")
        else:
            self.ui.labelStatisticheStoricheAggregateSquadraInTrasferta.setText(self.predizione.trasfertaRankingStorico['statisticheAggregate'])
            # end if
        self.pb.setProgressBar()    
    # end popolaFrameRankingCampionatiPrecedenti()
    
    def popolaFrameRankingCampionatoAttuale(self):
        """Mostra il ranking delle squadre nel campionato attuale"""
        
        # --- Generale ---
        self.ui.labelRankingCampionatoAttualeGeneraleSquadraDiCasa.setText(self.predizione.casaRankingAttuale['generali'])
        self.pb.setProgressBar()
        self.ui.labelRankingCampionatoAttualeGeneraleSquadraInTrasferta.setText(self.predizione.trasfertaRankingAttuale['generali'])
        self.pb.setProgressBar()
        
        #  --- In Casa ---
        self.ui.labelRankingCampionatoAttualeInCasaSquadraDiCasa.setText(self.predizione.casaRankingAttuale['casa'])
        self.pb.setProgressBar()
        self.ui.labelRankingCampionatoAttualeInCasaSquadraInTrasferta.setText(self.predizione.trasfertaRankingAttuale['casa'])
        self.pb.setProgressBar()
        
        # --- In Trasferta ---
        self.ui.labelRankingCampionatoAttualeInTrasfertaSquadraDiCasa.setText(self.predizione.casaRankingAttuale['trasferta'])
        self.pb.setProgressBar()
        self.ui.labelRankingCampionatoAttualeInTrasfertaSquadraInTrasferta.setText(self.predizione.trasfertaRankingAttuale['trasferta'])
        self.pb.setProgressBar()
    # end popolaFrameframeRankingCampionatoAttuale()
    
    def popolaFrameRankingUltime5Partite(self):
        """Mostra il ranking delle squadre nelle ultime 5 partite"""
        
        # --- Generale ---
        self.ui.labelRankingUltime5PartiteGeneraleSqaudraDiCasa.setText(self.predizione.casaRankingUltime5['generali'])
        self.pb.setProgressBar()
        self.ui.labelRankingUltime5PartiteGeneraleSquadraInTrasferta.setText(self.predizione.trasfertaRankingUltime5['generali'])
        self.pb.setProgressBar()
        
        #  --- In Casa ---
        self.ui.labelRankingUltime5PartiteInCasaSquadraDiCara.setText(self.predizione.casaRankingUltime5['casa'])
        self.pb.setProgressBar()    
        self.ui.labelRankingUltime5PartiteInCasaSquadraInTrasferta.setText(self.predizione.trasfertaRankingUltime5['casa'])
        self.pb.setProgressBar()
        
        # --- In Trasferta ---
        self.ui.labelRankingUltime5PartiteInTrasfertaSquadraDiCasa.setText(self.predizione.casaRankingUltime5['trasferta'])
        self.pb.setProgressBar()
        self.ui.labelRankingUltime5PartiteInTrasfertaSquadraInTrasferta.setText(self.predizione.trasfertaRankingUltime5['trasferta'])
        self.pb.setProgressBar()
    # end popolaFrameRankingUltime5Partite()
    
    def popolaFrameScontriStoriciDiretti(self, scontriDiretti):
        """Mostra gli scontri storici diretti tra le due squadre"""
        
        # scontri trovati
        self.ui.labelScontriTrovati.setText(self.predizione.scontri.numeroScontri)
        self.pb.setProgressBar()
        
        # bilancio scontri diretti
        if scontriDiretti:
            self.ui.labelBilancioScontriDirettiSquadraDiCasa.setText(self.predizione.scontri.bilancioScontri['casa'])
            self.pb.setProgressBar()
            self.ui.labelBilancioScontriDirettiSquadraInTrasferta.setText(self.predizione.scontri.bilancioScontri['trasferta'])
            self.pb.setProgressBar()
            self.ui.labelBilancioScontriDirettiPareggi.setText(self.predizione.scontri.bilancioScontri['pareggi'])
            self.pb.setProgressBar()
        else:
            self.ui.labelBilancioScontriDirettiSquadraDiCasa.setText("N/A")
            self.pb.setProgressBar()
            self.ui.labelBilancioScontriDirettiSquadraInTrasferta.setText("N/A")
            self.pb.setProgressBar()
            self.ui.labelBilancioScontriDirettiPareggi.setText("N/A")
            self.pb.setProgressBar()
        # end if
        
        # ultime 5 partite
        if scontriDiretti:
            for index in range(len(self.predizione.scontri.ultime5Partite)):
                if index == 0:
                    self.ui.labelUltime5PartiteTraLe2Squadre_1.setText(self.predizione.scontri.ultime5Partite[index])
                elif index == 1:
                    self.ui.labelUltime5PartiteTraLe2Squadre_2.setText(self.predizione.scontri.ultime5Partite[index])
                elif index == 2:
                    self.ui.labelUltime5PartiteTraLe2Squadre_3.setText(self.predizione.scontri.ultime5Partite[index])
                elif index == 3:
                    self.ui.labelUltime5PartiteTraLe2Squadre_4.setText(self.predizione.scontri.ultime5Partite[index])
                elif index == 4:
                    self.ui.labelUltime5PartiteTraLe2Squadre_5.setText(self.predizione.scontri.ultime5Partite[index])
                self.pb.setProgressBar()
                # end if
            # end for
        else:
            self.ui.labelUltime5PartiteTraLe2Squadre_1.setText("N/A")
            self.pb.setProgressBar()
            self.ui.labelUltime5PartiteTraLe2Squadre_2.setText("N/A")
            self.pb.setProgressBar()
            self.ui.labelUltime5PartiteTraLe2Squadre_3.setText("N/A")
            self.pb.setProgressBar()
            self.ui.labelUltime5PartiteTraLe2Squadre_4.setText("N/A")
            self.pb.setProgressBar()
            self.ui.labelUltime5PartiteTraLe2Squadre_5.setText("N/A")
            self.pb.setProgressBar()
        # end if
    # end popolaFrameScontriStoriciDiretti()
    
    @catturaEccezione
    def popolaScommessaConsigliata(self):
        self.ui.labelScommessaConsigliataDoppiaChance.setText(f"Scommessa Consigliata: {self.predizione.scommessaConsigliata['doppiaChance']}")
        self.pb.setProgressBar()
        self.ui.labelScommessaConsigliataProbabilitaSuccesso.setText(f"Probabilità di Successo: {self.predizione.scommessaConsigliata['probabilita']}")
        self.pb.setProgressBar()
        self.ui.labelScommessaConsigliataLivelloRischio.setText(f"Livello di Rischio: {self.predizione.scommessaConsigliata['livelloRischio']}")
        self.pb.setProgressBar()
    # end popolaScommessaConsigliata()
    
    @catturaEccezione
    def popolaComboSuggerita(self):
        if self.predizione.comboSuggerita == "":
            self.ui.labelAltreOpzioniSuggerimenti.setText("Combo suggerita: Nessuna Combo da suggerire")
        else:
            self.ui.labelAltreOpzioniSuggerimenti.setText(f"Combo suggerita: {self.predizione.comboSuggerita}")
        self.pb.setProgressBar()
    # end popolaComboSuggerita()
    
    @catturaEccezione
    def popolaMotivazioneTecnica(self):
        self.ui.labelMotivazioneTecnicaPredizione.setText(f"📊 Predizione esito: {self.predizione.motivazioneTecnica['predizioneEsito']}")
        self.pb.setProgressBar()
        self.ui.labelMotivazioneTecnicaGoalsPrevisti.setText(f"⚽ Goal previsti: {self.predizione.motivazioneTecnica['goalsPrevisti']}")
        self.pb.setProgressBar()
        self.ui.labelMotivazioneTecnicaFormaRecente.setText(f"🔥 Forma recente: {self.predizione.motivazioneTecnica['formaRecente']}")
        self.pb.setProgressBar()
        self.ui.labelMotivazioneTecnicaRankingAttuale.setText(f"🏆 Ranking attuale: {self.predizione.motivazioneTecnica['rankingAttuale']}")
        self.pb.setProgressBar()
        self.ui.labelMotivazioneTecnicaScontriDiretti.setText(f"⚔️ Scontri diretti: {self.predizione.motivazioneTecnica['scontriDiretti']}")
        self.pb.setProgressBar()
    # end popolaMotivazioneTecnica()
    
    @catturaEccezione
    def popolaCommentoFinale(self):
        self.ui.labelCommentoFinaleIndicatori.setText(self.predizione.commentoFinale['analisiContesto'])
        self.pb.setProgressBar()
        self.ui.labelCommentoFinaleConfidenza.setText(self.predizione.commentoFinale['confidenza'])
        self.pb.setProgressBar()
    # end popolaCommentoFinale()
    
    @catturaEccezione
    def popolaAnalisiFormaCasa(self):
        self.predizione.dettaglio_forma()
        self.ui.labelAnalisiSquadraDiCasa.setText(self.predizione.analisiFormaCasa['squadra'])
        self.pb.setProgressBar()
        self.ui.labelAnalisiSqudraDiCasaInCasa.setText(self.predizione.analisiFormaCasa['partiteInCasa'])
        self.pb.setProgressBar()
        self.ui.labelAnalisiSqudraDiCasaInTrasferta.setText(self.predizione.analisiFormaCasa['partiteInTrasferta'])
        self.pb.setProgressBar()
        self.ui.labelAnalisiSqudraDiCasaGenerale.setText(self.predizione.analisiFormaCasa['partiteGenerali'])
        self.pb.setProgressBar()
        self.ui.labelMediaPuntiCasa.setText(self.predizione.analisiFormaCasa['formaGenerale'])
    # end popolaAnalisiFormaCasa()
    
    def popolaAnalisiFormaTrasferta(self):
        self.predizione.dettaglio_forma()
        self.ui.labelAnalisiSquadraInTrasferta.setText(self.predizione.analisiFormaTrasferta['squadra'])
        self.pb.setProgressBar()
        self.ui.labelAnalisiSqudraInTrasfertaInCasa.setText(self.predizione.analisiFormaTrasferta['partiteInCasa'])
        self.pb.setProgressBar()
        self.ui.labelAnalisiSqudraInTrasfertaInTrasferta.setText(self.predizione.analisiFormaTrasferta['partiteInTrasferta'])
        self.pb.setProgressBar()
        self.ui.labelAnalisiSquadraInTrasfertaGenerale.setText(self.predizione.analisiFormaTrasferta['partiteGenerali'])
        self.pb.setProgressBar()
        self.ui.labelMediaPuntiTrasferta.setText(self.predizione.analisiFormaTrasferta['formaGenerale'])
        self.pb.setProgressBar()
    # end popolaAnalisiFormaTrasferta()
    
    def setGraficoConfrontoForma(self):
        """Stampa il grafico di confronto forma recente tra le 2 squadre"""
        self.predizione.grafico_confronto()
        pixmap = QPixmap(myFile.graficoConfrontoSquadre)
        scaled_pixmap = pixmap.scaled(self.ui.labelGrafico.size())
        self.ui.labelGrafico.setPixmap(scaled_pixmap)
        self.pb.setProgressBar()
    # end setGraficoConfrontoForma()
       
    
    @catturaEccezione
    def reset(self, event = None):
        """Resetta l'interfaccia"""
        # PREDIZIONI
        self.ui.comboBoxCasa.setCurrentIndex(0)
        self.ui.comboBoxTrasferta.setCurrentIndex(0)
        self.ui.labelGoalPrevisti.setText("Goals Previsti: -----")
        self.ui.labelEsitoPrevisto.setText("Esito Previsto: -----")
        self.ui.labelDoppiaChanceSuggerita.setText("Doppia Chance Suggerita: -----")
        self.ui.labelProbabilitaVittoria.setText("1 (Vittoria Casa): -----")
        self.ui.labelProbabilitaPareggio.setText("X (Pareggio): -----")
        self.ui.labelProbabilitaSconfitta.setText("2 (Vittoria Trasferta): -----")
        self.ui.labelUnder15.setText("Under 1.5: -----")
        self.ui.labelOver15.setText("Over 1.5: -----")
        self.ui.labelUnder25.setText("Under 2.5: -----")
        self.ui.labelOver25.setText("Over 2.5: -----")
        self.ui.labelFormaRecenteSquadraDiCasa.setText("-----: -----/3.0 punti/partita")
        self.ui.labelFormaRecenteSquadraInTrasferta.setText("-----: -----/3.0 punti/partita")
        # Ranking Campionati Precedenti
        self.ui.labelRankingCampionatiPrecedentiGeneraleSquadraDiCasa.setText("-----")
        self.ui.labelRankingCampionatiPrecedentiGeneraleSquadraInTrasferta.setText("-----")
        self.ui.labelRankingCampionatiPrecedentiInCasaSquadraDiCasa.setText("-----")
        self.ui.labelRankingCampionatiPrecedentiInCasaSquadraInTrasferta.setText("-----")
        self.ui.labelRankingCampionatiPrecedentiInTrafertaSquadraDiCasa.setText("-----")
        self.ui.labelRankingCampionatiPrecedentiInTrafertaSquadraInTrasferta.setText("-----")
        self.ui.labelStatisticheStoricheAggregateSquadraDiCasa.setText("-----")
        self.ui.labelStatisticheStoricheAggregateSquadraInTrasferta.setText("-----")
        # Ranking Campionato Attuale
        self.ui.labelRankingCampionatoAttualeGeneraleSquadraDiCasa.setText("-----")
        self.ui.labelRankingCampionatoAttualeGeneraleSquadraInTrasferta.setText("-----")
        self.ui.labelRankingCampionatoAttualeInCasaSquadraDiCasa.setText("-----")
        self.ui.labelRankingCampionatoAttualeInCasaSquadraInTrasferta.setText("-----")
        self.ui.labelRankingCampionatoAttualeInTrasfertaSquadraDiCasa.setText("-----")
        self.ui.labelRankingCampionatoAttualeInTrasfertaSquadraInTrasferta.setText("-----")
        # Ranking Ultime 5 Partite
        self.ui.labelRankingUltime5PartiteGeneraleSqaudraDiCasa.setText("-----")
        self.ui.labelRankingUltime5PartiteGeneraleSquadraInTrasferta.setText("-----")
        self.ui.labelRankingUltime5PartiteInCasaSquadraDiCara.setText("-----")
        self.ui.labelRankingUltime5PartiteInCasaSquadraInTrasferta.setText("-----")
        self.ui.labelRankingUltime5PartiteInTrasfertaSquadraDiCasa.setText("-----")
        self.ui.labelRankingUltime5PartiteInTrasfertaSquadraInTrasferta.setText("-----")
        # Scontri Storici Diretti
        self.ui.labelScontriTrovati.setText("-----")    
        self.ui.labelBilancioScontriDirettiSquadraDiCasa.setText("-----")
        self.ui.labelBilancioScontriDirettiSquadraInTrasferta.setText("-----")
        self.ui.labelBilancioScontriDirettiPareggi.setText("-----")
        self.ui.labelUltime5PartiteTraLe2Squadre_1.setText("-----")
        self.ui.labelUltime5PartiteTraLe2Squadre_2.setText("-----")
        self.ui.labelUltime5PartiteTraLe2Squadre_3.setText("-----")
        self.ui.labelUltime5PartiteTraLe2Squadre_4.setText("-----")
        self.ui.labelUltime5PartiteTraLe2Squadre_5.setText("-----")
        # scommessa consigliata
        self.ui.labelScommessaConsigliataDoppiaChance.setText("Scommessa Consigliata: -----")
        self.ui.labelScommessaConsigliataProbabilitaSuccesso.setText("Probabilità di Successo: -----")
        self.ui.labelScommessaConsigliataLivelloRischio.setText("Livello di Rischio: -----")
        # altre opzioni
        self.ui.labelAltreOpzioniSuggerimenti.setText("Combo suggerita: -----")
        # motivazione tecnica
        self.ui.labelMotivazioneTecnicaPredizione.setText("📊 Predizione esito: -----")
        self.ui.labelMotivazioneTecnicaGoalsPrevisti.setText("⚽ Goal previsti: -----")
        self.ui.labelMotivazioneTecnicaFormaRecente.setText("🔥 Forma recente: -----")
        self.ui.labelMotivazioneTecnicaRankingAttuale.setText("🏆 Ranking attuale: -----")
        self.ui.labelMotivazioneTecnicaScontriDiretti.setText("⚔️ Scontri diretti: -----")
        # commento finale
        self.ui.labelCommentoFinaleIndicatori.setText("📝 Indicatori contrastanti: -----")
        self.ui.labelCommentoFinaleConfidenza.setText("💡 Confidenza predizione: -----")
        # sqaudra di casa analisi forma
        self.ui.labelAnalisiSquadraDiCasa.setText("---- - Analisi Forma")
        self.ui.labelAnalisiSqudraDiCasaInCasa.setText("🏠 In CASA (ultime 5): -----")
        self.ui.labelAnalisiSqudraDiCasaInTrasferta.setText("✈️ In TRASFERTA (ultime 5): -----")
        self.ui.labelAnalisiSqudraDiCasaGenerale.setText("📊 GENERALE (ultime 5): -----")
        self.ui.labelMediaPuntiCasa.setText("Media Punti/partita: -----")
        # sqaudra in trasferta analisi forma
        self.ui.labelAnalisiSquadraInTrasferta.setText("---- - Analisi Forma")
        self.ui.labelAnalisiSqudraInTrasfertaInCasa.setText("🏠 In CASA (ultime 5): -----")
        self.ui.labelAnalisiSqudraInTrasfertaInTrasferta.setText("✈️ In TRASFERTA (ultime 5): -----")
        self.ui.labelAnalisiSquadraInTrasfertaGenerale.setText("📊 GENERALE (ultime 5): -----")
        self.ui.labelMediaPuntiTrasferta.setText("Media Punti/partita: -----")
        # Grafico
        self.ui.labelGrafico.setText("Grafico di confronto: -----")
    # end reset()
        
    
# end of RunPredizioni class


if __name__ == "__main__":
    app = QApplication(sys.argv)
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
    window = RunPredizioni()
    window.show()
    sys.exit(app.exec_())
    
    