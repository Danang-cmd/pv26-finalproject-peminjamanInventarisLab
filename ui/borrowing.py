import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QDialog, QFormLayout, QLineEdit, QComboBox,
                               QDateEdit, QMessageBox, QFileDialog, QLabel, QSpinBox, 
                               QFrame, QDialogButtonBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextDocument
from PySide6.QtPrintSupport import QPrinter
from models.borrowing_model import BorrowingModel

# ──────────────────────────────────────────────
#  HELPER FUNCTION: Pop-up Pesan Sesuai Tema
# ──────────────────────────────────────────────
def _show_message(parent, type_str, title, text, buttons=QMessageBox.Ok, default_button=QMessageBox.Ok):
    """Membuat QMessageBox yang mendukung tema terang/gelap secara dinamis."""
    msg = QMessageBox(parent)
    if type_str == "info":
        msg.setIcon(QMessageBox.Information)
    elif type_str == "warning":
        msg.setIcon(QMessageBox.Warning)
    elif type_str == "question":
        msg.setIcon(QMessageBox.Question)
    
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)
    msg.setDefaultButton(default_button)
    
    # Ambil status tema dari parent
    theme = "light"
    if parent:
        theme = parent.property("theme") or ("dark" if getattr(parent, 'is_dark_mode', False) else "light")
    msg.setProperty("theme", theme)
    
    # Muat file styling agar selector CSS bekerja pada pop-up
    styles = []
    for path in ["assets/global.qss", "assets/borrowing.qss"]:
        try:
            with open(path, "r") as f:
                styles.append(f.read())
        except FileNotFoundError:
            pass
    if styles:
        msg.setStyleSheet("\n".join(styles))
        
    return msg.exec()

# ──────────────────────────────────────────────
#  DIALOG: Tambah / Edit Peminjaman Alat
# ──────────────────────────────────────────────
class BorrowDialog(QDialog):
    def __init__(self, parent=None, is_dark=False, borrow_data=None):
        super().__init__(parent)
        self.borrow_data = borrow_data
        self.setWindowTitle("Edit Peminjaman" if borrow_data else "Form Peminjaman Alat")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Sinkronisasi tema
        self.theme_state = "dark" if is_dark else "light"
        self.setProperty("theme", self.theme_state)
        self._apply_theme()
        
        self._build_ui()
        
        if not borrow_data:
            self.combo_status.setEnabled(False)  # Default Dipinjam untuk data baru
            self.load_items()
        else:
            self._populate(borrow_data)

    def _apply_theme(self):
        """Memuat stylesheet tema ke dalam jendela dialog."""
        styles = []
        for path in ["assets/global.qss", "assets/borrowing.qss"]:
            try:
                with open(path, "r") as f:
                    styles.append(f.read())
            except FileNotFoundError:
                pass
        if styles:
            self.setStyleSheet("\n".join(styles))

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)
        
        # Judul Dialog
        title_lbl = QLabel("Edit Peminjaman" if self.borrow_data else "Form Peminjaman Alat")
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        main_layout.addWidget(title_lbl)
        
        # Garis Pembatas (Divider) sesuai tema
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        if self.theme_state == "dark":
            divider.setStyleSheet("background-color: #334155; max-height: 1px; border: none;")
        else:
            divider.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")
        main_layout.addWidget(divider)
        
        # Form inputs
        form = QFormLayout()
        form.setSpacing(12)
        
        self.input_nama = QLineEdit()
        self.input_nim = QLineEdit()
        
        self.combo_alat = QComboBox()
        self.combo_alat.setStyleSheet("QComboBox QAbstractItemView { border: 1px solid #475569; }")
        
        self.input_jumlah = QSpinBox()
        self.input_jumlah.setMinimum(1)
        self.input_jumlah.setMaximum(999)
        
        self.date_pinjam = QDateEdit(QDate.currentDate())
        self.date_pinjam.setCalendarPopup(True)
        self.date_kembali = QDateEdit(QDate.currentDate().addDays(7))
        self.date_kembali.setCalendarPopup(True)
        
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Dipinjam", "Dikembalikan"])
        
        form.addRow("Nama Mahasiswa:", self.input_nama)
        form.addRow("NIM:", self.input_nim)
        form.addRow("Pilih Alat:", self.combo_alat)
        form.addRow("Jumlah:", self.input_jumlah)
        form.addRow("Tanggal Pinjam:", self.date_pinjam)
        form.addRow("Tenggat Kembali:", self.date_kembali)
        form.addRow("Status:", self.combo_status)
        
        main_layout.addLayout(form)
        
        # Tombol Simpan / Batal
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Simpan Data")
        buttons.button(QDialogButtonBox.Cancel).setText("Batal")
        buttons.accepted.connect(self.validate_and_save)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        # Hubungkan perubahan alat dengan pengecekan stok maksimal
        self.combo_alat.currentIndexChanged.connect(self._update_max_stok)

    def load_items(self):
        rows = BorrowingModel.get_available_items()
        for row in rows:
            self.combo_alat.addItem(f"{row[1]} (Stok: {row[2]})", row[0])
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
        self.input_jumlah.setEnabled(False)  

        # Gunakan Model untuk _populate
        item = BorrowingModel.get_item_by_id(data["item_id"])
        if item:
            self.combo_alat.addItem(f"{item[1]}", item[0])

    def validate_and_save(self):
        if not self.input_nama.text().strip() or not self.input_nim.text().strip():
            _show_message(self, "warning", "Error", "Nama dan NIM tidak boleh kosong!")
            return
        if self.combo_alat.currentIndex() == -1:
            _show_message(self, "warning", "Error", "Tidak ada alat yang dipilih atau stok habis!")
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

# ──────────────────────────────────────────────
#  HALAMAN UTAMA PEMINJAMAN
# ──────────────────────────────────────────────
class BorrowingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_dark_mode = False
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)
        
        # 1. Input Pencarian (Sekarang Berada di Atas)
        search_layout = QHBoxLayout()
        self.input_search = QLineEdit()
        self.input_search.setPlaceholderText(" 🔍  Cari berdasarkan Nama Mahasiswa atau NIM...")
        self.input_search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 13px;
                background-color: transparent;
            }
        """)
        self.input_search.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.input_search)
        
        # 2. Tombol-tombol CRUD (Berada di bawah Pencarian)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        btn_add = QPushButton("  ＋  Pinjam Alat")
        btn_add.setObjectName("PrimaryActionButton")
        btn_add.clicked.connect(self.add_borrow)

        btn_edit = QPushButton("  ✏       Edit Data")
        btn_edit.setObjectName("BtnEdit")
        btn_edit.clicked.connect(self.edit_borrow)

        btn_hapus = QPushButton("  🗑    Hapus Data")
        btn_hapus.setObjectName("BtnHapus")
        btn_hapus.clicked.connect(self.delete_borrow)
        
        btn_export = QPushButton("   📄    Export PDF")
        btn_export.setObjectName("BtnExport")
        btn_export.clicked.connect(self.export_pdf)

        top_layout.addWidget(btn_add)
        top_layout.addWidget(btn_edit)
        top_layout.addWidget(btn_hapus)
        top_layout.addWidget(btn_export)
        top_layout.addStretch()

        # 3. Tabel Utama
        self.table_borrow = QTableWidget()
        self.table_borrow.setColumnCount(9)
        self.table_borrow.setHorizontalHeaderLabels([
            "ID", "Nama Mahasiswa", "NIM", "Nama Alat", "Jumlah", "Tgl Pinjam", "Tgl Kembali", "Status", "Item ID"
        ])

        header = self.table_borrow.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)

        self.table_borrow.setColumnHidden(0, True)
        self.table_borrow.setColumnHidden(7, False)
        self.table_borrow.setColumnHidden(8, True)
        self.table_borrow.setAlternatingRowColors(True)
        self.table_borrow.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_borrow.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_borrow.verticalHeader().setVisible(False)
        self.table_borrow.doubleClicked.connect(self.edit_borrow)

        self.lbl_count = QLabel("0 peminjaman ditemukan")
        self.lbl_count.setStyleSheet("font-size: 12px; color: #94a3b8;")

        # Masukkan ke dalam urutan layout vertikal utama
        layout.addLayout(search_layout)   # Pertama: Kolom Pencarian
        layout.addLayout(top_layout)      # Kedua: Tombol-tombol Aksi
        layout.addWidget(self.table_borrow)
        layout.addWidget(self.lbl_count)

    def load_data(self):
        # Ambil data dari model
        rows = BorrowingModel.get_all()

        self.table_borrow.setUpdatesEnabled(False)
        self.table_borrow.setRowCount(len(rows))
        current_date = QDate.currentDate()
        
        for row_idx, row_data in enumerate(rows):
            status_db = row_data[7]
            tgl_kembali_str = row_data[6]
            tgl_kembali_qd = QDate.fromString(tgl_kembali_str, "yyyy-MM-dd")

            status_display = status_db
            if status_db == "Dipinjam" and tgl_kembali_qd < current_date:
                status_display = "Terlambat"

            for col_idx, col_data in enumerate(row_data):
                text_to_show = status_display if col_idx == 7 else str(col_data)
                item = QTableWidgetItem(text_to_show)

                if col_idx in [1, 3]:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table_borrow.setItem(row_idx, col_idx, item)
                
            if status_display == "Dikembalikan":
                for col_idx in range(self.table_borrow.columnCount()):
                    cell = self.table_borrow.item(row_idx, col_idx)
                    if cell: cell.setForeground(Qt.darkGreen)
            elif status_display == "Terlambat":
                for col_idx in range(self.table_borrow.columnCount()):
                    cell = self.table_borrow.item(row_idx, col_idx)
                    if cell:
                        cell.setForeground(Qt.red)
                        font = cell.font()
                        font.setBold(True)
                        cell.setFont(font)
            else:
                for col_idx in range(self.table_borrow.columnCount()):
                    cell = self.table_borrow.item(row_idx, col_idx)
                    if cell: cell.setForeground(Qt.blue)

        self.table_borrow.setUpdatesEnabled(True)
        self.lbl_count.setText(f"{len(rows)} peminjaman ditemukan")
        self.filter_data()

    def filter_data(self):
        search_text = self.input_search.text().strip().lower()
        visible_row_count = 0

        for row in range(self.table_borrow.rowCount()):
            item_nama = self.table_borrow.item(row, 1)
            item_nim = self.table_borrow.item(row, 2)

            nama = item_nama.text().lower() if item_nama else ""
            nim = item_nim.text().lower() if item_nim else ""

            if not search_text or search_text in nama or search_text in nim:
                self.table_borrow.setRowHidden(row, False)
                visible_row_count += 1
            else:
                self.table_borrow.setRowHidden(row, True)

        self.lbl_count.setText(f"{visible_row_count} peminjaman ditemukan")

    def _get_selected_item(self):
        row = self.table_borrow.currentRow()
        if row < 0:
            _show_message(self, "info", "Pilih Data", "Pilih baris peminjaman terlebih dahulu dari tabel.")
            return None

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
            "status": status_real, 
            "item_id": int(self.table_borrow.item(row, 8).text())
        }

    def add_borrow(self):
        dialog = BorrowDialog(self, is_dark=self.is_dark_mode)
        if dialog.exec():
            data = dialog.get_data()
            try:
                BorrowingModel.add(data)
                self.load_data()
                _show_message(self, "info", "Sukses", "Data peminjaman berhasil disimpan!")
            except Exception as e:
                _show_message(self, "warning", "Error", f"Terjadi kesalahan saat menyimpan: {e}")

    def edit_borrow(self):
        selected = self._get_selected_item()
        if not selected: return
        
        dialog = BorrowDialog(self, is_dark=self.is_dark_mode, borrow_data=selected)
        if dialog.exec():
            data = dialog.get_data()
            try:
                BorrowingModel.update(selected["id"], data, selected)
                self.load_data()
                _show_message(self, "info", "Sukses", "Data peminjaman berhasil diperbarui!")
            except ValueError as ve:
                _show_message(self, "warning", "Error", str(ve))
            except Exception as e:
                _show_message(self, "warning", "Error", f"Terjadi kesalahan: {e}")

    def delete_borrow(self):
        selected = self._get_selected_item()
        if not selected: return

        konfirmasi = _show_message(
            self, "question", "Konfirmasi Hapus",
            f"Yakin ingin menghapus data peminjaman oleh {selected['nama_mhs']}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes: return
        
        try:
            BorrowingModel.delete(selected["id"], selected)
            self.load_data()
            _show_message(self, "info", "Sukses", "Data peminjaman berhasil dihapus!")
        except Exception as e:
            _show_message(self, "warning", "Error", f"Gagal menghapus data: {e}")

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan PDF", "Laporan_Peminjaman.pdf", "PDF Files (*.pdf)")
        if not path:
            return 
            
        html = """
        <h1 style='text-align: center;'>Laporan Peminjaman Alat</h1>
        <hr>
        <table border='1' cellspacing='0' cellpadding='5' width='100%' style='border-collapse: collapse;'>
            <tr style='background-color: #f1f5f9;'>
                <th>Nama Mahasiswa</th>
                <th>NIM</th>
                <th>Nama Alat</th>
                <th>Jumlah</th>
                <th>Tgl Pinjam</th>
                <th>Tgl Kembali</th>
                <th>Status</th>
            </tr>
        """
        for row in range(self.table_borrow.rowCount()):
            if self.table_borrow.isRowHidden(row):
                continue 

            html += "<tr>"
            for col in range(1, 8):
                item = self.table_borrow.item(row, col)
                text = item.text() if item else ""

                if col == 7:
                    if text == "Terlambat":
                        html += f"<td style='color: red; font-weight: bold; text-align: center;'>{text}</td>"
                    elif text == "Dikembalikan":
                        html += f"<td style='color: green; text-align: center;'>{text}</td>"
                    else:
                        html += f"<td style='color: blue; text-align: center;'>{text}</td>"
                else:
                    align = "left" if col in [1, 3] else "center"
                    html += f"<td style='text-align: {align};'>{text}</td>"

            html += "</tr>"
        html += "</table>"
        
        document = QTextDocument()
        document.setHtml(html)
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        document.print_(printer)
        
        _show_message(self, "info", "Sukses", f"Data peminjaman berhasil diekspor ke:\n{path}")

    def set_theme(self, state):
        self.is_dark_mode = (state == "dark")
        self.setProperty("theme", state)
        try:
            with open("assets/borrowing.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass