from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AggiornaClassificaWindow(object):
    def setupUi(self, AggiornaClassificaWindow):
        AggiornaClassificaWindow.setObjectName("AggiornaClassificaWindow")
        AggiornaClassificaWindow.resize(800, 600)
        AggiornaClassificaWindow.setWindowTitle("Aggiornamento Classifica - Estrazione Partite")
        
        # Widget centrale
        self.centralwidget = QtWidgets.QWidget(AggiornaClassificaWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Layout principale verticale
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Titolo
        self.labelTitolo = QtWidgets.QLabel(self.centralwidget)
        self.labelTitolo.setObjectName("labelTitolo")
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.labelTitolo.setFont(font)
        self.labelTitolo.setAlignment(QtCore.Qt.AlignCenter)  # type: ignore
        
        # Spacer
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        
        # Frame informazioni
        self.frameInfo = QtWidgets.QFrame(self.centralwidget)
        self.frameInfo.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameInfo.setObjectName("frameInfo")
        
        # Layout orizzontale per le info
        self.horizontalLayoutInfo = QtWidgets.QHBoxLayout(self.frameInfo)
        self.horizontalLayoutInfo.setObjectName("horizontalLayoutInfo")
        
        # Label stato
        self.labelStato = QtWidgets.QLabel(self.frameInfo)
        self.labelStato.setObjectName("labelStato")
        self.labelStato.setText("Stato: In attesa di inizio...")
        self.horizontalLayoutInfo.addWidget(self.labelStato)
        
        # Spacer orizzontale
        spacerItemH = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayoutInfo.addItem(spacerItemH)
        
        # Label contatori
        self.labelContatori = QtWidgets.QLabel(self.frameInfo)
        self.labelContatori.setObjectName("labelContatori")
        self.labelContatori.setText("Giornata: 0/34 | Partite: 0")
        self.horizontalLayoutInfo.addWidget(self.labelContatori)
        
        self.verticalLayout.addWidget(self.frameInfo)
        
        # Progress Bar
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(34)
        self.progressBar.setValue(0)
        self.verticalLayout.addWidget(self.progressBar)
        
        # Spacer
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem2)
        
        # Label per il TextBrowser
        self.labelLog = QtWidgets.QLabel(self.centralwidget)
        self.labelLog.setObjectName("labelLog")
        font2 = QtGui.QFont()
        font2.setPointSize(10)
        font2.setBold(True)
        font2.setWeight(75)
        self.labelLog.setFont(font2)
        self.labelLog.setText("Log delle operazioni:")
        self.verticalLayout.addWidget(self.labelLog)
        
        # TextBrowser per i log
        self.textBrowserLog = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowserLog.setObjectName("textBrowserLog")
        self.textBrowserLog.setFont(QtGui.QFont("Consolas", 9))
        self.verticalLayout.addWidget(self.textBrowserLog)
        
        # Imposta il widget centrale
        AggiornaClassificaWindow.setCentralWidget(self.centralwidget)
        
        # Menu bar (opzionale, vuoto per ora)
        self.menubar = QtWidgets.QMenuBar(AggiornaClassificaWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        AggiornaClassificaWindow.setMenuBar(self.menubar)
        
        # Status bar
        self.statusbar = QtWidgets.QStatusBar(AggiornaClassificaWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.showMessage("Pronto")
        AggiornaClassificaWindow.setStatusBar(self.statusbar)
        
        QtCore.QMetaObject.connectSlotsByName(AggiornaClassificaWindow)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AggiornaClassificaWindow = QtWidgets.QMainWindow()
    ui = Ui_AggiornaClassificaWindow()
    ui.setupUi(AggiornaClassificaWindow)
    AggiornaClassificaWindow.show()
    sys.exit(app.exec_())