import os
import subprocess
import re
import urllib.request
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

from myPath import myPath, myFile
from TrasformaFileCsv import modificaNomiSquadre, sitiUfficialiSquadre, traduciMesi, traduciGiorniSettimana


class GestoreStagione:
    """
    Classe responsabile della gestione del rollover annuale del campionato:
    - Archiviazione della stagione passata in CampionatiPrecedenti.csv
    - Rilevamento delle 20 squadre del nuovo campionato da SoccerStats / web
    - Verifica e download degli scudetti mancanti in Immagini/Scudetti/
    - Aggiornamento di Csv/UrlSquadre.csv con i loghi e i siti ufficiali corretti
    """

    def __init__(self):
        self.csv_campionato = myFile.campionatoCorrente
        self.csv_storico = myFile.campionatiPrecedenti
        self.csv_url_squadre = myFile.urlSquadre
        self.dir_scudetti = myPath.scudetti

    def archivia_stagione_precedente(self, stagione_da_archiviare="2025/26") -> bool:
        """
        Converte le partite presenti in Campionato.csv e le accoda a CampionatiPrecedenti.csv
        se la stagione indicata non è già presente nell'archivio storico.
        """
        if not os.path.exists(self.csv_campionato):
            print(f"[ARCHIVIO] File {self.csv_campionato} non trovato. Nessuna archiviazione.")
            return False

        df_corrente = pd.read_csv(self.csv_campionato, sep=';')
        if df_corrente.empty:
            print("[ARCHIVIO] File Campionato.csv vuoto.")
            return False

        # Verifica storico esistente
        df_storico = pd.DataFrame()
        if os.path.exists(self.csv_storico):
            df_storico = pd.read_csv(self.csv_storico, sep=';')
            if 'Campionato' in df_storico.columns:
                stagioni_presenti = df_storico['Campionato'].unique().tolist()
                if stagione_da_archiviare in stagioni_presenti:
                    print(f"[ARCHIVIO] La stagione {stagione_da_archiviare} è già presente in {self.csv_storico}.")
                    return False

        print(f"[ARCHIVIO] Inizio archiviazione stagione {stagione_da_archiviare} in CampionatiPrecedenti.csv...")

        # Trasforma i dati nel formato: Campionato;GiornoSettimana;GiornoMese;Mese;Casa;Trasferta;GoalCasa;GoalTrasferta
        righe_archiviate = []
        for _, row in df_corrente.iterrows():
            data_str = str(row.get('Data', '')).strip()
            # Esempio: "Mon 25 Aug" -> split
            parti_data = data_str.split()
            
            giorno_sett = 'Dom'
            giorno_mese = '1'
            mese = 'Set'
            
            if len(parti_data) >= 3:
                giorno_sett_en = parti_data[0]
                giorno_mese = parti_data[1]
                mese_en = parti_data[2][:3]
                
                giorno_sett = traduciGiorniSettimana.get(giorno_sett_en, giorno_sett_en)
                mese = traduciMesi.get(mese_en, mese_en)
            elif len(parti_data) == 2:
                giorno_mese = parti_data[0]
                mese_en = parti_data[1][:3]
                mese = traduciMesi.get(mese_en, mese_en)

            casa = str(row.get('Casa', '')).strip()
            trasferta = str(row.get('Trasferta', '')).strip()
            
            # Uniforma nomi squadre
            casa = modificaNomiSquadre.get(casa, casa)
            trasferta = modificaNomiSquadre.get(trasferta, trasferta)
            
            goal_casa = row.get('GoalCasa', None)
            goal_trasferta = row.get('GoalTrasferta', None)

            # Salva solo se ci sono goal validi
            if pd.notna(goal_casa) and pd.notna(goal_trasferta) and str(goal_casa).strip().isdigit() and str(goal_trasferta).strip().isdigit():
                righe_archiviate.append({
                    'Campionato': stagione_da_archiviare,
                    'GiornoSettimana': giorno_sett,
                    'GiornoMese': int(giorno_mese),
                    'Mese': mese,
                    'Casa': casa,
                    'Trasferta': trasferta,
                    'GoalCasa': int(goal_casa),
                    'GoalTrasferta': int(goal_trasferta)
                })

        if not righe_archiviate:
            print("[ARCHIVIO] Nessuna partita valida trovata da archiviare.")
            return False

        df_nuove_archiviate = pd.DataFrame(righe_archiviate)

        if not df_storico.empty:
            df_storico_aggiornato = pd.concat([df_storico, df_nuove_archiviate], ignore_index=True)
        else:
            df_storico_aggiornato = df_nuove_archiviate

        # Crea backup storico prima di scrivere
        backup_storico = self.csv_storico.replace('.csv', '_backup.csv')
        if os.path.exists(self.csv_storico):
            import shutil
            shutil.copy2(self.csv_storico, backup_storico)

        df_storico_aggiornato.to_csv(self.csv_storico, sep=';', index=False)
        print(f"[ARCHIVIO] ✅ Archiviate {len(df_nuove_archiviate)} partite della stagione {stagione_da_archiviare} in {self.csv_storico}")
        
        # Reset di Campionato.csv per la nuova stagione
        df_vuoto = pd.DataFrame(columns=['Giornata', 'Data', 'Casa', 'GoalCasa', 'GoalTrasferta', 'Trasferta', 'Esiti'])
        df_vuoto.to_csv(self.csv_campionato, sep=';', index=False)
        print(f"[ARCHIVIO] 🆕 Reinizializzato {self.csv_campionato} per il nuovo campionato.")
        return True

    def estrai_squadre_campionato_online(self) -> list:
        """
        Estrae la lista delle 20 squadre del campionato di Serie A da SoccerStats tramite curl.
        In caso di problemi di connessione, utilizza la lista predefinita aggiornata.
        """
        url = "https://www.soccerstats.com/latest.asp?league=italy"
        cmd = ["curl.exe", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36", url]
        
        squadre = []
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=15)
            if res.returncode == 0 and res.stdout:
                soup = BeautifulSoup(res.stdout, 'lxml')
                
                # Cerchiamo le squadre nelle tabelle segmenti / classifica
                testo_completo = soup.text
                for nome_raw in sitiUfficialiSquadre.keys():
                    # Verifica presenza nel testo o con varianti inglesi
                    varianti = [nome_raw]
                    for eng, ita in modificaNomiSquadre.items():
                        if ita == nome_raw:
                            varianti.append(eng)
                    
                    for v in varianti:
                        if re.search(r'\b' + re.escape(v) + r'\b', testo_completo, re.IGNORECASE):
                            if nome_raw not in squadre:
                                squadre.append(nome_raw)
                            break
        except Exception as e:
            print(f"[SQUADRE] Errore durante l'estrazione squadre da SoccerStats: {e}")

        # Se abbiamo trovato esattamente o circa 20 squadre
        if len(squadre) >= 18:
            print(f"[SQUADRE] Trovate {len(squadre)} squadre online da SoccerStats.")
            return sorted(squadre)

        # Fallback lista ufficiale Serie A 2026/2027
        squadre_default_2026_27 = [
            'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Fiorentina',
            'Frosinone', 'Genoa', 'Inter', 'Juventus', 'Lazio',
            'Lecce', 'Milan', 'Monza', 'Napoli', 'Parma',
            'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Venezia'
        ]
        print(f"[SQUADRE] Utilizzo lista di 20 squadre Serie A 2026/27 (trovate {len(squadre_default_2026_27)}).")
        return sorted(squadre_default_2026_27)

    def verifica_e_scarica_scudetti(self, squadre: list):
        """
        Verifica per ogni squadra se l'immagine dello scudetto esiste in Immagini/Scudetti/{Squadra}.png.
        Se manca, ricerca e scarica automaticamente il logo trasparente PNG da Wikipedia.
        """
        os.makedirs(self.dir_scudetti, exist_ok=True)

        for squadra in squadre:
            path_scudetto = os.path.join(self.dir_scudetti, f"{squadra}.png")
            if not os.path.exists(path_scudetto) or os.path.getsize(path_scudetto) == 0:
                print(f"[SCUDETTI] Scudetto mancante per {squadra}. Ricerca e download in corso...")
                # Cerca su Wikipedia italiana
                query_name = squadra.replace(" ", "_")
                wiki_urls = [
                    f"https://it.wikipedia.org/wiki/{query_name}_Calcio",
                    f"https://it.wikipedia.org/wiki/{query_name}",
                    f"https://it.wikipedia.org/wiki/Associazione_Calcio_{query_name}",
                    f"https://it.wikipedia.org/wiki/Unione_Sportiva_{query_name}"
                ]
                
                downloaded = False
                for w_url in wiki_urls:
                    try:
                        cmd = ["curl.exe", "-s", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", w_url]
                        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=10)
                        if res.returncode == 0 and res.stdout:
                            # Cerca immagini di stemmi PNG
                            png_matches = re.findall(r'//upload\.wikimedia\.org/wikipedia/it/[^"]+\.png', res.stdout)
                            if not png_matches:
                                png_matches = re.findall(r'//upload\.wikimedia\.org/wikipedia/commons/[^"]+\.png', res.stdout)
                            
                            if png_matches:
                                # Filtra thumbnail con dimensione appropriata (almeno 250px o prima immagine utile)
                                target_img = None
                                for match in png_matches:
                                    if "logo" in match.lower() or "stemma" in match.lower() or squadra.lower() in match.lower():
                                        target_img = "https:" + match
                                        break
                                if not target_img:
                                    target_img = "https:" + png_matches[0]
                                
                                req = urllib.request.Request(target_img, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                                with urllib.request.urlopen(req, timeout=10) as resp, open(path_scudetto, 'wb') as out_file:
                                    out_file.write(resp.read())
                                
                                if os.path.exists(path_scudetto) and os.path.getsize(path_scudetto) > 500:
                                    print(f"[SCUDETTI] ✅ Scaricato scudetto per {squadra} ({os.path.getsize(path_scudetto)} bytes) in {path_scudetto}")
                                    downloaded = True
                                    break
                    except Exception as e:
                        continue

                if not downloaded:
                    print(f"[SCUDETTI] ⚠️ Impossibile scaricare automaticamente lo scudetto per {squadra}.")


    def aggiorna_url_squadre_csv(self, squadre: list):
        """
        Aggiorna Csv/UrlSquadre.csv con le 20 squadre correnti, i percorsi dei loghi e i siti ufficiali.
        """
        righe = []
        for squadra in sorted(squadre):
            url_sito = sitiUfficialiSquadre.get(squadra, f"https://www.google.com/search?q={squadra}+calcio+sito+ufficiale")
            logo_rel = f"Campionato di calcio 2026-27\\image\\Scudetti//{squadra}.png"
            righe.append({
                'Squadre': squadra,
                'InGioco': 1,
                'Logo': logo_rel,
                'Url': url_sito
            })

        df_url = pd.DataFrame(righe)
        df_url.to_csv(self.csv_url_squadre, sep=';', index=False)
        print(f"[URL SQUADRE] ✅ Aggiornato {self.csv_url_squadre} con {len(righe)} squadre.")

    def esegui_rollover_stagione_completo(self, stagione_passata="2025/26"):
        """
        Esegue il flusso completo di cambio stagione:
        1. Archivia Campionato.csv in CampionatiPrecedenti.csv
        2. Rileva le 20 squadre del nuovo campionato
        3. Verifica e scarica gli scudetti
        4. Aggiorna Csv/UrlSquadre.csv
        """
        print("=" * 60)
        print("🔄 AVVIO PROCEDURA ROLLOVER CAMBIO STAGIONE")
        print("=" * 60)

        # 1. Archiviazione storico
        self.archivia_stagione_precedente(stagione_passata)

        # 2. Estrazione nuove squadre
        squadre = self.estrai_squadre_campionato_online()

        # 3. Download scudetti mancanti
        self.verifica_e_scarica_scudetti(squadre)

        # 4. Aggiornamento urlSquadre.csv
        self.aggiorna_url_squadre_csv(squadre)

        print("=" * 60)
        print("✅ PROCEDURA ROLLOVER CAMBIO STAGIONE COMPLETATA")
        print("=" * 60)
        return squadre


if __name__ == "__main__":
    gestore = GestoreStagione()
    gestore.esegui_rollover_stagione_completo("2025/26")
