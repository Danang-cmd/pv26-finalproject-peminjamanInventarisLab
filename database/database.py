import sqlite3
import os

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_inventory.db")

def connect_db():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Tabel 1: Inventaris (6 Kolom)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode_alat TEXT UNIQUE,
            nama_alat TEXT,
            kategori TEXT,
            stok_total INTEGER,
            stok_tersedia INTEGER
        )
    ''')

    # Tabel 2: Peminjaman
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_mhs TEXT,
            nim_mhs TEXT,
            item_id INTEGER,
            tgl_pinjam DATE,
            tgl_kembali DATE,
            status TEXT,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    ''')

    # ── FITUR UPDATE OTOMATIS ──────────────────────────────────────────
    # Mencoba menambahkan kolom 'jumlah' secara paksa ke database lama.
    # Jika kolomnya sudah ada, program akan mengabaikannya secara aman.
    try:
        cursor.execute("ALTER TABLE borrowings ADD COLUMN jumlah INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass  # Kolom sudah ada, tidak perlu diapa-apakan lagi
    # ───────────────────────────────────────────────────────────────────

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database berhasil diinisialisasi.")