from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PySide6.QtCore import Qt, QDate
import models.dashboard_model as dashboard_model # Import model yang baru dibuat

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        self.lbl_welcome = QLabel(" 👋  Selamat Datang di Dashboard Laboratorium")
        self.lbl_welcome.setObjectName("DashboardHeader")
        self.main_layout.addWidget(self.lbl_welcome)

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(20)

        self.card_total_items, self.val_total_items = self.create_card("Total Jenis Alat", " 📦 ")
        self.cards_layout.addWidget(self.card_total_items, 0, 0)

        self.card_borrowed, self.val_borrowed = self.create_card("Sedang Dipinjam", " 🔄 ")
        self.cards_layout.addWidget(self.card_borrowed, 0, 1)

        self.card_total_stock, self.val_total_stock = self.create_card("Total Stok Fisik", " 📊 ")
        self.cards_layout.addWidget(self.card_total_stock, 1, 0)

        self.card_late, self.val_late = self.create_card("Terlambat", "  ⏰  ")
        self.cards_layout.addWidget(self.card_late, 1, 1)

        self.main_layout.addLayout(self.cards_layout)
        self.main_layout.addStretch()

    def create_card(self, title_text, icon):
        card = QFrame()
        card.setObjectName("DashboardCard")
        layout = QVBoxLayout(card)

        title = QLabel(f"{icon}  {title_text}")
        title.setObjectName("CardTitle")

        value = QLabel("0")
        value.setObjectName("CardValue")
        value.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(value)
        return card, value

    def load_data(self):
        """Load data wok"""
        self.val_total_items.setText(str(dashboard_model.get_total_jenis_alat()))
        
        self.val_borrowed.setText(str(dashboard_model.get_total_alat_dipinjam()))
        
        self.val_total_stock.setText(str(dashboard_model.get_total_stok_fisik()))
        
        current_date_str = QDate.currentDate().toString("yyyy-MM-dd")
        self.val_late.setText(str(dashboard_model.get_total_peminjaman_terlambat(current_date_str)))

    def set_theme(self, state):
        self.setProperty("theme", state)
        try:
            with open("assets/dashboard.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass