# 🔬 Sistem Peminjaman Inventaris Laboratorium
### Aplikasi Desktop Berbasis PySide6

> **Final Project — Pemrograman Visual (PemVIs)**
> Program Studi Teknik Informatika — Universitas Mataram
> Tahun Akademik 2025 / 2026

---

## 👥 Disusun Oleh

| Nama | NIM |
|------|-----|
| Danang Adiwijaya | F1D02310044 |
| Wimar Aryasmarta Prakasa | F1D02410026 |
| Mohammad Klisman Reynaldi | F1D022063 |

---

## 📋 Daftar Isi

1. [Deskripsi Aplikasi dan Latar Belakang](#1-deskripsi-aplikasi-dan-latar-belakang)
2. [Pembagian Tugas Anggota Kelompok](#2-pembagian-tugas-anggota-kelompok)
3. [Penjelasan Fitur-Fitur Utama](#3-penjelasan-fitur-fitur-utama)
4. [Alur Program](#4-alur-program)
5. [Skema Database](#5-skema-database)
6. [Screenshot Tampilan Antarmuka](#6-screenshot-tampilan-antarmuka)
7. [Cara Menjalankan Aplikasi](#7-cara-menjalankan-aplikasi)
8. [Kendala yang Dihadapi dan Cara Mengatasinya](#8-kendala-yang-dihadapi-dan-cara-mengatasinya)

---

## 1. Deskripsi Aplikasi dan Latar Belakang

### 1.1 Deskripsi Aplikasi

**Sistem Peminjaman Inventaris Laboratorium (LabSys)** adalah aplikasi desktop yang dikembangkan menggunakan framework **PySide6** berbasis Python. Aplikasi ini dirancang untuk membantu pengelolaan aset dan peralatan di laboratorium Informatika, mencakup:

- Pencatatan inventaris alat
- Pengelolaan data peminjaman oleh mahasiswa
- Visualisasi statistik penggunaan alat secara real-time

Aplikasi terdiri dari **tiga halaman utama** yang dapat diakses melalui navigasi sidebar: **Dashboard**, **Kelola Inventaris**, dan **Peminjaman**. Data disimpan secara lokal menggunakan **SQLite** dengan dua tabel yang saling berelasi, yaitu tabel `items` dan tabel `borrowings`.

### 1.2 Latar Belakang Pemilihan Topik

Laboratorium Informatika memiliki berbagai peralatan seperti mikrokontroler, sensor, modul elektronik, dan alat ukur yang sering dipinjam oleh mahasiswa untuk keperluan praktikum maupun proyek. Selama ini, pencatatan peminjaman masih dilakukan secara manual menggunakan kertas atau spreadsheet sederhana, yang rentan terhadap:

- Kesalahan pencatatan
- Kehilangan data
- Kesulitan dalam memantau ketersediaan stok secara real-time

Berdasarkan permasalahan tersebut, kelompok memilih topik **Sistem Peminjaman Inventaris Laboratorium** sebagai proyek akhir. Topik ini dinilai memiliki relevansi nyata dengan kebutuhan sehari-hari di lingkungan kampus, sekaligus mencakup seluruh fitur wajib yang ditentukan — mulai dari pengelolaan data dengan SQLite, antarmuka multi-halaman, validasi input, hingga ekspor laporan.

---

## 2. Pembagian Tugas Anggota Kelompok

| Nama | NIM | Tugas |
|------|-----|-------|
| Danang Adiwijaya | F1D02310044 | Dashboard, struktur utama aplikasi (`main.py`), navigasi sidebar, tema dark/light, status bar, menu bar, integrasi antar halaman |
| Wimar Aryasmarta Prakasa | F1D02410026 | Halaman Peminjaman (`borrowing.py`): form pinjam, validasi input, cetak bukti PDF, logika update stok saat peminjaman dicatat |
| Mohammad Klisman Reynaldi | F1D022063 | Halaman Kelola Inventaris (`inventory.py`): fitur CRUD alat, dialog tambah/edit, konfirmasi hapus, indikator stok, export CSV, styling QSS inventaris |

> Seluruh anggota kelompok berkontribusi pada inisialisasi database (`database.py`), pengujian fungsionalitas antarmuka, serta penyusunan laporan akhir. Setiap anggota memiliki riwayat commit di repository GitHub sebagai bukti kontribusi nyata dalam pengerjaan proyek.

---

## 3. Penjelasan Fitur-Fitur Utama

### 3.1 Dashboard

Halaman pertama yang ditampilkan saat aplikasi dibuka. Dashboard menampilkan **ringkasan kondisi inventaris laboratorium** secara visual, meliputi:

- ✅ Total alat yang terdaftar di laboratorium
- ✅ Jumlah alat yang tersedia dan sedang dipinjam
- ✅ Daftar peminjaman aktif terkini
- ✅ Statistik penggunaan alat dalam bentuk ringkasan

> Dashboard diperbarui secara otomatis setiap kali pengguna berpindah ke halaman ini melalui navigasi sidebar.

### 3.2 Kelola Inventaris

Halaman ini digunakan untuk **mengelola data alat laboratorium** secara lengkap. Fitur yang tersedia:

- **Tambah Alat** — Membuka dialog form dengan validasi input (kode, nama, kategori, stok total, stok tersedia)
- **Edit Alat** — Memuat data alat yang dipilih ke dalam form untuk diubah; dapat diakses melalui tombol atau double-click baris tabel
- **Hapus Alat** — Menampilkan konfirmasi sebelum menghapus; dilindungi oleh pengecekan peminjaman aktif sehingga alat yang sedang dipinjam tidak dapat dihapus
- **Pencarian real-time** berdasarkan nama alat
- **Filter berdasarkan kategori**: Komputer & Jaringan, Elektronik & Mikrokontroler, Alat Ukur, Kabel & Konektor, Komponen Elektronik, Lainnya
- **Indikator warna merah** pada baris alat dengan stok tersedia = 0
- **Export data inventaris** ke format CSV
- **Label jumlah item** yang ditemukan di bawah tabel

### 3.3 Peminjaman

Halaman ini mencatat dan mengelola **transaksi peminjaman alat** oleh mahasiswa. Fitur yang tersedia:

- **Form peminjaman** dengan input nama mahasiswa, NIM, pilihan alat (hanya alat dengan stok > 0), tanggal pinjam, dan tenggat kembali
- **Validasi input**: nama dan NIM tidak boleh kosong; alat harus dipilih
- Saat peminjaman disimpan, **stok tersedia alat otomatis berkurang 1** di database
- **Tampilan tabel** seluruh riwayat peminjaman dengan kolom status
- **Cetak bukti peminjaman** dalam format PDF menggunakan QPrinter

### 3.4 Fitur Pendukung

- 🌙 **Toggle Dark/Light Mode** — dapat diakses melalui menu File, berlaku di seluruh halaman secara konsisten
- 📋 **Menu Bar** — berisi File (toggle tema, exit), Help (about aplikasi), dan Exit
- 📌 **Status Bar** — menampilkan nama dan NIM seluruh anggota kelompok di pojok kanan bawah
- 🎨 **Styling QSS** — tema visual konsisten diterapkan di setiap halaman melalui file `.qss` terpisah

---

## 4. Alur Program

### 4.1 Alur Umum Aplikasi

Berikut adalah alur umum program saat aplikasi dijalankan:

```
1. Aplikasi dijalankan melalui main.py
2. Fungsi init_db() dipanggil untuk membuat tabel items dan borrowings 
   jika belum ada, serta mengisi data dummy awal
3. MainWindow ditampilkan dengan sidebar navigasi dan QStackedWidget 
   berisi tiga halaman
4. Halaman default yang ditampilkan adalah Dashboard
5. Pengguna dapat berpindah halaman melalui tombol sidebar; 
   setiap perpindahan memicu load_data() untuk memperbarui tampilan
```

### 4.2 Alur Peminjaman Alat

Berikut adalah alur spesifik saat pengguna melakukan peminjaman alat:

```
1. Pengguna membuka halaman Peminjaman dan menekan tombol '+ Pinjam Alat'
2. BorrowDialog terbuka, dropdown alat hanya menampilkan alat 
   dengan stok_tersedia > 0
3. Pengguna mengisi nama, NIM, memilih alat, dan menentukan tanggal
4. Validasi dijalankan — jika ada field kosong atau alat tidak dipilih, 
   muncul pesan error
5. Jika valid: data disimpan ke tabel borrowings dan stok_tersedia alat 
   dikurangi 1 dalam satu transaksi database
6. Tabel peminjaman diperbarui dan notifikasi sukses ditampilkan
```

---

## 5. Skema Database

Aplikasi menggunakan satu file SQLite (`lab_inventory.db`) dengan **dua tabel** yang saling berelasi melalui foreign key.

### 5.1 Tabel `items`

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| `id` | INTEGER | Primary Key, Auto Increment |
| `kode_alat` | TEXT | UNIQUE — Kode unik alat (contoh: `ARD-01`) |
| `nama_alat` | TEXT | Nama lengkap alat laboratorium |
| `kategori` | TEXT | Kategori alat (Elektronik & Mikrokontroler, dll) |
| `stok_total` | INTEGER | Jumlah total unit alat yang dimiliki lab |
| `stok_tersedia` | INTEGER | Jumlah unit yang saat ini tersedia untuk dipinjam |

### 5.2 Tabel `borrowings`

| Kolom | Tipe Data | Keterangan |
|-------|-----------|------------|
| `id` | INTEGER | Primary Key, Auto Increment |
| `nama_mhs` | TEXT | Nama lengkap mahasiswa peminjam |
| `nim_mhs` | TEXT | NIM mahasiswa peminjam |
| `item_id` | INTEGER | Foreign Key referensi ke `items(id)` |
| `tgl_pinjam` | DATE | Tanggal alat mulai dipinjam |
| `tgl_kembali` | DATE | Tenggat waktu pengembalian alat |
| `status` | TEXT | Status peminjaman: `'Dipinjam'` atau `'Dikembalikan'` |

> **Relasi antar tabel:** `borrowings.item_id` → `items.id` *(Many-to-One)*
> Satu alat dapat dipinjam berkali-kali, namun setiap transaksi peminjaman hanya merujuk ke satu alat. Integritas relasi dijaga melalui `FOREIGN KEY` constraint pada SQLite.

---

## 6. Screenshot Tampilan Antarmuka

### 6.1 Halaman Dashboard
Menampilkan ringkasan statistik inventaris dan daftar peminjaman aktif. Sidebar navigasi terlihat di sisi kiri dengan tombol aktif yang ditandai secara visual.

### 6.2 Halaman Kelola Inventaris
Menampilkan tabel daftar alat dengan fitur pencarian, filter kategori, dan tombol CRUD (Tambah, Edit, Hapus). Baris alat dengan stok habis ditampilkan dengan teks berwarna merah.

### 6.3 Dialog Tambah / Edit Alat
Dialog form yang muncul saat tombol Tambah atau Edit ditekan, berisi field kode alat, nama alat, kategori (dropdown), stok total, dan stok tersedia beserta validasi input.

### 6.4 Halaman Peminjaman
Menampilkan tabel riwayat peminjaman dan tombol untuk menambah data peminjaman baru serta cetak bukti PDF.

### 6.5 Tampilan Dark Mode
Tampilan aplikasi saat dark mode diaktifkan melalui menu **File > Toggle Dark/Light Mode**, menunjukkan konsistensi tema di seluruh halaman.

---

## 7. Cara Menjalankan Aplikasi

### Prasyarat

Pastikan Python **3.9+** telah terinstall. Install seluruh dependensi menggunakan perintah berikut:

```bash
pip install -r requirements.txt
```

**Dependensi yang dibutuhkan (`requirements.txt`):**

```
PySide6>=6.5.0
reportlab>=4.0.0
matplotlib>=3.7.0
```

### Menjalankan Aplikasi

```bash
python main.py
```

### Struktur Direktori

```
pv26-finalproject-peminjamanInventarisLab/
│
├── main.py                    # Entry point aplikasi & MainWindow
│
├── database/
│   ├── database.py            # Inisialisasi & koneksi SQLite
│   └── lab_inventory.db       # File database SQLite
│
├── ui/
│   ├── dashboard.py           # Halaman Dashboard
│   ├── inventory.py           # Halaman Kelola Inventaris
│   └── borrowing.py           # Halaman Peminjaman
│
├── models/
│   └── dashboard_model.py     # Model data untuk Dashboard
│
├── assets/
│   ├── global.qss             # Stylesheet global (dark/light theme)
│   ├── dashboard.qss          # Stylesheet halaman Dashboard
│   ├── inventory.qss          # Stylesheet halaman Inventaris
│   └── borrowing.qss          # Stylesheet halaman Peminjaman
│
└── requirements.txt           # Dependensi Python
```

---

## 8. Kendala yang Dihadapi dan Cara Mengatasinya

### 8.1 Sinkronisasi Database Antar Modul

**Kendala:** Pada awal pengembangan, path file database (`lab_inventory.db`) menggunakan path relatif sederhana (`DB_NAME = "lab_inventory.db"`). Akibatnya, saat aplikasi dijalankan dari direktori yang berbeda, SQLite membuat file database baru yang kosong alih-alih membaca file yang sudah ada. Hal ini menyebabkan data yang sudah diinput tidak muncul dan perubahan stok tidak tersimpan dengan benar.

**Cara mengatasi:** Path database diubah menjadi path absolut menggunakan `os.path.abspath(__file__)`, sehingga file database selalu merujuk ke lokasi yang sama yaitu di dalam folder `database/`, tanpa bergantung pada direktori kerja saat aplikasi dijalankan.

```python
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_inventory.db")
```

---

### 8.2 Stok Alat Tidak Berkurang Saat Peminjaman

**Kendala:** Setelah fitur peminjaman berhasil menyimpan data ke tabel `borrowings`, kolom `stok_tersedia` pada tabel `items` tidak berubah. Pengguna yang melakukan peminjaman tetap melihat stok yang sama di halaman Kelola Inventaris.

**Cara mengatasi:** Ditemukan bahwa query `UPDATE items SET stok_tersedia = stok_tersedia - 1` ditulis **setelah** perintah `conn.commit()`, sehingga perubahan stok tidak pernah di-commit ke database. Urutan kode diperbaiki agar `INSERT` dan `UPDATE` dieksekusi terlebih dahulu sebelum satu perintah `conn.commit()` dipanggil, memastikan kedua operasi tersimpan dalam **satu transaksi yang atomik**.

---

### 8.3 Teks Dropdown Tidak Terlihat pada Dark Mode

**Kendala:** Saat aplikasi berada dalam mode gelap (*dark mode*), teks pada dropdown list (`QComboBox`) menjadi tidak terlihat karena warna teks ikut berubah menjadi putih, sementara background popup dropdown juga berwarna terang akibat style yang tidak mencakup elemen `QAbstractItemView`.

**Cara mengatasi:** Ditambahkan style CSS eksplisit untuk `QComboBox QAbstractItemView` dan `QComboBox QAbstractItemView::item` pada file `inventory.qss`, mencakup pengaturan warna teks dan background untuk kedua tema (light dan dark) secara terpisah. Hal yang sama diterapkan untuk widget `QSpinBox` yang digunakan di dalam dialog form.

---

### 8.4 Relevansi Data dengan Laboratorium Informatika

**Kendala:** Data awal (*dummy data*) dan kategori yang digunakan pada awal pengembangan tidak mencerminkan jenis alat yang sebenarnya ada di Laboratorium Informatika. Kategori seperti `'Gelas Kaca'` dan `'Mekanik'` tidak relevan dengan konteks laboratorium komputer dan elektronik.

**Cara mengatasi:** Kategori diperbarui menjadi kategori yang relevan dengan lab Informatika seperti **Komputer & Jaringan**, **Elektronik & Mikrokontroler**, **Alat Ukur**, **Kabel & Konektor**, dan **Komponen Elektronik**. Data dummy juga diperbarui dengan alat-alat yang umum digunakan seperti **Arduino Uno**, **Raspberry Pi**, **ESP32**, breadboard, multimeter, dan sensor ultrasonik.

---

## 📌 Bukti Kontribusi Anggota Kelompok

Kontribusi setiap anggota kelompok dapat diverifikasi melalui **riwayat commit** pada repository GitHub proyek. Setiap anggota melakukan commit secara mandiri pada bagian yang menjadi tanggung jawabnya masing-masing.

---

<div align="center">
  <p>
    <strong>Sistem Peminjaman Inventaris Laboratorium</strong><br>
    Program Studi Teknik Informatika — Universitas Mataram<br>
    2025 / 2026
  </p>
  <p>
    <em>Danang Adiwijaya (F1D02310044) &nbsp;|&nbsp; Wimar Aryasmarta Prakasa (F1D02410026) &nbsp;|&nbsp; Mohammad Klisman Reynaldi (F1D022063)</em>
  </p>
</div>
