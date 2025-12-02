# === GRUP 1: IMPORTS & DASHBOARD ===
from datetime import datetime
from tabulate import tabulate
import query as db

def dashboard_penjual(sesi):
    # Menampilkan menu dashboard penjual dan mengarahkan ke fitur yang dipilih hingga logout
    toko = db.ambil_toko_by_user(sesi['id'])  # db.ambil_toko_by_user: ambil profil toko berdasarkan id akun
    if not toko:  # Jika tidak ada data toko untuk user ini
        print("Toko tidak ditemukan.")  # Beri tahu pengguna bahwa toko tidak tersedia
        input("Tekan ENTER untuk melanjutkan...")  # Jeda agar pesan terbaca
        return  # Keluar dari fungsi dashboard jika toko tidak ada
    
    while True:  # Loop menu utama penjual yang berjalan terus hingga pengguna memilih logout
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        print(f'''
--- DASHBOARD TOKO: {toko[1]} ---
1. Inventaris Produk
2. Pesanan Masuk
3. Riwayat & Laporan
4. Ulasan Pembeli
5. Aduan ke Admin
6. Logout''')
        
        try:
            pilihan = input("Silakan pilih aksi yang menarik: ").strip()  # Ambil pilihan menu dari user
        except Exception as e:
            print(f"Error input: {e}")
            continue

        if not pilihan:  # Jika kosong, ulangi
            continue

        if pilihan == '1':  # Jika pilih 1, masuk ke menu inventaris produk
            menu_inventaris(toko[0])
        elif pilihan == '2':  # Jika pilih 2, masuk ke menu pesanan masuk
            menu_pesanan(toko[0])
        elif pilihan == '3':  # Jika pilih 3, tampilkan statistik toko
            tampilkan_statistik_toko(toko[0])
        elif pilihan == '4':  # Jika pilih 4, buka menu ulasan pelanggan
            menu_ulasan(toko[0])
        elif pilihan == '5':  # Jika pilih 5, buka menu aduan untuk admin
            menu_aduan(sesi['id'])
        elif pilihan == '6':  # Jika pilih 6, keluar (logout) dari dashboard penjual
            return
        else:  # Jika input bukan 1-6
            print("Pilihan tidak valid.")  # Beri tahu bahwa input tidak sesuai
            try:
                input("Tekan ENTER untuk melanjutkan...")  # Jeda agar pesan terbaca
            except Exception as e:
                print(f"Error input: {e}")
                continue

# === GRUP 2: FITUR INVENTARIS (PRODUK) ===

def menu_inventaris(toko_id):
    # Menampilkan dan mengelola daftar produk milik toko: tambah, edit, hapus, atau kembali
    while True:  # Loop menu inventaris, akan terus tampil sampai pengguna memilih kembali
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        print("--- KELOLA PRODUK ---")
        produk = db.ambil_produk_toko(toko_id)  # db.ambil_produk_toko: ambil daftar produk milik toko
        
        if not produk:  # Jika tidak ada produk pada toko ini
            print("Belum ada produk.")  # Informasikan bahwa inventaris kosong
        else:  # Jika ada produk, siapkan dan tampilkan dalam tabel
            data_produk = []  # List penampung baris tabel
            for item in produk:  # Loop setiap produk untuk membentuk baris tabel
                diskon_persen = f"{int((item[4] or 0) * 100)}%" if item[4] else "0%"  # Hitung diskon dalam persen
                data_produk.append([
                    item[0],  # ID Produk
                    item[1],  # Nama Produk
                    item[2],  # Stok
                    db.format_mata_uang(item[3]),  # db.format_mata_uang: format harga ke Rupiah
                    diskon_persen  # Diskon dalam persen
                ])
            
            print(tabulate(data_produk, headers=["ID", "Nama", "Stok", "Harga", "Diskon"], tablefmt="fancy_grid"))  # Tampilkan tabel
        
        print('''
\n1. Tambah Produk
2. Edit Produk
3. Hapus Produk
4. Kembali''')  # Menu aksi inventaris
        
        try:
            pilihan = input("Pilih aksi: ").strip()  # Ambil pilihan aksi
        except Exception as e:
            print(f"Error input: {e}")
            continue

        if not pilihan:  # Jika kosong, ulangi
            continue

        if pilihan == '4':  # Jika pilih 4 -> kembali ke dashboard penjual
            return
        elif pilihan == '1':  # Jika pilih 1 -> masuk ke form tambah produk
            menu_tambah_produk(toko_id)
        elif pilihan == '2':  # Jika pilih 2 -> masuk ke form edit produk
            menu_edit_produk(toko_id)
        elif pilihan == '3':  # Jika pilih 3 -> masuk ke form hapus produk
            menu_hapus_produk(toko_id)
        else:  # Jika input di luar 1-4
            print("Pilihan tidak valid.")  # Beri tahu input salah
            try:
                input("Tekan ENTER untuk melanjutkan...")  # Jeda
            except Exception as e:
                print(f"Error input: {e}")
                continue
            
def menu_tambah_produk(toko_id):
    print("\n--- TAMBAH PRODUK BARU ---")
    print("(Ketik 'batal' di inputan nama jika ingin membatalkan)")
    # 1. Input Nama (Wajib Diisi)
    while True:
        nama = db.input_varchar("Nama produk: ", 100)
        if nama.lower() == 'batal': return # Opsi keluar
        if nama:
            break
        print("Nama produk wajib diisi.")
    # 2. Input Harga (Wajib Angka)
    while True:
        harga_str = db.input_angka("Harga normal: ", 10)
        if harga_str:
            harga = int(harga_str) # Konversi ke integer untuk DB
            if stok <= 0:  # Cek apakah harga 0 atau negatif
                print("Stok tidak boleh 0 atau negatif!")
                continue  #  Ulangi input dari awal
            break  #  Keluar dari loop
        print("Harga wajib diisi angka.")
    # 3. Input Stok (Wajib Angka)
    while True:
        stok_str = db.input_angka("Stok awal: ", 10)
        if stok_str:
            stok = int(stok_str)
            if stok <= 0:  # Cek apakah harga 0 atau negatif
                print("Stok tidak boleh 0 atau negatif!")
                continue  #  Ulangi input dari awal
            break  #  Keluar dari loop
        print("Stok wajib diisi angka.")
    # 4. Input Tanggal Kadaluarsa (Validasi Format YYYY-MM-DD)
    while True:
        kadaluarsa = db.input_varchar("Tanggal kadaluarsa (YYYY-MM-DD): ", 10)
        if not kadaluarsa:
            print("Tanggal wajib diisi.")
            continue
        try:
            # Cek apakah format sesuai DATE Postgres
            datetime.strptime(kadaluarsa, '%Y-%m-%d')
            break
        except ValueError:
            print("Format salah! Harap gunakan format Tahun-Bulan-Hari (contoh: 2025-12-31).")
    # 5. Input Batas Pengambilan (Validasi Format YYYY-MM-DD)
    while True:
        batas_ambil = db.input_varchar("Batas pengambilan (YYYY-MM-DD): ", 10)
        if not batas_ambil:
            print("Tanggal wajib diisi.")
            continue
        try:
            datetime.strptime(batas_ambil, '%Y-%m-%d')
            # Opsional: Validasi logika (batas ambil tidak boleh melebihi kadaluarsa)
            if batas_ambil > kadaluarsa:
                print("Batas pengambilan tidak boleh melebihi tanggal kadaluarsa.")
                continue
            break
        except ValueError:
            print("Format salah! Harap gunakan format Tahun-Bulan-Hari (contoh: 2025-12-31).")
    # 6. Input Diskon (Wajib Angka, 0-100)
    while True:
        input_diskon = db.input_angka("Diskon (0-100, isi 0 jika tidak ada): ", 3)
        if input_diskon:
            diskon_val = int(input_diskon)
            if 0 <= diskon_val <= 100:
                diskon = float(diskon_val) / 100 # Konversi ke desimal (0.2) untuk DB
                break
            else:
                print("Diskon harus antara 0 sampai 100.")
        else:
            print("Diskon wajib diisi (isi 0 jika tidak ada).")
    # 7. Input Deskripsi (Wajib Diisi)
    while True:
        deskripsi = db.input_varchar("Deskripsi produk: ", 500)
        if deskripsi:
            break
        print("Deskripsi wajib diisi.")
    # 8. Pilih Kategori
    kategori = db.ambil_semua_kategori()
    if not kategori:
        print("Tidak ada kategori tersedia di sistem. Hubungi Admin.")
        return
    print("\nPilih Kategori:")
    print(tabulate(kategori, headers=["ID", "Kategori"], tablefmt="fancy_grid"))
    while True:
        id_kategori_input = db.input_angka("Pilih ID kategori: ", 10)
        if not id_kategori_input:
            print("Kategori wajib dipilih.")
            continue
        # Validasi apakah ID ada di daftar
        id_valid = False
        for kat in kategori:
            if str(kat[0]) == id_kategori_input:
                id_valid = True
                break
        if id_valid:
            id_kategori = int(id_kategori_input) # Siap masuk DB
            break
        else:
            print("ID Kategori tidak valid. Silakan pilih dari tabel di atas.")
    # Eksekusi Simpan ke Database
    if db.tambah_produk_baru(nama, harga, stok, diskon, deskripsi, kadaluarsa, batas_ambil, id_kategori, toko_id):
        print("Produk berhasil ditambahkan!")
    else:
        print("Gagal menambahkan produk (Error Database).")
    
    input("Tekan ENTER untuk melanjutkan...")
    
def menu_edit_produk(toko_id):  # Fungsi untuk mengedit produk toko
    try:  # Tangkap error input
        id_produk = input("\nMasukkan ID produk yang ingin diedit: ").strip()  # Minta ID produk dari user
    except Exception as e:  # Jika error input
        print(f"Error input: {e}")  # Tampilkan error
        return  # Keluar fungsi

    if not id_produk:  # Jika ID kosong
        return  # Keluar fungsi

    produk = db.ambil_produk_toko(toko_id)  # Ambil produk milik toko
    if not any(str(item[0]) == id_produk for item in produk):  # Jika ID tidak ada di produk toko
        print("Produk tidak ditemukan atau bukan milik toko Anda.")  # Pesan error
        input("Tekan ENTER untuk melanjutkan...")  # Tunggu user
        return  # Keluar fungsi

    print("\nEdit Produk (kosongkan jika tidak ingin mengubah)")  # Instruksi untuk user

    nama_baru = db.input_varchar("Nama baru: ", 100)  # Input nama baru
    while True:
        harga_baru = db.input_angka("Harga baru: ", 10)  # Input harga baru
        if harga_baru:
            harga = int(harga_baru) # Konversi ke integer untuk DB
            if harga <= 0:  # Cek apakah harga 0 atau negatif
                print("Harga tidak boleh 0 atau negatif!")
                continue  #  Ulangi input dari awal
            break  #  Kelaur dari loop
        print("Harga wajib diisi angka.")
    while True:
        stok_baru = db.input_angka("Stok baru: ", 10)  # Input stok baru
        if stok_baru:
            stok = int(stok_baru)  # Konversi ke integer untuk DB
            if stok <= 0:  # Cek apakah harga 0 atau negatif
                print("Stok tidak boleh 0 atau negatif!")
                continue  #  Ulangi input dari awal
            break  #  Keluar dari loop
        print("Stok wajin diisi angka.")
    diskon_baru = db.input_angka("Diskon baru (0-100): ", 3)  # Input diskon baru
    deskripsi_baru = db.input_varchar("Deskripsi baru: ", 500)  # Input deskripsi baru
    kadaluarsa_baru = db.input_varchar("Tanggal kadaluarsa baru (YYYY-MM-DD): ", 10)  # Input tanggal kadaluarsa
    batas_ambil_baru = db.input_varchar("Batas pengambilan baru (YYYY-MM-DD): ", 10)  # Input batas pengambilan

    perubahan = False  # Flag perubahan

    # --- BAGIAN 3: Eksekusi Update ---
    # bagian ini akan meng-update informasi produk jika ada isian baru dari user 
    try:
        if nama_baru:
            db.update_data_produk(id_produk, "nama_produk", nama_baru, toko_id)
            perubahan = True

        if harga_baru:
            db.update_data_produk(id_produk, "harga_per_produk", harga_baru, toko_id)
            perubahan = True

        if stok_baru:
            db.update_data_produk(id_produk, "stok_produk", stok_baru, toko_id)
            perubahan = True

        if diskon_baru:
            # Konversi diskon ke desimal (contoh: 20 jadi 0.2)
            db.update_data_produk(id_produk, "diskon", float(diskon_baru) / 100, toko_id)
            perubahan = True

        if deskripsi_baru:
            db.update_data_produk(id_produk, "deskripsi", deskripsi_baru, toko_id)
            perubahan = True

        if kadaluarsa_baru:
            db.update_data_produk(id_produk, "tanggal_kadaluarsa", kadaluarsa_baru, toko_id)
            perubahan = True

        if batas_ambil_baru:
            db.update_data_produk(id_produk, "batas_waktu_pengambilan", batas_ambil_baru, toko_id)
            perubahan = True
