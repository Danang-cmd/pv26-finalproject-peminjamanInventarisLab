import database.database as database

def get_total_jenis_alat():
    """Mengambil total jenis alat yang terdaftar di sistem."""
    conn = database.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM items")
    result = cur.fetchone()[0] or 0
    conn.close()
    return result

def get_total_alat_dipinjam():
    """Mengambil total kuantitas alat yang fisiknya sedang di luar (Dipinjam/Terlambat)."""
    conn = database.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(jumlah) FROM borrowings WHERE status IN ('Dipinjam', 'Terlambat')")
    result = cur.fetchone()[0] or 0
    conn.close()
    return result

def get_total_stok_fisik():
    """Mengambil total keseluruhan stok fisik barang yang dimiliki lab."""
    conn = database.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(stok_total) FROM items")
    result = cur.fetchone()[0] or 0
    conn.close()
    return result

def get_total_peminjaman_terlambat(current_date_str):
    """Mengambil jumlah transaksi peminjaman yang melewati tenggat waktu."""
    conn = database.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM borrowings WHERE status='Dipinjam' AND tgl_kembali < ?", (current_date_str,))
    result = cur.fetchone()[0] or 0
    conn.close()
    return result