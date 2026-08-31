
import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QLabel
from PyQt5.QtGui import QPixmap
import sys

# I miei Moduli
from ErrorManager import catturaEccezione
from InfoPopUp import InfoPopup
from myPath import myPath, myFile

# Import relativo se usato come modulo, assoluto se eseguito direttamente
from EstrazioneDati import *
from CreaGrafici import *
from UI.Grafici import Ui_MainWindow
    # import CreaGrafici as gf
    # from Grafici import Ui_MainWindow


class PopUp(InfoPopup):
    @catturaEccezione
    def __init__(self, messaggio: str, parent=None):
        super().__init__(messaggio, parent)
    # end __init__()

    @catturaEccezione
    def mostra(self):
        self.show()
        QtWidgets.QApplication.processEvents()  # Qui è corretto: assicura che il popup sia visibile subito
    # end mostra()
    
    @catturaEccezione
    def setProgressBar(self, valore: int):
        self.setProgress(valore)
        QtWidgets.QApplication.processEvents()  # Qui è corretto: aggiorna la UI immediatamente
    # end progressbar()
    

class StringaIntestazioniStatistiche:
    @catturaEccezione
    def __init__(self, squadra: str):
        self.squadra = squadra
        self._1 = ['a','e','i','o','u']
        self._2 = ['Fiorentina','Juventus','Lazio','Roma']
    # end __init__()
       
    @catturaEccezione
    def stringaIntestazioniGenerali(self) -> str:
        '''Restituisce una stringa formattata di intestazione per le statistiche generali'''
     
        if self.squadra[0].lower() in self._1:   # Controlla se la prima lettera è una vocale
            text = f'Statistiche generali dell\' {self.squadra}' # Se la squadra inizia con una vocale
        elif self.squadra in self._2:   # Controlla se la squadra fa parte della lista _2
            text = f'Statistiche generali della  {self.squadra}'
        else:   # Se la squadra inizia con una consonante
            text = f'Statistiche generali del {self.squadra}'
        # end if
        return text
    # end stringaIntestazioniGenerali() 
    
    @catturaEccezione
    def stringaIntestazioniInCasa(self) -> str:
        '''Restituisce una stringa formattata di intestazione per le statistiche in casa'''
        if self.squadra[0].lower() in self._1:   # Controlla se la prima lettera è una vocale
            text = f'Statistiche in casa dell\' {self.squadra}' # Se la squadra inizia con una vocale
        elif self.squadra in self._2:   # Controlla se la squadra fa parte della lista _2
            text = f'Statistiche in casa della  {self.squadra}'
        else:   # Se la squadra inizia con una consonante
            text = f'Statistiche in casa del {self.squadra}'
        # end if
        return text
    # end stringaIntestazioniInCasa()
    
    @catturaEccezione
    def stringaIntestazioniInTrasferta(self) -> str:
        '''Restituisce una stringa formattata di intestazione per le statistiche in trasferta'''
        if self.squadra[0].lower() in self._1:   # Controlla se la prima lettera è una vocale
            text = f'Statistiche in trasferta dell\' {self.squadra}' # Se la squadra inizia con una vocale
        elif self.squadra in self._2:   # Controlla se la squadra fa parte della lista _2
            text = f'Statistiche in trasferta della  {self.squadra}'
        else:   # Se la squadra inizia con una consonante
            text = f'Statistiche in trasferta del {self.squadra}'
        # end if
        return text
    # end stringaIntestazioniInTrasferta()

