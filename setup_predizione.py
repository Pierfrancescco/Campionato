#!/usr/bin/env python3
"""
Script per verificare e preparare la struttura dati per EsitoDalRanking.py
"""

import pandas as pd
import os

def verifica_file_csv():
    """Verifica la struttura dei file CSV"""
    print("=== VERIFICA STRUTTURA FILE CSV ===")
    
    file_corrente = 'Csv/Campionato.csv'
    file_storico = 'Csv/CampionatiPrecedenti.csv'
    
    for file_path in [file_corrente, file_storico]:
        if os.path.exists(file_path):
            print(f"\n📁 File: {file_path}")
            df = pd.read_csv(file_path, sep=';')
            print(f"  Righe: {len(df)}")
            print(f"  Colonne: {list(df.columns)}")
            print(f"  Prime 3 righe:")
            print(df.head(3))
            
            # Verifica le squadre uniche
            if 'Casa' in df.columns and 'Trasferta' in df.columns:
                squadre_casa = set(df['Casa'].unique())
                squadre_trasferta = set(df['Trasferta'].unique())
                squadre_totali = squadre_casa.union(squadre_trasferta)
                print(f"  Squadre totali: {len(squadre_totali)}")
                print(f"  Squadre: {sorted(list(squadre_totali))}")
        else:
            print(f"❌ File non trovato: {file_path}")

def converti_formato_legacy():
    """Converte i file CSV nel formato atteso da EsitoDalRanking.py legacy"""
    print("\n=== CONVERSIONE FORMATO LEGACY ===")
    
    file_input = 'Csv/Campionato.csv'
    file_output = 'Campionato.CSV'
    
    if os.path.exists(file_input):
        df = pd.read_csv(file_input, sep=';')
        
        # Mappa le colonne al formato atteso dal codice legacy
        if 'Casa' in df.columns and 'Trasferta' in df.columns:
            df_legacy = pd.DataFrame()
            df_legacy['Home'] = df['Casa']
            df_legacy['Away'] = df['Trasferta']
            df_legacy['GoalHome'] = df['GoalCasa']
            df_legacy['GoalAway'] = df['GoalTrasferta']
            
            # Aggiungi colonne necessarie per il calcolo
            # Simuliamo dati per Win, Draw, Lose, GamesPlayed
            df_legacy['Win'] = 0  # Sarà calcolato dinamicamente
            df_legacy['Draw'] = 0  # Sarà calcolato dinamicamente  
            df_legacy['Lose'] = 0  # Sarà calcolato dinamicamente
            df_legacy['GamesPlayed'] = 1  # Una partita per riga
            
            # Aggiungi colonne per la forma recente (simulate)
            for i in range(1, 6):
                df_legacy[f'HomeMatch_{i}_Ago'] = 'X'  # Placeholder
                df_legacy[f'AwayMatch_{i}_Ago'] = 'X'  # Placeholder
                df_legacy[f'HomeMatch_{i}_Ago_InHome'] = 'X'  # Placeholder
                df_legacy[f'AwayMatch_{i}_Ago_InAway'] = 'X'  # Placeholder
            
            df_legacy.to_csv(file_output, sep=';', index=False)
            print(f"✅ File convertito: {file_output}")
            print(f"  Righe: {len(df_legacy)}")
            print(f"  Colonne: {list(df_legacy.columns)}")
        else:
            print(f"❌ Colonne Casa/Trasferta non trovate in {file_input}")
    else:
        print(f"❌ File di input non trovato: {file_input}")

def crea_file_test_partita():
    """Crea uno script di test per una partita specifica"""
    print("\n=== CREAZIONE SCRIPT TEST PARTITA ===")
    
    # Verifica quali squadre sono disponibili
    file_corrente = 'Csv/Campionato.csv'
    if os.path.exists(file_corrente):
        df = pd.read_csv(file_corrente, sep=';')
        squadre = sorted(set(df['Casa'].unique()).union(set(df['Trasferta'].unique())))
        
        if len(squadre) >= 2:
            squadra1, squadra2 = squadre[0], squadre[1]
            
            script_content = f'''#!/usr/bin/env python3
"""
Test rapido per predizione partita
"""

from EsitoDalRanking import PredizionePartita

if __name__ == "__main__":
    print("🏆 Test predizione: {squadra1} vs {squadra2}")
    
    try:
        predizione = PredizionePartita("{squadra1}", "{squadra2}", peso_attuale=0.7)
        predizione.prevedi()
        predizione.dettaglio_forma()
        predizione.grafico_confronto()
        
        print("\\n✅ Test completato!")
    except Exception as e:
        print(f"❌ Errore: {{e}}")
        import traceback
        traceback.print_exc()
'''
            
            with open('test_partita_rapido.py', 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            print(f"✅ Creato test_partita_rapido.py per {squadra1} vs {squadra2}")
        else:
            print("❌ Non abbastanza squadre per creare test")
    else:
        print(f"❌ File {file_corrente} non trovato")

if __name__ == "__main__":
    print("🔧 SETUP E VERIFICA SISTEMA PREDIZIONE")
    
    verifica_file_csv()
    converti_formato_legacy()
    crea_file_test_partita()
    
    print("\n🏁 Setup completato!")
    print("\nPer testare il sistema:")
    print("1. python test_partita_rapido.py")
    print("2. python test_predizione_avanzata.py")
    print("3. python EsitoDalRanking.py <squadra1> <squadra2>")