import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QMessageBox
from PySide6.QtGui import QAction
import database.database as database

# Import UI yang sudah dipisah
from ui.dashboard import DashboardPage
from ui.inventory import InventoryPage
from ui.borrowing import BorrowingPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Peminjaman Inventaris Lab")
        self.resize(1100, 650)
        database.init_db()

        self.is_dark_mode = False
        self.setup_ui()
        self.apply_theme()
        
        self.insert_dummy_data()

    def setup_ui(self):
        menubar = self.menuBar()

        # --- MENU FILE ---
        file_menu = menubar.addMenu("File")
        
        toggle_theme_action = QAction("Toggle Dark/Light Mode", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        file_menu.addAction(toggle_theme_action)

        # --- MENU HELP (Sekarang Berisi Dropdown) ---
        help_menu = menubar.addMenu("Help")
        
        # Membuat item "About" di dalam menu Help
        about_action = QAction("About Application", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # --- TOMBOL EXIT (SEJAJAR DI MENU BAR) ---
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menubar.addAction(exit_action)

        # --- STATUS BAR (POJOK KANAN BAWAH) ---
        # Kita buat QLabel khusus agar teks bisa diatur posisinya dan di-style lewat QSS
        self.status_label = QLabel("Danang Adiwijaya (F1D02310044) | Wimar (F1D024000) | Mohammad Klisman Reynaldi (F1D022063)")
        self.status_label.setObjectName("StatusLabel")
        
        # permanent widget otomatis meletakkan widget di pojok kanan bawah
        self.statusBar().addPermanentWidget(self.status_label)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar Navigation
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(8)

        lbl_menu = QLabel("NAVIGATION")
        lbl_menu.setObjectName("SidebarTitle")
        sidebar_layout.addWidget(lbl_menu)

        self.btn_dashboard = QPushButton(" Dashboard")
        self.btn_inventory = QPushButton(" Kelola Inventaris")
        self.btn_borrow = QPushButton(" Peminjaman")

        for btn in [self.btn_dashboard, self.btn_inventory, self.btn_borrow]:
            btn.setObjectName("SidebarButton")
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        # Stacked Widget & Pages
        self.pages = QStackedWidget()
        self.pages.setObjectName("MainContent")
        
        self.page_dashboard = DashboardPage()
        self.page_inventory = InventoryPage()
        self.page_borrow = BorrowingPage()
        
        self.pages.addWidget(self.page_dashboard)
        self.pages.addWidget(self.page_inventory)
        self.pages.addWidget(self.page_borrow)

        # Setup Navigation Logic
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0, self.page_dashboard.load_data))
        self.btn_inventory.clicked.connect(lambda: self.switch_page(1, self.page_inventory.load_data))
        self.btn_borrow.clicked.connect(lambda: self.switch_page(2, self.page_borrow.load_data))

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)
        
        self.switch_page(0, self.page_dashboard.load_data) # Default

    def show_about(self):
        """Menampilkan dialog informasi anggota kelompok saat menu Help -> About diklik"""
        about_text = (
            "Sistem Peminjaman Inventaris Lab\n\n"
            "Aplikasi ini adalah sistem manajemen internal berbasis antarmuka grafis (GUI) yang dirancang khusus untuk mempermudah tugas seorang petugas laboratorium dalam mendata aset lab serta mengelola transaksi peminjaman barang secara digital, menggantikan pencatatan manual di buku besar."
        )
        
        # Buat objek dialog secara eksplisit agar bisa ditempel properti tema
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About Application")
        msg_box.setText(about_text)
        msg_box.setIcon(QMessageBox.Information)
        
        # Samakan properti tema dengan status window saat ini
        state = "dark" if self.is_dark_mode else "light"
        msg_box.setProperty("theme", state)
        
        msg_box.exec()

    def switch_page(self, index, load_func=None):
        self.pages.setCurrentIndex(index)
        if load_func:
            load_func()
            
        buttons = [self.btn_dashboard, self.btn_inventory, self.btn_borrow]
        for i, btn in enumerate(buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def apply_theme(self):
        state = "dark" if self.is_dark_mode else "light"
        self.setProperty("theme", state)
        self.statusBar().setProperty("theme", state)
        
        # Tambahkan ini agar label status bar baru juga ikut memperbarui temanya
        if hasattr(self, 'status_label'):
            self.status_label.setProperty("theme", state)

        # Load Global Styles
        try:
            with open("assets/global.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass

        # FORCE REFRESH
        self.style().unpolish(self)
        self.style().polish(self)
        self.statusBar().style().unpolish(self.statusBar())
        self.statusBar().style().polish(self.statusBar())
        
        # Refresh style untuk label status bar baru
        if hasattr(self, 'status_label'):
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)

        # Trigger Theme Update di masing-masing page
        self.page_dashboard.set_theme(state)
        self.page_inventory.set_theme(state)
        self.page_borrow.set_theme(state)

    def insert_dummy_data(self):
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM items")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO items (kode_alat, nama_alat, kategori, stok_total, stok_tersedia) VALUES ('ELK-01', 'Osiloskop', 'Elektronik', 5, 5)")
            cur.execute("INSERT INTO items (kode_alat, nama_alat, kategori, stok_total, stok_tersedia) VALUES ('GLS-01', 'Gelas Ukur 50ml', 'Gelas Kaca', 20, 20)")
            conn.commit()
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())