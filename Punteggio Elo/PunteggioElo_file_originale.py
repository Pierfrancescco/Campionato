import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Backend non-interattivo per evitare problemi di visualizzazione
import matplotlib.pyplot as plt
import math


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
        """Carica le squadre e inizializza i rating"""
        teams_df = pd.read_csv(self.squadre_file, sep=";")
        
        # Aggiungi colonna InitialRating se non esiste
        if "InitialRating" not in teams_df.columns:
            teams_df["InitialRating"] = 1000
            
        # Salva file rating iniziali
        rating_df = teams_df[["Teams", "InitialRating"]].copy()
        rating_df.to_csv("RatingIniziali.csv", index=False, sep=";")
        
        # Carica rating iniziali
        initial_df = pd.read_csv("RatingIniziali.csv", sep=";")
        self.initial_ratings = dict(zip(initial_df["Teams"], initial_df["InitialRating"]))
    
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
        
        # Bonus casa (opzionale, puoi regolarlo)
        home_advantage = 50 if is_team1_home else -50
        r1_adjusted = r1 + home_advantage
        
        # Calcola probabilità
        prob_team1_win = 1 / (1 + 10 ** ((r2 - r1_adjusted) / 400))
        prob_draw = 0.25  # Stima fissa per il pareggio, puoi migliorarla
        prob_team2_win = 1 - prob_team1_win - prob_draw
        
        # Assicurati che le probabilità siano positive
        if prob_team2_win < 0:
            prob_team2_win = 0.05
            prob_draw = 1 - prob_team1_win - prob_team2_win
        
        # Determina risultato più probabile
        probs = [prob_team1_win, prob_draw, prob_team2_win]
        results = ["1", "X", "2"]
        most_likely = results[probs.index(max(probs))]
        
        # Suggerimenti per goal (basati su differenza rating)
        rating_diff = abs(r1 - r2)
        if rating_diff > 100:
            goals_suggestion = "Over 2.5" if r1_adjusted > r2 else "Under 2.5"
        else:
            goals_suggestion = "Under 2.5"
        
        # Suggerimento doppia chance
        double_chance = None
        if prob_team1_win > 0.4:
            double_chance = "1X"
        elif prob_team2_win > 0.4:
            double_chance = "2X"
        elif prob_draw > 0.3:
            double_chance = "12"
            
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
            "goals_suggestion": goals_suggestion,
            "double_chance": double_chance,
            "rating_difference": round(rating_diff, 1)
        }
    
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
    # Crea il sistema Elo
    elo_system = EloPredictor()
    
    # Esempio di previsione
    team1 = "Juventus"
    team2 = "Milan"
    
    prediction = elo_system.predict_match(team1, team2, is_team1_home=True)
    
    if "error" not in prediction:
        print(f"\n=== PREVISIONE: {team1} vs {team2} ===")
        print(f"Rating {team1}: {prediction['ratings'][team1]}")
        print(f"Rating {team2}: {prediction['ratings'][team2]}")
        print(f"Probabilità 1: {prediction['probabilities']['1']}%")
        print(f"Probabilità X: {prediction['probabilities']['X']}%") 
        print(f"Probabilità 2: {prediction['probabilities']['2']}%")
        print(f"Risultato più probabile: {prediction['most_likely_result']}")
        print(f"Suggerimento goal: {prediction['goals_suggestion']}")
        print(f"Doppia chance: {prediction['double_chance']}")
        
        # Crea grafico di confronto
        elo_system.create_comparison_chart(team1, team2)
    else:
        print(prediction["error"])