# bagian penanganan error umum saat update
    except Exception as e:
        print(f"Error saat update produk: {e}")
        print("Perubahan tidak dapat disimpan.")
        input("Tekan ENTER...")
        return

    # --- Konfirmasi Akhir ---
    if perubahan:
        print("Produk berhasil diupdate!")


def menu_hapus_produk(toko_id):
    # Menghapus (soft delete) satu produk milik toko
    try:
        id_produk = input("\nMasukkan ID produk yang ingin dihapus: ").strip()  # Ambil ID produk target
    except Exception as e:
        print(f"Error input: {e}")
        return
    
    if not id_produk:  # Jika input kosong
        return  # Kembali tanpa tindakan
        
    produk = db.ambil_produk_toko(toko_id)  # db.ambil_produk_toko: ambil daftar produk milik toko
    produk_ada = False  # Flag untuk memeriksa apakah ID ada
    for item in produk:  # Cek satu per satu
        if str(item[0]) == id_produk:  # Jika ID cocok
            produk_ada = True  # Tandai ditemukan
            break  # Hentikan pencarian
    
    if not produk_ada:  # Jika tidak ditemukan
        print("Produk tidak ditemukan.")  # Beri tahu pengguna
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
        return  # Keluar
    
    try:
        konfirmasi = input("Yakin ingin menghapus produk ini? (y/n): ").strip().lower()  # Minta konfirmasi
    except Exception as e:
        print(f"Error input: {e}")
        return
    if konfirmasi == 'y':  # Jika setuju menghapus
        db.hapus_produk(id_produk, toko_id)  # db.hapus_produk: soft delete produk berdasarkan id dan toko
        print("Produk berhasil dihapus.")  # Beri pesan sukses
    else:  # Jika tidak setuju menghapus
        print("Penghapusan dibatalkan.")  # Beri pesan batal
    
    input("Tekan ENTER untuk melanjutkan...")  # Jeda

# === GRUP 3: FITUR PESANAN ===

