import os
import sys
from datetime import datetime, date
import pandas as pd
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    import requests as standard_requests
    HAS_CURL_CFFI = False

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from UI.AggiornaCampionato_ui import Ui_AggiornaClassificaWindow
from myPath import myPath, myFile
from GestoreStagione import GestoreStagione
from TrasformaFileCsv import modificaNomiSquadre


class WorkerThread(QThread):
    # Segnali per comunicare con la GUI
    log_signal = pyqtSignal(str)          # Per i messaggi di log
    progress_signal = pyqtSignal(int)     # Per la progress bar
    counter_signal = pyqtSignal(int, int) # Per i contatori (giornata, partite totali)
    status_signal = pyqtSignal(str)       # Per lo stato
    finished_signal = pyqtSignal(int)     # Per il completamento
    
    def __init__(self):
        super().__init__()
        self.should_stop = False
        
    def stop(self):
        self.should_stop = True
        
    def run(self):
        self.status_signal.emit("Stato: Controllo cambio stagione e file esistenti...")
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Verifica cambio stagione e squadre...")
        
        # 1. Esecuzione procedura automatica cambio stagione e archiviazione storico
        try:
            gestore = GestoreStagione()
            gestore.esegui_rollover_stagione_completo(stagione_passata="2025/26")
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 📂 Controllo archivio e squadre completato con successo.")
        except Exception as e:
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Nota rollover: {e}")

        csv_path = myFile.campionatoCorrente
        csv_backup_path = csv_path.replace('.csv', '_backup.csv')
        existing_matches = []
        start_round = 1
        end_round = 38
        
        # 2. Controllo partite già salvate nella stagione corrente
        if os.path.exists(csv_path):
            try:
                import shutil
                shutil.copy2(csv_path, csv_backup_path)
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 💾 Creato backup: Campionato_backup.csv")
                
                existing_df = pd.read_csv(csv_path, sep=';')
                if not existing_df.empty and 'Giornata' in existing_df.columns:
                    existing_matches = existing_df.to_dict('records')
                    last_round = int(existing_df['Giornata'].max())
                    self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Ultima giornata registrata: {last_round}")
                    start_round = max(1, last_round)
                    self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Scarico dati a partire dalla giornata {start_round}")
                else:
                    self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 📄 File CSV vuoto, scarico dall'inizio")
            except Exception as e:
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Errore lettura CSV: {str(e)}")
                start_round = 1
        else:
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🆕 Inizializzazione nuovo campionato: estrazione 38 giornate")
        
        self.status_signal.emit("Stato: Estrazione in corso...")
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] Inizia l'estrazione delle partite dalle giornate {start_round} a {end_round}...")
        
        total_matches = 0
        new_matches = []
        
        for num in range(int(start_round), int(end_round) + 1):
            if self.should_stop:
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Estrazione interrotta dall'utente")
                self.status_signal.emit("Stato: Interrotto")
                return
                
            url = f"https://www.soccerstats.com/results.asp?league=italy&pmtype=round{num}"
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Estrazione partite per la giornata {num}...")
            
            partite = extract_matches(url, self.log_signal.emit)
            
            if partite:
                for partita in partite:
                    partita['Giornata'] = num
                    
                new_matches.extend(partite)
                total_matches += len(partite)
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Trovate {len(partite)} partite per la giornata {num}")
            else:
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Nessuna partita giocata per la giornata {num}.")
                self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ⏩ Stop ricerca: le prossime giornate non sono ancora state giocate.")
                self.progress_signal.emit(100)
                break
                
            progress = int(((num - start_round + 1) / (end_round - start_round + 1)) * 38)
            self.counter_signal.emit(num, len(existing_matches) + total_matches)
            self.progress_signal.emit(progress)
            
            self.msleep(400)
        
        # 3. Unione e deduplicazione delle partite
        if start_round > 1 and existing_matches and new_matches:
            tmp_df = pd.DataFrame(new_matches)
            existing_df = pd.DataFrame(existing_matches)
            
            tmp_df = self.cambiaNomiAlleSquadre(tmp_df)
            combined_df = pd.concat([existing_df, tmp_df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(subset=['Data', 'Casa', 'Trasferta'], keep='last')
            
            if 'Giornata' in combined_df.columns:
                combined_df = combined_df.sort_values(by=['Giornata', 'Data'])
                
            all_matches = combined_df.to_dict('records')
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Dati aggiornati e sincronizzati con le ultime partite.")
        elif start_round == 1 and new_matches:
            all_matches = new_matches
        else:
            all_matches = existing_matches + new_matches
            
        # 4. Salvataggio in Campionato.csv
        if all_matches:
            df = pd.DataFrame(all_matches)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            df = self.cambiaNomiAlleSquadre(df)
            
            # Assicura ordine colonne coerente
            colonne_ordine = ['Giornata', 'Data', 'Casa', 'GoalCasa', 'GoalTrasferta', 'Trasferta', 'Esiti']
            for col in colonne_ordine:
                if col not in df.columns:
                    df[col] = None
            df = df[colonne_ordine]
            
            df.to_csv(csv_path, sep=';', index=False)
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 💾 Salvate {len(all_matches)} partite in {csv_path}")
            
            # 5. Ricalcolo e aggiornamento automatico Classifica.csv
            self.aggiornaClassificaCsv(df)
        
        self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🎉 Sincronizzazione completata! Totale partite: {len(all_matches) if all_matches else 0}")
        self.status_signal.emit("Stato: Completato")
        self.finished_signal.emit(len(all_matches) if all_matches else 0)

    def cambiaNomiAlleSquadre(self, df: pd.DataFrame) -> pd.DataFrame:
        """Uniforma i nomi delle squadre secondo la mappa ufficiale"""
        if df.empty:
            return df
        for old_name, new_name in modificaNomiSquadre.items():
            if 'Casa' in df.columns:
                df['Casa'] = df['Casa'].replace(old_name, new_name)
            if 'Trasferta' in df.columns:
                df['Trasferta'] = df['Trasferta'].replace(old_name, new_name)
        return df

    def aggiornaClassificaCsv(self, df_partite: pd.DataFrame):
        """Calcola e salva Classifica.csv in base alle partite giocate"""
        try:
            squadre = pd.concat([df_partite['Casa'], df_partite['Trasferta']]).dropna().unique()
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

            for _, row in df_partite.iterrows():
                casa = row['Casa']
                trasferta = row['Trasferta']
                gc = row['GoalCasa']
                gt = row['GoalTrasferta']

                if pd.isna(gc) or pd.isna(gt) or not str(gc).strip().isdigit() or not str(gt).strip().isdigit():
                    continue

                gh = int(gc)
                ga = int(gt)

                classifica[casa]['PartiteGiocate'] += 1
                classifica[trasferta]['PartiteGiocate'] += 1
                classifica[casa]['GoalFatti'] += gh
                classifica[casa]['GoalSubiti'] += ga
                classifica[trasferta]['GoalFatti'] += ga
                classifica[trasferta]['GoalSubiti'] += gh
                classifica[casa]['DifferenzaReti'] = classifica[casa]['GoalFatti'] - classifica[casa]['GoalSubiti']
                classifica[trasferta]['DifferenzaReti'] = classifica[trasferta]['GoalFatti'] - classifica[trasferta]['GoalSubiti']

                if gh > ga:
                    classifica[casa]['Vittorie'] += 1
                    classifica[casa]['Punti'] += 3
                    classifica[trasferta]['Sconfitte'] += 1
                elif gh < ga:
                    classifica[trasferta]['Vittorie'] += 1
                    classifica[trasferta]['Punti'] += 3
                    classifica[casa]['Sconfitte'] += 1
                else:
                    classifica[casa]['Pareggi'] += 1
                    classifica[trasferta]['Pareggi'] += 1
                    classifica[casa]['Punti'] += 1
                    classifica[trasferta]['Punti'] += 1

            df_classifica = pd.DataFrame(list(classifica.values()))
            df_classifica = df_classifica.sort_values(['Punti', 'DifferenzaReti', 'GoalFatti'], ascending=[False, False, False])
            
            classifica_path = myFile.classifica
            df_classifica.to_csv(classifica_path, sep=';', index=False)
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] 🏆 Classifica aggiornata con successo.")
        except Exception as e:
            self.log_signal.emit(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Errore calcolo classifica: {e}")


class AggiornaClassificaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_AggiornaClassificaWindow()
        self.ui.setupUi(self)
        
        # Imposta icona dell'applicazione
        from PyQt5.QtGui import QIcon
        icon_path = os.path.join(myPath.icone, "iconaApp.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.worker = None
        self.inizia_estrazione()
        
    def inizia_estrazione(self):
        if self.worker and self.worker.isRunning():
            return
            
        self.ui.textBrowserLog.clear()
        self.ui.progressBar.setValue(0)
        self.ui.labelContatori.setText("Giornata: 0/38 | Partite: 0")
        
        self.worker = WorkerThread()
        self.worker.log_signal.connect(self.aggiungi_log)
        self.worker.progress_signal.connect(self.ui.progressBar.setValue)
        self.worker.counter_signal.connect(self.aggiorna_contatori)
        self.worker.status_signal.connect(self.ui.labelStato.setText)
        self.worker.finished_signal.connect(self.estrazione_completata)
        self.worker.start()
        
    def estrazione_completata(self, partite_totali):
        self.ui.statusbar.showMessage(f"Estrazione completata - {partite_totali} partite estratte")
        from PyQt5.QtCore import QTimer
        from PyQt5.QtWidgets import QApplication
        QTimer.singleShot(2500, lambda: QApplication.quit())
        
    def aggiungi_log(self, messaggio):
        self.ui.textBrowserLog.append(messaggio)
        scrollbar = self.ui.textBrowserLog.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
        
    def aggiorna_contatori(self, giornata, partite_totali):
        self.ui.labelContatori.setText(f"Giornata: {giornata}/38 | Partite: {partite_totali}")


def is_future_date_or_time(date_str):
    """Verifica se la data appartiene a partite future rispetto alla data di sistema"""
    try:
        today = date.today()
        date_part = date_str.split(' ', 1)[1] if ' ' in date_str else date_str
        
        months = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                  'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        month_str = date_part.split(' ')[1][:3]
        match_month = months.get(month_str, today.month)
        
        current_year = today.year
        if today.month <= 7 and match_month >= 8:
            match_year = current_year - 1
        elif today.month >= 8 and match_month <= 7:
            match_year = current_year + 1
        else:
            match_year = current_year
            
        full_date_str = f"{date_part} {match_year}"
        match_date = datetime.strptime(full_date_str, "%d %b %Y").date()
        return match_date > today
    except Exception:
        return False


def is_valid_score(home_goals, away_goals):
    """Verifica che la stringa rappresenti gol validi e non un orario"""
    try:
        home = int(home_goals.strip())
        away = int(away_goals.strip())
        if home > 20 or away > 59:
            return False
        return home <= 15 and away <= 15
    except Exception:
        return False


def extract_matches(url, log_callback=None):
    """Estrae le partite dal web tramite client curl_cffi / curl / requests"""
    if log_callback:
        log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Scaricando {url}...")

    html_content = ""
    
    # 1. Tentativo con curl_cffi (bypass Cloudflare)
    if HAS_CURL_CFFI:
        try:
            resp = cffi_requests.get(url, impersonate="chrome124", timeout=15)
            if resp.status_code == 200:
                html_content = resp.text
        except Exception as e:
            if log_callback:
                log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Nota curl_cffi: {e}")

    # 2. Fallback con curl.exe di sistema se necessario
    if not html_content or "btable" not in html_content:
        try:
            import subprocess
            cmd = ["curl.exe", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", url]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=15)
            if res.returncode == 0 and res.stdout:
                html_content = res.stdout
        except Exception:
            pass

    if not html_content:
        if log_callback:
            log_callback(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Errore di connessione durante lo scaricamento")
        return []

    soup = BeautifulSoup(html_content, 'lxml')
    tables = soup.find_all('table', {'id': 'btable'})
    if not tables:
        return []

    table_matches = tables[0]
    rows = table_matches.find_all('tr')
    matches = []

    for r in rows:
        cols = r.find_all('td')
        if len(cols) >= 4:
            row_data = [c.text.strip() for c in cols]
            if row_data[1] and (":" in row_data[2] or "-" in row_data[2]):
                date_str = row_data[0]
                home_team = row_data[1]
                score_str = row_data[2]
                away_team = row_data[3]

                if is_future_date_or_time(date_str):
                    continue

                home_goals, away_goals = None, None
                if ":" in score_str:
                    home_goals, away_goals = score_str.split(":")
                elif "-" in score_str and score_str != " - ":
                    home_goals, away_goals = score_str.split("-")

                if home_goals and away_goals:
                    if not is_valid_score(home_goals, away_goals):
                        continue

                segno = None
                if home_goals and away_goals:
                    try:
                        hg = int(home_goals.strip())
                        ag = int(away_goals.strip())
                        if hg > ag:
                            segno = '1'
                        elif hg < ag:
                            segno = '2'
                        else:
                            segno = 'X'
                    except ValueError:
                        pass

                match_info = {
                    'Giornata': None,
                    'Data': date_str,
                    'Casa': home_team,
                    'GoalCasa': home_goals.strip() if home_goals else None,
                    'GoalTrasferta': away_goals.strip() if away_goals else None,
                    'Trasferta': away_team,
                    'Esiti': segno if segno else score_str
                }
                matches.append(match_info)

    return matches


def main():
    app = QApplication(sys.argv)
    window = AggiornaClassificaWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()