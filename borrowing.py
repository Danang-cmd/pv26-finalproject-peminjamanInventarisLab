from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QDialog, QFormLayout, QLineEdit, QComboBox, 
                               QDateEdit, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
import database.database as database

class BorrowDialog(QDialog):
    def __init__(self, parent=None, is_dark=False):
        super().__init__(parent)
        self.setWindowTitle("Form Peminjaman Alat")
        self.setMinimumWidth(350)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(12)

        self.input_nama = QLineEdit()
        self.input_nim = QLineEdit()

        self.combo_alat = QComboBox()
        self.load_items()

        self.date_pinjam = QDateEdit(QDate.currentDate())
        self.date_pinjam.setCalendarPopup(True)
        self.date_kembali = QDateEdit(QDate.currentDate().addDays(7))
        self.date_kembali.setCalendarPopup(True)

        self.btn_save = QPushButton("Simpan Data")
        self.btn_save.clicked.connect(self.validate_and_save)

        self.layout.addRow("Nama Mahasiswa:", self.input_nama)
        self.layout.addRow("NIM:", self.input_nim)
        self.layout.addRow("Pilih Alat:", self.combo_alat)
        self.layout.addRow("Tanggal Pinjam:", self.date_pinjam)
        self.layout.addRow("Tenggat Kembali:", self.date_kembali)
        self.layout.addRow("", self.btn_save)
        self.apply_theme("dark" if is_dark else "light")
        
    def load_items(self):
        conn = database.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_alat, stok_tersedia FROM items WHERE stok_tersedia > 0")
        for row in cursor.fetchall():
            self.combo_alat.addItem(f"{row[1]} (Stok: {row[2]})", row[0])
        conn.close()

    def validate_and_save(self):
        if not self.input_nama.text().strip() or not self.input_nim.text().strip():
            QMessageBox.warning(self, "Error", "Nama dan NIM tidak boleh kosong!")
            return
        if self.combo_alat.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "Tidak ada alat yang dipilih atau stok habis!")
            return
        self.accept()

    def apply_theme(self, state):
        self.setProperty("theme", state)
        try:
            with open("assets/global.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass

class BorrowingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        btn_add = QPushButton("+ Pinjam Alat")
        btn_add.setObjectName("PrimaryActionButton")
        btn_add.clicked.connect(self.add_borrow)

        btn_export = QPushButton("Cetak Bukti (PDF)")
        btn_export.setObjectName("ActionButton")
        btn_export.clicked.connect(self.export_pdf)

        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_export)
        top_layout.addStretch()

        self.table_borrow = QTableWidget()
        self.table_borrow.setColumnCount(7)
        self.table_borrow.setHorizontalHeaderLabels(["ID", "Nama Mhs", "NIM", "Alat ID", "Tgl Pinjam", "Tgl Kembali", "Status"])
        self.table_borrow.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_borrow.setAlternatingRowColors(True)

        layout.addLayout(top_layout)
        layout.addWidget(self.table_borrow)

    def load_data(self):
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM borrowings")
        rows = cur.fetchall()
        conn.close()

        self.table_borrow.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.table_borrow.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def add_borrow(self):
        dialog = BorrowDialog(self, is_dark=self.is_dark_mode)
        if dialog.exec():
            nama = dialog.input_nama.text()
            nim = dialog.input_nim.text()
            item_id = dialog.combo_alat.currentData()
            tgl_pinjam = dialog.date_pinjam.date().toString("yyyy-MM-dd")
            tgl_kembali = dialog.date_kembali.date().toString("yyyy-MM-dd")

            conn = database.connect_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO borrowings (nama_mhs, nim_mhs, item_id, tgl_pinjam, tgl_kembali, status) VALUES (?, ?, ?, ?, ?, 'Dipinjam')",
                        (nama, nim, item_id, tgl_pinjam, tgl_kembali))
            conn.commit()
            conn.close()
            self.load_data()
            QMessageBox.information(self, "Sukses", "Data peminjaman berhasil disimpan!")

    def export_pdf(self):
        row = self.table_borrow.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih data peminjaman di tabel terlebih dahulu!")
            return

        nama = self.table_borrow.item(row, 1).text()
        nim = self.table_borrow.item(row, 2).text()
        tgl_pinjam = self.table_borrow.item(row, 4).text()

        path, _ = QFileDialog.getSaveFileName(self, "Cetak Bukti PDF", f"Bukti_{nim}.pdf", "PDF Files (*.pdf)")
        if path:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            doc = QTextDocument()
            html = f"""
            <h1 style="text-align: center; color: #0f172a;">UNIVERSITAS MATARAM</h1>
            <h2 style="text-align: center; color: #475569;">Bukti Peminjaman Inventaris Laboratorium</h2>
            <hr style="border: 1px solid #cbd5e1;">
            <table style="width: 100%; margin-top: 20px; font-size: 14px;">
                <tr><td style="width: 30%; font-weight: bold;">Nama Mahasiswa</td><td>: {nama}</td></tr>
                <tr><td style="font-weight: bold;">NIM</td><td>: {nim}</td></tr>
                <tr><td style="font-weight: bold;">Tanggal Pinjam</td><td>: {tgl_pinjam}</td></tr>
            </table>
            <br><br>
            <p style="color: #64748b; font-style: italic;">Harap kembalikan alat sesuai dengan tenggat waktu yang ditentukan.</p>
            """
            doc.setHtml(html)
            doc.print_(printer)
            QMessageBox.information(self, "Sukses", "Bukti PDF berhasil dicetak!")

    def set_theme(self, state):
        self.is_dark_mode = (state == "dark")
        self.setProperty("theme", state)
        try:
            with open("assets/borrowing.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass