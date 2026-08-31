#!/usr/bin/env python3
"""
Test per la versione avanzata di EsitoDalRanking.py
Verifica tutte le nuove funzionalità aggiunte
"""

import sys
import os

# Aggiungi il percorso corrente al path per importare i moduli
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from EsitoDalRanking import PredizionePartita

def test_predizione_avanzata():
    """Test completo delle funzionalità avanzate"""
    print("=== TEST PREDIZIONE AVANZATA ===")
    print("Testing con Juventus vs Inter...")
    
    try:
        # Crea istanza della predizione
        predizione = PredizionePartita("Juventus", "Inter", peso_attuale=0.7)
        
        print("\n1. Test predizione base...")
        predizione.prevedi()
        
        print("\n2. Test dettaglio forma...")
        predizione.dettaglio_forma()
        
        print("\n3. Test grafico confronto...")
        predizione.grafico_confronto()
        
        print("\n✅ Test completato con successo!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

def test_estrazione_dati():
    """Test delle nuove funzionalità di EstrazioneDati"""
    print("\n=== TEST ESTRAZIONE DATI ===")
    
    try:
        from EstrazioneDati import EstrazioneDati
        
        # Test con file Excel se esiste
        excel_file = 'Excel/Campionato.xlsm'
        if os.path.exists(excel_file):
            ed = EstrazioneDati(excel_file)
            
            print("Test squadre...")
            squadre = ed.squadre()
            print(f"Trovate {len(squadre)} squadre")
            
            if len(squadre) > 0:
                squadra_test = squadre[0]
                print(f"\nTest con squadra: {squadra_test}")
                
                # Test nuove funzioni
                punti = ed.punti(squadra_test)
                print(f"Punti: {punti}")
                
                pos_generale = ed.getRankingSquadra(squadra_test, 'generali')
                print(f"Posizione generale: {pos_generale}")
                
                pos_casa = ed.getRankingSquadra(squadra_test, 'casa')
                print(f"Posizione casa: {pos_casa}")
                
                # Test classifica
                classifica = ed.creaClassifica('generali')
                print(f"\nClassifica generale (prime 5):")
                print(classifica.head())
                
        else:
            print(f"File {excel_file} non trovato, skip test EstrazioneDati")
            
    except Exception as e:
        print(f"❌ Errore nel test EstrazioneDati: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Avvio test completo sistema predizione avanzata")
    
    # Test 1: EstrazioneDati
    test_estrazione_dati()
    
    # Test 2: Predizione avanzata
    test_predizione_avanzata()
    
    print("\n🏁 Test completati!")