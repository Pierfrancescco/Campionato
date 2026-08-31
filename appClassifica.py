from numpy import euler_gamma
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QTableView, QMainWindow, QAbstractItemView, QFrame, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, QUrl
from PyQt5.QtGui import QBrush, QColor, QFont, QDesktopServices

import sys
import webbrowser
import os
import time

# I miei import
from UI.Classifica import Ui_MainWindow
from ErrorManager import catturaEccezione
from EstrazioneDati import EstrazioneDati 

class MyTableModel(QAbstractTableModel):
    @catturaEccezione
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
    # end __init__()
    
    @catturaEccezione
    def rowCount(self, parent=None):
        return len(self._data)
    # end rowCount()
    
    @catturaEccezione
    def columnCount(self, parent=None):
        return len(self._headers)
    # end columnCount()
    
    @catturaEccezione
    def _getPuntiSquadra(self, row_idx: int) -> int:
        """Estrae i punti della squadra alla riga specificata"""
        try:
            if 'Punti' in self._headers:
                col_idx = self._headers.index('Punti')
            else:
                col_idx = -1
            return int(self._data[row_idx][col_idx])
        except (ValueError, TypeError, IndexError):
            return 0

    @catturaEccezione
    def data(self, index, role=Qt.DisplayRole):  # type: ignore
        if not index.isValid():
            return QVariant()
        
        # Valore della cella
        if role == Qt.DisplayRole:  # type: ignore
            return str(self._data[index.row()][index.column()])
            
        # Colorazione dinamica dello sfondo basata sulle soglie di punteggio
        elif role == Qt.BackgroundRole:  # type: ignore
            punti_squadra = self._getPuntiSquadra(index.row())
            soglie = self._calcolaSogliePunti()
            
            if soglie:
                # 1. Se punti >= soglia_Champions -> Colore Blu (#007BFF) [include tutti i pari merito al 4° posto]
                if punti_squadra >= soglie['soglia_Champions']:
                    return QBrush(QColor("#007BFF"))
                
                # 2. Se punti <= soglia_Retrocessione -> Colore Rosso (#DC3545) [include tutti i pari merito con le ultime 3]
                elif soglie['soglia_Retrocessione'] is not None and punti_squadra <= soglie['soglia_Retrocessione']:
                    return QBrush(QColor("#DC3545"))
                
                # 3. Se punti == soglia_Europa_League -> Colore Giallo (#FFD700)
                elif soglie['soglia_Europa_League'] is not None and punti_squadra == soglie['soglia_Europa_League']:
                    return QBrush(QColor("#FFD700"))
                
                # 4. Sfumatura verde per Conference League
                elif soglie['soglia_Conference_League'] is not None and punti_squadra == soglie['soglia_Conference_League'] and index.row() in (5, 6):
                    return QBrush(QColor("#28A745"))
                
                # 5. Per i punteggi intermedi -> Bianco (#FFFFFF)
                else:
                    return QBrush(QColor("#FFFFFF"))
            else:
                return QBrush(QColor("#FFFFFF"))
                
        # Contrasto colore del testo per massima leggibilità
        elif role == Qt.ForegroundRole:  # type: ignore
            punti_squadra = self._getPuntiSquadra(index.row())
            soglie = self._calcolaSogliePunti()
            
            if soglie:
                # Testo bianco su sfondi scuri (Blu Champions, Rosso Retrocessione, Verde Conference)
                if punti_squadra >= soglie['soglia_Champions']:
                    return QBrush(QColor("#FFFFFF"))
                elif soglie['soglia_Retrocessione'] is not None and punti_squadra <= soglie['soglia_Retrocessione']:
                    return QBrush(QColor("#FFFFFF"))
                elif soglie['soglia_Conference_League'] is not None and punti_squadra == soglie['soglia_Conference_League'] and index.row() in (5, 6):
                    return QBrush(QColor("#FFFFFF"))
                else:
                    return QBrush(QColor("#212529"))  # Testo scuro su Giallo e Bianco
            return QBrush(QColor("#212529"))

        # Gestione dell'allineamento del testo
        elif role == Qt.TextAlignmentRole:  # type: ignore
            # Colonne da centrare (usando gli indici delle colonne)
            colonne_centrate = [0, 2, 3, 4, 5, 6, 7, 8, 9]  # Pos, PG, V, P, S, GF, GS, DR, Punti
            if index.column() in colonne_centrate:
                return Qt.AlignCenter  # type: ignore
            else:
                return Qt.AlignLeft | Qt.AlignVCenter  # type: ignore
        
        return QVariant()
    # end data()
    
    @catturaEccezione
    def _calcolaSogliePunti(self):
        """
        Calcola le soglie di punteggio dinamiche basate sulla classifica ordinata:
        - soglia_Champions: punti della squadra al 4° posto (indice 3)
        - soglia_Europa_League: punti della prima squadra sotto la zona Champions
        - soglia_Conference_League: punti della squadra in zona Conference
        - soglia_Retrocessione: punti della 18ª squadra (terz'ultima)
        """
        if not self._data or len(self._data) == 0:
            return None
        
        num_squadre = len(self._data)
        
        # Punti al 4° posto (indice 3)
        idx_champions = min(3, num_squadre - 1)
        soglia_champions = self._getPuntiSquadra(idx_champions)
        
        # Europa League: prima squadra con punteggio strettamente inferiore a soglia_champions
        soglia_europa = None
        for r_idx in range(idx_champions + 1, num_squadre):
            pts = self._getPuntiSquadra(r_idx)
            if pts < soglia_champions:
                soglia_europa = pts
                break
                
        # Conference League: prima squadra con punteggio strettamente inferiore a soglia_europa
        soglia_conference = None
        if soglia_europa is not None:
            for r_idx in range(num_squadre):
                pts = self._getPuntiSquadra(r_idx)
                if pts < soglia_europa:
                    soglia_conference = pts
                    break
        
        # Retrocessione: punti della 18ª squadra (terz'ultima)
        idx_retro = max(0, num_squadre - 3)
        soglia_retrocessione = self._getPuntiSquadra(idx_retro)
        
        return {
            'soglia_Champions': soglia_champions,
            'soglia_Europa_League': soglia_europa,
            'soglia_Conference_League': soglia_conference,
            'soglia_Retrocessione': soglia_retrocessione
        }
    # end _calcolaSogliePunti()
    
    @catturaEccezione
    def setData(self, index, value, role=Qt.EditRole):  # type: ignore
        if not index.isValid():
            return False
        # end if

        if index.row() >= len(self._data) or index.column() >= len(self._headers):
            return False
        # end if

        self._data[index.row()][index.column()] = value
        self.dataChanged.emit(index, index, [role])
        return True
    # end setData()    

    @catturaEccezione
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:  # type: ignore
            if orientation == Qt.Horizontal:  # type: ignore  # type: ignore
                return self._headers[section]  # Restituisce l'intestazione della colonna
            else:
                return str(section + 1)  # Restituisce il numero della riga
        # end if
        return QVariant()
    # end headerData()
# end MyTableModel


class AppClassifica(QMainWindow):
    @catturaEccezione
    def __init__(self):
        super().__init__()
        self.fileCampionato_csv = f'Csv\\Campionato.csv'
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.tabella = self.ui.tableView
        self.resize(self.dimensioniFinestra()[0], self.dimensioniFinestra()[1])
        self.setWindowTitle("Classifica Campionato di calcio Serie A 2026/27")

        self.df = None
        self.fileClassifica = self.creaClassifica()

        self.parametriTabella()
        
        self.setStyleSheet("""
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
        
        # Collegamento del pulsante alla funzione di uscita
        self.ui.pushButton.setToolTip("Esci")
        self.ui.pushButton.clicked.connect(self.close_window)
        
        # Collegamento dei pulsanti Sky Sport (ora nel Designer)
        self.collegaPulsantiSky()
        
        # self.creaTabella()
        # Percorso assoluto del file CSV nella stessa directory di questo script
        

        
        
        self.caricaDati(self.fileClassifica)
    # end i__init__()
    
    @catturaEccezione
    def creaClassifica(self):
        # estrattore = EstrazioneDati(self.fileCampionato_xlsm)
        # self.df = estrattore.dataFrame()
        self.df = pd.read_csv(self.fileCampionato_csv, sep=';')
        # Calcola la classifica dal DataFrame delle partite con le nuove colonne
        df = self.df.copy()
        squadre = pd.concat([df['Casa'], df['Trasferta']]).unique() # Ottiene tutte le squadre uniche da entrambe le colonne
        classifica = {squadra: {
            'Squadra': squadra,
            'Punti': 0,
            'PartiteGiocate': 0,
            'Vittorie': 0,
            'Pareggi': 0,
            'Sconfitte': 0,
            'GoalFatti': 0,
            'GoalSubiti': 0,
            'DifferenzaReti': 0
        } for squadra in squadre}

        for _, row in df.iterrows():
            Casa = row['Casa']
            Trasferta = row['Trasferta']
            gh = int(row['GoalCasa']) # Goal fatti in casa
            ga = int(row['GoalTrasferta']) # Goal fatti in trasferta

            # Aggiorna partite giocate
            classifica[Casa]['PartiteGiocate'] += 1
            classifica[Trasferta]['PartiteGiocate'] += 1

            # Aggiorna goal fatti/subiti
            classifica[Casa]['GoalFatti'] += gh
            classifica[Casa]['GoalSubiti'] += ga
            classifica[Trasferta]['GoalFatti'] += ga
            classifica[Trasferta]['GoalSubiti'] += gh

            # Aggiorna differenza reti
            classifica[Casa]['DifferenzaReti'] = classifica[Casa]['GoalFatti'] - classifica[Casa]['GoalSubiti']
            classifica[Trasferta]['DifferenzaReti'] = classifica[Trasferta]['GoalFatti'] - classifica[Trasferta]['GoalSubiti']

            # Risultato partita
            if gh > ga:
                # Casa vince
                classifica[Casa]['Vittorie'] += 1
                classifica[Casa]['Punti'] += 3
                classifica[Trasferta]['Sconfitte'] += 1
            elif gh < ga:
                # Trasferta vince
                classifica[Trasferta]['Vittorie'] += 1
                classifica[Trasferta]['Punti'] += 3
                classifica[Casa]['Sconfitte'] += 1
            else:
                # Pareggio
                classifica[Casa]['Pareggi'] += 1
                classifica[Trasferta]['Pareggi'] += 1
                classifica[Casa]['Punti'] += 1
                classifica[Trasferta]['Punti'] += 1

        # Costruisci DataFrame classifica
        df_classifica = pd.DataFrame(list(classifica.values()))
        # Ordina per punti, differenza reti, goal fatti
        df_classifica = df_classifica.sort_values(['Punti', 'DifferenzaReti', 'GoalFatti'], ascending=[False, False, False])

        # Salva su CSV
        file_csv = 'Csv/Classifica.csv'
        df_classifica.to_csv(file_csv, sep=';', index=False)
        return file_csv
        
        
    
    @catturaEccezione
    def dimensioniFinestra(self):
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            screen_width = geometry.width()
            screen_height = geometry.height()
        else:
            # Fallback per valori predefiniti
            screen_width = 1920
            screen_height = 1080
        window_height = screen_height - 40  # 40px è un'approssimazione dell'altezza della barra
        # Assicuriamoci che ci sia spazio sufficiente per il frame Sky
        min_width = 1500  # Larghezza minima per contenere tabella + frame Sky
        return max(screen_width, min_width), window_height
    # end dimensioniFinestra()
    
    @catturaEccezione
    def parametriTabella(self): 
        self.tabella.setFont(self.fontTable())
        self.tabella.setShowGrid(False)
        
        # Impostazione per selezionare l'intera riga quando si clicca su una cella
        self.tabella.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Font più grande per l'header
        header_font = QFont()
        header_font.setPointSize(16)  # Font più grande per l'header
        header_font.setBold(True)
        
        # Configurazione header orizzontale
        horizontal_header = self.tabella.horizontalHeader()
        if horizontal_header:
            horizontal_header.setFont(header_font)
            horizontal_header.setStyleSheet("QHeaderView::section { border: none; }")  # Rimuove i separatori
        
        # Nasconde l'header verticale (numeri delle righe a sinistra)
        vertical_header = self.tabella.verticalHeader()
        if vertical_header:
            vertical_header.setVisible(False)
        
        # Ridimensionamento automatico delle colonne
        self.tabella.resizeColumnsToContents()  # Adatta la larghezza al contenuto
        self.tabella.resizeRowsToContents()     # Adatta l'altezza al contenuto
    # end parametriTabella()
    
    @catturaEccezione
    def importaDati(self, path):
        df = self.determinaPosizioni(path)
        headers = df.columns.tolist()
        for header in headers:
            if header == 'PartiteGiocate':
                headers[headers.index(header)] = 'PG'
            elif header == 'Vittorie':
                headers[headers.index(header)] = 'V'
            elif header == 'Pareggi':
                headers[headers.index(header)] = 'P'
            elif header == 'Sconfitte':
                headers[headers.index(header)] = 'S'
            elif header == 'GoalFatti':
                headers[headers.index(header)] = 'GF'
            elif header == 'GoalSubiti':
                headers[headers.index(header)] = 'GS'
            elif header == 'DifferenzaReti':
                headers[headers.index(header)] = 'DR'
            # end if
        # end for
        data = df.values.tolist()
        
        return headers, data
    # end importaDati()
    
    @catturaEccezione
    def determinaPosizioni(self, path):
        df = pd.read_csv(path, sep=';')
        # Ordinamento ufficiale Serie A: Punti, DifferenzaReti, GoalFatti
        if 'DifferenzaReti' in df.columns and 'GoalFatti' in df.columns:
            df = df.sort_values(['Punti', 'DifferenzaReti', 'GoalFatti'], ascending=[False, False, False]).reset_index(drop=True)
        else:
            df = df.sort_values('Punti', ascending=False).reset_index(drop=True)
            
        df['Pos'] = range(1, len(df) + 1)
        
        # Ordine colonne standard per la visualizzazione
        colonne_ordine = ['Pos', 'Squadra', 'PartiteGiocate', 'Vittorie', 'Pareggi', 'Sconfitte', 'GoalFatti', 'GoalSubiti', 'DifferenzaReti', 'Punti']
        colonne_presenti = [c for c in colonne_ordine if c in df.columns]
        # Inserisci eventuali altre colonne presenti
        for c in df.columns:
            if c not in colonne_presenti:
                colonne_presenti.append(c)
        df = df[colonne_presenti]
        
        return df
    # end determinaPosizioni()

    @catturaEccezione
    def caricaDati(self, path):
        headers, data = self.importaDati(path)
        self.model = MyTableModel(data, headers)
        self.tabella.setModel(self.model)
        
        # Ridimensiona di nuovo dopo aver caricato i dati
        self.tabella.resizeColumnsToContents()
        self.tabella.resizeRowsToContents()
        
        # Imposta larghezze uniformi per le colonne numeriche
        larghezza_numerica = 100  # Larghezza standard per colonne numeriche
        
        self.tabella.setColumnWidth(0, larghezza_numerica)    # Pos
        self.tabella.setColumnWidth(2, larghezza_numerica)    # PG  
        self.tabella.setColumnWidth(3, larghezza_numerica)    # V
        self.tabella.setColumnWidth(4, larghezza_numerica)    # P
        self.tabella.setColumnWidth(5, larghezza_numerica)    # S
        self.tabella.setColumnWidth(6, larghezza_numerica)    # GF
        self.tabella.setColumnWidth(7, larghezza_numerica)    # GS
        self.tabella.setColumnWidth(8, larghezza_numerica)    # DR
        self.tabella.setColumnWidth(9, larghezza_numerica)    # Punti
        
        # La colonna Squadra (indice 1) mantiene la larghezza automatica
    # end caricaDati()

    @catturaEccezione
    def fontTable(self):
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(True)
        return font
    # end fontTable()
    
    @catturaEccezione
    def collegaPulsantiSky(self):
        """Collega i pulsanti Sky Sport ai relativi link (pulsanti nel tuo Designer)"""
        # Mappa dei pulsanti e relativi URL (secondo il tuo layout)
        pulsanti_sky = {
            'sky_btn_classifica': "https://sport.sky.it/calcio/serie-a/classifica",
            'sky_btn_risultati': "https://sport.sky.it/calcio/serie-a/calendario-risultati",
            'sky_btn_news': "https://sport.sky.it/calcio/serie-a",
            'sky_btn_formazioni': "https://sport.sky.it/calcio/serie-a/probabili-formazioni",
            'sky_btn_squadre': "https://sport.sky.it/calcio/serie-a/2025/06/01/serie-a-2025-2026-squadre#00",
            'sky_btn_marcatori': "https://sport.sky.it/calcio/serie-a/classifica-marcatori",
            'sky_btn_programma': "https://www.goal.com/it/notizie/calendario-serie-a-dove-vedere-le-partite-su-sky-dazn/15xq0ezenmop915t22cio9f74h",
            'sky_btn_partite': "https://programmi.sky.it/sport/calcio/serie-a",
            'sky_btn_app': "https://www.sky.it/tv/sky-go",
            'sky_btn_highlights': "https://sport.sky.it/calcio/serie-a/highlights/ultima-giornata"
        }
        
        # Collega ogni pulsante al suo URL
        for nome_pulsante, url in pulsanti_sky.items():
            pulsante = getattr(self.ui, nome_pulsante, None)
            if pulsante:
                pulsante.clicked.connect(lambda checked, link=url: self.apri_link_sky(link))
            else:
                print(f"Attenzione: Pulsante {nome_pulsante} non trovato nell'UI")
            # end if
        # end for
    
    @catturaEccezione
    def apri_link_sky(self, url):
        """Apre il link di Sky Sport nel browser predefinito"""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Errore nell'apertura del link: {e}")
    # end apri_link_sky()
    
    @catturaEccezione
    def close_window(self, event = None):
        """Wrapper per il metodo close che non restituisce valori"""
        self.close()
    # end close_window()
    # end apri_link_sky()
    
    @catturaEccezione
    def esci_applicazione(self, checked=False):
        """Funzione che chiude l'applicazione quando viene cliccato il pulsante"""
        self.close()
    # end esci_applicazione()
# end App

@catturaEccezione
def main():
    
    
    # 🕒 INIZIO MISURAZIONE TEMPO (Riga 292)
    tempo_inizio = time.time()
    
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
    appClassifica = AppClassifica()
    appClassifica.show()
    
    # 🕒 FINE MISURAZIONE TEMPO (Riga 296)
    tempo_fine = time.time()
    tempo_esecuzione = tempo_fine - tempo_inizio
    
    print(f"⏱️  Tempo di esecuzione (righe 292-296): {tempo_esecuzione:.4f} secondi")
    print(f"⏱️  Tempo di esecuzione (righe 292-296): {tempo_esecuzione*1000:.2f} millisecondi")
    
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()
    