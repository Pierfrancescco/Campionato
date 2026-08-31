import os
import stat
import pandas as pd 
from pathlib import Path
import numpy as np

# I miei moduli
from ErrorManager import catturaEccezione
from TrasformaFileCsv import *
from TrasformaFileCsv import *
from myPath import myPath, myFile


class MetaDatiDf:
    @catturaEccezione
    def __init__(self, file_xlsm: str):
        import os
        self.file_xlsm = file_xlsm
        # print(f"[DEBUG] Percorso file ricevuto: {self.file_xlsm}")
        if not isinstance(self.file_xlsm, str) or not self.file_xlsm:
            print("[ERRORE] Il percorso del file deve essere una stringa non vuota.")
            self.df = None
            self.file_csv = None
            return
        if not os.path.exists(self.file_xlsm):
            print(f"[ERRORE] File non trovato: {self.file_xlsm}")
            self.df = None
            self.file_csv = None
            return
        if not self.file_xlsm.lower().endswith(('.xls', '.xlsx', '.xlsm','.csv')):
            print(f"[ERRORE] Estensione file non supportata: {self.file_xlsm}")
            self.df = None
            self.file_csv = None
            return
        try:
            if self.file_xlsm.lower().endswith('.csv'):
                self.file_csv = self.file_xlsm  
                self.df = pd.read_csv(f'{self.file_csv}', sep=';')
                return
            else:
               
                sheets_dict = pd.read_excel(self.file_xlsm, sheet_name=None)# Unisci tutti i DataFrame in uno solo
                self.df = pd.concat(sheets_dict.values(), ignore_index=True)
        except Exception as e:
            print(f"[ERRORE] Errore durante il caricamento del file Excel: {e}")
            self.df = None
            self.file_csv = None
            return
        
        # Salva anche il percorso del file csv generato
        # Ottieni il nome base del file senza percorso e cambia estensione in .csv
        base_name = os.path.splitext(os.path.basename(self.file_xlsm))[0]
        self.file_csv = f"{base_name}.csv"
        self.df.to_csv(f'Csv\\{self.file_csv}', sep=';', index=False)
        EstrazioneDati.trasformaDataframe(self.file_csv)
    # end __init__()
    @catturaEccezione
    def creaMetaDati(self):
        """
        Crea un dizionario completo con tutti i metadati del DataFrame
        e salva un report dettagliato in formato CSV e JSON
        """
        if self.df is None:
            print("[ERRORE] DataFrame non disponibile. Impossibile creare metadati.")
            return
        
        from datetime import datetime
        
        # Metadati strutturali
        self.meta_dati = {
            # Informazioni sulla struttura
            'forma': {
                'num_righe': self.df.shape[0],
                'num_colonne': self.df.shape[1],
                'dimensioni_totali': self.df.size,
                'numero_dimensioni': self.df.ndim
            },
            
            # Informazioni sulle colonne
            'colonne': {
                'nomi_colonne': self.df.columns.tolist(),
                'tipi_dati': self.df.dtypes.apply(lambda x: x.name).to_dict(),
                'valori_unici_per_colonna': self.df.nunique().to_dict()
            },
            
            # Qualità dei dati
            'qualita_dati': {
                'valori_mancanti_per_colonna': self.df.isnull().sum().to_dict(),
                'percentuale_valori_mancanti': (self.df.isnull().sum() / len(self.df) * 100).round(2).to_dict(),
                'numero_righe_duplicate': self.df.duplicated().sum(),
                'percentuale_righe_duplicate': round(self.df.duplicated().sum() / len(self.df) * 100, 2)
            },
            
            # Uso della memoria
            'memoria': {
                'memoria_per_colonna_bytes': self.df.memory_usage(deep=True).to_dict(),
                'memoria_totale_mb': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2)
            },
            
            # Metadati personalizzati
            'metadati_file': {
                'percorso_file': self.file_xlsm,
                'data_elaborazione': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'responsabile': 'Sistema automatico',
                'versione': '1.0'
            }
        }
        
        # Aggiungi statistiche descrittive per colonne numeriche
        if self.df is not None:
            colonne_numeriche = self.df.select_dtypes(include=[np.number]).columns.tolist()
            if colonne_numeriche:
                self.meta_dati['statistiche_numeriche'] = {}
            for col in colonne_numeriche:
                if self.df is not None:
                    self.meta_dati['statistiche_numeriche'][col] = {
                        'media': round(self.df[col].mean(), 2),
                        'mediana': round(self.df[col].median(), 2),
                        'deviazione_standard': round(self.df[col].std(), 2),
                        'minimo': self.df[col].min(),
                        'massimo': self.df[col].max(),
                        'quartile_25': round(self.df[col].quantile(0.25), 2),
                        'quartile_75': round(self.df[col].quantile(0.75), 2)
                    }
        
        # Aggiungi informazioni per colonne categoriche
        if self.df is not None:
            colonne_categoriche = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
            if colonne_categoriche:
                self.meta_dati['statistiche_categoriche'] = {}
                for col in colonne_categoriche:
                    self.meta_dati['statistiche_categoriche'][col] = {
                        'valori_piu_frequenti': self.df[col].value_counts().head(5).to_dict(),
                        'numero_categorie': self.df[col].nunique()
                    }
        
        return self.meta_dati
    # end creaMetaDati()
    
    @catturaEccezione
    def salvaMetaDati(self, formato='csv'):
        """
        Salva i metadati in formato CSV o JSON
        
        Args:
            formato (str): 'csv', 'json' o 'entrambi'
        """
        import json
        import os
        if not hasattr(self, 'meta_dati'):
            self.creaMetaDati()
        # Usa il nome base del file xlsm per generare i metadati
        base_name = os.path.splitext(os.path.basename(self.file_xlsm))[0]
        base_path = f"{base_name}_metadati"
        if formato in ['csv', 'entrambi']:
            # Crea un DataFrame per il report CSV
            report_data = []
            # Informazioni generali
            report_data.extend([
                ['STRUTTURA DEL DATASET', ''],
                ['Numero righe', self.meta_dati['forma']['num_righe']],
                ['Numero colonne', self.meta_dati['forma']['num_colonne']],
                ['Dimensioni totali', self.meta_dati['forma']['dimensioni_totali']],
                ['Memoria totale (MB)', self.meta_dati['memoria']['memoria_totale_mb']],
                ['', ''],
                ['QUALITÀ DEI DATI', ''],
                ['Righe duplicate', self.meta_dati['qualita_dati']['numero_righe_duplicate']],
                ['% Righe duplicate', f"{self.meta_dati['qualita_dati']['percentuale_righe_duplicate']}%"],
                ['', '']
            ])
            # Informazioni per colonna
            report_data.append(['INFORMAZIONI PER COLONNA', ''])
            for col in self.meta_dati['colonne']['nomi_colonne']:
                tipo = self.meta_dati['colonne']['tipi_dati'][col]
                valori_unici = self.meta_dati['colonne']['valori_unici_per_colonna'][col]
                valori_mancanti = self.meta_dati['qualita_dati']['valori_mancanti_per_colonna'][col]
                perc_mancanti = self.meta_dati['qualita_dati']['percentuale_valori_mancanti'][col]
                report_data.extend([
                    [f"Colonna: {col}", ''],
                    ['  Tipo dato', tipo],
                    ['  Valori unici', valori_unici],
                    ['  Valori mancanti', f"{valori_mancanti} ({perc_mancanti}%)"]
                ])
            # Salva CSV
            meta_df = pd.DataFrame(report_data, columns=['Informazione', 'Valore'])
            csv_path = f"{base_path}.csv"
            meta_df.to_csv(f'Csv\\{csv_path}', index=False)
            print(f"Metadati CSV salvati in: {csv_path}")
        if formato in ['json', 'entrambi']:
            # Salva JSON
            json_path = f"{base_path}.json"
            with open(f'Json\\{json_path}', 'w', encoding='utf-8') as f:
                json.dump(self.meta_dati, f, indent=2, ensure_ascii=False, default=str)
            print(f"Metadati JSON salvati in: {json_path}")
    # end salvaMetaDati()
    
    @catturaEccezione
    def stampaReportMetaDati(self):
        """
        Stampa un report completo dei metadati a console
        """
        if not hasattr(self, 'meta_dati'):
            self.creaMetaDati()
        
        print("=" * 60)
        print("REPORT METADATI DATASET")
        print("=" * 60)
        
        # Informazioni generali
        print(f"\n📊 STRUTTURA DATASET:")
        print(f"   Righe: {self.meta_dati['forma']['num_righe']:,}")
        print(f"   Colonne: {self.meta_dati['forma']['num_colonne']}")
        print(f"   Dimensioni totali: {self.meta_dati['forma']['dimensioni_totali']:,}")
        print(f"   Memoria utilizzata: {self.meta_dati['memoria']['memoria_totale_mb']} MB")
        
        # Qualità dati
        print(f"\n🔍 QUALITÀ DATI:")
        print(f"   Righe duplicate: {self.meta_dati['qualita_dati']['numero_righe_duplicate']} ({self.meta_dati['qualita_dati']['percentuale_righe_duplicate']}%)")
        
        totale_valori_mancanti = sum(self.meta_dati['qualita_dati']['valori_mancanti_per_colonna'].values())
        print(f"   Valori mancanti totali: {totale_valori_mancanti}")
        
        # Informazioni colonne
        print(f"\n📋 COLONNE ({len(self.meta_dati['colonne']['nomi_colonne'])}):")
        for col in self.meta_dati['colonne']['nomi_colonne']:
            tipo = self.meta_dati['colonne']['tipi_dati'][col]
            valori_unici = self.meta_dati['colonne']['valori_unici_per_colonna'][col]
            valori_mancanti = self.meta_dati['qualita_dati']['valori_mancanti_per_colonna'][col]
            perc_mancanti = self.meta_dati['qualita_dati']['percentuale_valori_mancanti'][col]
            
            print(f"   • {col} ({tipo}): {valori_unici} valori unici, {valori_mancanti} mancanti ({perc_mancanti}%)")
        
        # Statistiche numeriche (se presenti)
        if 'statistiche_numeriche' in self.meta_dati:
            print(f"\n📈 STATISTICHE COLONNE NUMERICHE:")
            for col, stats in self.meta_dati['statistiche_numeriche'].items():
                print(f"   {col}:")
                print(f"     Media: {stats['media']}, Mediana: {stats['mediana']}")
                print(f"     Min: {stats['minimo']}, Max: {stats['massimo']}")
                print(f"     Std Dev: {stats['deviazione_standard']}")
        
        print("=" * 60)
    # end stampaReportMetaDati()
