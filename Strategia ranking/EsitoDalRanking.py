import pandas as pd
import matplotlib
import sys
import os
matplotlib.use('Agg')  # Backend non-grafico per salvare file
import matplotlib.pyplot as plt

class PredizionePartita:
    def __init__(self, squadra_casa, squadra_trasferta, percorso_corrente='Csv/Campionato.csv', percorso_storico='Csv/CampionatiPrecedenti.csv', peso_attuale=0.6):
        self.squadra_casa = squadra_casa.strip()
        self.squadra_trasferta = squadra_trasferta.strip()
        self.peso_attuale = peso_attuale
        
        # Carica i dati CSV
        print(f"Caricando dati da {percorso_corrente}...")
        self.dati_corrente = pd.read_csv(percorso_corrente, sep=';')
        try:
            print(f"Caricando dati storici da {percorso_storico}...")
            self.dati_storico = pd.read_csv(percorso_storico, sep=';')
        except:
            print("Dati storici non disponibili")
            self.dati_storico = None
        
        # Crea le statistiche aggregate
        self.statistiche = self._costruisci_statistiche_combine()

    def _aggregazione_statistiche(self, df):
        """Aggrega le statistiche dal DataFrame CSV con colonne: Casa, Trasferta, GoalCasa, GoalTrasferta"""
        # Calcola gli esiti per ogni partita
        df = df.copy()
        df['EsitoCasa'] = df.apply(lambda row: '1' if row['GoalCasa'] > row['GoalTrasferta'] 
                                             else 'X' if row['GoalCasa'] == row['GoalTrasferta'] 
                                             else '2', axis=1)
        
        # Crea DataFrame per squadre in casa
        casa_stats = df.groupby('Casa').agg({
            'GoalCasa': 'sum',      # Goal fatti in casa
            'GoalTrasferta': 'sum', # Goal subiti in casa
            'Casa': 'count'         # Partite giocate in casa
        }).rename(columns={
            'GoalCasa': 'GF_casa',
            'GoalTrasferta': 'GS_casa', 
            'Casa': 'PG_casa'
        })
        
        # Aggiungi vittorie, pareggi, sconfitte in casa
        casa_stats['V_casa'] = df[df['EsitoCasa'] == '1'].groupby('Casa').size().reindex(casa_stats.index, fill_value=0)
        casa_stats['X_casa'] = df[df['EsitoCasa'] == 'X'].groupby('Casa').size().reindex(casa_stats.index, fill_value=0)
        casa_stats['S_casa'] = df[df['EsitoCasa'] == '2'].groupby('Casa').size().reindex(casa_stats.index, fill_value=0)
        
        # Crea DataFrame per squadre in trasferta
        trasferta_stats = df.groupby('Trasferta').agg({
            'GoalTrasferta': 'sum', # Goal fatti in trasferta
            'GoalCasa': 'sum',      # Goal subiti in trasferta
            'Trasferta': 'count'    # Partite giocate in trasferta
        }).rename(columns={
            'GoalTrasferta': 'GF_trasferta',
            'GoalCasa': 'GS_trasferta',
            'Trasferta': 'PG_trasferta'
        })
        
        # Aggiungi vittorie, pareggi, sconfitte in trasferta
        trasferta_stats['V_trasferta'] = df[df['EsitoCasa'] == '2'].groupby('Trasferta').size().reindex(trasferta_stats.index, fill_value=0)
        trasferta_stats['X_trasferta'] = df[df['EsitoCasa'] == 'X'].groupby('Trasferta').size().reindex(trasferta_stats.index, fill_value=0)
        trasferta_stats['S_trasferta'] = df[df['EsitoCasa'] == '1'].groupby('Trasferta').size().reindex(trasferta_stats.index, fill_value=0)
        
        # Unisci tutte le squadre
        tutte_squadre = set(df['Casa'].unique()) | set(df['Trasferta'].unique())
        aggregato = pd.DataFrame(index=sorted(tutte_squadre))
        
        # Merge dei dati casa e trasferta
        aggregato = aggregato.join(casa_stats, how='left').join(trasferta_stats, how='left')
        aggregato = aggregato.fillna(0)
        
        # Calcola totali
        aggregato['GF'] = aggregato['GF_casa'] + aggregato['GF_trasferta']
        aggregato['GS'] = aggregato['GS_casa'] + aggregato['GS_trasferta']
        aggregato['V'] = aggregato['V_casa'] + aggregato['V_trasferta']
        aggregato['X'] = aggregato['X_casa'] + aggregato['X_trasferta']
        aggregato['S'] = aggregato['S_casa'] + aggregato['S_trasferta']
        aggregato['PG'] = aggregato['PG_casa'] + aggregato['PG_trasferta']
        
        return aggregato[['GF', 'GS', 'V', 'X', 'S', 'PG', 'GF_casa', 'GS_casa', 'V_casa', 'X_casa', 'S_casa', 'PG_casa', 
                         'GF_trasferta', 'GS_trasferta', 'V_trasferta', 'X_trasferta', 'S_trasferta', 'PG_trasferta']]

    def _costruisci_statistiche_combine(self):
        attuale = self._aggregazione_statistiche(self.dati_corrente)
        if self.dati_storico is not None:
            storico = self._aggregazione_statistiche(self.dati_storico)
            
            # Combina i dati, mantenendo solo le squadre comuni per le medie
            forza_attuale = self._calcola_forza(attuale)
            forza_storica = self._calcola_forza(storico)
            
            # Crea DataFrame combinato
            combinato = attuale.copy()
            combinato['Forza'] = forza_attuale
            
            # Aggiungi influenza storica per le squadre che esistono anche nello storico
            for squadra in combinato.index:
                if squadra in storico.index:
                    forza_comb = (self.peso_attuale * forza_attuale.loc[squadra] + 
                                 (1 - self.peso_attuale) * forza_storica.loc[squadra])
                    combinato.loc[squadra, 'Forza'] = forza_comb
            
            return combinato
        else:
            attuale['Forza'] = self._calcola_forza(attuale)
            return attuale

    def _calcola_forza(self, df):
        α, β, γ, δ, ε = 1, 0.8, 3, 1, 2
        return α * df['GF'] - β * df['GS'] + γ * df['V'] + δ * df['X'] - ε * df['S']

    def _calcola_forma_squadra(self, nome_squadra, where='generali'):
        """Calcola la forma della squadra basata sulle ultime 5 partite"""
        df = self.dati_corrente.copy()
        
        # Trova tutte le partite della squadra
        if where == 'generali':
            partite_squadra = df[(df['Casa'] == nome_squadra) | (df['Trasferta'] == nome_squadra)]
        elif where == 'casa':
            partite_squadra = df[df['Casa'] == nome_squadra]
        elif where == 'trasferta':
            partite_squadra = df[df['Trasferta'] == nome_squadra]
        
        # Prendi le ultime 5 partite
        ultime_partite = partite_squadra.tail(5)
        
        forma_totale = 0
        for _, partita in ultime_partite.iterrows():
            # Determina l'esito per la squadra
            if partita['Casa'] == nome_squadra:  # Squadra gioca in casa
                if partita['GoalCasa'] > partita['GoalTrasferta']:  # Vittoria
                    forma_totale += 3
                elif partita['GoalCasa'] == partita['GoalTrasferta']:  # Pareggio
                    forma_totale += 1
                # Sconfitta = 0 punti
            else:  # Squadra gioca in trasferta
                if partita['GoalTrasferta'] > partita['GoalCasa']:  # Vittoria
                    forma_totale += 3
                elif partita['GoalTrasferta'] == partita['GoalCasa']:  # Pareggio
                    forma_totale += 1
                # Sconfitta = 0 punti
        
        # Media della forma (punti per partita)
        return forma_totale / max(1, len(ultime_partite))

    def _calcola_probabilita_avanzata(self):
        """Calcola probabilità più accurate considerando forza e forma"""
        casa = self.statistiche.loc[self.squadra_casa]
        trasferta = self.statistiche.loc[self.squadra_trasferta]
        
        # Forza base
        forza_casa = casa['Forza']
        forza_trasferta = trasferta['Forza']
        diff_forza = forza_casa - forza_trasferta
        
        # Forma recente
        forma_casa = self._calcola_forma_squadra(self.squadra_casa)
        forma_trasferta = self._calcola_forma_squadra(self.squadra_trasferta)
        diff_forma = (forma_casa - forma_trasferta) * 10  # Peso della forma
        
        # Combinazione forza + forma
        diff_totale = diff_forza + diff_forma
        
        # Probabilità base con fattore casa
        p1 = min(0.85, max(0.15, 0.45 + diff_totale / 200))  # Leggero vantaggio casa
        p2 = min(0.85, max(0.15, 0.35 - diff_totale / 200))
        px = max(0.10, 1 - (p1 + p2))
        
        return p1, px, p2, forma_casa, forma_trasferta

    def prevedi(self):
        casa = self.statistiche.loc[self.squadra_casa]
        trasferta = self.statistiche.loc[self.squadra_trasferta]
        
        # Calcoli base
        goal_casa = round((casa['GF'] / casa['PG'] + trasferta['GS'] / trasferta['PG']) / 2, 1)
        goal_trasferta = round((trasferta['GF'] / trasferta['PG'] + casa['GS'] / casa['PG']) / 2, 1)
        goal_totali = goal_casa + goal_trasferta
        
        # Calcoli avanzati con forma (più accurati)
        p1, px, p2, forma_casa, forma_trasferta = self._calcola_probabilita_avanzata()
        
        # Esito previsto basato sulle probabilità (più accurato)
        if p1 > p2 and p1 > px:
            esito = '1'
            doppia_chance = '1X'
        elif p2 > p1 and p2 > px:
            esito = '2'
            doppia_chance = 'X2'
        else:
            esito = 'X'
            doppia_chance = '12'
        
        # Over/Under 2.5 e 1.5
        probabilita_under_25 = max(0, 1 - goal_totali / 5)
        probabilita_over_25 = 1 - probabilita_under_25
        probabilita_under_15 = max(0, 1 - goal_totali / 3.5)
        probabilita_over_15 = 1 - probabilita_under_15

        print(f"=== ANALISI PARTITA ===")
        print(f"PARTITA: {self.squadra_casa} vs {self.squadra_trasferta}")
        print(f"\n--- PREDIZIONE GOAL ---")
        print(f"Goal previsti: {self.squadra_casa} {goal_casa} - {goal_trasferta} {self.squadra_trasferta}")
        print(f"Esito previsto: {esito}")
        print(f"Doppia chance suggerita: {doppia_chance}")
        print(f"\n--- PROBABILITA ESITO ---")
        print(f"1 (Vittoria {self.squadra_casa}): {p1:.0%}")
        print(f"X (Pareggio): {px:.0%}")
        print(f"2 (Vittoria {self.squadra_trasferta}): {p2:.0%}")
        print(f"\n--- OVER/UNDER ---")
        print(f"Under 1.5: {probabilita_under_15:.0%}")
        print(f"Over 1.5: {probabilita_over_15:.0%}")
        print(f"Under 2.5: {probabilita_under_25:.0%}")
        print(f"Over 2.5: {probabilita_over_25:.0%}")
        print(f"\n--- FORMA RECENTE (ultime 5 partite) ---")
        print(f"{self.squadra_casa}: {forma_casa:.1f}/3.0 punti/partita")
        print(f"{self.squadra_trasferta}: {forma_trasferta:.1f}/3.0 punti/partita")
        
        # Ranking campionato attuale
        self._mostra_ranking_campionato_attuale()
        
        # Ranking ultime 5 partite
        self._mostra_ranking_ultime_5_partite()
        
        # Ranking campionati precedenti
        self._mostra_ranking_storico()
        
        # Scontri diretti storici
        self._mostra_scontri_diretti_storici()
        
        # Analisi AI e raccomandazioni scommesse
        self._analisi_ai_e_consigli(p1, px, p2, forma_casa, forma_trasferta, goal_totali, probabilita_under_25, probabilita_over_25)

    def grafico_confronto(self):
        casa = self.statistiche.loc[self.squadra_casa]
        trasferta = self.statistiche.loc[self.squadra_trasferta]
        forma_casa = self._calcola_forma_squadra(self.squadra_casa, 'generali')
        forma_trasferta = self._calcola_forma_squadra(self.squadra_trasferta, 'generali')
        
        # Aggiungi dati di ranking
        try:
            classifica = self._crea_classifica(self.dati_corrente, 'generali')
            pos_casa = classifica[classifica['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
            pos_trasferta = classifica[classifica['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
            ranking_casa_gen = 21 - pos_casa  # Inverti per visualizzazione (più alto = meglio)
            ranking_trasferta_gen = 21 - pos_trasferta
        except:
            ranking_casa_gen = 0
            ranking_trasferta_gen = 0
        
        etichette = ['Forza', 'GF', 'GS', 'V', 'X', 'S', 'Forma', 'Ranking']
        valori_casa = [casa['Forza']/10, casa['GF'], casa['GS'], casa['V'], casa['X'], casa['S'], forma_casa*10, ranking_casa_gen]
        valori_trasferta = [trasferta['Forza']/10, trasferta['GF'], trasferta['GS'], trasferta['V'], trasferta['X'], trasferta['S'], forma_trasferta*10, ranking_trasferta_gen]
        
        x = range(len(etichette))
        plt.figure(figsize=(14, 8))
        plt.bar(x, valori_casa, width=0.4, label=self.squadra_casa, align='center', alpha=0.8)
        plt.bar([i + 0.4 for i in x], valori_trasferta, width=0.4, label=self.squadra_trasferta, align='center', alpha=0.8)
        plt.xticks([i + 0.2 for i in x], etichette, rotation=45)
        plt.ylabel('Valori (normalizzati)')
        plt.title(f'Confronto Completo: {self.squadra_casa} vs {self.squadra_trasferta}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('confronto_squadre.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Grafico salvato come 'confronto_squadre.png'")
        
    def dettaglio_forma(self):
        """Mostra il dettaglio delle ultime 5 partite per ogni squadra"""
        print(f"\n=== DETTAGLIO FORMA ===")
        
        for squadra in [self.squadra_casa, self.squadra_trasferta]:
            print(f"\n{squadra} - Analisi forma:")
            
            df = self.dati_corrente.copy()
            
            # Partite in casa (quando la squadra gioca in casa)
            partite_casa = df[df['Casa'] == squadra].tail(5)
            print("  🏠 In CASA (ultime 5): ", end="")
            for _, partita in partite_casa.iterrows():
                if partita['GoalCasa'] > partita['GoalTrasferta']:
                    print("1 ", end="")  # Vittoria
                elif partita['GoalCasa'] == partita['GoalTrasferta']:
                    print("X ", end="")  # Pareggio
                else:
                    print("2 ", end="")  # Sconfitta
            if len(partite_casa) < 5:
                for _ in range(5 - len(partite_casa)):
                    print("- ", end="")
            print()
            
            # Partite in trasferta (quando la squadra gioca fuori casa)
            partite_trasferta = df[df['Trasferta'] == squadra].tail(5)
            print("  ✈️  In TRASFERTA (ultime 5): ", end="")
            for _, partita in partite_trasferta.iterrows():
                if partita['GoalTrasferta'] > partita['GoalCasa']:
                    print("1 ", end="")  # Vittoria
                elif partita['GoalTrasferta'] == partita['GoalCasa']:
                    print("X ", end="")  # Pareggio
                else:
                    print("2 ", end="")  # Sconfitta
            if len(partite_trasferta) < 5:
                for _ in range(5 - len(partite_trasferta)):
                    print("- ", end="")
            print()
            
            # Risultati generali (tutte le partite insieme)
            partite_generali = df[(df['Casa'] == squadra) | (df['Trasferta'] == squadra)].tail(5)
            print("  📊 GENERALE (ultime 5): ", end="")
            for _, partita in partite_generali.iterrows():
                if partita['Casa'] == squadra:  # Squadra in casa
                    if partita['GoalCasa'] > partita['GoalTrasferta']:
                        print("1 ", end="")  # Vittoria
                    elif partita['GoalCasa'] == partita['GoalTrasferta']:
                        print("X ", end="")  # Pareggio
                    else:
                        print("2 ", end="")  # Sconfitta
                else:  # Squadra in trasferta
                    if partita['GoalTrasferta'] > partita['GoalCasa']:
                        print("1 ", end="")  # Vittoria
                    elif partita['GoalTrasferta'] == partita['GoalCasa']:
                        print("X ", end="")  # Pareggio
                    else:
                        print("2 ", end="")  # Sconfitta
            if len(partite_generali) < 5:
                for _ in range(5 - len(partite_generali)):
                    print("- ", end="")
            print(" ← Usati per calcolo forma")
            
            forma = self._calcola_forma_squadra(squadra, 'generali')
            print(f"  💪 Media punti/partita: {forma:.2f}/3.0")
    
    def _crea_classifica(self, df, where='generali'):
        """Crea classifica dalle statistiche aggregate"""
        stats = self._aggregazione_statistiche(df)
        classifica_data = []
        
        for squadra in stats.index:
            if where == 'generali':
                punti = stats.loc[squadra, 'V'] * 3 + stats.loc[squadra, 'X']
                partite = stats.loc[squadra, 'PG']
                vittorie = stats.loc[squadra, 'V']
                pareggi = stats.loc[squadra, 'X']
                sconfitte = stats.loc[squadra, 'S']
                gf = stats.loc[squadra, 'GF']
                gs = stats.loc[squadra, 'GS']
            elif where == 'casa':
                punti = stats.loc[squadra, 'V_casa'] * 3 + stats.loc[squadra, 'X_casa']
                partite = stats.loc[squadra, 'PG_casa']
                vittorie = stats.loc[squadra, 'V_casa']
                pareggi = stats.loc[squadra, 'X_casa']
                sconfitte = stats.loc[squadra, 'S_casa']
                gf = stats.loc[squadra, 'GF_casa']
                gs = stats.loc[squadra, 'GS_casa']
            elif where == 'trasferta':
                punti = stats.loc[squadra, 'V_trasferta'] * 3 + stats.loc[squadra, 'X_trasferta']
                partite = stats.loc[squadra, 'PG_trasferta']
                vittorie = stats.loc[squadra, 'V_trasferta']
                pareggi = stats.loc[squadra, 'X_trasferta']
                sconfitte = stats.loc[squadra, 'S_trasferta']
                gf = stats.loc[squadra, 'GF_trasferta']
                gs = stats.loc[squadra, 'GS_trasferta']
            
            dr = gf - gs
            
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
        
        classifica_df = pd.DataFrame(classifica_data)
        classifica_df = classifica_df.sort_values(['Punti', 'DR', 'GF'], ascending=[False, False, False])
        classifica_df['Posizione'] = range(1, len(classifica_df) + 1)
        
        return classifica_df

    def _mostra_ranking_campionato_attuale(self):
        """Mostra il ranking delle squadre nel campionato attuale"""
        print(f"\n=== RANKING CAMPIONATO ATTUALE ===")
            
        try:
            # Ranking generale
            classifica_generale = self._crea_classifica(self.dati_corrente, 'generali')
            pos_casa_gen = classifica_generale[classifica_generale['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
            pos_trasferta_gen = classifica_generale[classifica_generale['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
            
            # Ranking casa
            classifica_casa = self._crea_classifica(self.dati_corrente, 'casa')
            pos_casa_casa = classifica_casa[classifica_casa['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
            pos_trasferta_casa = classifica_casa[classifica_casa['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
            
            # Ranking trasferta
            classifica_trasferta = self._crea_classifica(self.dati_corrente, 'trasferta')
            pos_casa_trasf = classifica_trasferta[classifica_trasferta['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
            pos_trasferta_trasf = classifica_trasferta[classifica_trasferta['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
            
            print(f"\n📊 GENERALE:")
            print(f"  {self.squadra_casa}: {pos_casa_gen}° posto")
            print(f"  {self.squadra_trasferta}: {pos_trasferta_gen}° posto")
            
            print(f"\n🏠 IN CASA:")
            print(f"  {self.squadra_casa}: {pos_casa_casa}° posto")
            print(f"  {self.squadra_trasferta}: {pos_trasferta_casa}° posto")
            
            print(f"\n✈️  IN TRASFERTA:")
            print(f"  {self.squadra_casa}: {pos_casa_trasf}° posto")
            print(f"  {self.squadra_trasferta}: {pos_trasferta_trasf}° posto")
            
        except Exception as e:
            print(f"Errore nel calcolo del ranking: {e}")
    
    def _calcola_ranking_ultime_5(self, where='generali'):
        """Calcola il ranking basato sulle ultime 5 partite"""
        df = self.dati_corrente.copy()
        tutte_squadre = set(df['Casa'].unique()) | set(df['Trasferta'].unique())
        ranking_data = []
        
        for squadra in tutte_squadre:
            try:
                forma = self._calcola_forma_squadra(squadra, where)
                
                # Trova le ultime partite per contare quante sono
                if where == 'generali':
                    partite_squadra = df[(df['Casa'] == squadra) | (df['Trasferta'] == squadra)]
                elif where == 'casa':
                    partite_squadra = df[df['Casa'] == squadra]
                elif where == 'trasferta':
                    partite_squadra = df[df['Trasferta'] == squadra]
                
                ultime_partite = partite_squadra.tail(5)
                punti = forma * len(ultime_partite)
                
                ranking_data.append({
                    'Squadra': squadra,
                    'Punti': punti,
                    'Partite': len(ultime_partite),
                    'Media': forma
                })
            except:
                continue
        
        # Ordina per punti e media
        ranking_df = pd.DataFrame(ranking_data)
        if not ranking_df.empty:
            ranking_df = ranking_df.sort_values(['Punti', 'Media'], ascending=[False, False])
            ranking_df['Posizione'] = range(1, len(ranking_df) + 1)
        
        return ranking_df
    
    def _mostra_ranking_ultime_5_partite(self):
        """Mostra il ranking basato sulle ultime 5 partite"""
        print(f"\n=== RANKING ULTIME 5 PARTITE ===")
        
        try:
            # Ranking generale ultime 5
            ranking_gen = self._calcola_ranking_ultime_5('generali')
            pos_casa_gen = ranking_gen[ranking_gen['Squadra'] == self.squadra_casa]['Posizione']
            pos_trasferta_gen = ranking_gen[ranking_gen['Squadra'] == self.squadra_trasferta]['Posizione']
            
            # Ranking casa ultime 5
            ranking_casa = self._calcola_ranking_ultime_5('casa')
            pos_casa_casa = ranking_casa[ranking_casa['Squadra'] == self.squadra_casa]['Posizione']
            pos_trasferta_casa = ranking_casa[ranking_casa['Squadra'] == self.squadra_trasferta]['Posizione']
            
            # Ranking trasferta ultime 5
            ranking_trasf = self._calcola_ranking_ultime_5('trasferta')
            pos_casa_trasf = ranking_trasf[ranking_trasf['Squadra'] == self.squadra_casa]['Posizione']
            pos_trasferta_trasf = ranking_trasf[ranking_trasf['Squadra'] == self.squadra_trasferta]['Posizione']
            
            print(f"\n📊 GENERALE (ultime 5):")
            casa_pos_gen = pos_casa_gen.iloc[0] if not pos_casa_gen.empty else "N/A"
            trasf_pos_gen = pos_trasferta_gen.iloc[0] if not pos_trasferta_gen.empty else "N/A"
            print(f"  {self.squadra_casa}: {casa_pos_gen}° posto")
            print(f"  {self.squadra_trasferta}: {trasf_pos_gen}° posto")
            
            print(f"\n🏠 IN CASA (ultime 5):")
            casa_pos_casa = pos_casa_casa.iloc[0] if not pos_casa_casa.empty else "N/A"
            trasf_pos_casa = pos_trasferta_casa.iloc[0] if not pos_trasferta_casa.empty else "N/A"
            print(f"  {self.squadra_casa}: {casa_pos_casa}° posto")
            print(f"  {self.squadra_trasferta}: {trasf_pos_casa}° posto")
            
            print(f"\n✈️  IN TRASFERTA (ultime 5):")
            casa_pos_trasf = pos_casa_trasf.iloc[0] if not pos_casa_trasf.empty else "N/A"
            trasf_pos_trasf = pos_trasferta_trasf.iloc[0] if not pos_trasferta_trasf.empty else "N/A"
            print(f"  {self.squadra_casa}: {casa_pos_trasf}° posto")
            print(f"  {self.squadra_trasferta}: {trasf_pos_trasf}° posto")
            
        except Exception as e:
            print(f"Errore nel calcolo del ranking ultime 5: {e}")
    
    def _mostra_ranking_storico(self):
        """Mostra il ranking delle squadre nei campionati precedenti"""
        print(f"\n=== RANKING CAMPIONATI PRECEDENTI ===")
        
        if self.dati_storico is None:
            print("Dati storici non disponibili")
            return
            
        try:
            # Verifica se le squadre esistono nei dati storici
            squadre_storiche = set(self.dati_storico['Casa'].unique()) | set(self.dati_storico['Trasferta'].unique())
            
            if self.squadra_casa not in squadre_storiche:
                print(f"⚠️  {self.squadra_casa} non presente nei campionati precedenti")
                casa_disponibile = False
            else:
                casa_disponibile = True
                
            if self.squadra_trasferta not in squadre_storiche:
                print(f"⚠️  {self.squadra_trasferta} non presente nei campionati precedenti")
                trasferta_disponibile = False
            else:
                trasferta_disponibile = True
            
            if not casa_disponibile and not trasferta_disponibile:
                print("Nessuna delle due squadre ha dati storici disponibili")
                return
            
            # Ranking generale storico
            classifica_storica_gen = self._crea_classifica(self.dati_storico, 'generali')
            
            # Ranking casa storico
            classifica_storica_casa = self._crea_classifica(self.dati_storico, 'casa')
            
            # Ranking trasferta storico
            classifica_storica_trasf = self._crea_classifica(self.dati_storico, 'trasferta')
            
            print(f"\n📊 GENERALE (campionati precedenti):")
            if casa_disponibile:
                pos_casa_gen = classifica_storica_gen[classifica_storica_gen['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
                print(f"  {self.squadra_casa}: {pos_casa_gen}° posto")
            if trasferta_disponibile:
                pos_trasferta_gen = classifica_storica_gen[classifica_storica_gen['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
                print(f"  {self.squadra_trasferta}: {pos_trasferta_gen}° posto")
            
            print(f"\n🏠 IN CASA (campionati precedenti):")
            if casa_disponibile:
                pos_casa_casa = classifica_storica_casa[classifica_storica_casa['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
                print(f"  {self.squadra_casa}: {pos_casa_casa}° posto")
            if trasferta_disponibile:
                pos_trasferta_casa = classifica_storica_casa[classifica_storica_casa['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
                print(f"  {self.squadra_trasferta}: {pos_trasferta_casa}° posto")
            
            print(f"\n✈️  IN TRASFERTA (campionati precedenti):")
            if casa_disponibile:
                pos_casa_trasf = classifica_storica_trasf[classifica_storica_trasf['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
                print(f"  {self.squadra_casa}: {pos_casa_trasf}° posto")
            if trasferta_disponibile:
                pos_trasferta_trasf = classifica_storica_trasf[classifica_storica_trasf['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
                print(f"  {self.squadra_trasferta}: {pos_trasferta_trasf}° posto")
            
            # Mostra anche statistiche aggregate storiche
            if casa_disponibile or trasferta_disponibile:
                print(f"\n📈 STATISTICHE STORICHE AGGREGATE:")
                stats_storiche = self._aggregazione_statistiche(self.dati_storico)
                
                if casa_disponibile:
                    casa_stats = stats_storiche.loc[self.squadra_casa]
                    print(f"  {self.squadra_casa}: {int(casa_stats['PG'])} partite, {int(casa_stats['V'])}-{int(casa_stats['X'])}-{int(casa_stats['S'])}, {int(casa_stats['GF'])}-{int(casa_stats['GS'])}")
                
                if trasferta_disponibile:
                    trasf_stats = stats_storiche.loc[self.squadra_trasferta]
                    print(f"  {self.squadra_trasferta}: {int(trasf_stats['PG'])} partite, {int(trasf_stats['V'])}-{int(trasf_stats['X'])}-{int(trasf_stats['S'])}, {int(trasf_stats['GF'])}-{int(trasf_stats['GS'])}")
            
        except Exception as e:
            print(f"Errore nel calcolo del ranking storico: {e}")
    
    def _mostra_scontri_diretti_storici(self):
        """Mostra gli scontri diretti storici tra le due squadre"""
        print(f"\n=== SCONTRI DIRETTI STORICI ===")
        
        if self.dati_storico is None:
            print("Dati storici non disponibili")
            return
        
        try:
            # Trova tutti gli scontri diretti storici
            scontri_diretti = self.dati_storico[
                ((self.dati_storico['Casa'] == self.squadra_casa) & (self.dati_storico['Trasferta'] == self.squadra_trasferta)) |
                ((self.dati_storico['Casa'] == self.squadra_trasferta) & (self.dati_storico['Trasferta'] == self.squadra_casa))
            ]
            
            if len(scontri_diretti) == 0:
                print(f"Nessuno scontro diretto storico trovato tra {self.squadra_casa} e {self.squadra_trasferta}")
                return
            
            print(f"Trovati {len(scontri_diretti)} scontri diretti storici")
            
            # Calcola le statistiche degli scontri diretti
            vittorie_casa = 0
            vittorie_trasferta = 0
            pareggi = 0
            
            for _, partita in scontri_diretti.iterrows():
                if partita['Casa'] == self.squadra_casa:
                    # Squadra casa gioca effettivamente in casa
                    if partita['GoalCasa'] > partita['GoalTrasferta']:
                        vittorie_casa += 1
                    elif partita['GoalCasa'] == partita['GoalTrasferta']:
                        pareggi += 1
                    else:
                        vittorie_trasferta += 1
                else:
                    # Squadra casa gioca in trasferta (inverti la logica)
                    if partita['GoalTrasferta'] > partita['GoalCasa']:
                        vittorie_casa += 1
                    elif partita['GoalCasa'] == partita['GoalTrasferta']:
                        pareggi += 1
                    else:
                        vittorie_trasferta += 1
            
            print(f"\n🏆 BILANCIO SCONTRI DIRETTI:")
            print(f"  {self.squadra_casa}: {vittorie_casa} vittorie")
            print(f"  {self.squadra_trasferta}: {vittorie_trasferta} vittorie")
            print(f"  Pareggi: {pareggi}")
            
            # Mostra le ultime 5 partite tra le due squadre
            ultime_5_scontri = scontri_diretti.tail(5)
            print(f"\n📅 ULTIME {len(ultime_5_scontri)} PARTITE TRA LE DUE SQUADRE:")
            
            for _, partita in ultime_5_scontri.iterrows():
                data = f"{partita['GiornoMese']}/{partita['Mese']}"
                risultato = f"{partita['Casa']} {partita['GoalCasa']}-{partita['GoalTrasferta']} {partita['Trasferta']}"
                print(f"  {data}: {risultato}")
                
        except Exception as e:
            print(f"Errore nel calcolo degli scontri diretti: {e}")
    
    def _analisi_ai_e_consigli(self, p1, px, p2, forma_casa, forma_trasferta, goal_totali, prob_under_25, prob_over_25):
        """Analisi AI completa con raccomandazioni scommesse intelligenti"""
        print(f"\n🤖 === ANALISI AI E RACCOMANDAZIONI SCOMMESSE ===")
        
        try:
            # Raccolta dati per l'analisi
            casa_stats = self.statistiche.loc[self.squadra_casa]
            trasferta_stats = self.statistiche.loc[self.squadra_trasferta]
            
            # Ottieni ranking
            classifica = self._crea_classifica(self.dati_corrente, 'generali')
            pos_casa = classifica[classifica['Squadra'] == self.squadra_casa]['Posizione'].iloc[0]
            pos_trasferta = classifica[classifica['Squadra'] == self.squadra_trasferta]['Posizione'].iloc[0]
            
            # Analisi scontri diretti
            scontri_info = self._analizza_scontri_diretti_per_ai()
            
            # Determina la scommessa principale
            scommessa_principale = self._determina_scommessa_principale(p1, px, p2)
            
            # Analisi rischio/rendimento
            livello_rischio = self._calcola_livello_rischio(p1, px, p2, forma_casa, forma_trasferta)
            
            print(f"\n🎯 **SCOMMESSA CONSIGLIATA: {scommessa_principale['nome']}**")
            print(f"💰 Probabilità di successo: {scommessa_principale['probabilita']:.0%}")
            print(f"⚡ Livello rischio: {livello_rischio}")
            
            print(f"\n🧠 **MOTIVAZIONE TECNICA:**")
            
            # Analisi predizione
            if p1 > p2 and p1 > px:
                favorito = self.squadra_casa
                prob_favorito = p1
            elif p2 > p1 and p2 > px:
                favorito = self.squadra_trasferta
                prob_favorito = p2
            else:
                favorito = "Equilibrio"
                prob_favorito = max(p1, p2)
            
            print(f"📊 Predizione esito: {favorito} favorito con {prob_favorito:.0%} di probabilità")
            print(f"⚽ Goal previsti: {self.squadra_casa} vs {self.squadra_trasferta} → {goal_totali:.1f} goal totali")
            
            # Analisi forma
            diff_forma = forma_casa - forma_trasferta
            if abs(diff_forma) < 0.3:
                forma_analisi = "Forma equilibrata tra le squadre"
            elif diff_forma > 0:
                forma_analisi = f"{self.squadra_casa} in forma migliore ({forma_casa:.1f} vs {forma_trasferta:.1f})"
            else:
                forma_analisi = f"{self.squadra_trasferta} in forma migliore ({forma_trasferta:.1f} vs {forma_casa:.1f})"
            print(f"🔥 Forma recente: {forma_analisi}")
            
            # Analisi ranking
            if pos_casa < pos_trasferta:
                ranking_analisi = f"{self.squadra_casa} meglio classificato ({pos_casa}° vs {pos_trasferta}°)"
            elif pos_trasferta < pos_casa:
                ranking_analisi = f"{self.squadra_trasferta} meglio classificato ({pos_trasferta}° vs {pos_casa}°)"
            else:
                ranking_analisi = f"Squadre alla pari in classifica ({pos_casa}° posto)"
            print(f"🏆 Ranking attuale: {ranking_analisi}")
            
            # Scontri diretti
            if scontri_info:
                print(f"⚔️  Scontri diretti: {scontri_info}")
            
            # Raccomandazioni aggiuntive
            self._raccomandazioni_aggiuntive(prob_under_25, prob_over_25, p1, px, p2, forma_casa, forma_trasferta)
            
            # Commento finale intelligente
            self._commento_finale_ai(scommessa_principale, p1, px, p2, forma_casa, forma_trasferta, pos_casa, pos_trasferta)
            
        except Exception as e:
            print(f"Errore nell'analisi AI: {e}")
    
    def _determina_scommessa_principale(self, p1, px, p2):
        """Determina la scommessa principale basata su probabilità e rischio"""
        
        # Strategia conservativa per probabilità molto alte
        if p1 >= 0.65:
            return {"nome": "Doppia Chance 1X (Casa o Pareggio)", "probabilita": p1 + px}
        elif p2 >= 0.65:
            return {"nome": "Doppia Chance X2 (Pareggio o Trasferta)", "probabilita": px + p2}
        
        # Strategia per favorito chiaro
        elif p1 >= 0.55:
            return {"nome": f"1 (Vittoria {self.squadra_casa})", "probabilita": p1}
        elif p2 >= 0.55:
            return {"nome": f"2 (Vittoria {self.squadra_trasferta})", "probabilita": p2}
        
        # Strategia per equilibrio
        elif px >= 0.25:
            return {"nome": "Doppia Chance 12 (Vittoria di una delle due)", "probabilita": p1 + p2}
        
        # Default: doppia chance del più probabile
        else:
            if p1 > p2:
                return {"nome": "Doppia Chance 1X (Casa o Pareggio)", "probabilita": p1 + px}
            else:
                return {"nome": "Doppia Chance X2 (Pareggio o Trasferta)", "probabilita": px + p2}
    
    def _calcola_livello_rischio(self, p1, px, p2, forma_casa, forma_trasferta):
        """Calcola il livello di rischio della scommessa"""
        max_prob = max(p1, px, p2)
        diff_forma = abs(forma_casa - forma_trasferta)
        
        if max_prob >= 0.70 and diff_forma < 0.5:
            return "🟢 BASSO"
        elif max_prob >= 0.60 or diff_forma > 1.0:
            return "🟡 MEDIO"
        else:
            return "🔴 ALTO"
    
    def _analizza_scontri_diretti_per_ai(self):
        """Analizza i scontri diretti per l'AI"""
        if self.dati_storico is None:
            return None
        
        try:
            scontri_diretti = self.dati_storico[
                ((self.dati_storico['Casa'] == self.squadra_casa) & (self.dati_storico['Trasferta'] == self.squadra_trasferta)) |
                ((self.dati_storico['Casa'] == self.squadra_trasferta) & (self.dati_storico['Trasferta'] == self.squadra_casa))
            ]
            
            if len(scontri_diretti) == 0:
                return "Nessun precedente storico"
            
            vittorie_casa = 0
            vittorie_trasferta = 0
            pareggi = 0
            
            for _, partita in scontri_diretti.iterrows():
                if partita['Casa'] == self.squadra_casa:
                    if partita['GoalCasa'] > partita['GoalTrasferta']:
                        vittorie_casa += 1
                    elif partita['GoalCasa'] == partita['GoalTrasferta']:
                        pareggi += 1
                    else:
                        vittorie_trasferta += 1
                else:
                    if partita['GoalTrasferta'] > partita['GoalCasa']:
                        vittorie_casa += 1
                    elif partita['GoalCasa'] == partita['GoalTrasferta']:
                        pareggi += 1
                    else:
                        vittorie_trasferta += 1
            
            if vittorie_casa > vittorie_trasferta:
                return f"{self.squadra_casa} dominante ({vittorie_casa}-{vittorie_trasferta}-{pareggi})"
            elif vittorie_trasferta > vittorie_casa:
                return f"{self.squadra_trasferta} dominante ({vittorie_trasferta}-{vittorie_casa}-{pareggi})"
            else:
                return f"Equilibrio storico ({vittorie_casa}-{vittorie_trasferta}-{pareggi})"
                
        except:
            return None
    
    def _raccomandazioni_aggiuntive(self, prob_under_25, prob_over_25, p1, px, p2, forma_casa, forma_trasferta):
        """Fornisce raccomandazioni aggiuntive"""
        print(f"\n📊 **ALTRE OPZIONI INTERESSANTI:**")
        
        # Under/Over
        if prob_under_25 >= 0.60:
            print(f"🎯 Under 2.5 ({prob_under_25:.0%}) → Partita tattica/chiusa")
        elif prob_over_25 >= 0.60:
            print(f"🎯 Over 2.5 ({prob_over_25:.0%}) → Partita ricca di goal")
        
        # Goal squadre
        if forma_casa >= 2.0 and forma_trasferta >= 2.0:
            print(f"⚽ Entrambe le squadre segnano → Buona forma offensiva")
        elif forma_casa <= 1.0 or forma_trasferta <= 1.0:
            print(f"🛡️  Possibile 'No Goal' → Una squadra in difficoltà")
        
        # Combinazioni intelligenti
        max_prob = max(p1, px, p2)
        if max_prob >= 0.60 and prob_under_25 >= 0.55:
            if p1 == max_prob:
                print(f"💡 Combo suggerita: 1 + Under 2.5")
            elif p2 == max_prob:
                print(f"💡 Combo suggerita: 2 + Under 2.5")
            else:
                print(f"💡 Combo suggerita: X + Under 2.5")
    
    def _commento_finale_ai(self, scommessa_principale, p1, px, p2, forma_casa, forma_trasferta, pos_casa, pos_trasferta):
        """Commento finale intelligente"""
        print(f"\n💡 **COMMENTO FINALE AI:**")
        
        # Analisi del contesto
        if forma_casa > forma_trasferta + 0.5 and pos_casa < pos_trasferta:
            commento = f"Il {self.squadra_casa} ha sia forma che ranking migliori. Scelta sicura per la scommessa consigliata."
        elif forma_trasferta > forma_casa + 0.5 and pos_trasferta < pos_casa:
            commento = f"Il {self.squadra_trasferta} è in forma smagliante e meglio classificato. Attenzione al fattore trasferta."
        elif abs(forma_casa - forma_trasferta) < 0.3:
            commento = f"Partita molto equilibrata. La scommessa consigliata bilancia rischio e rendimento."
        else:
            commento = f"Indicatori contrastanti. La scommessa consigliata è la più prudente."
        
        print(commento)
        
        # Consiglio finale basato sulla probabilità
        prob_successo = scommessa_principale['probabilita']
        if prob_successo >= 0.75:
            print(f"🟢 **Confidenza ALTA** - Scommessa consigliata con ottime probabilità di successo.")
        elif prob_successo >= 0.65:
            print(f"🟡 **Confidenza MEDIA** - Scommessa equilibrata, buon rapporto rischio/rendimento.")
        else:
            print(f"🔴 **Confidenza BASSA** - Partita incerta, considera scommesse più conservative.")
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python EsitoDalRanking.py <squadra_casa> <squadra_trasferta>")
        sys.exit()

    squadra_casa = sys.argv[1]
    squadra_trasferta = sys.argv[2]
    predizione = PredizionePartita(squadra_casa, squadra_trasferta, peso_attuale=0.7)
    predizione.prevedi()
    predizione.dettaglio_forma()
    predizione.grafico_confronto()
