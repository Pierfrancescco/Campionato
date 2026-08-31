'''Quando il file Campionato.xlsm o altri file in Python tramite pandas,
viene creato un DataFrame con le seguenti colonne:
- Championship
- DayWeek
- DayMonth
- Month
- Home
- Away
- GoalHome
- GoalAway
Il file nomenclature in inglese che devono essere tradotte in italiano e
alcune squadre hanno nomi diversi rispetto a quelli reali.
Le squadre sono:
Inter Milano -> Inter
Milan AC -> Milan
Roma FC -> Roma che devono essere tradotte in:
Inter
Milan
Roma
'''

modificaNomiSquadre = {
    'Inter Milan': 'Inter',
    'AC Milan': 'Milan',
    'AS Roma': 'Roma',
    'Hellas': 'Hellas Verona',
    'Verona': 'Hellas Verona',
    'AC Monza': 'Monza'
}

sitiUfficialiSquadre = {
    'Atalanta': 'https://www.atalanta.it/',
    'Bologna': 'https://www.bolognafc.it/',
    'Cagliari': 'https://cagliaricalcio.com/',
    'Como': 'https://comofootball.com/',
    'Cremonese': 'https://uscremonese.it/',
    'Empoli': 'https://empolifc.com/',
    'Fiorentina': 'https://www.acffiorentina.com/',
    'Frosinone': 'https://www.frosinonecalcio.com/',
    'Genoa': 'https://genoacfc.it/',
    'Hellas Verona': 'https://www.hellasverona.it/',
    'Inter': 'https://www.inter.it/it',
    'Juventus': 'https://www.juventus.com/it',
    'Lazio': 'https://www.sslazio.it/it',
    'Lecce': 'https://www.uslecce.it/',
    'Milan': 'https://www.acmilan.com/it',
    'Monza': 'https://www.acmonza.com/',
    'Napoli': 'https://sscnapoli.it/',
    'Palermo': 'https://www.palermofc.com/',
    'Parma': 'https://www.parmacalcio1913.com/',
    'Pisa': 'https://pisasportingclub.com/',
    'Roma': 'https://www.asroma.com/it',
    'Salernitana': 'https://salernitana.it/',
    'Sampdoria': 'https://www.sampdoria.it/',
    'Sassuolo': 'https://www.sassuolocalcio.it/',
    'Spezia': 'https://www.speziacalcio.com/',
    'Torino': 'https://www.torinofc.it/',
    'Udinese': 'https://www.udinese.it/',
    'Venezia': 'https://www.veneziafc.it/'
}

modificaNomiColonne = {
    'Championship': 'Campionato',
    'DayWeek': 'GiornoSettimana',
    'DayMonth': 'GiornoMese',
    'Month': 'Mese',
    'Home': 'Casa',
    'Away': 'Trasferta',
    'GoalHome': 'GoalCasa',
    'GoalAway': 'GoalTrasferta'
}

traduciMesi = {
    'Jan': 'Gen',
    'Feb': 'Feb',
    'Mar': 'Mar',
    'Apr': 'Apr',
    'May': 'Mag',
    'Jun': 'Giu',
    'Jul': 'Lug',
    'Aug': 'Ago',
    'Sep': 'Set',
    'Oct': 'Ott',
    'Nov': 'Nov',
    'Dec': 'Dic'
}

traduciGiorniSettimana = {
    'Mo': 'Lun',
    'Tu': 'Mar',
    'We': 'Mer',
    'Th': 'Gio',
    'Fr': 'Ven',
    'Sa': 'Sab',
    'Su': 'Dom',
    'Mon': 'Lun',
    'Tue': 'Mar',
    'Wed': 'Mer',
    'Thu': 'Gio',
    'Fri': 'Ven',
    'Sat': 'Sab',
    'Sun': 'Dom'
}