def menu_pesanan(toko_id):
    # Menampilkan pesanan menunggu dan memungkinkan penjual mengubah status ke selesai atau batal
    while True:  # Loop menu pesanan, akan terus tampil sampai kembali
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        print("--- PESANAN MENUNGGU ---")
        pesanan = db.ambil_pesanan_masuk(toko_id)  # db.ambil_pesanan_masuk: ambil daftar pesanan waiting milik toko
        
        if not pesanan:  # Jika tidak ada pesanan
            print("Tidak ada pesanan baru.")  # Beri informasi kosong
        else:  # Jika ada pesanan
            data_pesanan = []  # List penampung baris tabel
            for item in pesanan:  # Loop tiap pesanan untuk susun tabel
                data_pesanan.append([
                    item[0],  # ID Pesanan
                    item[1],  # Nama Pembeli
                    item[2],  # Status
                    db.format_mata_uang(item[3])  # db.format_mata_uang: format jumlah ke Rupiah
                ])
            
            print(tabulate(data_pesanan, headers=["ID", "Pembeli", "Status", "Total"], tablefmt="fancy_grid"))  # Tampilkan tabel
        
        print("\n1. Tandai Selesai (Barang Diambil)")  # Aksi menandai selesai
        print("2. Batalkan Pesanan")  # Aksi membatalkan
        print("3. Kembali")  # Kembali ke menu sebelumnya
        
        pilihan = input("Pilih aksi: ").strip()  # Ambil pilihan aksi

        if not pilihan:  # Jika kosong, ulangi
            continue

        if pilihan == '3':  # Jika pilih 3
            return  # Keluar dari menu pesanan
        
        if not pesanan:  # Jika tidak ada pesanan, tidak bisa melakukan aksi 1/2
            try:
                input("Tekan ENTER untuk melanjutkan...")  # Jeda
            except Exception as e:
                print(f"Error input: {e}")
                continue
            continue  # Kembali ke awal loop menu pesanan

        try:
            id_pesanan = input("\nMasukkan ID pesanan: ").strip()  # Ambil ID pesanan yang akan diubah
        except Exception as e:
            print(f"Error input: {e}")
            continue
        if not id_pesanan:  # Jika kosong
            continue  # Kembali ke awal loop tanpa tindakan
        
        id_pesanan_valid = [str(item[0]) for item in pesanan]  # Kumpulan ID pesanan valid
        if id_pesanan not in id_pesanan_valid:  # Validasi ID yang dimasukkan
            print("ID pesanan tidak valid.")  # Beri tahu kesalahan ID
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
            continue  # Kembali ke awal loop menu pesanan
        
        if pilihan == '1':  # Jika pilih menandai selesai
            try:
                konfirmasi = input("Konfirmasi pesanan selesai? (y/n): ").strip().lower()  # Minta konfirmasi
            except Exception as e:
                print(f"Error input: {e}")
                continue
            if konfirmasi == 'y':  # Jika setuju
                db.update_status_pesanan_penjual(id_pesanan, 2, toko_id)  # db.update_status_pesanan_penjual: ubah status ke selesai
                print("Pesanan berhasil ditandai selesai.")  # Tampilkan pesan sukses
        
        elif pilihan == '2':  # Jika pilih batalkan pesanan
            try:
                konfirmasi = input("Yakin ingin membatalkan pesanan? (y/n): ").strip().lower()  # Minta konfirmasi
            except Exception as e:
                print(f"Error input: {e}")
                continue
            if konfirmasi == 'y':  # Jika setuju
                db.update_status_pesanan_penjual(id_pesanan, 3, toko_id)  # db.update_status_pesanan_penjual: ubah status ke batal
                print("Pesanan berhasil dibatalkan.")  # Tampilkan pesan sukses
        
        input("Tekan ENTER untuk melanjutkan...")  # Jeda sebelum kembali ke menu pesanan

# === GRUP 4: FITUR LAPORAN TOKO ===

def tampilkan_statistik_toko(toko_id):
    # Menampilkan ringkasan statistik toko dan 5 transaksi terakhir
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
    print("--- STATISTIK TOKO ---")
    
    total_produk, total_transaksi, total_pendapatan, riwayat_terakhir = db.ambil_statistik_toko(toko_id)  # db.ambil_statistik_toko: ambil ringkasan performa toko
    
    print(f'''
Ringkasan Performa:
Total Produk Aktif : {total_produk}
Transaksi Sukses   : {total_transaksi}
Total Pendapatan   : {db.format_mata_uang(total_pendapatan)}''')  # Tampilkan ringkasan utama
    
    print("\n" + "="*50)  # Garis pemisah
    
    if riwayat_terakhir:  # Jika ada data riwayat transaksi
        print("5 Transaksi Terakhir:")  # Judul bagian
        data_terakhir = []  # List penampung untuk tabel
        for item in riwayat_terakhir:  # Loop setiap transaksi untuk susun tabel
            data_terakhir.append([
                item[0].strftime('%Y-%m-%d'),  # Tanggal transaksi
                item[1],  # Kode pemesanan
                db.format_mata_uang(item[2])  # db.format_mata_uang: format jumlah ke Rupiah
            ])
        print(tabulate(data_terakhir, headers=["Tanggal", "Kode", "Total"], tablefmt="fancy_grid"))  # Tampilkan tabel
    else:  # Jika tidak ada riwayat transaksi selesai
        print("Belum ada transaksi selesai.")  # Beri tahu pengguna
    
    input("\nTekan ENTER untuk kembali...")  # Jeda sebelum kembali ke menu utama

# === GRUP 5: FITUR ULASAN & ADUAN ===

