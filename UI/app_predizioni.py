#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Applicazione principale per l'interfaccia delle Predizioni
Integrazione con EsitoDalRanking.py per analisi complete
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

# Aggiungi il percorso principale per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Predizioni import Ui_MainWindow
import EsitoDalRanking

class PredictionWorker(QThread):
    """Thread worker per elaborare le predizioni senza bloccare l'UI"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, squadra_casa, squadra_trasferta):
        super().__init__()
        self.squadra_casa = squadra_casa
        self.squadra_trasferta = squadra_trasferta
    
    def run(self):
        try:
            # Crea un'istanza dell'analizzatore
            analizzatore = EsitoDalRanking.EsitoDalRanking()
            
            # Genera le predizioni
            risultati = analizzatore.predici_partita(self.squadra_casa, self.squadra_trasferta)
            
            # Emetti i risultati
            self.finished.emit(risultati)
            
        except Exception as e:
            self.error.emit(str(e))

class PredizioniMainWindow(QMainWindow):
    """Finestra principale per le predizioni calcistiche"""
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Imposta il titolo della finestra
        self.setWindowTitle("🏆 Predizioni Calcistiche - Sistema AI Betting")
        
        # Worker thread
        self.worker = None
        
        # Inizializza l'interfaccia
        self.setup_initial_interface()
        
        # Timer per aggiornamenti automatici
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_update)
        
    def setup_initial_interface(self):
        """Configura l'interfaccia iniziale"""
        # Imposta valori di esempio (Roma vs Udinese)
        self.update_ui_with_data({
            'squadra_casa': 'Roma',
            'squadra_trasferta': 'Udinese',
            'goal_previsti_casa': 2.1,
            'goal_previsti_trasferta': 1.0,
            'esito_previsto': '1',
            'doppia_chance': '1X',
            'prob_vittoria_casa': 75,
            'prob_pareggio': 15,
            'prob_vittoria_trasferta': 10,
            'under_15': 25,
            'over_15': 75,
            'under_25': 45,
            'over_25': 55,
            'forma_casa': 2.4,
            'forma_trasferta': 1.6,
            'ranking_attuale': {
                'casa_generale': 4,
                'trasferta_generale': 9,
                'casa_casa': 8,
                'trasferta_trasferta': 9
            },
            'ranking_precedenti': {
                'casa_generale': 7,
                'trasferta_generale': 11,
                'casa_casa': 3,
                'trasferta_trasferta': 12
            },
            'ranking_ultime5': {
                'casa_generale': 6,
                'trasferta_generale': 9,
                'casa_casa': 8,
                'trasferta_trasferta': 10
            },
            'statistiche_storiche': {
                'casa': "228 partite, 113-51-64, 375-271",
                'trasferta': "228 partite, 62-73-93, 265-324"
            },
            'scontri_diretti': {
                'totali': 12,
                'vittorie_casa': 9,
                'vittorie_trasferta': 2,
                'pareggi': 1,
                'ultime_5': [
                    "16/Apr: Roma 3-0 Udinese",
                    "26/Nov: Roma 3-1 Udinese",
                    "25/Apr: Udinese 1-2 Roma",
                    "22/Set: Roma 3-0 Udinese",
                    "26/Gen: Udinese 1-2 Roma"
                ]
            },
            'ai_analisi': {
                'scommessa_consigliata': "1 (Vittoria Roma) - 75%",
                'motivazione': "Roma in ottima forma, Udinese in crisi",
                'livello_rischio': "BASSO",
                'altre_opzioni': "Over 2.5, 1X"
            }
        })
        
    def update_ui_with_data(self, data):
        """Aggiorna l'interfaccia con i dati forniti"""
        try:
            # Sezione Predizioni Goal
            goal_text = f"Goal previsti: {data['squadra_casa']} {data.get('goal_previsti_casa', 0):.1f} - {data.get('goal_previsti_trasferta', 0):.1f} {data['squadra_trasferta']}"
            self.ui.labelGoalPrevisti.setText(goal_text)
            self.ui.labelEsitoPrevisto.setText(f"Esito Previsto: {data.get('esito_previsto', 'N/A')}")
            self.ui.labelDoppiaChanceSuggerita.setText(f"Doppia chance suggerita: {data.get('doppia_chance', 'N/A')}")
            
            # Probabilità Esito
            self.ui.labelProbabilitaVittoria.setText(f"1 (Vittoria {data['squadra_casa']}): {data.get('prob_vittoria_casa', 0)}%")
            self.ui.labelProbabilitaPareggio.setText(f"X (Pareggio): {data.get('prob_pareggio', 0)}%")
            self.ui.labelProbabilitaSconfitta.setText(f"2 (Vittoria {data['squadra_trasferta']}): {data.get('prob_vittoria_trasferta', 0)}%")
            
            # Under/Over
            self.ui.labelUnder15.setText(f"Under 1.5: {data.get('under_15', 0)}%")
            self.ui.labelOver15.setText(f"Over 1.5: {data.get('over_15', 0)}%")
            self.ui.labelUnder25.setText(f"Under 2.5: {data.get('under_25', 0)}%")
            self.ui.labelOver25.setText(f"Over 2.5: {data.get('over_25', 0)}%")
            
            # Forma Recente
            self.ui.labelFormaRecenteSquadraDiCasa.setText(f"{data['squadra_casa']}: {data.get('forma_casa', 0):.1f}/3.0 punti/partita")
            self.ui.labelFormaRecenteSquadraInTrasferta.setText(f"{data['squadra_trasferta']}: {data.get('forma_trasferta', 0):.1f}/3.0 punti/partita")
            
            # Ranking Campionati Precedenti
            ranking_prec = data.get('ranking_precedenti', {})
            self.ui.labelGoalPrevisti_2.setText(f"{data['squadra_casa']}: {ranking_prec.get('casa_generale', 'N/A')}° posto")
            self.ui.labelEsitoPrevisto_2.setText(f"{data['squadra_trasferta']}: {ranking_prec.get('trasferta_generale', 'N/A')}° posto")
            self.ui.labelProbabilitaVittoria_2.setText(f"{data['squadra_casa']}: {ranking_prec.get('casa_casa', 'N/A')}° posto")
            self.ui.labelProbabilitaPareggio_2.setText(f"{data['squadra_trasferta']}: {ranking_prec.get('trasferta_trasferta', 'N/A')}° posto")
            
            # Statistiche storiche aggregate
            stat_storiche = data.get('statistiche_storiche', {})
            self.ui.labelFormaRecenteSquadraDiCasa_2.setText(f"{data['squadra_casa']}: {stat_storiche.get('casa', 'N/A')}")
            self.ui.labelFormaRecenteSquadraInTrasferta_2.setText(f"{data['squadra_trasferta']}: {stat_storiche.get('trasferta', 'N/A')}")
            
            # Ranking Campionato Attuale
            ranking_att = data.get('ranking_attuale', {})
            self.ui.labelGoalPrevisti_3.setText(f"{data['squadra_casa']}: {ranking_att.get('casa_generale', 'N/A')}° posto")
            self.ui.labelEsitoPrevisto_3.setText(f"{data['squadra_trasferta']}: {ranking_att.get('trasferta_generale', 'N/A')}° posto")
            self.ui.labelProbabilitaVittoria_3.setText(f"{data['squadra_casa']}: {ranking_att.get('casa_casa', 'N/A')}° posto")
            self.ui.labelProbabilitaPareggio_3.setText(f"{data['squadra_trasferta']}: {ranking_att.get('trasferta_trasferta', 'N/A')}° posto")
            
            # Ranking Ultime 5 Partite
            ranking_5 = data.get('ranking_ultime5', {})
            self.ui.labelGoalPrevisti_4.setText(f"{data['squadra_casa']}: {ranking_5.get('casa_generale', 'N/A')}° posto")
            self.ui.labelEsitoPrevisto_4.setText(f"{data['squadra_trasferta']}: {ranking_5.get('trasferta_generale', 'N/A')}° posto")
            self.ui.labelProbabilitaVittoria_4.setText(f"{data['squadra_casa']}: {ranking_5.get('casa_casa', 'N/A')}° posto")
            self.ui.labelProbabilitaPareggio_4.setText(f"{data['squadra_trasferta']}: {ranking_5.get('trasferta_trasferta', 'N/A')}° posto")
            
            # Statistiche storiche nella sezione destra
            self.ui.labelGoalPrevisti_5.setText(f"{data['squadra_casa']}: {stat_storiche.get('casa', 'N/A')}")
            self.ui.labelEsitoPrevisto_5.setText(f"{data['squadra_trasferta']}: {stat_storiche.get('trasferta', 'N/A')}")
            
            # Scontri diretti
            scontri = data.get('scontri_diretti', {})
            self.ui.labelProbabilitaVittoria_5.setText(f"Trovati {scontri.get('totali', 0)} scontri diretti storici")
            self.ui.labelProbabilitaVittoria_6.setText(f"{data['squadra_casa']}: {scontri.get('vittorie_casa', 0)} vittorie")
            self.ui.labelProbabilitaVittoria_7.setText(f"{data['squadra_trasferta']}: {scontri.get('vittorie_trasferta', 0)} vittorie")
            self.ui.labelProbabilitaVittoria_8.setText(f"Pareggi: {scontri.get('pareggi', 0)}")
            
            # Ultime 5 partite tra le squadre
            ultime_5 = scontri.get('ultime_5', [])
            if len(ultime_5) >= 5:
                self.ui.labelUnder15_5.setText(ultime_5[0])
                self.ui.labelOver15_5.setText(ultime_5[1])
                self.ui.labelOver15_6.setText(ultime_5[2])
                self.ui.labelOver15_7.setText(ultime_5[3])
                self.ui.labelOver15_8.setText(ultime_5[4])
            
            # Analisi AI - Scommessa consigliata
            ai_analisi = data.get('ai_analisi', {})
            self.ui.labelPredizioni_6.setText("🎯 " + ai_analisi.get('scommessa_consigliata', 'N/A'))
            
        except Exception as e:
            print(f"Errore nell'aggiornamento UI: {e}")
    
    def load_prediction(self, squadra_casa, squadra_trasferta):
        """Carica le predizioni per le squadre specificate"""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        
        self.worker = PredictionWorker(squadra_casa, squadra_trasferta)
        self.worker.finished.connect(self.on_prediction_finished)
        self.worker.error.connect(self.on_prediction_error)
        self.worker.start()
        
        # Mostra un indicatore di caricamento
        self.ui.labelTestataEsitiDalRanking.setText("=== Caricamento Predizioni... ===")
    
    def on_prediction_finished(self, data):
        """Gestisce il completamento delle predizioni"""
        self.update_ui_with_data(data)
        self.ui.labelTestataEsitiDalRanking.setText("=== Esiti Dal Ranking ===")
    
    def on_prediction_error(self, error_msg):
        """Gestisce gli errori nelle predizioni"""
        QMessageBox.warning(self, "Errore", f"Errore nel calcolo delle predizioni:\n{error_msg}")
        self.ui.labelTestataEsitiDalRanking.setText("=== Errore nel Caricamento ===")
    
    def auto_update(self):
        """Aggiornamento automatico periodico"""
        # Implementa aggiornamenti automatici se necessario
        pass

def main():
    """Funzione principale"""
    app = QApplication(sys.argv)
    
    # Imposta il font dell'applicazione
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Crea e mostra la finestra principale
    window = PredizioniMainWindow()
    window.show()
    
    # Esempio: carica predizioni per Roma vs Udinese
    # window.load_prediction("Roma", "Udinese")
    
    # Avvia l'applicazione
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()