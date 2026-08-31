from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from numpy import random as rnd
import os
# I miei moduli
from ErrorManager import catturaEccezione
from EstrazioneDati import EstrazioneDati
from myPath import myPath, myFile

class Grafici:
    """
    Classe per la generazione di grafici statistici relativi ai risultati di una squadra di calcio.
    Args:
        path (str): Percorso al file dei dati statistici.
        squadra (str): Nome della squadra di cui estrarre le statistiche.
        where (str, opzionale): Tipo di statistiche da estrarre ('generali', 'casa', 'trasferta'). Default 'generali'.
        squadraDi (str, opzionale): Specifica se la squadra è di casa o trasferta ('casa', 'trasferta'). Default 'casa'.
    Attributi:
        path (str): Percorso al file dei dati.
        squadra (str): Nome della squadra.
        where (str): Tipo di statistica selezionata.
        squadraDi (str): Casa o trasferta.
        estrattore (EstrazioneDati): Istanza della classe per l'estrazione dei dati.
    Metodi:
        crea_grafico():
            Genera e salva un grafico a barre con il numero di vittorie, pareggi e sconfitte della squadra selezionata.
    """
    @catturaEccezione
    def __init__(self, path: str, squadra: str, where: str = 'generali', squadraIn: str = 'casa'):
        self.path = path
        self.squadra = squadra
        self.where = where  # l'opzione è tra generali, casa, trasferta
        self.squadraIn = squadraIn  # l'opzione è tra casa, trasferta
        # referenzio le classi
        self.estrattore = EstrazioneDati(self.path)
        
        

    @catturaEccezione
    def crea_graficoStatistiche(self):
        """
        Crea e salva un grafico a barre che mostra il numero di vittorie, pareggi e sconfitte 
        per una squadra specifica. I dati vengono estratti tramite l'oggetto 'estrattore' 
        e rappresentati con barre colorate (verde per vittorie, giallo per pareggi, rosso per sconfitte).
        Il grafico include etichette sugli assi, titolo, legenda e viene salvato come file PNG 
        con un nome che include la variabile 'where' che indica in quale frame statistico sarà mostratoil grafico e 
        self.squadraIn che specica se la squadra (self.squadra) gioca in casa o in trasferta.
        Salva il file come: "grafico_{self.where}_{self.squadraIn}.png"
        """
        
        plt.clf()  # <-- svuota la figura corrente
        # Creo un array di indici per le barre
        index = np.arange(3)
        # Imposto la larghezza delle barre
        width = 0.3
        # Estraggo il numero di vittorie, pareggi e sconfitte per la squadra
        x = np.array([
            int(self.estrattore.vittorie(squadra=self.squadra, where=self.where)),
            int(self.estrattore.pareggi(squadra=self.squadra, where=self.where)),
            int(self.estrattore.sconfitte(squadra=self.squadra, where=self.where))
        ])
        # Definisco i colori per ciascuna barra
        colors = ['green', 'yellow', 'red']
        # Definisco le etichette per ciascuna barra
        labels = ['Vittorie', 'Pareggi', 'Sconfitte']
        # Ciclo per disegnare ciascuna barra
        for i in range(3):
            plt.bar(index[i], x[i], width=width, color=colors[i], label=labels[i])
        plt.xticks(index, labels, fontsize=14)  # <-- aumenta la dimensione del font delle etichette sull'asse x
        # Imposto le etichette sull'asse x
        plt.xticks(index, labels)
        # forzo numeri interi sull'asse y
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        # Imposto l'etichetta dell'asse y
        plt.ylabel('Numero di partite',
                    fontsize=18,
                    fontweight='bold',
                    fontstyle='italic')
        # Imposto il titolo del grafico
        plt.title(
            f'Statistiche {self.squadra}',
            fontsize=18,
            fontweight='bold',
            fontstyle='italic'
        )
        # Imposto l'etichetta dell'asse x
        plt.xlabel("Grafico degli esiti")
        # Aggiungo la legenda con il titolo
        plt.legend(title="Legenda colori", fontsize=14)
        # aggiungo la griglia
        plt.grid()
        
        # Salvo il grafico in un file PNG
        pathGrafico = f"{myPath.grafici}\\grafico_statistiche_{self.where}_{self.squadraIn}.png"
        # if os.path.exists(pathGrafico):
        #     os.remove(pathGrafico)
        plt.savefig(pathGrafico)
        # plt.show()
        return pathGrafico
    # end crea_graficoStatistiche()
    
    @catturaEccezione
    def crea_goalsFattiSubiti(self):
        """
        Genera e salva un grafico a barre che mostra il numero di gol fatti e subiti dalla squadra selezionata.
        Il metodo estrae i dati relativi ai gol fatti e subiti tramite l'oggetto 'estrattore', crea un grafico a barre
        con etichette e colori distinti per ciascuna categoria, imposta le opzioni di visualizzazione (titolo, etichette,
        legenda, griglia) e salva il grafico come file PNG. Restituisce il percorso del file salvato.
        Returns:
            str: Il percorso del file PNG contenente il grafico generato.
        Note:
            - Utilizza matplotlib per la generazione del grafico.
            - I dati vengono estratti in base ai parametri 'squadra', 'where' e 'squadraIn'.
            - Il grafico mostra due barre: una per i gol fatti e una per i gol subiti.
        """
        plt.clf()  # <-- svuota la figura corrente
        # Creo un array di indici per le barre
        index = np.arange(2)
        # Imposto la larghezza delle barre
        width = 0.5

        # Estraggo il numero di vittorie, pareggi e sconfitte per la squadra
        x = np.array([
            int(self.estrattore.goalsFatti(squadra=self.squadra, where=self.where)),
            int(self.estrattore.goalsSubiti(squadra=self.squadra, where=self.where))
        ])
        
        # Definisco i colori per ciascuna barra
        colors = ['green', 'red']
        
        # Definisco le etichette per ciascuna barra
        labels = ['Goals Fatti', 'Goals Subiti']

        for i in range(2):
            plt.bar(index[i], x[i], width=width, color=colors[i], label=labels[i])
        plt.xticks(index, labels, fontsize=14)  # <-- aumenta la dimensione del font delle etichette sull'asse x
        # Imposto le etichette sull'asse x
        plt.xticks(index, labels)
        # forzo numeri interi sull'asse y
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        # Imposto l'etichetta dell'asse y
        plt.ylabel('Numero di goals',
                    fontsize=18,
                    fontweight='bold',
                    fontstyle='italic')    
        
        # Imposto il titolo del grafico
        plt.title(
            f'Goals fatti e subiti {self.squadra}',
            fontsize=18,
            fontweight='bold',
            fontstyle='italic'
        )    
        # Imposto l'etichetta dell'asse x
        plt.xlabel("Grafico dei Goals")
        plt.legend(title="Legenda colori", fontsize=14)
        # aggiungo la griglia
        plt.grid()
        # Salvo il grafico in un file PNG
        pathGrafico = f"{myPath.grafici}\\grafico_goals_{self.where}_{self.squadraIn}.png"
        # if os.path.exists(pathGrafico):
        #     os.remove(pathGrafico)
        plt.savefig(pathGrafico)
        # plt.show()
        return pathGrafico    
    # end crea_GoalsFattiSubiti()

    def Crea_graficoTrend(self):
        valori = self.valoriPerTrendGenerale()
        partite = list(range(1, len(valori) + 1))
        plt.clf()  # <-- svuota la figura corrente
        
        X = valori
        Y = partite
        plt.plot(Y, X, marker='o', linestyle='-', color='b', label='Trend')
        plt.fill_between(partite, valori, color='b', alpha=0.1)
        # forzo numeri interi sull'asse y
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

        # forzo numeri interi sull'asse x
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        # Imposto il titolo del grafico
        plt.title(
            f'Trend {self.squadra}',
            fontsize=18,
            fontweight='bold',
            fontstyle='italic'
        )    
        
        # Imposto l'etichetta dell'asse x
        plt.xlabel(f"Grafico del trend di {self.where} {self.squadra}",)
        
         # Imposto l'etichetta dell'asse y
        plt.ylabel('Trend',
                    fontsize=18,
                    fontweight='bold',
                    fontstyle='italic')  
        
        plt.legend(title="Legenda colori", fontsize=14)
        # aggiungo la griglia
        plt.grid()
        
        # Salvo il grafico in un file PNG
        pathGrafico = f"{myPath.grafici}\\Trend_{self.where}_{self.squadraIn}.png"
        
        plt.savefig(pathGrafico)
        # plt.show()
        return pathGrafico     
    # end Crea_graficoTrend()
        
    def valoriPerTrendGenerale(self):
        esiti = self.estrattore.esitiOrdinati(self.squadra, self.where)
        risultati = []
        
        precedente = 0
        for esito in esiti:
            if esito == '1':    #se l'esito è == 1 viene sommato 1 al precedente e aggiunto alla lista risultati
                new = precedente + 1
            elif esito == '2':  #se l'esito è == 2 viene sottratto 1 al precedente e aggiunto alla lista risultati
                new = precedente - 1
            else:               #se l'esito è == X il precedente rimane invariato
                new = precedente
            risultati.append(new)
            precedente = new
        return risultati
    # end valoriPerTrendGenerale()
# Esempio di utilizzo
if __name__ == "__main__":
    # os.path.dirname(__file__) --> percorso corrente del file Classifica.csv 
    # os.path.join(os.path.dirname(__file__), '../Csv/Classifica.csv') --> percorso relativo al file Classifica.csv
    # os.path.abspath(...) --> percorso assoluto del file Classifica.csv
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Csv\\Campionato.csv'))
    squadra = "Torino"
    grafico = Grafici(path, squadra)
    grafico.crea_graficoStatistiche()
    indexs = np.arange(6)  # creo un array di 6 elementi




