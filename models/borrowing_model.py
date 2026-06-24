import database.database as database

class BorrowingModel:
    @staticmethod
    def get_all():
        """Mengambil semua data peminjaman beserta nama alat dari tabel items."""
        query = """
        SELECT b.id, b.nama_mhs, b.nim_mhs, i.nama_alat, b.jumlah,
               b.tgl_pinjam, b.tgl_kembali, b.status, b.item_id
        FROM borrowings b
        JOIN items i ON b.item_id = i.id
        ORDER BY b.id DESC
        """
        conn = database.connect_db()
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_available_items():
        """Mengambil daftar alat yang stoknya masih tersedia untuk dropdown."""
        conn = database.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_alat, stok_tersedia FROM items WHERE stok_tersedia > 0")
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_item_by_id(item_id):
        """Mengambil nama alat berdasarkan ID untuk kebutuhan edit data."""
        conn = database.connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nama_alat FROM items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        conn.close()
        return item

    @staticmethod
    def add(data: dict):
        """Menyimpan data peminjaman baru dan memotong stok alat."""
        conn = database.connect_db()
        cur = conn.cursor()
        try:
            # Insert ke tabel borrowings
            cur.execute(
                "INSERT INTO borrowings (nama_mhs, nim_mhs, item_id, jumlah, tgl_pinjam, tgl_kembali, status) VALUES (?, ?, ?, ?, ?, ?, 'Dipinjam')",
                (data["nama_mhs"], data["nim_mhs"], data["item_id"], data["jumlah"], data["tgl_pinjam"], data["tgl_kembali"])
            )
            # Kurangi stok_tersedia di tabel items
            cur.execute("UPDATE items SET stok_tersedia = stok_tersedia - ? WHERE id = ?", (data["jumlah"], data["item_id"]))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def update(borrow_id, data: dict, selected: dict):
        """Memperbarui data peminjaman dan menyesuaikan stok alat jika status berubah."""
        conn = database.connect_db()
        cur = conn.cursor()
        try:
            # Update data peminjaman
            cur.execute("UPDATE borrowings SET nama_mhs=?, nim_mhs=?, tgl_pinjam=?, tgl_kembali=?, status=? WHERE id=?",
                        (data["nama_mhs"], data["nim_mhs"], data["tgl_pinjam"], data["tgl_kembali"], data["status"], borrow_id))

            jumlah_alat = int(selected["jumlah"])
            
            # Logika pengembalian/peminjaman ulang stok
            if selected["status"] == "Dipinjam" and data["status"] == "Dikembalikan":
                cur.execute("UPDATE items SET stok_tersedia = stok_tersedia + ? WHERE id = ?", (jumlah_alat, selected["item_id"]))
            elif selected["status"] == "Dikembalikan" and data["status"] == "Dipinjam":
                cur.execute("SELECT stok_tersedia FROM items WHERE id = ?", (selected["item_id"],))
                stok = cur.fetchone()[0]
                if stok >= jumlah_alat:
                    cur.execute("UPDATE items SET stok_tersedia = stok_tersedia - ? WHERE id = ?", (jumlah_alat, selected["item_id"]))
                else:
                    raise ValueError("Stok alat sudah tidak mencukupi untuk dipinjam kembali.")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def delete(borrow_id, selected: dict):
        """Menghapus data peminjaman dan mengembalikan stok jika statusnya masih dipinjam."""
        conn = database.connect_db()
        cur = conn.cursor()
        try:
            if selected["status"] == "Dipinjam":
                cur.execute("UPDATE items SET stok_tersedia = stok_tersedia + ? WHERE id = ?", (int(selected["jumlah"]), selected["item_id"]))
            cur.execute("DELETE FROM borrowings WHERE id=?", (borrow_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()