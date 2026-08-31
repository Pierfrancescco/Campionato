
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QFileDialog, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHBoxLayout, QScrollArea
)

class MetadatiViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualizza Metadati Campionato")
        self.setGeometry(100, 100, 900, 700)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("File visualizzato: Campionato_metadati.csv")
        self.main_layout.addWidget(self.label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.buttonApri = QPushButton("Apri altro file metadati CSV")
        self.buttonApri.clicked.connect(self.carica_file)
        self.main_layout.addWidget(self.buttonApri)

        self.carica_file("Campionato_metadati.csv")

    def clear_frames(self):
        # Rimuove tutti i widget dal layout scroll
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def carica_file(self, file_path=None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona file metadati CSV", "", "CSV Files (*.csv)")
            if not file_path:
                return
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            self.label.setText(f"Errore apertura file: {e}")
            self.clear_frames()
            return
        self.label.setText(f"File visualizzato: {file_path}")
        self.clear_frames()

        # Raggruppa le righe per categoria, ignorando righe vuote
        current_group = None
        group_data = []
        import math
        for idx, row in df.iterrows():
            info = str(row['Informazione']).strip()
            valore_raw = row['Valore']
            # Gestione NaN (pandas interpreta celle vuote come float('nan'))
            if pd.isna(valore_raw):
                valore = ''
            else:
                valore = str(valore_raw).strip()
            # Ignora righe completamente vuote
            if not info and not valore:
                continue
            # Se la riga è una categoria (tutto maiuscolo, valore vuoto o NaN)
            if info.isupper() and not valore:
                if current_group and group_data:
                    self.add_groupbox(current_group, group_data)
                current_group = info
                group_data = []
            else:
                group_data.append((info, valore))
        # Ultimo gruppo
        if current_group and group_data:
            self.add_groupbox(current_group, group_data)

    def add_groupbox(self, title, data):
        from PyQt5.QtGui import QColor
        group = QGroupBox(title)
        vbox = QVBoxLayout(group)
        table = QTableWidget(len(data), 2)
        table.setHorizontalHeaderLabels(["Informazione", "Valore"])
        for i, (info, valore) in enumerate(data):
            item_info = QTableWidgetItem(info)
            item_valore = QTableWidgetItem(valore)
            # Evidenzia le celle che iniziano con 'Colonna:'
            if info.startswith('Colonna:'):
                item_info.setBackground(QColor(0, 0, 0))
                item_info.setForeground(QColor(255, 255, 255))
                item_valore.setBackground(QColor(0, 0, 0))
                item_valore.setForeground(QColor(255, 255, 255))
            table.setItem(i, 0, item_info)
            table.setItem(i, 1, item_valore)
        table.resizeColumnsToContents()
        vbox.addWidget(table)
        self.scroll_layout.addWidget(group)

def main():
    app = QApplication(sys.argv)
    viewer = MetadatiViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
