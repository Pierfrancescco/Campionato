# Moduli Python per la gestione delle eccezioni in un'applicazione PyQt5
#   - Mostra una finestra con il messaggio di errore, il nome del file e il numero della riga
#   - Decoratore per la gestione delle eccezioni nelle funzioni
#   - Esempio di utilizzo con un'applicazione PyQt5

import os
import sys
import traceback
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 

                              QTextEdit, QPushButton, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor


__version__ = 'versione 2.3.0'

# Carica le traduzioni degli errori
def load_translations():
    """Carica il file di traduzione degli errori"""
    try:
        translation_file = os.path.join(os.path.dirname(__file__), 'error_translations.json')
        with open(translation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # Se il file non esiste, ritorna traduzioni vuote
        return {"error_types": {}, "error_messages": {}, "keywords": {}}

_translations = load_translations()

def translate_error_message(message):
    """Traduce il messaggio di errore dall'inglese all'italiano"""
    if not message:
        return message
    
    translated = message
    
    # Traduce i frammenti di messaggio
    for eng, ita in _translations.get("error_messages", {}).items():
        if eng.lower() in translated.lower():
            # Cerca la corrispondenza case-insensitive ma mantieni il case del contesto
            import re
            pattern = re.compile(re.escape(eng), re.IGNORECASE)
            translated = pattern.sub(ita, translated)
    
    return translated

# Variabile globale per mantenere il riferimento alla finestra di errore
_error_window_instance = None

class ErrorWindow(QMainWindow):
    """
    Finestra per visualizzare gli errori con PyQt5
    """
    def __init__(self, error_message):
        super().__init__()
        self.setWindowTitle("Errore")
        self.setGeometry(100, 100, 1000, 350)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Text widget per mostrare l'errore con scrollbar
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setAcceptRichText(True)  # Abilita HTML
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)  # Wrap per HTML
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: white;
                font-family: Arial;
                font-size: 12pt;
            }
            QScrollBar:vertical {
                background-color: #2b2b2b;
                width: 15px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #5a5a5a;
                min-height: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #6a6a6a;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #2b2b2b;
                height: 15px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background-color: #5a5a5a;
                min-width: 20px;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #6a6a6a;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        self.text_edit.setHtml(error_message)  # Usa setHtml invece di setText
        layout.addWidget(self.text_edit)
        
        # Menu contestuale per copia/taglia/incolla
        self.text_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)
        
        # Pulsante chiudi
        self.close_button = QPushButton("Chiudi")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                font-size: 12pt;
                min-height: 50px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.close_button.clicked.connect(self.close_and_exit)
        layout.addWidget(self.close_button)
        
        # Suono di notifica
        QApplication.beep()
    
    def show_context_menu(self, position):
        """Mostra il menu contestuale per operazioni di clipboard"""
        menu = QMenu()
        
        copy_action = QAction("Copia", self)
        copy_action.triggered.connect(self.text_edit.copy)
        menu.addAction(copy_action)
        
        select_all_action = QAction("Seleziona tutto", self)
        select_all_action.triggered.connect(self.text_edit.selectAll)
        menu.addAction(select_all_action)
        
        menu.exec_(self.text_edit.mapToGlobal(position))
    
    def close_and_exit(self):
        """Chiude la finestra ed esce dall'applicazione"""
        self.close()
        sys.exit()


def show_error(error):
    """
    Display error message with file name and line number in a PyQt5 window
    """
    global _error_window_instance
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = traceback.extract_tb(exc_traceback)
    
    # Ottieni il nome dell'errore tradotto
    error_type_name = exc_type.__name__ if exc_type else "UnknownError"
    error_type_translated = _translations.get("error_types", {}).get(error_type_name, error_type_name)
    
    # Costruisce il messaggio con formattazione HTML
    error_message = '<span style="color: white;">Traceback (ultima chiamata più recente):</span><br>'
    
    for frame in tb:
        filename = frame.filename
        line_number = frame.lineno
        function_name = frame.name
        
        # Riga del file in bianco normale
        error_message += f'<span style="color: white;">  File "{filename}", linea {line_number}, in {function_name}</span><br><br>'
        
        # Codice sorgente in grigio chiaro
        if frame.line:
            error_message += f'<span style="color: #CCCCCC;">    {frame.line}</span><br><br>'
    
    # Traduce il messaggio di errore
    error_value_translated = translate_error_message(str(exc_value))
    
    # Tipo di errore e messaggio in ROSSO FOSFORESCENTE e GRASSETTO
    error_message += f'<span style="color: #FF3333; font-weight: bold; font-size: 14pt;">{error_type_translated}: {error_value_translated}</span><br>'
    
    # Crea l'applicazione PyQt5 se non esiste
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        needs_exec = True
    else:
        needs_exec = False
    
    # Crea e mostra la finestra di errore (mantieni il riferimento globale)
    _error_window_instance = ErrorWindow(error_message)
    _error_window_instance.show()
    
    # Esegui l'event loop solo se abbiamo creato una nuova applicazione
    if needs_exec:
        app.exec_()

def catturaEccezione(func):
    """
    Decorator for handling exceptions in functions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            show_error(e)
            return None
    return wrapper
# end catturaEccezione


class PopUpTagliaCopiaIncollaPerGestioneErrori:
    """Una classe per creare e gestire un menu popUp con clic destro del mouse con le opzioni Taglia, copia e Incolla.
    
    Questa classe è mantenuta per compatibilità ma non è più necessaria in PyQt5
    poiché la funzionalità del menu contestuale è integrata direttamente nella classe ErrorWindow.
    
    Args:
        root: widget padre (non utilizzato in PyQt5)
        widget: il widget a cui verrà allegato il menu popup (non utilizzato in PyQt5)
    """
    def __init__(self, root, widget):
        # Mantenuto per compatibilità, ma non fa nulla in PyQt5
        pass
# end PopUpTagliaCopiaIncolla

    # Example usage
if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == "__version":
        print(__version__)
        exit()
    
    @catturaEccezione
    def divide_numbers(checked=None):  # Accetta il parametro del click
        x = 10
        y = 0
        result = x / y  # This will raise a ZeroDivisionError
        print(result)  # Non restituisce nulla
    
    # Create a simple PyQt5 window
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("Error Handling Demo")
    window.setGeometry(200, 200, 300, 150)
    window.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    layout = QVBoxLayout()
    central_widget.setLayout(layout)
    
    # Add a button that triggers the error
    button = QPushButton("Test Error")
    button.clicked.connect(divide_numbers)
    button.setMinimumHeight(50)
    layout.addWidget(button)
    
    window.show()
    sys.exit(app.exec_())
    

