#!/usr/bin/env python3
"""
Test rapido per predizione partita
"""

from EsitoDalRanking import PredizionePartita

if __name__ == "__main__":
    print("🏆 Test predizione: Atalanta vs Bologna")
    
    try:
        predizione = PredizionePartita("Atalanta", "Bologna", peso_attuale=0.7)
        predizione.prevedi()
        predizione.dettaglio_forma()
        predizione.grafico_confronto()
        
        print("\n✅ Test completato!")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
