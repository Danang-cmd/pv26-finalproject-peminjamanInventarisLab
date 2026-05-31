from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
import database.database as database

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.lbl_summary = QLabel("Memuat ringkasan...")
        self.lbl_summary.setObjectName("DashboardSummary")
        layout.addWidget(self.lbl_summary)
        layout.addStretch()

    def load_data(self):
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM items")
        total_items = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM borrowings WHERE status='Dipinjam'")
        active_borrows = cur.fetchone()[0]
        conn.close()
        self.lbl_summary.setText(f"📋 Ringkasan Laboratorium\n\nTotal Jenis Alat: {total_items}\nAlat Sedang Dipinjam: {active_borrows}")

    def set_theme(self, state):
        self.setProperty("theme", state)
        try:
            with open("assets/dashboard.qss", "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            pass