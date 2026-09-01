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
from EstrazioneDati import EstrazioneDati, ottieni_dataframe_cache

class MyTableModel(QAbstractTableModel):
    @catturaEccezione
    def __init__(self, data, headers):
        super().__init__()
        self._data = data
        self._headers = headers
        
        # Pre-calcolo colori di sfondo e testo per ogni riga in base alla posizione esatta
        self._row_bg = []
        self._row_fg = []
        num_righe = len(self._data)
        for r_idx in range(num_righe):
            bg, fg = self._determinaStileRiga(r_idx, num_righe)
            self._row_bg.append(bg)
            self._row_fg.append(fg)
    # end __init__()
    
    def _determinaStileRiga(self, row_idx: int, num_righe: int):
        """
        Determina colore di sfondo e colore del testo in base alla posizione esatta in classifica:
        - Pos 1-4 (row 0-3): Champions League (Blu #007BFF, Testo Bianco)
        - Pos 5-6 (row 4-5): Europa League (Giallo #FFD700, Testo Scuro)
        - Pos 7 (row 6): Conference League (Verde #28A745, Testo Bianco)
        - Pos 8-17 (row 7-16): Zona Neutra (Bianco #FFFFFF, Testo Scuro)
        - Ultime 3 (18-20): Zona Retrocessione (Rosso #DC3545, Testo Bianco)
        """
        pos = row_idx + 1
        
        # 1. Champions League (Prime 4 posizioni)
        if pos <= 4:
            return QBrush(QColor("#007BFF")), QBrush(QColor("#FFFFFF"))
        
        # 2. Europa League (Posizioni 5 e 6)
        elif pos in (5, 6):
            return QBrush(QColor("#FFD700")), QBrush(QColor("#212529"))
        
        # 3. Conference League (7ª posizione)
        elif pos == 7:
            return QBrush(QColor("#28A745")), QBrush(QColor("#FFFFFF"))
        
        # 5. Zona Retrocessione (Ultime 3 posizioni: 18, 19, 20)
        elif pos > max(0, num_righe - 3):
            return QBrush(QColor("#DC3545")), QBrush(QColor("#FFFFFF"))
        
        # 4. Zona Neutra (Posizioni 8 - 17)
        else:
            return QBrush(QColor("#FFFFFF")), QBrush(QColor("#212529"))
    
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
            elif 'PT' in self._headers:
                col_idx = self._headers.index('PT')
            else:
                col_idx = -1
            return int(str(self._data[row_idx][col_idx]).strip())
        except (ValueError, TypeError, IndexError):
            return 0

    @catturaEccezione
    def data(self, index, role=Qt.DisplayRole):  # type: ignore
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        col = index.column()
        
        # Valore della cella
        if role == Qt.DisplayRole:  # type: ignore
            return str(self._data[row][col]).strip()
            
        # Colorazione dinamica dello sfondo (pre-calcolata)
        elif role == Qt.BackgroundRole:  # type: ignore
            if row < len(self._row_bg):
                return self._row_bg[row]
            return QBrush(QColor("#FFFFFF"))
                
        # Contrasto colore del testo (pre-calcolato)
        elif role == Qt.ForegroundRole:  # type: ignore
            if row < len(self._row_fg):
                return self._row_fg[row]
            return QBrush(QColor("#212529"))

        # Gestione dell'allineamento del testo
        elif role == Qt.TextAlignmentRole:  # type: ignore
            if col < len(self._headers) and self._headers[col] == 'Squadra':
                return Qt.AlignLeft | Qt.AlignVCenter  # type: ignore
            else:
                return Qt.AlignCenter  # type: ignore
        
        return QVariant()
    # end data()
    
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
        if hasattr(self.ui, 'label'):
            self.ui.label.setText("Classifica campionato di calcio serie A 2026/27")
            
        # Configurazione Legenda Posizioni (allineata a tabella e regole Serie A)
        if hasattr(self.ui, 'label_2'):
            self.ui.label_2.setText("Champions League (1°-4° posto)")
            self.ui.label_2.setStyleSheet("background-color: #007BFF; color: #FFFFFF; font-weight: bold; border-radius: 4px; padding: 4px;")
            self.ui.label_2.setGeometry(150, 860, 340, 36)
            
        if hasattr(self.ui, 'label_3'):
            self.ui.label_3.setText("Europa League (5°-6° posto)")
            self.ui.label_3.setStyleSheet("background-color: #FFD700; color: #212529; font-weight: bold; border-radius: 4px; padding: 4px;")
            self.ui.label_3.setGeometry(530, 860, 340, 36)
            
        if hasattr(self.ui, 'label_4'):
            self.ui.label_4.setText("Conference League (7° posto)")
            self.ui.label_4.setStyleSheet("background-color: #28A745; color: #FFFFFF; font-weight: bold; border-radius: 4px; padding: 4px;")
            self.ui.label_4.setGeometry(150, 915, 340, 36)
            
        if hasattr(self.ui, 'label_7'):
            self.ui.label_7.setText("Zona Retrocessione (18°-20° posto)")
            self.ui.label_7.setStyleSheet("background-color: #DC3545; color: #FFFFFF; font-weight: bold; border-radius: 4px; padding: 4px;")
            self.ui.label_7.setGeometry(530, 915, 340, 36)
            
        # Nascondi voci non utilizzate dalla legenda
        if hasattr(self.ui, 'label_5'):
            self.ui.label_5.setVisible(False)
        if hasattr(self.ui, 'label_6'):
            self.ui.label_6.setVisible(False)

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
        self.df = ottieni_dataframe_cache(self.fileCampionato_csv)
        if self.df is None or self.df.empty:
            return 'Csv/Classifica.csv'
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
        
        # Mappa abbreviazioni per le intestazioni della tabella
        mappa_abbreviazioni = {
            'PartiteGiocate': 'PG',
            'Vittorie': 'V',
            'Pareggi': 'P',
            'Sconfitte': 'S',
            'GoalFatti': 'GF',
            'GoalSubiti': 'GS',
            'DifferenzaReti': 'DR'
        }
        headers = [mappa_abbreviazioni.get(h.strip(), h.strip()) for h in df.columns.tolist()]
        data = df.values.tolist()
        
        return headers, data
    # end importaDati()
    
    @catturaEccezione
    def determinaPosizioni(self, path):
        df = ottieni_dataframe_cache(path)
        if df is None:
            df = pd.read_csv(path, sep=';')
            
        # Pulisci i nomi delle colonne da eventuali spazi bianchi
        df.columns = df.columns.str.strip()
        
        # Ordinamento ufficiale Serie A: Punti, DifferenzaReti, GoalFatti
        if 'DifferenzaReti' in df.columns and 'GoalFatti' in df.columns and 'Punti' in df.columns:
            df = df.sort_values(['Punti', 'DifferenzaReti', 'GoalFatti'], ascending=[False, False, False]).reset_index(drop=True)
        elif 'Punti' in df.columns:
            df = df.sort_values('Punti', ascending=False).reset_index(drop=True)
            
        df['Pos'] = range(1, len(df) + 1)
        
        # Rispetta fedelmente l'ordine delle colonne del file Classifica.csv preceduto da Pos
        altre_colonne = [c for c in df.columns if c != 'Pos']
        df = df[['Pos'] + altre_colonne]
        
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
        
        for c in range(len(headers)):
            if headers[c] != 'Squadra':
                self.tabella.setColumnWidth(c, larghezza_numerica)
        
        # La colonna Squadra mantiene la larghezza automatica
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
    def close_window(self, event=None):
        """Nasconde la finestra per riapertura istantanea"""
        self.hide()
    # end close_window()
    
    def closeEvent(self, event):
        """Nasconde la finestra alla chiusura standard invece di distruggerla"""
        self.hide()
        event.ignore()

    @catturaEccezione
    def esci_applicazione(self, checked=False):
        """Funzione che chiude l'applicazione quando viene cliccato il pulsante"""
        self.hide()
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
    