class AppStatistiche(QtWidgets.QMainWindow):
    
    @catturaEccezione
    def __init__(self):
        super(AppStatistiche, self).__init__()

        
        
        # Inizializza l'interfaccia utente
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle('Statistiche & Grafici')
        # Un'ulteriore inizializzazione può essere effettuata qui
        
        # Fix per la scrollbar: forza le dimensioni corrette del contenuto
        # Il problema era che widgetResizable=True ridimensionava il contenuto al viewport
        # Impostando una minimumSize, forziamo Qt a mantenere le dimensioni corrette
        self.ui.scrollAreaWidgetContentSquadraDiCasa.setMinimumSize(1881, 1200)
        self.ui.verticalLayoutWidget.setMinimumSize(1861, 1180)
        
        # Fix per la scrollbar della seconda scroll area (squadra in trasferta)
        self.ui.scrollAreaWidgetContentSquadraInTrasferta.setMinimumSize(1881, 1200)
        self.ui.verticalLayoutWidgetInTrasferta.setMinimumSize(1861, 1180)
        
        # Connessione del pusante per uscire
        self.ui.buttonExit.clicked.connect(self.close) # type: ignore
        
        # setto il testo delle combobox a ""
        # Aggiungi il testo placeholder come primo elemento
        self.ui.comboBoxSquadraDiCasa.insertItem(0, "Seleziona la squadra di casa")
        self.ui.comboBoxSquadraInTrasferta.insertItem(0, "Seleziona la squadra in trasferta")

        # Poi imposta l'indice al primo elemento (quello appena aggiunto)
        self.ui.comboBoxSquadraDiCasa.setCurrentIndex(0)
        self.ui.comboBoxSquadraInTrasferta.setCurrentIndex(0)

        # definisco le variabili
        # os.path.dirname(__file__) --> percorso corrente del file Classifica.csv 
        # os.path.join(os.path.dirname(__file__), '../Csv/Classifica.csv') --> percorso relativo al file Classifica.csv
        # os.path.abspath(...) --> percorso assoluto del file Classifica.csv
        self.campionatoCorrente = myFile.campionatoCorrente # os.path.abspath(os.path.join(os.path.dirname(__file__), '../Csv/Campionato.csv'))
        self.squadraDiCasa = ''
        self.squadraInTrasferta = ''
       
        # Istanzio le classi
        self.estrattore = EstrazioneDati(self.campionatoCorrente)
        
        # self.psg = None
        
        # Inserisco le squadre nelle combBox
        self.caricaElementiComboBox()
        
        # Connessioni degli eventi delle ComboBox
        self.ui.comboBoxSquadraDiCasa.currentTextChanged.connect(self.onSquadraDiCasaChanged)
        self.ui.comboBoxSquadraInTrasferta.currentTextChanged.connect(self.onSquadraInTrasfertaChanged)
    # end __init__()
    
    @catturaEccezione
    def caricaElementiComboBox(self):
        try:
            self.listaSquadre = self.estrattore.squadre()
        except AttributeError:
            raise AttributeError("ERRORE: Il metodo squadre() non esiste nella classe EstrazioneDati")
        except Exception as e:
            raise Exception(f"ERRORE: Errore durante l'estrazione delle squadre: {e}")
            
        
        # Controllo di sicurezza: verifica che squadre non sia None o vuoto
        if self.listaSquadre is None:
            raise Exception("ERRORE: Il metodo squadre() ha restituito None")
            # self.listaSquadre = []  # Inizializza come lista vuota
            # return
        
        if not self.listaSquadre:  # Se la lista è vuota
            raise ValueError(f"AVVISO: Nessuna squadra trovata nel file {self.path}")
            # return
            
        # Popola le ComboBox solo se ci sono squadre
        for squadra in self.listaSquadre:
            self.ui.comboBoxSquadraDiCasa.addItem(squadra)
            self.ui.comboBoxSquadraInTrasferta.addItem(squadra)

        # print(f"Caricate {len(self.listaSquadre)} squadre nelle ComboBox")
    # end caricaElementiComboBox()
    
    @catturaEccezione
    def onSquadraDiCasaChanged(self, testo_selezionato_dalla_combobox):
        """
        Gestisce l'evento di selezione della squadra di casa
        Il parametro 'testo_selezionato_dalla_combobox' viene passato automaticamente 
        dal segnale Qt currentTextChanged quando l'utente cambia selezione
        """
        # print(f"Qt ha passato automaticamente: {testo_selezionato_dalla_combobox}")

        # Se vengono selezionate due squadre uguali lancia un warning
        # if self.ui.comboBoxSquadraInTrasferta.currentText() == testo_selezionato_dalla_combobox:
        #     QMessageBox.warning(self, "Attenzione", "La squadra di casa non può essere la stessa della squadra in trasferta.")
        #     self.ui.comboBoxSquadraInTrasferta.setCurrentIndex(0)
        #     return
        # end if

        # se sono selezionate due squadre valide aggiorna l'etichetta
        # altrimenti resetta l'etichetta --> "Squadra di casa VS squadra in trasferta"
        if testo_selezionato_dalla_combobox != "Seleziona la squadra di casa" and self.ui.comboBoxSquadraInTrasferta.currentText() != "Seleziona la squadra in trasferta":
            self.ui.labelIntestazione_2.setText(f"Statistiche & Grafici: {testo_selezionato_dalla_combobox} VS {self.ui.comboBoxSquadraInTrasferta.currentText()}")
        else:
            self.ui.labelIntestazione_2.setText("Squadra di casa VS squadra in trasferta")
            # end if
        
            
        # popolo le etichette delle intestazioni delle statistiche
        if testo_selezionato_dalla_combobox != "Seleziona la squadra di casa":
            sis = StringaIntestazioniStatistiche(squadra=testo_selezionato_dalla_combobox)
            self.ui.labelIntestazioneGeneraliSquadraDiCasa.setText(sis.stringaIntestazioniGenerali())
            self.ui.labelIntestazioneInCasaSquadraDiCasa.setText(sis.stringaIntestazioniInCasa())
            self.ui.labelIntestazioneInTrasfertaSquadraDiCasa.setText(sis.stringaIntestazioniInTrasferta())
        
        # Qui puoi chiamare le funzioni per aggiornare i dati e i grafici
        # self.estraiDatiSquadraDiCasa()
        self.aggiornaStatisticheSquadraDiCasa(testo_selezionato_dalla_combobox)
        # self.aggiornaGraficiSquadraDiCasa(testo_selezionato_dalla_combobox)
    # end onSquadraDiCasaChanged()
    
    @catturaEccezione
    def onSquadraInTrasfertaChanged(self, testo_selezionato_dalla_combobox):
        """
        Gestisce l'evento di selezione della squadra in trasferta
        Il parametro 'testo_selezionato_dalla_combobox' viene passato automaticamente 
        dal segnale Qt currentTextChanged quando l'utente cambia selezione
        """
        # print(f"Qt ha passato automaticamente: {testo_selezionato_dalla_combobox}")
    
        # Se vengono selezionate due squadre uguali lancia un warning
        # if self.ui.comboBoxSquadraDiCasa.currentText() == testo_selezionato_dalla_combobox:
        #     QMessageBox.warning(self, "Attenzione", "La squadra in trasferta non può essere la stessa della squadra di casa.")
        #     self.ui.comboBoxSquadraInTrasferta.setCurrentIndex(0)
        #     return
        # end if
        
        # se sono selezionate due squadre valide aggiorna l'etichetta
        # altrimenti resetta l'etichetta --> "Squadra di casa VS squadra
        if testo_selezionato_dalla_combobox != "Seleziona la squadra in trasferta" and self.ui.comboBoxSquadraDiCasa.currentText() != "Seleziona la squadra di casa":
            self.ui.labelIntestazione_2.setText(f"{self.ui.comboBoxSquadraDiCasa.currentText()} VS {testo_selezionato_dalla_combobox}") 
        else:
            self.ui.labelIntestazione_2.setText("Squadra di casa VS squadra in trasferta")
        # end if
        
        # popolo le etichette delle intestazioni delle statistiche
        if testo_selezionato_dalla_combobox != "Seleziona la squadra in trasferta":
            sis = StringaIntestazioniStatistiche(squadra=testo_selezionato_dalla_combobox)
            self.ui.labelIntestazioneGeneraliSquadraInTrasferta.setText(sis.stringaIntestazioniGenerali())
            self.ui.labelIntestazioneInCasaSquadraInTrasferta.setText(sis.stringaIntestazioniInCasa())
            self.ui.labelIntestazioneInTrasfertaSquadraInTrasferta.setText(sis.stringaIntestazioniInTrasferta())

        # print(f"Squadra in trasferta selezionata: {testo_selezionato_dalla_combobox}")
        
        # Qui puoi chiamare le funzioni per aggiornare i dati e i grafici
        # self.estraiDatiSquadraInTrasferta()
        self.aggiornaStatisticheSquadraInTrasferta(testo_selezionato_dalla_combobox)
        # self.aggiornaGraficiSquadraInTrasferta(testo_selezionato_dalla_combobox)
    # end onSquadraInTrasfertaChanged()
    
    @catturaEccezione
    def mostra_grafico_statistiche(self,squadra: str, label_destinazione: QLabel, where: str, squadraIn: str):
        '''Mostra il grafico delle statistiche in un QLabel specificato'''
        graficoStatistiche = Grafici(path =self.campionatoCorrente, squadra=squadra, where=where, squadraIn=squadraIn)
        grafico = graficoStatistiche.crea_graficoStatistiche()
        pixmap = QPixmap(grafico)
        target_width = 600
        target_height = 270
        if not pixmap.isNull():
            # scaled_pixmap = pixmap.scaled(target_width, target_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            # ...existing code...
            scaled_pixmap = pixmap.scaled(
            target_width, 
            target_height, 
            QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
# ...existing code...
            label_destinazione.setPixmap(scaled_pixmap)
            label_destinazione.setScaledContents(False)
        else:
            label_destinazione.clear()
        # end if
        
    # end mostra_grafico_statistiche()
    
    @catturaEccezione
    def mostra_grafico_goals(self, squadra: str, label_destinazione: QLabel, where: str, squadraIn: str):
        '''Mostra il grafico dei goals in un QLabel specificato'''
        graficoGoals = Grafici(path =self.campionatoCorrente, squadra=squadra, where=where, squadraIn=squadraIn)
        grafico = graficoGoals.crea_goalsFattiSubiti()
        pixmap = QPixmap(grafico)
        target_width = 600
        target_height = 270
        if not pixmap.isNull():
            # scaled_pixmap = pixmap.scaled(target_width, target_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            # ...existing code...
            scaled_pixmap = pixmap.scaled(
                target_width, 
                target_height, 
                QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
# ...existing code...
            label_destinazione.setPixmap(scaled_pixmap)
            label_destinazione.setScaledContents(False)
        else:
            label_destinazione.clear()
        # end if
    # end mostra_grafico_goals()
    
    @catturaEccezione
    def mostra_grafico_trend(self,squadra: str, label_destinazione: QLabel, where: str, squadraIn: str):
        '''Mostra il grafico del trend in un QLabel specificato'''
        graficoTrend = Grafici(path =self.campionatoCorrente, squadra=squadra, where=where, squadraIn=squadraIn)
        grafico = graficoTrend.Crea_graficoTrend()
        pixmap = QPixmap(grafico)
        target_width = 600
        target_height = 270
        if not pixmap.isNull():
            # scaled_pixmap = pixmap.scaled(target_width, target_height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            # ...existing code...
            scaled_pixmap = pixmap.scaled(
                target_width, 
                target_height, 
                QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
# ...existing code...
            
            label_destinazione.setPixmap(scaled_pixmap)
            label_destinazione.setScaledContents(False)
        else:
            label_destinazione.clear()
        # end if
    
    
    
    @catturaEccezione
    def aggiornaStatisticheSquadraDiCasa(self, squadra):
        '''Aggiorna le statistiche della squadra di casa nell'interfaccia'''
  
        # 1. Crea il popup
        popup = PopUp("Aggiornamento statistiche in corso...")
        popup.mostra()
        
        progress = [0] * 15
        # Rimodulazione progress per 18 iterazioni (da 0 a 100)
        progress = [round(i * 100 / 24) for i in range(25)]
        
       
        # statistiche generali
        popup.setProgressBar(progress[0])  # Aggiorna la barra di avanzamento (es. 0%)
        self.ui.labelVittorie_ValoreGeneraliSquadraDiCasa.setText(self.estrattore.vittorie(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[1])  # Aggiorna la barra di avanzamento (es. 4%)
        self.ui.labelPareggi_ValoreGeneraliSquadraDiCasa.setText(self.estrattore.pareggi(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[2])  # Aggiorna la barra (es. 8%)
        self.ui.labelSconfitte_ValoreGeneraliSquadraDiCasa.setText(self.estrattore.sconfitte(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[3])  # Aggiorna la barra (es. 12%)
        self.ui.labelGoalsFatti_ValoreGeneraliSquadraDiCasa.setText(self.estrattore.goalsFatti(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[4])  # Aggiorna la barra (es. 16%)
        self.ui.labelGoalsSubiti_ValoreGeneraliSquadraDiCasa.setText(self.estrattore.goalsSubiti(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[5])  # Aggiorna la barra (es. 20%)
        
        # mostro i grafici
        self.mostra_grafico_statistiche(squadra = squadra, label_destinazione=self.ui.labelGraficoStatisticheGeneraliSquadraDiCasa, where='generali', squadraIn='casa')
        popup.setProgressBar(progress[6])  # Aggiorna la barra (es. 24%)
        self.mostra_grafico_goals(squadra = squadra, label_destinazione=self.ui.labelGraficoGoalFattiESubitiGeneraliSquadraDiCasa, where='generali', squadraIn='casa')
        popup.setProgressBar(progress[7])  # Aggiorna la barra (es. 28%)
        self.mostra_grafico_trend(squadra = squadra, label_destinazione=self.ui.labelGraficoTrandGeneraliSquadraDiCasa, where='generali', squadraIn='casa')
        popup.setProgressBar(progress[8])  # Aggiorna la barra (es. 32%)


        # statistiche in casa
        self.ui.labelVittorie_ValoreInCasaSquadraDiCasa.setText(self.estrattore.vittorie(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[9])  # Aggiorna la barra (es. 36%)
        self.ui.labelPareggi_ValoreInCasaSquadraDiCasa.setText(self.estrattore.pareggi(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[10])  # Aggiorna la barra (es. 40%)
        self.ui.labelSconfitte_ValoreInCasaSquadraDiCasa.setText(self.estrattore.sconfitte(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[11])  # Aggiorna la barra (es. 44%)
        self.ui.labelGoalsFatti_ValoreInCasaSquadraDiCasa.setText(self.estrattore.goalsFatti(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[12])  # Aggiorna la barra (es. 48%)
        self.ui.labelGoalsSubiti_ValoreInCasaSquadraDiCasa.setText(self.estrattore.goalsSubiti(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[13])  # Aggiorna la barra (es. 52%)
        
        # mostro i grafici
        self.mostra_grafico_statistiche(squadra = squadra, label_destinazione=self.ui.labelGraficoStatisticheInCasaSquadraDiCasa, where='casa', squadraIn='casa')
        popup.setProgressBar(progress[14])  # Aggiorna la barra (es. 56%)
        self.mostra_grafico_goals(squadra = squadra, label_destinazione=self.ui.labelGraficoGoalFattiESubitiInCasaSquadraDiCasa, where='casa', squadraIn='casa')
        popup.setProgressBar(progress[15])  # Aggiorna la barra (es. 60%)
        self.mostra_grafico_trend(squadra = squadra, label_destinazione=self.ui.labelGraficoTrandInCasaSquadraDiCasa, where='casa', squadraIn='casa')
        popup.setProgressBar(progress[16])  # Aggiorna la barra (es. 64%)

        # statistiche in trasferta
        self.ui.labelVittorie_ValoreInTrasfertaSquadraDiCasa.setText(self.estrattore.vittorie(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[17])  # Aggiorna la barra (es. 68%)
        self.ui.labelPareggi_ValoreInTrasfertaSquadraDiCasa.setText(self.estrattore.pareggi(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[18])  # Aggiorna la barra (es. 72%)
        self.ui.labelSconfitte_ValoreInTrasfertaSquadraDiCasa.setText(self.estrattore.sconfitte(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[19])  # Aggiorna la barra (es. 76%)
        self.ui.labelGoalsFatti_ValoreInTrasfertaSquadraDiCasa.setText(self.estrattore.goalsFatti(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[20])  # Aggiorna la barra (es. 76%)
        self.ui.labelGoalsSubiti_ValoreInTrasfertaSquadraDiCasa.setText(self.estrattore.goalsSubiti(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[21])  # Aggiorna la barra (es. 80%)
        
        # mostro i grafici
        self.mostra_grafico_statistiche(squadra = squadra, label_destinazione=self.ui.labelGraficoStatisticheInTrasfertaSquadraDiCasa, where='trasferta', squadraIn='casa')
        popup.setProgressBar(progress[22])  # Aggiorna la barra (es. 86%)
        self.mostra_grafico_goals(squadra = squadra, label_destinazione=self.ui.labelGraficoGoalFattiESubitiInTrasfertaSquadraDiCasa, where='trasferta', squadraIn='casa')
        popup.setProgressBar(progress[23])  # Aggiorna la barra (es. 92%)
        self.mostra_grafico_trend(squadra = squadra, label_destinazione=self.ui.labelGraficoTrandInTrasfertaSquadraDiCasa, where='trasferta', squadraIn='casa')
        popup.setProgressBar(progress[24])  # Aggiorna la barra (es. 96%)

        popup.close()  # Chiudi il popup quando hai finito
        # graficoStatisticheGenerali.crea_grafico()
    # end aggiornaStatisticheSquadraDiCasa()
    
    
    @catturaEccezione
    def aggiornaStatisticheSquadraInTrasferta(self, squadra):
        '''Aggiorna le statistiche della squadra in trasferta nell'interfaccia'''
        # 1. Crea il popup
        popup = PopUp("Aggiornamento statistiche in corso...")
        popup.mostra()
        
        progress = [0] * 15
        # Rimodulazione progress per 18 iterazioni (da 0 a 100)
        progress = [round(i * 100 / 24) for i in range(25)]
        
        # statistiche generali
        popup.setProgressBar(progress[0])  # Aggiorna la barra (es. 0%)
        self.ui.labelVittorie_ValoreGeneraliSquadraInTrasferta.setText(self.estrattore.vittorie(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[1])  # Aggiorna la barra (es. 4%)
        self.ui.labelPareggi_ValoreGeneraliSquadraInTrasferta.setText(self.estrattore.pareggi(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[2])  # Aggiorna la barra (es. 8%)
        self.ui.labelSconfitte_ValoreGeneraliSquadraInTrasferta.setText(self.estrattore.sconfitte(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[3])  # Aggiorna la barra (es. 12%)
        self.ui.labelGoalsFatti_ValoreGeneraliSquadraInTrasferta.setText(self.estrattore.goalsFatti(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[4])  # Aggiorna la barra (es. 16%)
        self.ui.labelGoalsSubiti_ValoreGeneraliSquadraInTrasferta.setText(self.estrattore.goalsSubiti(squadra = squadra, where = 'generali'))
        popup.setProgressBar(progress[5])  # Aggiorna la barra (es. 20%)
        
        # mostro i grafici generali
        self.mostra_grafico_statistiche(squadra = squadra, label_destinazione=self.ui.labelGraficoStatisticheGeneraliSquadraInTrasferta, where='generali', squadraIn='trasferta')
        popup.setProgressBar(progress[6])  # Aggiorna la barra (es. 24%)
        self.mostra_grafico_goals(squadra = squadra, label_destinazione=self.ui.labelGraficoGoalFattiESubitiGeneraliSquadraInTrasferta, where='generali', squadraIn='trasferta')
        popup.setProgressBar(progress[7])  # Aggiorna la barra (es. 28%)
        self.mostra_grafico_trend(squadra = squadra, label_destinazione=self.ui.labelGraficoTrandGeneraliSquadraInTrasferta, where='generali', squadraIn='trasferta')
        popup.setProgressBar(progress[8])  # Aggiorna la barra (es. 32%)

        # statistiche in casa
        self.ui.labelVittorie_ValoreInCasaSquadraInTrasferta.setText(self.estrattore.vittorie(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[9])  # Aggiorna la barra (es. 36%)
        self.ui.labelPareggi_ValoreInCasaSquadraInTrasferta.setText (self.estrattore.pareggi(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[10])  # Aggiorna la barra (es. 40%)
        self.ui.labelSconfitte_ValoreInCasaSquadraInTrasferta.setText(self.estrattore.sconfitte(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[11])  # Aggiorna la barra (es. 44%)
        self.ui.labelGoalsFatti_ValoreInCasaSquadraInTrasferta.setText(self.estrattore.goalsFatti(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[12])  # Aggiorna la barra (es. 48%)
        self.ui.labelGoalsSubiti_ValoreInCasaSquadraInTrasferta.setText(self.estrattore.goalsSubiti(squadra = squadra, where = 'casa'))
        popup.setProgressBar(progress[13])  # Aggiorna la barra (es. 52%)

        # mostro i grafici in casa
        self.mostra_grafico_statistiche(squadra = squadra, label_destinazione=self.ui.labelGraficoStatisticheInCasaSquadraInTrasferta, where='casa', squadraIn='trasferta')
        popup.setProgressBar(progress[14])  # Aggiorna la barra (es. 56%)
        self.mostra_grafico_goals(squadra = squadra, label_destinazione=self.ui.labelGraficoGoalFattiESubitiInCasaSquadraInTrasferta, where='casa', squadraIn='trasferta')
        popup.setProgressBar(progress[15])  # Aggiorna la barra (es. 60%)
        self.mostra_grafico_trend(squadra = squadra, label_destinazione=self.ui.labelGraficoTrandInCasaSquadraInTrasferta, where='casa', squadraIn='trasferta')
        popup.setProgressBar(progress[16])  # Aggiorna la barra (es. 64%)
        
        # statistiche in trasferta
        self.ui.labelVittorie_ValoreInTrasfertaSquadraInTrasferta.setText(self.estrattore.vittorie(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[17])  # Aggiorna la barra (es. 68%)
        self.ui.labelPareggi_ValoreInTrasfertaSquadraInTrasferta.setText(self.estrattore.pareggi(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[18])  # Aggiorna la barra (es. 72%)
        self.ui.labelSconfitte_ValoreInTrasfertaSquadraInTrasferta.setText(self.estrattore.sconfitte(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[19])  # Aggiorna la barra (es. 76%)
        self.ui.labelGoalsFatti_ValoreInTrasfertaSquadraInTrasferta.setText(self.estrattore.goalsFatti(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[20])  # Aggiorna la barra (es. 80%)
        self.ui.labelGoalsSubiti_ValoreInTrasfertaSquadraInTrasferta.setText(self.estrattore.goalsSubiti(squadra = squadra, where = 'trasferta'))
        popup.setProgressBar(progress[21])  # Aggiorna la barra (es. 84%)
        
        # mostro i grafici in trasferta
        self.mostra_grafico_statistiche(squadra = squadra, label_destinazione=self.ui.labelGraficoStatisticheInTrasfertaSquadraInTrasferta, where='trasferta', squadraIn='trasferta')
        popup.setProgressBar(progress[22])  # Aggiorna la barra (es. 88%)
        self.mostra_grafico_goals(squadra = squadra, label_destinazione=self.ui.labelGraficoGoalFattiESubitiInTrasfertaSquadraInTrasferta, where='trasferta', squadraIn='trasferta')
        popup.setProgressBar(progress[23])  # Aggiorna la barra (es. 92%)
        self.mostra_grafico_trend(squadra = squadra, label_destinazione=self.ui.labelGraficoTrandInTrasfertaSquadraInTrasferta, where='trasferta', squadraIn='trasferta')
        popup.setProgressBar(progress[24])  # Aggiorna la barra (es. 96%)
        popup.close()  # Chiudi il popup quando hai finito
        
    # end aggiornaStatisticheSquadraInTrasferta()
# end MainWindow class

@catturaEccezione
def main():
    
    
    
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
    window = AppStatistiche()
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
   
    main()
# End of appGrafici.py