def menu_ulasan(toko_id):
    # Menampilkan daftar ulasan untuk produk toko dan memberi opsi balas ulasan
    while True:  # Loop menu ulasan hingga pengguna kembali
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        print("--- ULASAN PELANGGAN ---")
        ulasan = db.ambil_ulasan_toko(toko_id)  # db.ambil_ulasan_toko: ambil daftar ulasan untuk produk milik toko
        
        if not ulasan:  # Jika belum ada ulasan
            print("Belum ada ulasan dari pelanggan.")  # Beri tahu pengguna
        else:  # Jika ada ulasan
            for item in ulasan:  # Loop setiap ulasan dan tampilkan barisnya
                print(f"\nProduk: {item[1]}")  # Nama Produk
                print(f"Pelanggan: {item[2]}")  # Nama Pelanggan
                print(f"Rating: {item[3]}/5")  # Nilai rating
                print(f"Komentar: {item[4]}")  # Isi komentar
                print(f"Balasan: {item[5] or 'Belum dibalas'}")  # Balasan (atau teks default)
                print(f"ID Ulasan: {item[0]}")  # ID ulasan untuk referensi
                print("-" * 50)  # Garis pemisah
        
        if ulasan:  # Jika ada ulasan, tampilkan menu aksi
            print("\n1. Balas Ulasan")  # Aksi membalas
            print("2. Kembali")  # Aksi kembali

            try:
                pilihan = input("Pilih aksi: ").strip()  # Ambil pilihan pengguna
            except Exception as e:
                print(f"Error input: {e}")
                continue

            if not pilihan:  # Jika kosong, ulangi
                continue

            if pilihan == '2':  # Jika pilih kembali
                return  # Keluar dari menu ulasan
            elif pilihan == '1':  # Jika pilih balas ulasan
                balas_ulasan(toko_id)  # Masuk ke form balas ulasan
        else:  # Jika tidak ada ulasan sama sekali
            input("\nTekan ENTER untuk kembali...")  # Jeda agar pesan terbaca
            return  # Kembali ke dashboard


def balas_ulasan(toko_id):
    # Mengirim balasan untuk satu ulasan milik produk toko (dicek kepemilikannya terlebih dahulu)
    try:
        id_ulasan = input("\nMasukkan ID ulasan: ").strip()  # Ambil ID ulasan target
    except Exception as e:
        print(f"Error input: {e}")
        return
    
    if not id_ulasan:  # Jika input kosong
        return  # Kembali tanpa tindakan
    
    if not db.cek_kepemilikan_ulasan(id_ulasan, toko_id):  # db.cek_kepemilikan_ulasan: validasi ulasan milik toko
        print("ID ulasan tidak valid atau bukan untuk produk toko Anda.")  # Beri tahu jika ID tidak valid atau bukan milik toko
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
        return  # Kembali tanpa mengirim balasan
    
    try:
        isi_balasan = input("Tulis balasan untuk pelanggan: ").strip()  # Ambil teks balasan
    except Exception as e:
        print(f"Error input: {e}")
        return
    
    if isi_balasan:  # Jika balasan tidak kosong
        db.kirim_balasan_ulasan(isi_balasan, id_ulasan)  # db.kirim_balasan_ulasan: simpan balasan ulasan
        print("Balasan berhasil dikirim!")  # Tampilkan pesan sukses
    else:  # Jika balasan kosong
        print("Balasan tidak boleh kosong.")  # Beri tahu pengguna
    
    input("Tekan ENTER untuk melanjutkan...")  # Jeda


def menu_aduan(user_id):
    # Mengirim aduan dari penjual kepada admin
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
    print("--- KIRIM ADUAN KE ADMIN ---")
    
    subjek = db.input_varchar("Subjek aduan: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not subjek:  # Jika subjek kosong
        print("Subjek wajib diisi.")  # Beri tahu pengguna
        try:
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
        except Exception as e:
            print(f"Error input: {e}")
            return
        return  # Kembali ke menu sebelumnya
        
    deskripsi = input("Deskripsi aduan: ").strip()  # Ambil deskripsi aduan
    if not deskripsi:  # Jika deskripsi kosong
        print("Deskripsi wajib diisi.")  # Beri tahu pengguna
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
        return  # Kembali ke menu sebelumnya
    
    db.kirim_aduan(subjek, deskripsi, user_id)  # db.kirim_aduan: simpan aduan baru
    print("Aduan berhasil dikirim ke Admin!")  # Beri pesan sukses
    try:
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
    except Exception as e:
        print(f"Error input: {e}")
        return