# end MetaDatiDf

class UltimiCinquePartite:
    @catturaEccezione
    def __init__(self, df: pd.DataFrame ):
        self.df = df

    # end __init__()
    
    @catturaEccezione
    def estraiUltimeCinquePartite(self, squadra: str) -> list:
        
        # aggiunge la colonna Esiti a DataFrame
        self.aggiungiColonnaEsiti()

        # Filtra le partite della squadra (sia in casa che in trasferta)
        partite_squadra = self.df.query(f'Casa == "{squadra}" or Trasferta == "{squadra}"')

        # Prendi le ultime cinque partite
        ultimeCinquePartite = partite_squadra['Esiti'].tail(5).tolist()
        
        return ultimeCinquePartite
    # end estraiUltimeCinquePartite()
    
    @catturaEccezione
    def estraiUltimeCinquePartiteInCasa(self, squadra: str) -> list:
       # aggiunge la colonna Esiti a DataFrame se necessario
        self.aggiungiColonnaEsiti()

        # Filtra le partite della squadra in casa
        partite_squadra = self.df.query(f'Casa == "{squadra}"')

        # Prendi le ultime cinque partite
        ultimeCinquePartiteInCasa = partite_squadra['Esiti'].tail(5).tolist()
        
        return ultimeCinquePartiteInCasa
    # end estraiUltimeCinquePartiteInCasa()
    
    @catturaEccezione
    def estraiUltimeCinquePartiteInTrasferta(self, squadra: str) -> list:
        # aggiunge la colonna Esiti a DataFrame se necessario
        self.aggiungiColonnaEsiti()

        # Filtra le partite della squadra in trasferta
        partite_squadra = self.df.query(f'Trasferta == "{squadra}"')

        # Prendi le ultime cinque partite
        ultimeCinquePartiteInTrasferta = partite_squadra['Esiti'].tail(5).tolist()

        return ultimeCinquePartiteInTrasferta
    # end estraiUltimeCinquePartiteInTrasferta()

    @catturaEccezione
    def aggiungiColonnaEsiti(self) -> None:
        if self.df is not None and 'Esiti' not in self.df.columns:
            # Nota: qui serve il file_xlsm per creare EstrazioneDati, ma non è disponibile
            # Per ora aggiungiamo una colonna vuota o usiamo un valore di default
            self.df['Esiti'] = 'N/A'  # Placeholder temporaneo
        # end if
    # end aggiugiColonnaEsiti()


