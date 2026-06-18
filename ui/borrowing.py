import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTableWidget, QTableWidgetItem, QHeaderView, 
                               QDialog, QFormLayout, QLineEdit, QComboBox, 
                               QDateEdit, QMessageBox, QFileDialog, QLabel, QSpinBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
import database.database as database

class BorrowDialog(QDialog):
    def __init__(self, parent=None, is_dark=False, borrow_data=None):
        super().__init__(parent)
        self.borrow_data = borrow_data
        self.setWindowTitle("Edit Peminjaman" if borrow_data else "Form Peminjaman Alat")
        self.setMinimumWidth(350)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(12)
        
        self.input_nama = QLineEdit()
        self.input_nim = QLineEdit()
        self.combo_alat = QComboBox()
        
        # Tambahan: Input jumlah alat
        self.input_jumlah = QSpinBox()
        self.input_jumlah.setMinimum(1)
        self.input_jumlah.setMaximum(999)
        
        self.date_pinjam = QDateEdit(QDate.currentDate())
        self.date_pinjam.setCalendarPopup(True)
        self.date_kembali = QDateEdit(QDate.currentDate().addDays(7))
        self.date_kembali.setCalendarPopup(True)
        
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Dipinjam", "Dikembalikan"])
        
        self.btn_save = QPushButton("Simpan Data")
        self.btn_save.clicked.connect(self.validate_and_save)
        
        self.layout.addRow("Nama Mahasiswa:", self.input_nama)
        self.layout.addRow("NIM:", self.input_nim)
        self.layout.addRow("Pilih Alat:", self.combo_alat)
        self.layout.addRow("Jumlah:", self.input_jumlah)
        self.layout.addRow("Tanggal Pinjam:", self.date_pinjam)
        self.layout.addRow("Tenggat Kembali:", self.date_kembali)
        self.layout.addRow("Status:", self.combo_status)
        self.layout.addRow("", self.btn_save)

        if not borrow_data:
            self.combo_status.setEnabled(False) # Default Dipinjam untuk data baru
            self.load_items()
        else:
            self._populate(borrow_data)
            
        self.apply_theme("dark" if is_dark else "light")

    def load_items(self):
        conn = database.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_alat, stok_tersedia FROM items WHERE stok_tersedia > 0")
        for row in cursor.fetchall():
            self.combo_alat.addItem(f"{row[1]} (Stok: {row[2]})", row[0])
        conn.close()
        
        # Hubungkan perubahan alat dengan pengecekan stok maksimal
        self.combo_alat.currentIndexChanged.connect(self._update_max_stok)
        self._update_max_stok()

    def _update_max_stok(self):
        text = self.combo_alat.currentText()
        if "(Stok: " in text:
            try:
                stok = int(text.split("(Stok: ")[1].replace(")", ""))
                self.input_jumlah.setMaximum(stok)
            except:
                self.input_jumlah.setMaximum(999)

    def _populate(self, data):
        self.input_nama.setText(data["nama_mhs"])
        self.input_nim.setText(data["nim_mhs"])
        self.input_jumlah.setValue(int(data.get("jumlah", 1)))
        self.date_pinjam.setDate(QDate.fromString(data["tgl_pinjam"], "yyyy-MM-dd"))
        self.date_kembali.setDate(QDate.fromString(data["tgl_kembali"], "yyyy-MM-dd"))
        self.combo_status.setCurrentText(data["status"])

        self.combo_alat.setEnabled(False) 
        self.input_jumlah.setEnabled(False) # Kuantitas dikunci saat edit agar sinkronisasi stok lebih aman

        conn = database.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_alat FROM items WHERE id = ?", (data["item_id"],))
        item = cursor.fetchone()
        if item:
            self.combo_alat.addItem(f"{item[1]}", item[0])
        conn.close()

    def validate_and_save(self):
        if not self.input_nama.text().strip() or not self.input_nim.text().strip():
            QMessageBox.warning(self, "Error", "Nama dan NIM tidak boleh kosong!")
            return
        if self.combo_alat.currentIndex() == -1:
            QMessageBox.warning(self, "Error", "Tidak ada alat yang dipilih atau stok habis!")
            return
        self.accept()

    def get_data(self):
        return {
            "nama_mhs": self.input_nama.text().strip(),
            "nim_mhs": self.input_nim.text().strip(),
            "item_id": self.combo_alat.currentData(),
            "jumlah": self.input_jumlah.value(),
            "tgl_pinjam": self.date_pinjam.date().toString("yyyy-MM-dd"),
            "tgl_kembali": self.date_kembali.date().toString("yyyy-MM-dd"),
            "status": self.combo_status.currentText()
        }

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
        # ... (Bagian atas setup_ui tetap sama seperti milikmu) ...
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        btn_add = QPushButton("  ＋  Pinjam Alat")
        btn_add.setObjectName("PrimaryActionButton")
        btn_add.clicked.connect(self.add_borrow)

        btn_edit = QPushButton("  ✏   Edit Data")
        btn_edit.setObjectName("BtnEdit")
        btn_edit.clicked.connect(self.edit_borrow)

        btn_hapus = QPushButton("  🗑   Hapus Data")
        btn_hapus.setObjectName("BtnHapus")
        btn_hapus.clicked.connect(self.delete_borrow)

        btn_export = QPushButton("Cetak Bukti (PDF)")
        btn_export.setObjectName("ActionButton")
        btn_export.clicked.connect(self.export_pdf)

        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_edit)
        top_layout.addWidget(btn_hapus)
        top_layout.addWidget(btn_export)
        top_layout.addStretch()

        # ── Tabel ──────────────────────────────
        self.table_borrow = QTableWidget()
        self.table_borrow.setColumnCount(9) # Tetap 9 kolom
        self.table_borrow.setHorizontalHeaderLabels([
            "ID", "Nama Mahasiswa", "NIM", "Nama Alat", "Jumlah", "Tgl Pinjam", "Tgl Kembali", "Status", "Item ID"
        ])
        
        header = self.table_borrow.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Nama Mhs
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # NIM
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Nama Alat
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Jumlah
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Tgl Pinjam
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Tgl Kembali
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents) # Status (Lebar otomatis pas teks)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents) # Item ID
        
        # SEKARANG HANYA SEMBUNYIKAN KOLOM ID (0) DAN ITEM ID (8)
        self.table_borrow.setColumnHidden(0, True)
        self.table_borrow.setColumnHidden(7, False) # Diubah jadi False agar status TAMPIL
        self.table_borrow.setColumnHidden(8, True)

        self.table_borrow.setAlternatingRowColors(True)
        self.table_borrow.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_borrow.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_borrow.verticalHeader().setVisible(False)
        self.table_borrow.doubleClicked.connect(self.edit_borrow)

        self.lbl_count = QLabel("0 peminjaman ditemukan")
        self.lbl_count.setStyleSheet("font-size: 12px; color: #94a3b8;")

        layout.addLayout(top_layout)
        layout.addWidget(self.table_borrow)
        layout.addWidget(self.lbl_count)

    def load_data(self):
        conn = database.connect_db()
        cur = conn.cursor()
        
        query = """
            SELECT b.id, b.nama_mhs, b.nim_mhs, i.nama_alat, b.jumlah, 
                   b.tgl_pinjam, b.tgl_kembali, b.status, b.item_id 
            FROM borrowings b
            JOIN items i ON b.item_id = i.id
            ORDER BY b.id DESC
        """
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()

        self.table_borrow.setUpdatesEnabled(False)
        self.table_borrow.setRowCount(len(rows))
        
        current_date = QDate.currentDate() # Ambil tanggal hari ini

        for row_idx, row_data in enumerate(rows):
            # Ambil data asli dari database
            status_db = row_data[7]
            tgl_kembali_str = row_data[6]
            tgl_kembali_qd = QDate.fromString(tgl_kembali_str, "yyyy-MM-dd")

            # Logika Cek Keterlambatan otomatis
            status_display = status_db
            if status_db == "Dipinjam" and tgl_kembali_qd < current_date:
                status_display = "Terlambat"

            for col_idx, col_data in enumerate(row_data):
                # Jika sedang di kolom status (indeks 7), gunakan status_display hasil pengecekan kita
                text_to_show = status_display if col_idx == 7 else str(col_data)
                
                item = QTableWidgetItem(text_to_show)
                if col_idx in [1, 3]:  # Nama Mahasiswa & Nama Alat rata kiri
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table_borrow.setItem(row_idx, col_idx, item)
            
            # Pewarnaan baris/teks berdasarkan status display aktual
            if status_display == "Dikembalikan":
                for col_idx in range(self.table_borrow.columnCount()):
                    cell = self.table_borrow.item(row_idx, col_idx)
                    if cell: 
                        cell.setForeground(Qt.darkGreen)
            elif status_display == "Terlambat":
                for col_idx in range(self.table_borrow.columnCount()):
                    cell = self.table_borrow.item(row_idx, col_idx)
                    if cell: 
                        # Warna Merah Tua untuk yang terlambat
                        cell.setForeground(Qt.red)
                        font = cell.font()
                        font.setBold(True)
                        cell.setFont(font)
            else: # Status "Dipinjam" tapi belum terlambat
                for col_idx in range(self.table_borrow.columnCount()):
                    cell = self.table_borrow.item(row_idx, col_idx)
                    if cell: 
                        cell.setForeground(Qt.blue) # Biru menunjukkan masih dalam masa pinjam aktif

        self.table_borrow.setUpdatesEnabled(True)
        self.lbl_count.setText(f"{len(rows)} peminjaman ditemukan")

    def _get_selected_item(self):
        row = self.table_borrow.currentRow()
        if row < 0:
            QMessageBox.information(self, "Pilih Data", "Pilih baris peminjaman terlebih dahulu dari tabel.")
            return None
            
        # Jika teks di tabel adalah "Terlambat", kembalikan ke status aslinya "Dipinjam" untuk form edit
        status_table = self.table_borrow.item(row, 7).text()
        status_real = "Dipinjam" if status_table == "Terlambat" else status_table

        return {
            "id": self.table_borrow.item(row, 0).text(),
            "nama_mhs": self.table_borrow.item(row, 1).text(),
            "nim_mhs": self.table_borrow.item(row, 2).text(),
            "nama_alat": self.table_borrow.item(row, 3).text(),
            "jumlah": self.table_borrow.item(row, 4).text(),
            "tgl_pinjam": self.table_borrow.item(row, 5).text(),
            "tgl_kembali": self.table_borrow.item(row, 6).text(),
            "status": status_real, # Menggunakan status real agar combobox form edit sinkron
            "item_id": int(self.table_borrow.item(row, 8).text())
        }

    def add_borrow(self):
        dialog = BorrowDialog(self, is_dark=self.is_dark_mode)
        if dialog.exec():
            data = dialog.get_data()
            conn = database.connect_db()
            cur = conn.cursor()
            
            cur.execute(
                "INSERT INTO borrowings (nama_mhs, nim_mhs, item_id, jumlah, tgl_pinjam, tgl_kembali, status) VALUES (?, ?, ?, ?, ?, ?, 'Dipinjam')",
                (data["nama_mhs"], data["nim_mhs"], data["item_id"], data["jumlah"], data["tgl_pinjam"], data["tgl_kembali"])
            )
            # Kurangi stok berdasarkan jumlah yang dipinjam
            cur.execute("UPDATE items SET stok_tersedia = stok_tersedia - ? WHERE id = ?", (data["jumlah"], data["item_id"]))
            
            conn.commit()
            conn.close()
            self.load_data()
            QMessageBox.information(self, "Sukses", "Data peminjaman berhasil disimpan!")

    def edit_borrow(self):
        selected = self._get_selected_item()
        if not selected: return
            
        dialog = BorrowDialog(self, is_dark=self.is_dark_mode, borrow_data=selected)
        if dialog.exec():
            data = dialog.get_data()
            conn = database.connect_db()
            cur = conn.cursor()

            cur.execute("UPDATE borrowings SET nama_mhs=?, nim_mhs=?, tgl_pinjam=?, tgl_kembali=?, status=? WHERE id=?",
                        (data["nama_mhs"], data["nim_mhs"], data["tgl_pinjam"], data["tgl_kembali"], data["status"], selected["id"]))

            jumlah_alat = int(selected["jumlah"])
            
            if selected["status"] == "Dipinjam" and data["status"] == "Dikembalikan":
                cur.execute("UPDATE items SET stok_tersedia = stok_tersedia + ? WHERE id = ?", (jumlah_alat, selected["item_id"]))
            elif selected["status"] == "Dikembalikan" and data["status"] == "Dipinjam":
                cur.execute("SELECT stok_tersedia FROM items WHERE id = ?", (selected["item_id"],))
                stok = cur.fetchone()[0]
                if stok >= jumlah_alat:
                    cur.execute("UPDATE items SET stok_tersedia = stok_tersedia - ? WHERE id = ?", (jumlah_alat, selected["item_id"]))
                else:
                    QMessageBox.warning(self, "Error", "Stok alat sudah tidak mencukupi untuk dipinjam kembali.")
                    conn.rollback()
                    conn.close()
                    return
                    
            conn.commit()
            conn.close()
            self.load_data()
            QMessageBox.information(self, "Sukses", "Data peminjaman berhasil diperbarui!")

    def delete_borrow(self):
        selected = self._get_selected_item()
        if not selected: return

        konfirmasi = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Yakin ingin menghapus data peminjaman oleh {selected['nama_mhs']}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes: return
            
        conn = database.connect_db()
        cur = conn.cursor()

        if selected["status"] == "Dipinjam":
            cur.execute("UPDATE items SET stok_tersedia = stok_tersedia + ? WHERE id = ?", (int(selected["jumlah"]), selected["item_id"]))

        cur.execute("DELETE FROM borrowings WHERE id=?", (selected["id"],))
        conn.commit()
        conn.close()
        self.load_data()
        QMessageBox.information(self, "Sukses", "Data peminjaman berhasil dihapus!")

    def export_pdf(self):
        selected = self._get_selected_item()
        if not selected: return
        
        nama = selected["nama_mhs"]
        nim = selected["nim_mhs"]
        alat = selected["nama_alat"]
        jumlah = selected["jumlah"]
        tgl_pinjam = selected["tgl_pinjam"]
        
        path, _ = QFileDialog.getSaveFileName(self, "Cetak Bukti PDF", f"Bukti_{nim}.pdf", "PDF Files (*.pdf)")
        if path:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            doc = QTextDocument()
            html = f"""
            <h1 style="text-align: center; color: #0f172a;">UNIVERSITAS MATARAM</h1>
            <h2 style="text-align: center; color: #475569;">Bukti Peminjaman Inventaris</h2>
            <hr style="border: 1px solid #cbd5e1;">
            <table style="width: 100%; margin-top: 20px; font-size: 14px;">
                <tr><td style="width: 30%; font-weight: bold;">Nama Mahasiswa</td><td>: {nama}</td></tr>
                <tr><td style="font-weight: bold;">NIM</td><td>: {nim}</td></tr>
                <tr><td style="font-weight: bold;">Nama Alat</td><td>: {alat}</td></tr>
                <tr><td style="font-weight: bold;">Jumlah</td><td>: {jumlah} Unit</td></tr>
                <tr><td style="font-weight: bold;">Tanggal Pinjam</td><td>: {tgl_pinjam}</td></tr>
            </table>
            <br><br>
            <p style="color: #64748b; font-style: italic;">Harap kembalikan alat sesuai dengan tenggat waktu.</p>
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