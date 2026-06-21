import csv
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QComboBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
                               QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QFrame)
from PySide6.QtCore import Qt
import database.database as database

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
        theme = parent.property("theme") or "light"
    msg.setProperty("theme", theme)
    
    # Muat file styling global & inventaris agar selector CSS bekerja
    styles = []
    for path in ["assets/global.qss", "assets/inventory.qss"]:
        try:
            with open(path, "r") as f:
                styles.append(f.read())
        except FileNotFoundError:
            pass
    if styles:
        msg.setStyleSheet("\n".join(styles))
        
    return msg.exec()

# ──────────────────────────────────────────────
#  DIALOG: Tambah / Edit Alat
# ──────────────────────────────────────────────
class ItemDialog(QDialog):
    """Dialog dipakai untuk Tambah maupun Edit item inventaris."""
    KATEGORI_LIST = ["Komputer & Jaringan", "Elektronik & Mikrokontroler", "Alat Ukur", "Kabel & Konektor", "Komponen Elektronik", "Lainnya"]
    
    def __init__(self, parent=None, item_data: dict = None):
        super().__init__(parent)
        self.item_data = item_data  # None → mode Tambah, dict → mode Edit
        self.setWindowTitle("Edit Alat" if item_data else "Tambah Alat Baru")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        # Sinkronisasi tema aktif dari halaman induk (parent)
        self.theme_state = "light"
        if parent:
            self.theme_state = parent.property("theme") or "light"
        self.setProperty("theme", self.theme_state)
        self._apply_theme()
        
        self._build_ui()
        if item_data:
            self._populate(item_data)
            
    def _apply_theme(self):
        """Memuat stylesheet tema ke dalam jendela dialog."""
        styles = []
        for path in ["assets/global.qss", "assets/inventory.qss"]:
            try:
                with open(path, "r") as f:
                    styles.append(f.read())
            except FileNotFoundError:
                pass
        if styles:
            self.setStyleSheet("\n".join(styles))

    # ── build ──────────────────────────────────
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)
        
        # Judul dialog
        title = QLabel("Edit Data Alat" if self.item_data else "Tambah Alat Baru")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title)
        
        # Garis pembatas yang menyesuaikan tema terang/gelap
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        if self.theme_state == "dark":
            divider.setStyleSheet("background-color: #334155; max-height: 1px; border: none;")
        else:
            divider.setStyleSheet("background-color: #e2e8f0; max-height: 1px; border: none;")
        layout.addWidget(divider)
        
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)
        
        self.input_kode = QLineEdit()
        self.input_kode.setPlaceholderText("Contoh: ELK-01")
        self.input_nama = QLineEdit()
        self.input_nama.setPlaceholderText("Nama lengkap alat")
        
        self.input_kategori = QComboBox()
        self.input_kategori.addItems(self.KATEGORI_LIST)
        
        # Solusi agar list dropdown di dalam dialog juga ikut tema
        self.input_kategori.setStyleSheet("QComboBox QAbstractItemView { border: 1px solid #475569; }")
        
        self.input_stok_total = QSpinBox()
        self.input_stok_total.setMinimum(1)
        self.input_stok_total.setMaximum(9999)
        self.input_stok_total.valueChanged.connect(self._sync_stok_tersedia)
        
        self.input_stok_tersedia = QSpinBox()
        self.input_stok_tersedia.setMinimum(0)
        self.input_stok_tersedia.setMaximum(9999)
        
        form.addRow("Kode Alat *", self.input_kode)
        form.addRow("Nama Alat *", self.input_nama)
        form.addRow("Kategori *", self.input_kategori)
        form.addRow("Stok Total *", self.input_stok_total)
        form.addRow("Stok Tersedia *", self.input_stok_tersedia)
        layout.addLayout(form)
        
        # Tombol OK / Batal
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Simpan")
        buttons.button(QDialogButtonBox.Cancel).setText("Batal")
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def _sync_stok_tersedia(self, total_value):
        """Saat mode Tambah: stok tersedia otomatis ikuti stok total."""
        if not self.item_data:
            self.input_stok_tersedia.setValue(total_value)
            
    def _populate(self, data: dict):
        """Isi form dengan data yang sudah ada (mode Edit)."""
        self.input_kode.setText(data.get("kode_alat", ""))
        self.input_nama.setText(data.get("nama_alat", ""))
        idx = self.input_kategori.findText(data.get("kategori", ""))
        if idx >= 0:
            self.input_kategori.setCurrentIndex(idx)
        self.input_stok_total.setValue(int(data.get("stok_total", 1)))
        self.input_stok_tersedia.setValue(int(data.get("stok_tersedia", 1)))
        
    # ── validasi ───────────────────────────────
    def _validate_and_accept(self):
        errors = []
        if not self.input_kode.text().strip():
            errors.append("• Kode alat harus diisi")
        if not self.input_nama.text().strip():
            errors.append("• Nama alat harus diisi")
        if self.input_stok_tersedia.value() > self.input_stok_total.value():
            errors.append("• Stok tersedia tidak boleh melebihi stok total")
            
        if errors:
            _show_message(self, "warning", "Validasi Gagal",
                          "Perbaiki kesalahan berikut:\n\n" + "\n".join(errors))
            return
        self.accept()
        
    # ── getter ─────────────────────────────────
    def get_data(self) -> dict:
        return {
            "kode_alat":      self.input_kode.text().strip().upper(),
            "nama_alat":      self.input_nama.text().strip(),
            "kategori":       self.input_kategori.currentText(),
            "stok_total":     self.input_stok_total.value(),
            "stok_tersedia":  self.input_stok_tersedia.value(),
        }

# ──────────────────────────────────────────────
#  HALAMAN UTAMA INVENTARIS
# ──────────────────────────────────────────────
class InventoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    # ── UI ─────────────────────────────────────
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)
        
        # ── Baris atas: Search + Filter + Tombol ──
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        self.search_inv = QLineEdit()
        self.search_inv.setPlaceholderText("Cari nama alat...")
        self.search_inv.textChanged.connect(self.load_data)
        
        self.filter_kategori = QComboBox()
        self.filter_kategori.addItems(["Semua Kategori", "Komputer & Jaringan",
                                       "Elektronik & Mikrokontroler", "Alat Ukur",
                                       "Kabel & Konektor", "Komponen Elektronik", "Lainnya"])
        self.filter_kategori.currentTextChanged.connect(self.load_data)
        
        btn_export_csv = QPushButton("Export CSV")
        btn_export_csv.setObjectName("ActionButton")
        btn_export_csv.clicked.connect(self.export_csv)
        
        top_layout.addWidget(QLabel("Cari:"))
        top_layout.addWidget(self.search_inv, 2)
        top_layout.addWidget(QLabel("Filter:"))
        top_layout.addWidget(self.filter_kategori, 1)
        top_layout.addWidget(btn_export_csv)
        
        # ── Baris tombol CRUD ──────────────────
        crud_layout = QHBoxLayout()
        crud_layout.setSpacing(8)
        
        self.btn_tambah = QPushButton("＋  Tambah Alat")
        self.btn_tambah.setObjectName("BtnTambah")
        self.btn_tambah.clicked.connect(self.tambah_item)
        
        self.btn_edit = QPushButton("✏  Edit Alat")
        self.btn_edit.setObjectName("BtnEdit")
        self.btn_edit.clicked.connect(self.edit_item)
        
        self.btn_hapus = QPushButton("🗑  Hapus Alat")
        self.btn_hapus.setObjectName("BtnHapus")
        self.btn_hapus.clicked.connect(self.hapus_item)
        
        crud_layout.addWidget(self.btn_tambah)
        crud_layout.addWidget(self.btn_edit)
        crud_layout.addWidget(self.btn_hapus)
        crud_layout.addStretch()
        
        # ── Tabel ──────────────────────────────
        self.table_inv = QTableWidget()
        self.table_inv.setColumnCount(6)
        self.table_inv.setHorizontalHeaderLabels(
            ["ID", "Kode", "Nama Alat", "Kategori", "Total Stok", "Tersedia"])
        
        header = self.table_inv.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(1, QHeaderView.Interactive)      
        header.setSectionResizeMode(2, QHeaderView.Stretch)          
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) 
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) 
        
        self.table_inv.setColumnWidth(1, 100)
        self.table_inv.setColumnHidden(0, True)
        self.table_inv.setAlternatingRowColors(True)
        self.table_inv.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_inv.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table_inv.verticalHeader().setVisible(False)
        self.table_inv.doubleClicked.connect(self.edit_item)
        
        # ── Keterangan jumlah data ─────────────
        self.lbl_count = QLabel("0 item ditemukan")
        self.lbl_count.setStyleSheet("font-size: 12px; color: #94a3b8;")
        
        layout.addLayout(top_layout)
        layout.addLayout(crud_layout)
        layout.addWidget(self.table_inv)
        layout.addWidget(self.lbl_count)
        
    # ── Load data ──────────────────────────────
    def load_data(self):
        search_text = self.search_inv.text().lower()
        kategori = self.filter_kategori.currentText()
        
        query = "SELECT * FROM items WHERE nama_alat LIKE ?"
        params = [f"%{search_text}%"]
        if kategori != "Semua Kategori":
            query += " AND kategori = ?"
            params.append(kategori)
        query += " ORDER BY nama_alat ASC"
        
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        
        self.table_inv.setUpdatesEnabled(False)
        self.table_inv.setRowCount(len(rows))
        
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                if col_idx in [1, 2, 3]:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignCenter)
                self.table_inv.setItem(row_idx, col_idx, item)
                
            stok_tersedia = int(row_data[5]) if row_data[5] is not None else 0
            if stok_tersedia == 0:
                for col_idx in range(self.table_inv.columnCount()):
                    cell = self.table_inv.item(row_idx, col_idx)
                    if cell:
                        cell.setForeground(Qt.red)
                        
        self.table_inv.setUpdatesEnabled(True)
        self.lbl_count.setText(f"{len(rows)} item ditemukan")
        
    # ── Ambil baris terpilih ───────────────────
    def _get_selected_item(self) -> dict | None:
        row = self.table_inv.currentRow()
        if row < 0:
            _show_message(self, "info", "Pilih Data",
                          "Pilih baris alat terlebih dahulu dari tabel.")
            return None
        return {
            "id":            self.table_inv.item(row, 0).text(),
            "kode_alat":     self.table_inv.item(row, 1).text(),
            "nama_alat":     self.table_inv.item(row, 2).text(),
            "kategori":      self.table_inv.item(row, 3).text(),
            "stok_total":    self.table_inv.item(row, 4).text(),
            "stok_tersedia": self.table_inv.item(row, 5).text(),
        }
        
    # ── TAMBAH ─────────────────────────────────
    def tambah_item(self):
        dlg = ItemDialog(self)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        try:
            conn = database.connect_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO items (kode_alat, nama_alat, kategori, stok_total, stok_tersedia) "
                "VALUES (?, ?, ?, ?, ?)",
                (data["kode_alat"], data["nama_alat"], data["kategori"],
                 data["stok_total"], data["stok_tersedia"])
            )
            conn.commit()
            conn.close()
            
            _show_message(self, "info", "Berhasil",
                          f"Alat '{data['nama_alat']}' berhasil ditambahkan.")
            self.load_data()
        except Exception as e:
            _show_message(self, "warning", "Gagal",
                          f"Gagal menyimpan data.\nKode alat mungkin sudah dipakai.\n\nDetail: {e}")
            
    # ── EDIT ───────────────────────────────────
    def edit_item(self):
        selected = self._get_selected_item()
        if not selected:
            return
        dlg = ItemDialog(self, item_data=selected)
        if dlg.exec() != QDialog.Accepted:
            return
        data = dlg.get_data()
        try:
            conn = database.connect_db()
            cur = conn.cursor()
            cur.execute(
                "UPDATE items SET kode_alat=?, nama_alat=?, kategori=?, "
                "stok_total=?, stok_tersedia=? WHERE id=?",
                (data["kode_alat"], data["nama_alat"], data["kategori"],
                 data["stok_total"], data["stok_tersedia"], selected["id"])
            )
            conn.commit()
            conn.close()
            
            _show_message(self, "info", "Berhasil",
                          f"Data '{data['nama_alat']}' berhasil diperbarui.")
            self.load_data()
        except Exception as e:
            _show_message(self, "warning", "Gagal", f"Gagal memperbarui data.\n\nDetail: {e}")
            
    # ── HAPUS ──────────────────────────────────
    def hapus_item(self):
        selected = self._get_selected_item()
        if not selected:
            return
            
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM borrowings WHERE item_id=? AND status='Dipinjam'",
            (selected["id"],)
        )
        sedang_dipinjam = cur.fetchone()[0]
        conn.close()
        
        if sedang_dipinjam > 0:
            _show_message(self, "warning", "Tidak Dapat Dihapus",
                          f"Alat '{selected['nama_alat']}' sedang dalam status dipinjam.\n"
                          "Selesaikan peminjaman terlebih dahulu sebelum menghapus.")
            return
            
        konfirmasi = _show_message(
            self,
            "question",
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus alat berikut?\n\n"
            f"  Kode : {selected['kode_alat']}\n"
            f"  Nama : {selected['nama_alat']}\n\n"
            "Tindakan ini tidak dapat dibatalkan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if konfirmasi != QMessageBox.Yes:
            return
            
        try:
            conn = database.connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM items WHERE id=?", (selected["id"],))
            conn.commit()
            conn.close()
            
            _show_message(self, "info", "Berhasil",
                          f"Alat '{selected['nama_alat']}' berhasil dihapus.")
            self.load_data()
        except Exception as e:
            _show_message(self, "warning", "Gagal", f"Gagal menghapus data.\n\nDetail: {e}")
            
    # ── Export CSV ─────────────────────────────
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                
                headers = [
                    self.table_inv.horizontalHeaderItem(i).text()
                    for i in range(1, self.table_inv.columnCount())
                ]
                writer.writerow(headers)
                
                for row in range(self.table_inv.rowCount()):
                    row_data = []
                    for col in range(1, self.table_inv.columnCount()):
                        cell = self.table_inv.item(row, col)
                        row_data.append(cell.text() if cell else "")
                    writer.writerow(row_data)
                    
            _show_message(self, "info", "Sukses",
                          "Data inventaris berhasil diekspor!\n\n"
                          "Silakan buka file tersebut di Excel/WPS untuk melihat tabel yang rapi.")
        except Exception as e:
            _show_message(self, "warning", "Gagal", f"Gagal mengekspor data.\n\nDetail: {e}")
            
    # ── Tema ───────────────────────────────────
    def set_theme(self, state):
        self.setProperty("theme", state)
        try:
            with open("assets/inventory.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass