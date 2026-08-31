import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend non-interattivo per evitare problemi di visualizzazione
import matplotlib.pyplot as plt
import math
import sys


class EloPredictor:
    """
    Classe per calcolare rating Elo e fare previsioni sui match
    """
    
    def __init__(self, K=30, squadre_file="squadre.csv", campionato_file="Campionato.CSV"):
        """
        Inizializza il sistema Elo
        
        Args:
            K (int): Fattore K per i calcoli Elo (default: 30)
            squadre_file (str): Path del file con i nomi delle squadre
            campionato_file (str): Path del file con le partite
        """
        self.K = K
        self.squadre_file = squadre_file
        self.campionato_file = campionato_file
        
        # Inizializza rating e storia
        self.ratings = {}
        self.elo_history = {}
        self.matches_history = []
        
        # Carica e processa i dati
        self._load_teams()
        self._load_matches()
        self._calculate_all_elo()
    
    def _load_teams(self):
        """Carica le squadre e calcola i rating iniziali dai campionati precedenti"""
        teams_df = pd.read_csv(self.squadre_file, sep=";")
        
        # Calcola rating iniziali dai campionati precedenti
        self.initial_ratings = self._calculate_initial_ratings_from_history()
        
        # Aggiungi rating calcolati alle squadre
        teams_df["InitialRating"] = teams_df["Teams"].map(
            lambda team: self.initial_ratings.get(team, 1000)
        )
        
        # Salva file rating iniziali
        rating_df = teams_df[["Teams", "InitialRating"]].copy()
        rating_df.to_csv("RatingIniziali.csv", index=False, sep=";")
        
        print(f"Rating iniziali calcolati da {len(self.initial_ratings)} squadre storiche")
    
    def _calculate_initial_ratings_from_history(self):
        """
        Calcola i rating iniziali basandosi sui campionati precedenti
        
        Returns:
            dict: Dizionario con rating iniziali per ogni squadra
        """
        try:
            # Carica dati storici
            historical_df = pd.read_csv("CampionatiPrecedenti.CSV", sep=";")
            historical_matches = historical_df[["Home", "Away", "GoalHome", "GoalAway"]].copy()
            
            # Inizializza rating storici (tutti partono da 1000)
            teams_historical = pd.unique(historical_matches[["Home", "Away"]].values.ravel())
            historical_ratings = {team: 1000.0 for team in teams_historical}
            
            print(f"Processando {len(historical_matches)} partite storiche per {len(teams_historical)} squadre...")
            
            # Calcola Elo sui dati storici
            for idx, row in historical_matches.iterrows():
                if pd.isna(row["Home"]) or pd.isna(row["Away"]):
                    continue
                    
                home, away = row["Home"], row["Away"]
                g_home, g_away = row["GoalHome"], row["GoalAway"]
                
                # Salta se mancano i dati dei goal
                if pd.isna(g_home) or pd.isna(g_away):
                    continue
                
                r_home = historical_ratings.get(home, 1000)
                r_away = historical_ratings.get(away, 1000)

                # Determina risultato
                if g_home > g_away:
                    res_home = 1
                elif g_home == g_away:
                    res_home = 0.5
                else:
                    res_home = 0

                # Aggiorna rating storici
                new_r_home, new_r_away = self._update_elo(r_home, r_away, res_home)
                historical_ratings[home] = new_r_home
                historical_ratings[away] = new_r_away
            
            print(f"Rating storici calcolati. Range: {min(historical_ratings.values()):.1f} - {max(historical_ratings.values()):.1f}")
            return historical_ratings
            
        except FileNotFoundError:
            print("File CampionatiPrecedenti.CSV non trovato. Usando rating di default (1000)")
            return {}
        except Exception as e:
            print(f"Errore nel calcolo rating storici: {e}. Usando rating di default (1000)")
            return {}
    
    def _load_matches(self):
        """Carica le partite del campionato"""
        matches_df = pd.read_csv(self.campionato_file, sep=";")
        self.matches = matches_df[["Home", "Away", "GoalHome", "GoalAway"]].copy()
        
        # Inizializza rating per tutte le squadre presenti nelle partite
        teams = pd.unique(self.matches[["Home", "Away"]].values.ravel())
        self.ratings = {team: self.initial_ratings.get(team, 1000) for team in teams}
        
        # Inizializza storia per ogni squadra
        for team in teams:
            self.elo_history[team] = [self.ratings[team]]
    
    def _update_elo(self, r1, r2, res1):
        """
        Aggiorna i rating Elo per due squadre
        
        Args:
            r1 (float): Rating squadra 1
            r2 (float): Rating squadra 2
            res1 (float): Risultato squadra 1 (1=vittoria, 0.5=pareggio, 0=sconfitta)
            
        Returns:
            tuple: Nuovi rating (r1_new, r2_new)
        """
        expected1 = 1 / (1 + 10 ** ((r2 - r1) / 400))
        expected2 = 1 - expected1
        score1 = res1
        score2 = 1 - res1
        r1_new = r1 + self.K * (score1 - expected1)
        r2_new = r2 + self.K * (score2 - expected2)
        return r1_new, r2_new
    
    def _calculate_all_elo(self):
        """Calcola tutti i rating Elo basandosi sulla storia delle partite"""
        for _, row in self.matches.iterrows():
            home, away = row["Home"], row["Away"]
            g_home, g_away = row["GoalHome"], row["GoalAway"]
            r_home, r_away = self.ratings[home], self.ratings[away]

            # Determina risultato
            if g_home > g_away:
                res_home = 1
            elif g_home == g_away:
                res_home = 0.5
            else:
                res_home = 0

            # Aggiorna rating
            new_r_home, new_r_away = self._update_elo(r_home, r_away, res_home)
            self.ratings[home], self.ratings[away] = new_r_home, new_r_away
            
            # Salva nella storia
            self.elo_history[home].append(new_r_home)
            self.elo_history[away].append(new_r_away)
            
            # Salva match nella storia
            self.matches_history.append({
                'home': home,
                'away': away,
                'goals_home': g_home,
                'goals_away': g_away,
                'result': res_home,
                'elo_home_after': new_r_home,
                'elo_away_after': new_r_away
            })
    
    def predict_match(self, team1, team2, is_team1_home=True):
        """
        Predice l'esito di una partita tra due squadre
        
        Args:
            team1 (str): Nome prima squadra
            team2 (str): Nome seconda squadra  
            is_team1_home (bool): Se team1 gioca in casa (default: True)
            
        Returns:
            dict: Dizionario con previsioni e statistiche
        """
        if team1 not in self.ratings or team2 not in self.ratings:
            return {"error": f"Una o entrambe le squadre non trovate: {team1}, {team2}"}
        
        r1 = self.ratings[team1]
        r2 = self.ratings[team2]
        
        # Bonus casa
        home_advantage = 50 if is_team1_home else -50
        r1_adjusted = r1 + home_advantage
        
        # Calcola probabilità base
        prob_team1_win = 1 / (1 + 10 ** ((r2 - r1_adjusted) / 400))
        
        # Calcolo pareggio più sofisticato basato sulla differenza di rating
        rating_diff = abs(r1_adjusted - r2)
        if rating_diff < 25:
            prob_draw = 0.45  # Squadre praticamente identiche - PAREGGIO MOLTO PROBABILE
        elif rating_diff < 50:
            prob_draw = 0.38  # Squadre molto equilibrate
        elif rating_diff < 75:
            prob_draw = 0.32  # Squadre equilibrate
        elif rating_diff < 100:
            prob_draw = 0.26  # Squadre abbastanza equilibrate
        elif rating_diff < 150:
            prob_draw = 0.20  # Leggero divario
        else:
            prob_draw = 0.15  # Grande divario
        
        # Forma recente (calcolata prima per influenzare il pareggio)
        recent_form = self._get_recent_form(team1, team2)
        form_diff = abs(recent_form[team1] - recent_form[team2])
        
        # Se forme simili e rating simili = aumenta probabilità pareggio
        if rating_diff < 50 and form_diff < 0.15:
            prob_draw += 0.08  # Bonus pareggio per forme simili
            prob_draw = min(0.50, prob_draw)  # Massimo 50% per il pareggio
        
        # Ricalcola probabilità di vittoria considerando il pareggio
        remaining_prob = 1 - prob_draw
        prob_team1_win = prob_team1_win * remaining_prob
        prob_team2_win = remaining_prob - prob_team1_win
        
        # Assicurati che le probabilità siano positive
        if prob_team2_win < 0:
            prob_team2_win = 0.05
            prob_team1_win = remaining_prob - prob_team2_win
        
        # Determina risultato più probabile
        probs = [prob_team1_win, prob_draw, prob_team2_win]
        results = ["1", "X", "2"]
        most_likely = results[probs.index(max(probs))]
        
        # Calcolo Under/Over più accurato basato sui rating e sulla storia
        under_over_analysis = self._calculate_under_over(team1, team2, r1, r2)
        
        # Suggerimento doppia chance (criteri più intelligenti)
        double_chance = None
        
        # Se una squadra ha probabilità alta -> 1X o 2X
        if prob_team1_win > 0.42:
            double_chance = "1X"
        elif prob_team2_win > 0.42:
            double_chance = "2X"
        # Se il pareggio è probabile -> 12 (escludi pareggio)
        elif prob_draw > 0.30:
            double_chance = "12"
        # Partita molto equilibrata -> prendi la squadra di casa + pareggio
        elif abs(prob_team1_win - prob_team2_win) < 0.15:
            double_chance = "1X" if is_team1_home else "2X"
            
        return {
            "team1": team1,
            "team2": team2,
            "team1_home": is_team1_home,
            "ratings": {
                team1: round(r1, 1),
                team2: round(r2, 1)
            },
            "probabilities": {
                "1": round(prob_team1_win * 100, 1),
                "X": round(prob_draw * 100, 1), 
                "2": round(prob_team2_win * 100, 1)
            },
            "most_likely_result": most_likely,
            "under_over": under_over_analysis,
            "recent_form": recent_form,
            "double_chance": double_chance,
            "rating_difference": round(rating_diff, 1),
            "confidence": self._calculate_confidence(probs)
        }
    
    def _calculate_under_over(self, team1, team2, r1, r2):
        """Calcola probabilità Under/Over 2.5 goal"""
        # Analizza goal dalle partite storiche
        goals_data = self._analyze_goals_history(team1, team2)
        
        # Fattore rating: squadre più forti tendono a segnare di più
        rating_factor = (r1 + r2) / 2000  # Normalizzato
        
        # Probabilità base Under/Over
        if goals_data['avg_goals'] > 2.8:
            prob_over = 0.65 + (rating_factor - 1) * 0.1
        elif goals_data['avg_goals'] > 2.3:
            prob_over = 0.55 + (rating_factor - 1) * 0.1
        else:
            prob_over = 0.40 + (rating_factor - 1) * 0.1
        
        prob_over = max(0.2, min(0.8, prob_over))
        prob_under = 1 - prob_over
        
        return {
            "under_2_5": round(prob_under * 100, 1),
            "over_2_5": round(prob_over * 100, 1),
            "suggestion": "Over 2.5" if prob_over > 0.55 else "Under 2.5",
            "avg_goals_history": round(goals_data['avg_goals'], 1)
        }
    
    def _analyze_goals_history(self, team1, team2):
        """Analizza la storia dei goal delle squadre"""
        team1_goals = []
        team2_goals = []
        
        for match in self.matches_history:
            if match['home'] == team1 or match['away'] == team1:
                if match['home'] == team1:
                    team1_goals.append(match['goals_home'] + match['goals_away'])
                else:
                    team1_goals.append(match['goals_home'] + match['goals_away'])
            
            if match['home'] == team2 or match['away'] == team2:
                if match['home'] == team2:
                    team2_goals.append(match['goals_home'] + match['goals_away'])
                else:
                    team2_goals.append(match['goals_home'] + match['goals_away'])
        
        all_goals = team1_goals + team2_goals
        avg_goals = sum(all_goals) / len(all_goals) if all_goals else 2.5
        
        return {
            "avg_goals": avg_goals,
            "team1_avg": sum(team1_goals) / len(team1_goals) if team1_goals else 2.5,
            "team2_avg": sum(team2_goals) / len(team2_goals) if team2_goals else 2.5
        }
    
    def _get_recent_form(self, team1, team2, last_matches=5):
        """Calcola la forma recente delle squadre (ultimi 5 match)"""
        def get_team_form(team):
            recent_results = []
            count = 0
            
            for match in reversed(self.matches_history):
                if count >= last_matches:
                    break
                    
                if match['home'] == team:
                    if match['result'] == 1:
                        recent_results.append(3)  # Vittoria
                    elif match['result'] == 0.5:
                        recent_results.append(1)  # Pareggio
                    else:
                        recent_results.append(0)  # Sconfitta
                    count += 1
                elif match['away'] == team:
                    if match['result'] == 0:
                        recent_results.append(3)  # Vittoria
                    elif match['result'] == 0.5:
                        recent_results.append(1)  # Pareggio
                    else:
                        recent_results.append(0)  # Sconfitta
                    count += 1
            
            return sum(recent_results) / (3 * len(recent_results)) if recent_results else 0.5
        
        return {
            team1: round(get_team_form(team1), 2),
            team2: round(get_team_form(team2), 2)
        }
    
    def _calculate_confidence(self, probabilities):
        """Calcola il livello di confidenza della previsione"""
        max_prob = max(probabilities)
        if max_prob > 0.6:
            return "Alta"
        elif max_prob > 0.45:
            return "Media"
        else:
            return "Bassa"
    
    def get_team_rating(self, team_name):
        """Ottieni il rating attuale di una squadra"""
        return self.ratings.get(team_name, None)
    
    def get_all_ratings(self, sorted_by_rating=True):
        """Ottieni tutti i rating"""
        if sorted_by_rating:
            return dict(sorted(self.ratings.items(), key=lambda x: x[1], reverse=True))
        return self.ratings.copy()
    
    def create_comparison_chart(self, team1, team2, save_path="confronto_elo.png"):
        """
        Crea un grafico di confronto tra due squadre
        
        Args:
            team1 (str): Nome prima squadra
            team2 (str): Nome seconda squadra
            save_path (str): Path dove salvare il grafico
        """
        if team1 not in self.elo_history or team2 not in self.elo_history:
            print(f"Errore: Una o entrambe le squadre non trovate: {team1}, {team2}")
            return
        
        plt.figure(figsize=(12, 6))
        
        # Plot evoluzione rating
        matches_range = range(len(self.elo_history[team1]))
        plt.plot(matches_range, self.elo_history[team1], 
                label=f"{team1}", color="blue", linewidth=2, marker='o', markersize=4)
        plt.plot(matches_range, self.elo_history[team2], 
                label=f"{team2}", color="red", linewidth=2, marker='s', markersize=4)
        
        # Configurazione grafico
        plt.title(f"Confronto Rating Elo: {team1} vs {team2}", fontsize=14, fontweight='bold')
        plt.xlabel("Partite Giocate", fontsize=12)
        plt.ylabel("Rating Elo", fontsize=12)
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        
        # Aggiungi rating attuali come annotazioni
        current_rating_1 = self.elo_history[team1][-1]
        current_rating_2 = self.elo_history[team2][-1]
        
        plt.annotate(f'{current_rating_1:.1f}', 
                    xy=(len(matches_range)-1, current_rating_1),
                    xytext=(5, 5), textcoords='offset points',
                    color='blue', fontweight='bold')
        plt.annotate(f'{current_rating_2:.1f}', 
                    xy=(len(matches_range)-1, current_rating_2),
                    xytext=(5, -15), textcoords='offset points',
                    color='red', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Grafico di confronto salvato come '{save_path}'")


# Esempio di utilizzo
if __name__ == "__main__":
    # Verifica che siano stati forniti esattamente 2 argomenti
    if len(sys.argv) != 3:
        print("Uso: python PunteggioElo.py <squadra1> <squadra2>")
        print("Esempio: python PunteggioElo.py Lazio Torino")
        sys.exit(1)

    # Ottieni le squadre dagli argomenti della riga di comando
    team1 = sys.argv[1]
    team2 = sys.argv[2]
    # Crea il sistema Elo
    elo_system = EloPredictor()
    
    # # Esempio di previsione
    # team1 = "Lazio"
    # team2 = "Torino"
    
    prediction = elo_system.predict_match(team1, team2, is_team1_home=True)
    
    if "error" not in prediction:
        print(f"\n=== PREVISIONE: {team1} vs {team2} ===")
        print(f"Rating {team1}: {prediction['ratings'][team1]}")
        print(f"Rating {team2}: {prediction['ratings'][team2]}")
        print(f"Probabilità 1: {prediction['probabilities']['1']}%")
        print(f"Probabilità X: {prediction['probabilities']['X']}%") 
        print(f"Probabilità 2: {prediction['probabilities']['2']}%")
        print(f"Risultato più probabile: {prediction['most_likely_result']}")
        print(f"Confidenza: {prediction['confidence']}")
        print(f"Under 2.5: {prediction['under_over']['under_2_5']}%")
        print(f"Over 2.5: {prediction['under_over']['over_2_5']}%")
        print(f"Suggerimento goal: {prediction['under_over']['suggestion']}")
        print(f"Doppia chance: {prediction['double_chance']}")
        print(f"Forma recente {team1}: {prediction['recent_form'][team1]}")
        print(f"Forma recente {team2}: {prediction['recent_form'][team2]}")
        
        # Crea grafico di confronto
        elo_system.create_comparison_chart(team1, team2)
    else:
        print(prediction["error"])