class EstrazioneDati:
    
    '''Classe per l'estrazione di informazioni derivate dal DataFrame
       contenente i dati del campionato'''
    @catturaEccezione
    def __init__(self, file):
        print(f"[DEBUG - Estrazione dati ] Inizializzazione EstrazioneDati con file: {file}")
        if file is None:
            raise ValueError("Il percorso del file non può essere None")
        estensione = os.path.splitext(file)[1].lower() # Verifica l'estensione del file
        
        print(f"[DEBUG - Estrazione dati ] Estensione file: {estensione}")
        if estensione in ['.xls', '.xlsx', '.xlsm']:
            self.file = self.assegnaNomeFile(file) # Assegna il nome del file
            # carico il DataFrame
            self.df = self.caricaDataFrame(self.file)
        elif estensione == '.csv':
            self.file = file
            # carico il DataFrame da csv
            self.caricaDataFrameDaCsv(self.file)    
        else:
            raise ValueError(f"Estensione file non supportata: {estensione}")
        
        # inizializzo i metadati
        self.md = MetaDatiDf(self.file)
        # inizializzo la lista delle squadre
        self.listaSquadre = []
    # end __init__()
    
    @catturaEccezione
    def controllaDataFrame(self):
        # Controlla se il DataFrame è valido
        if self.df.empty:
            raise ValueError("Il DataFrame è vuoto")
    # end controllaDataFrame()
    
    @catturaEccezione
    def assegnaNomeFile(self, file_xlsm):
        if not os.path.exists(file_xlsm):
            raise FileNotFoundError(f"File non trovato: {file_xlsm}")
        self.file = file_xlsm
        return self.file
    # end assegnaNomeFile()

    @catturaEccezione
    def caricaDataFrame(self, file_xlsm):
        # Carica tutti i fogli in un dizionario di DataFrame
        import os
        # print(f"[DEBUG] Path file Excel usato: {file_xlsm}")
        try:
            if not os.path.isfile(file_xlsm):
                dir_path = os.path.dirname(file_xlsm)
                for f in os.listdir(dir_path):
                    print(f"  - {f}")
                raise FileNotFoundError(f"File non trovato: {file_xlsm}")
            # end if

            if not file_xlsm.lower().endswith(('.xls', '.xlsx', '.xlsm')):
                raise ValueError(f"Estensione file non supportata: {file_xlsm}")
            # end if

            sheets_dict = pd.read_excel(file_xlsm, sheet_name=None) # legge tutti i fogli del file Campionato.xlsm
        except Exception as e:
            
            raise ValueError(f"Errore durante il caricamento del file Excel: {e}")
        # end try-except

        # Unisci tutti i DataFrame in uno solo
        self.df = pd.concat(sheets_dict.values(), ignore_index=True)
        
        # sostituisco il file .xlsm con un .csv
        file_csv = file_xlsm.replace('.xlsm', '.csv')
        file_csv = os.path.basename(file_csv)

        self.df.to_csv(f'Csv\\{file_csv}', sep=';', index=False)

        # potrei evitare di fare questo passaggio
        # ma così mantengo la compatibilità con il resto del codice
        # e ho la possibilità di ispezionare il file con Vscode
        self.df = EstrazioneDati.trasformaDataframe(file_csv)
        self.aggiungiColonnaEsiti(file_csv)
        self.controllaDataFrame()
        return self.df
    # end caricaDataFrame()
    
    @catturaEccezione
    def caricaDataFrameDaCsv(self, file_csv):
        # Carica il DataFrame da un file CSV già trasformato
        self.df = pd.read_csv(f'{file_csv}', sep=';')
        self.controllaDataFrame()
        return self.df
    
    @catturaEccezione
    @staticmethod
    def trasformaDataframe(file_csv):
        # Legge il file CSV in un DataFrame
        df = pd.read_csv(f'Csv\\{file_csv}', sep=';')

        # Rinomina le colonne
        df.rename(columns=modificaNomiColonne, inplace=True)
        
        # Pulizia spazi bianchi e traduzione nomi squadre
        for col in df.select_dtypes(include=['object']).columns:
            # Rimuovi spazi bianchi
            df[col] = df[col].astype(str).str.strip()
            # Traduci i nomi delle squadre solo per le colonne 'Casa' e 'Trasferta'
            if col == 'Casa':
                df[col] = df[col].replace(modificaNomiSquadre)
            elif col == 'Trasferta':
                df[col] = df[col].replace(modificaNomiSquadre)
            # end if
        # end for
        # Traduci i mesi
        df['Mese'] = df['Mese'].replace(traduciMesi)
        
        # Traduci i giorni della settimana
        df['GiornoSettimana'] = df['GiornoSettimana'].replace(traduciGiorniSettimana)

        # # Rinomina la colonna 'GiornoSettimana' in 'Giorno'
        # df.rename(columns={'GiornoSettimana': 'Giorno'}, inplace=True)

        # Salva il DataFrame trasformato in un nuovo file CSV
        df.to_csv(f'Csv\\{file_csv}', sep=';', index=False)
        
        return df
    # end trasformaDataframe()
    
    @catturaEccezione
    def aggiungiColonnaEsiti(self, file_csv):
        # Aggiunge la colonna Esiti al DataFrame
        self.df['Esiti'] = self.df.apply(lambda row: self.calcolaEsito(row), axis=1)
        self.df.to_csv(f'Csv\\{file_csv}', sep=';', index=False)
    # end aggiungiColonnaEsiti()
    
    @catturaEccezione
    def calcolaEsito(self, row) -> str:
        # Calcola l'esito per una singola riga
        if row['GoalCasa'] > row['GoalTrasferta']:
            esito = '1'
        elif row['GoalCasa'] == row['GoalTrasferta']:
            esito = 'X'
        elif row['GoalCasa'] < row['GoalTrasferta']:
            esito = '2'
        else:
            esito = ''
        # end if
        
        return esito
    # end calcolaEsito()

    @catturaEccezione
    def dataFrame(self):
        return self.df
    # end dataFrame()
    
    @catturaEccezione
    def squadre(self):
    # Combina squadre di casa e ospiti per un elenco completo
        squadre_casa = self.df['Casa'].unique()
        squadre_trasferta = self.df['Trasferta'].unique() if 'Trasferta' in self.df.columns else []
        self.listaSquadre = list(set(list(squadre_casa) + list(squadre_trasferta)))
        # print(f"[DEBUG] Squadre estratte: {self.listaSquadre}")
        return sorted(self.listaSquadre)
    # end squadre()
    
    @catturaEccezione
    def vittorie(self, squadra: str, where: str = 'generali') -> str:
        '''Estrae il numero di vittorie della squadra a seconda del valore di where\n
           se where = 'generali' conta le vittorie in casa e in trasferta\n
           se where = 'casa' conta le vittorie in casa\n
           se where = 'trasferta' conta le vittorie in trasferta'''
        
        vinte = 0 #vittorie
        
        # vittorie generali
        if where == 'generali':
            # Conta le vittorie in casa e in trasferta
            vittorie_casa = self.df.query(f'Casa == "{squadra}" and Esiti == "1"').shape[0]
            vittorie_trasferta = self.df.query(f'Trasferta == "{squadra}" and Esiti == "2"').shape[0]
            vinte = vittorie_casa + vittorie_trasferta
        # end if
        
        # vittorie in casa
        if where == 'casa':
            # Conta le vittorie in casa
            vinte = self.df.query(f'Casa == "{squadra}" and Esiti == "1"').shape[0]
        # end if
        
        # vittorie in trasferta
        if where == 'trasferta':
            # Conta le vittorie in trasferta
            vinte = self.df.query(f'Trasferta == "{squadra}" and Esiti == "2"').shape[0]
        # end if

        return str(vinte)
    # end estraiVittorieGenerali()
    
    @catturaEccezione
    def pareggi(self, squadra: str, where: str = 'generali') -> str:
        '''Estrae il numero di pareggi della squadra a seconda del valore di where\n
           se where = 'generali' conta i pareggi in casa e in trasferta\n
           se where = 'casa' conta i pareggi in casa\n
           se where = 'trasferta' conta i pareggi in trasferta'''
        
        pareggiate = 0 #pareggi

        if where == 'generali':
            # Conta i pareggi in casa e in trasferta
            pareggi_casa = self.df.query(f'Casa == "{squadra}" and Esiti == "X"').shape[0]
            pareggi_trasferta = self.df.query(f'Trasferta == "{squadra}" and Esiti == "X"').shape[0]
            pareggiate = pareggi_casa + pareggi_trasferta
        elif where == 'casa':
            # Conta i pareggi in casa
            pareggiate = self.df.query(f'Casa == "{squadra}" and Esiti == "X"').shape[0]
        elif where == 'trasferta':
            # Conta i pareggi in trasferta
            pareggiate = self.df.query(f'Trasferta == "{squadra}" and Esiti == "X"').shape[0]
        # end if
        return str(pareggiate)
    # end estraiPareggiGenerali()
    
    @catturaEccezione
    def sconfitte(self, squadra: str, where: str = 'generali') -> str:
        '''Estrae il numero di sconfitte di una squadra a seconda del valore di where\n
           se where = 'generali' conta le sconfitte in casa e in trasferta\n
           se where = 'casa' conta le sconfitte in casa\n
           se where = 'trasferta' conta le sconfitte in trasferta'''
        
        perse = 0 #sconfitte

        if where == 'generali':
        # Conta le sconfitte in casa e in trasferta
            sconfitte_casa = self.df.query(f'Casa == "{squadra}" and Esiti == "2"').shape[0]
            sconfitte_trasferta = self.df.query(f'Trasferta == "{squadra}" and Esiti == "1"').shape[0]
            perse = sconfitte_casa + sconfitte_trasferta
        elif where == 'casa':
            # Conta le sconfitte in casa
            perse = self.df.query(f'Casa == "{squadra}" and Esiti == "2"').shape[0]
        elif where == 'trasferta':
            # Conta le sconfitte in trasferta
            perse = self.df.query(f'Trasferta == "{squadra}" and Esiti == "1"').shape[0]
        # end if
        return str(perse)
    # end estraiSconfitteGenerali()
    
    @catturaEccezione
    def goalsFatti(self, squadra: str, where: str = 'generali') -> str:
        '''Estrae il numero di goals fatti di una squadra a seconda del valore di where\n
           se where = 'generali' conta i goals fatti in casa e in trasferta\n
           se where = 'casa' conta i goals fatti in casa\n
           se where = 'trasferta' conta i goals fatti in trasferta'''
        
        goals_fatti = 0
        
        if where == 'generali':
            # Conta i goals fatti in casa e in trasferta
            goals_fatti_casa = self.df[self.df['Casa'] == squadra]['GoalCasa'].sum()
            goals_fatti_trasferta = self.df[self.df['Trasferta'] == squadra]['GoalTrasferta'].sum()
            goals_fatti = goals_fatti_casa + goals_fatti_trasferta
        elif where == 'casa':
            # Conta i goals fatti in casa
            goals_fatti = self.df[self.df['Casa'] == squadra]['GoalCasa'].sum()
        elif where == 'trasferta':
            # Conta i goals fatti in trasferta
            goals_fatti = self.df[self.df['Trasferta'] == squadra]['GoalTrasferta'].sum()
        # end if
        
        return str(goals_fatti)
    # end estraiGoalsFatti()
    
    @catturaEccezione
    def goalsSubiti(self, squadra: str, where: str = 'generali') -> str:
        '''Estrae il numero di goals subiti di una squadra a seconda del valore di where\n
           se where = 'generali' conta i goals subiti in casa e in trasferta\n
           se where = 'casa' conta i goals subiti in casa\n
           se where = 'trasferta' conta i goals subiti in trasferta'''
        
        goals_subiti = 0
        
        if where == 'generali':
            # Conta i goals subiti in casa e in trasferta
            goals_subiti_casa = self.df[self.df['Trasferta'] == squadra]['GoalCasa'].sum()
            goals_subiti_trasferta = self.df[self.df['Casa'] == squadra]['GoalTrasferta'].sum()
            goals_subiti = goals_subiti_casa + goals_subiti_trasferta
        elif where == 'casa':
            # Conta i goals subiti in casa
            goals_subiti = self.df[self.df['Casa'] == squadra]['GoalTrasferta'].sum()
        elif where == 'trasferta':
            # Conta i goals subiti in trasferta
            goals_subiti = self.df[self.df['Trasferta'] == squadra]['GoalCasa'].sum()
        # end if
        
        return str(goals_subiti)
    # end estraiGoalsSubiti()
    
    
    @catturaEccezione   
    def esitiOrdinati(self, squadra: str, where: str = 'generali') -> list:
        """
        Restituisce una lista degli esiti delle partite di una squadra, ordinati cronologicamente e normalizzati rispetto alla squadra in esame.
        Gli esiti sono normalizzati come segue:
        - '1': Vittoria della squadra in esame (sia in casa che in trasferta)
        - '2': Sconfitta della squadra in esame (sia in casa che in trasferta)
        - 'X': Pareggio
        Args:
            squadra (str): Nome della squadra di cui si vogliono ottenere gli esiti.
        Returns:
            list: Lista degli esiti normalizzati ('1', '2', 'X') per la squadra specificata.
        """
        
        esiti = []
        if where == 'generali':
            squadraInEsame = self.df.query(f'Casa == "{squadra}" or Trasferta == "{squadra}"')

            for _, row in squadraInEsame.iterrows():    #itero la series
                esito = str(row['Esiti']).strip()  #estraggo l'esito 
                if esito == 'X': # se l'esito è X in casa o trasferta non cambia
                    new = 'X'
                else:
                    if row['Casa'] == squadra:
                        if esito == '1':    # se gioca in casa 1 rimane 1 ma va aggiunto alla lista
                            new ='1'
                        elif esito == '2':  # se gioca in casa e perde resta 2 e va aggiunto alla lista
                            new = '2'
                        # end if
                    else:  # squadra is away
                        if esito == '2': # se gioca in trasferta e vince diventa 1
                            new = '1'
                        elif esito == '1':  # se gioca in trasferta e perde diventa 2
                            new = '2'
                        # end if
                    # end if
                # end if
                esiti.append(new)
            # end for
        elif where == 'casa':
            squadraInEsame = self.df.query(f'Casa == "{squadra}"')

            for _, row in squadraInEsame.iterrows():    #itero la series
                esito = str(row['Esiti']).strip()  #estraggo l'esito 
                if esito == 'X': # se l'esito è X in casa non cambia
                    new = 'X'
                else:
                    if esito == '1':    # se gioca in casa 1 rimane 1 ma va aggiunto alla lista
                        new ='1'
                    elif esito == '2':  # se gioca in casa e perde resta 2 e va aggiunto alla lista
                        new = '2'
                    # end if
                # end if
                esiti.append(new)
            # end for
        elif where == 'trasferta':
            squadraInEsame = self.df.query(f'Trasferta == "{squadra}"')

            for _, row in squadraInEsame.iterrows():    #itero la series
                esito = str(row['Esiti']).strip()  #estraggo l'esito 
                if esito == 'X': # se l'esito è X in trasferta non cambia
                    new = 'X'
                else:
                    if esito == '2': # se gioca in trasferta e vince diventa 1
                        new = '1'
                    elif esito == '1':  # se gioca in trasferta e perde diventa 2
                        new = '2'
                    # end if
                # end if    
                esiti.append(new)
            # end for
        # end if
        return esiti
    # end esitiOrdinati()

    @catturaEccezione
    def ultimeCinquePartite(self, squadra: str) -> list:
        ucp = UltimiCinquePartite(self.df)
        ultime_cinque_partite = ucp.estraiUltimeCinquePartite(squadra)
        return ultime_cinque_partite

    @catturaEccezione
    def ultimeCinquePartiteInCasa(self, squadra: str) -> list:
        ucp = UltimiCinquePartite(self.df)
        ultime_cinque_partite_in_casa = ucp.estraiUltimeCinquePartiteInCasa(squadra)
        return ultime_cinque_partite_in_casa
    # end estraiUltimeCinquePartiteInCasa

    @catturaEccezione
    def ultimeCinquePartiteInTrasferta(self, squadra: str) -> list:
        ucp = UltimiCinquePartite(self.df)
        ultime_cinque_partite_in_trasferta = ucp.estraiUltimeCinquePartiteInTrasferta(squadra)
        return ultime_cinque_partite_in_trasferta
    # end estraiUltimeCinquePartiteInTrasferta

    @catturaEccezione
    def partiteGiocate(self, squadra: str, where: str = 'generali') -> int:
        '''Calcola il numero di partite giocate da una squadra'''
        if where == 'generali':
            partite_casa = self.df.query(f'Casa == "{squadra}"').shape[0]
            partite_trasferta = self.df.query(f'Trasferta == "{squadra}"').shape[0]
            return partite_casa + partite_trasferta
        elif where == 'casa':
            return self.df.query(f'Casa == "{squadra}"').shape[0]
        elif where == 'trasferta':
            return self.df.query(f'Trasferta == "{squadra}"').shape[0]
        return 0
    
    @catturaEccezione
    def punti(self, squadra: str, where: str = 'generali') -> int:
        '''Calcola i punti di una squadra (3 per vittoria, 1 per pareggio)'''
        vittorie = int(self.vittorie(squadra, where))
        pareggi = int(self.pareggi(squadra, where))
        return vittorie * 3 + pareggi * 1
    
    @catturaEccezione 
    def differenzaReti(self, squadra: str, where: str = 'generali') -> int:
        '''Calcola la differenza reti di una squadra'''
        gf = int(self.goalsFatti(squadra, where))
        gs = int(self.goalsSubiti(squadra, where))
        return gf - gs
    
    @catturaEccezione
    def creaClassifica(self, where: str = 'generali') -> pd.DataFrame:
        '''Crea una classifica completa delle squadre'''
        squadre = self.squadre()
        classifica_data = []
        
        for squadra in squadre:
            punti = self.punti(squadra, where)
            partite = self.partiteGiocate(squadra, where)
            vittorie = int(self.vittorie(squadra, where))
            pareggi = int(self.pareggi(squadra, where))
            sconfitte = int(self.sconfitte(squadra, where))
            gf = int(self.goalsFatti(squadra, where))
            gs = int(self.goalsSubiti(squadra, where))
            dr = self.differenzaReti(squadra, where)
            
            classifica_data.append({
                'Squadra': squadra,
                'Punti': punti,
                'Partite': partite,
                'Vittorie': vittorie,
                'Pareggi': pareggi,
                'Sconfitte': sconfitte,
                'GF': gf,
                'GS': gs,
                'DR': dr
            })
        
        # Ordina per punti, differenza reti e goal fatti
        classifica_df = pd.DataFrame(classifica_data)
        classifica_df = classifica_df.sort_values(['Punti', 'DR', 'GF'], ascending=[False, False, False])
        classifica_df['Posizione'] = range(1, len(classifica_df) + 1)
        
        return classifica_df[['Posizione', 'Squadra', 'Punti', 'Partite', 'Vittorie', 'Pareggi', 'Sconfitte', 'GF', 'GS', 'DR']]
    
    @catturaEccezione
    def getRankingSquadra(self, squadra: str, where: str = 'generali') -> int:
        '''Ottiene la posizione in classifica di una squadra'''
        classifica = self.creaClassifica(where)
        posizione = classifica[classifica['Squadra'] == squadra]['Posizione']
        return posizione.iloc[0] if not posizione.empty else len(self.squadre()) + 1

# end EstrazioneDatiPerGrafici

if __name__ == "__main__":
    # os.path.dirname(__file__) --> percorso corrente del file Classifica.csv 
    # os.path.join(os.path.dirname(__file__), '../Csv/Classifica.csv') --> percorso relativo al file Classifica.csv
    # os.path.abspath(...) --> percorso assoluto del file Classifica.csv
    file = myFile.campionatoCorrente
    if not os.path.exists(file):
        print(f"File non trovato: {file}")
        exit(1)
    else:
        print(f"[DEBUG] File trovato: {file}")
    # end if

    # md = MetaDatiDf(file)
    # md.creaMetaDati()
    # md.stampaReportMetaDati()
    # md.salvaMetaDati(formato='entrambi')
    
    # ed = EstrazioneDati('Excel/Campionato.xlsm')
    # df = ed.dataFrame()
    # ed.ultimeCinquePartite('Juventus')
    # print(df.head())
    dati = EstrazioneDati(file)
    dati.squadre()    
