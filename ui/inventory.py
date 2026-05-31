import csv
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox)
import database.database as database

class InventoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        self.search_inv = QLineEdit()
        self.search_inv.setPlaceholderText("Cari nama alat...")
        self.search_inv.textChanged.connect(self.load_data)

        self.filter_kategori = QComboBox()
        self.filter_kategori.addItems(["Semua Kategori", "Elektronik", "Gelas Kaca", "Mekanik"])
        self.filter_kategori.currentTextChanged.connect(self.load_data)

        btn_export_csv = QPushButton("Export CSV")
        btn_export_csv.setObjectName("ActionButton")
        btn_export_csv.clicked.connect(self.export_csv)

        top_layout.addWidget(QLabel("Cari:"))
        top_layout.addWidget(self.search_inv, 2)
        top_layout.addWidget(QLabel("Filter:"))
        top_layout.addWidget(self.filter_kategori, 1)
        top_layout.addWidget(btn_export_csv)

        self.table_inv = QTableWidget()
        self.table_inv.setColumnCount(6)
        self.table_inv.setHorizontalHeaderLabels(["ID", "Kode", "Nama Alat", "Kategori", "Total Stok", "Tersedia"])
        self.table_inv.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_inv.setAlternatingRowColors(True)

        layout.addLayout(top_layout)
        layout.addWidget(self.table_inv)

    def load_data(self):
        search_text = self.search_inv.text().lower()
        kategori = self.filter_kategori.currentText()
        query = "SELECT * FROM items WHERE nama_alat LIKE ?"
        params = [f"%{search_text}%"]
        if kategori != "Semua Kategori":
            query += " AND kategori = ?"
            params.append(kategori)

        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        self.table_inv.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.table_inv.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if path:
            with open(path, mode='w', newline='') as file:
                writer = csv.writer(file)
                headers = [self.table_inv.horizontalHeaderItem(i).text() for i in range(self.table_inv.columnCount())]
                writer.writerow(headers)
                for row in range(self.table_inv.rowCount()):
                    row_data = [self.table_inv.item(row, col).text() if self.table_inv.item(row, col) else "" for col in range(self.table_inv.columnCount())]
                    writer.writerow(row_data)
            QMessageBox.information(self, "Sukses", "Data inventaris berhasil diekspor ke CSV!")

    def set_theme(self, state):
        self.setProperty("theme", state)
        try:
            with open("assets/inventory.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass