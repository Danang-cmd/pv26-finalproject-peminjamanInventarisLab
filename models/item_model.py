import database.database as database

class ItemModel:
    @staticmethod
    def get_all(search_text="", kategori="Semua Kategori"):
        """Mengambil data alat berdasarkan pencarian dan filter."""
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
        
        return rows

    @staticmethod
    def add(data: dict):
        """Menambahkan alat baru ke database."""
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

    @staticmethod
    def update(item_id, data: dict):
        """Memperbarui data alat yang sudah ada."""
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute(
            "UPDATE items SET kode_alat=?, nama_alat=?, kategori=?, "
            "stok_total=?, stok_tersedia=? WHERE id=?",
            (data["kode_alat"], data["nama_alat"], data["kategori"],
             data["stok_total"], data["stok_tersedia"], item_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def is_borrowed(item_id) -> bool:
        """Mengecek apakah alat sedang dipinjam."""
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM borrowings WHERE item_id=? AND status='Dipinjam'",
            (item_id,)
        )
        sedang_dipinjam = cur.fetchone()[0]
        conn.close()
        
        return sedang_dipinjam > 0

    @staticmethod
    def delete(item_id):
        """Menghapus alat dari database."""
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM items WHERE id=?", (item_id,))
        conn.commit()
        conn.close()