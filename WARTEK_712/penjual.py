# === GRUP 1: IMPORTS & DASHBOARD ===
from tabulate import tabulate
import query as db


def dashboard_penjual(sesi):
    toko = db.ambil_toko_by_user(sesi['id'])
    if not toko:
        print("Toko tidak ditemukan.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    while True:
        db.bersihkan_layar()
        print(f'''
--- DASHBOARD TOKO: {toko[1]} ---
1. Inventaris Produk
2. Pesanan Masuk
3. Riwayat & Laporan
4. Ulasan Pembeli
5. Aduan ke Admin
6. Logout''')
        
        pilihan = input("Silakan pilih aksi yang menarik: ").strip()
        
        if pilihan == '1': 
            menu_inventaris(toko[0])
        elif pilihan == '2': 
            menu_pesanan(toko[0])
        elif pilihan == '3': 
            tampilkan_statistik_toko(toko[0])
        elif pilihan == '4': 
            menu_ulasan(toko[0])
        elif pilihan == '5': 
            menu_aduan(sesi['id'])
        elif pilihan == '6': 
            return
        else:
            print("Pilihan tidak valid.")
            input("Tekan ENTER untuk melanjutkan...")

# === GRUP 2: FITUR INVENTARIS (PRODUK) ===

def menu_inventaris(toko_id):
    while True:
        db.bersihkan_layar()
        print("--- KELOLA PRODUK ---")
        produk = db.ambil_produk_toko(toko_id)
        
        if not produk:
            print("Belum ada produk.")
        else:
            data_produk = []
            for item in produk:
                diskon_persen = f"{int((item[4] or 0) * 100)}%" if item[4] else "0%"
                data_produk.append([
                    item[0], 
                    item[1], 
                    item[2], 
                    db.format_mata_uang(item[3]), 
                    diskon_persen
                ])
            
            print(tabulate(data_produk, headers=["ID", "Nama", "Stok", "Harga", "Diskon"], tablefmt="fancy_grid"))
        
        print('''
\n1. Tambah Produk
2. Edit Produk
3. Hapus Produk
4. Kembali''')
        
        pilihan = input("Pilih aksi: ").strip()
        
        if pilihan == '4': 
            return
        elif pilihan == '1':
            menu_tambah_produk(toko_id)
        elif pilihan == '2':
            menu_edit_produk(toko_id)
        elif pilihan == '3':
            menu_hapus_produk(toko_id)
        else:
            print("Pilihan tidak valid.")
            input("Tekan ENTER untuk melanjutkan...")
            

def menu_tambah_produk(toko_id):
    print("\n--- TAMBAH PRODUK BARU ---")
    
    nama = db.input_varchar("Nama produk: ", 100)
    if not nama:
        print("Nama produk wajib diisi.")
        return
        
    harga = input("Harga normal: ").strip()
    if not harga or not harga.isdigit():
        print("Harga harus angka.")
        return
        
    stok = input("Stok awal: ").strip()
    if not stok or not stok.isdigit():
        print("Stok harus angka.")
        return
        
    kadaluarsa = db.input_varchar("Tanggal kadaluarsa (YYYY-MM-DD): ", 10)
    batas_ambil = db.input_varchar("Batas pengambilan (YYYY-MM-DD): ", 10)
    
    input_diskon = input("Diskon (0-100, Enter untuk 0): ").strip()
    diskon = float(input_diskon) / 100 if input_diskon and input_diskon.isdigit() else 0
    
    deskripsi = input("Deskripsi produk: ").strip()
    
    kategori = db.ambil_semua_kategori()
    if not kategori:
        print("Tidak ada kategori tersedia.")
        return
    
    print("\nPilih Kategori:")
    print(tabulate(kategori, headers=["ID", "Kategori"], tablefmt="fancy_grid"))
    id_kategori = input("Pilih ID kategori: ").strip()
    
    if not id_kategori:
        print("Kategori wajib dipilih.")
        return
    
    id_kategori_valid = [str(kat[0]) for kat in kategori]
    if id_kategori not in id_kategori_valid:
        print("ID kategori tidak valid.")
        return
    
    if db.tambah_produk_baru(nama, harga, stok, diskon, deskripsi, kadaluarsa, batas_ambil, id_kategori, toko_id):
        print("Produk berhasil ditambahkan!")
    else:
        print("Gagal menambahkan produk.")
    
    input("Tekan ENTER untuk melanjutkan...")

def menu_edit_produk(toko_id):
    id_produk = input("\nMasukkan ID produk yang ingin diedit: ").strip()
    
    if not id_produk:
        return
        
    produk = db.ambil_produk_toko(toko_id)
    produk_ada = any(str(item[0]) == id_produk for item in produk)
    
    if not produk_ada:
        print("Produk tidak ditemukan.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    print("\nEdit Produk (kosongkan jika tidak ingin mengubah)")
    
    nama_baru = db.input_varchar("Nama baru: ", 100)
    harga_baru = input("Harga baru: ").strip()
    stok_baru = input("Stok baru: ").strip()
    diskon_baru = input("Diskon baru (0-100): ").strip()
    deskripsi_baru = input("Deskripsi baru: ").strip()
    kadaluarsa_baru = db.input_varchar("Tanggal kadaluarsa baru: ", 10)
    batas_ambil_baru = db.input_varchar("Batas pengambilan baru: ", 10)
    
    perubahan = False
    
    if nama_baru:
        db.update_data_produk(id_produk, "nama_produk", nama_baru)
        perubahan = True
    
    if harga_baru and harga_baru.isdigit():
        db.update_data_produk(id_produk, "harga_per_produk", harga_baru)
        perubahan = True
    
    if stok_baru and stok_baru.isdigit():
        db.update_data_produk(id_produk, "stok_produk", stok_baru)
        perubahan = True
    
    if diskon_baru and diskon_baru.isdigit():
        db.update_data_produk(id_produk, "diskon", float(diskon_baru) / 100)
        perubahan = True
    
    if deskripsi_baru:
        db.update_data_produk(id_produk, "deskripsi", deskripsi_baru)
        perubahan = True
    
    if kadaluarsa_baru:
        db.update_data_produk(id_produk, "tanggal_kadaluarsa", kadaluarsa_baru)
        perubahan = True
    
    if batas_ambil_baru:
        db.update_data_produk(id_produk, "batas_waktu_pengambilan", batas_ambil_baru)
        perubahan = True
    
    if perubahan:
        print("Produk berhasil diupdate!")
    else:
        print("Tidak ada perubahan.")
    
    input("Tekan ENTER untuk melanjutkan...")


def menu_hapus_produk(toko_id):
    id_produk = input("\nMasukkan ID produk yang ingin dihapus: ").strip()
    
    if not id_produk:
        return
        
    produk = db.ambil_produk_toko(toko_id)
    produk_ada = any(str(item[0]) == id_produk for item in produk)
    
    if not produk_ada:
        print("Produk tidak ditemukan.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    konfirmasi = input("Yakin ingin menghapus produk ini? (y/n): ").strip().lower()
    if konfirmasi == 'y':
        db.hapus_produk(id_produk, toko_id)
        print("Produk berhasil dihapus.")
    else:
        print("Penghapusan dibatalkan.")
    
    input("Tekan ENTER untuk melanjutkan...")

# === GRUP 3: FITUR PESANAN ===

def menu_pesanan(toko_id):
    while True:
        db.bersihkan_layar()
        print("--- PESANAN MENUNGGU ---")
        pesanan = db.ambil_pesanan_masuk(toko_id)
        
        if not pesanan:
            print("Tidak ada pesanan baru.")
        else:
            data_pesanan = []
            for item in pesanan:
                data_pesanan.append([
                    item[0], 
                    item[1], 
                    item[2], 
                    db.format_mata_uang(item[3])])
            
            print(tabulate(data_pesanan, headers=["ID", "Pembeli", "Status", "Total"], tablefmt="fancy_grid"))
        
        print("\n1. Tandai Selesai (Barang Diambil)")
        print("2. Batalkan Pesanan")
        print("3. Kembali")
        
        pilihan = input("Pilih aksi: ").strip()
        
        if pilihan == '3': 
            return
        
        if not pesanan:
            input("Tekan ENTER untuk melanjutkan...")
            continue
        
        id_pesanan = input("\nMasukkan ID pesanan: ").strip()
        if not id_pesanan:
            continue
        
        id_pesanan_valid = [str(item[0]) for item in pesanan]
        if id_pesanan not in id_pesanan_valid:
            print("ID pesanan tidak valid.")
            input("Tekan ENTER untuk melanjutkan...")
            continue
        
        if pilihan == '1':
            konfirmasi = input("Konfirmasi pesanan selesai? (y/n): ").strip().lower()
            if konfirmasi == 'y':
                db.update_status_pesanan_penjual(id_pesanan, 2, toko_id)
                print("Pesanan berhasil ditandai selesai.")
        
        elif pilihan == '2':
            konfirmasi = input("Yakin ingin membatalkan pesanan? (y/n): ").strip().lower()
            if konfirmasi == 'y':
                db.update_status_pesanan_penjual(id_pesanan, 3, toko_id)
                print("Pesanan berhasil dibatalkan.")
        
        input("Tekan ENTER untuk melanjutkan...")

# === GRUP 4: FITUR LAPORAN TOKO ===

def tampilkan_statistik_toko(toko_id):
    db.bersihkan_layar()
    print("--- STATISTIK TOKO ---")
    
    total_produk, total_transaksi, total_pendapatan, riwayat_terakhir = db.ambil_statistik_toko(toko_id)
    
    print(f'''
\nRingkasan Performa:")
Total Produk Aktif : {total_produk}")
Transaksi Sukses   : {total_transaksi}")
Total Pendapatan   : {db.format_mata_uang(total_pendapatan)}''')
    
    print("\n" + "="*50)
    
    if riwayat_terakhir:
        print("5 Transaksi Terakhir:")
        data_terakhir = []
        for item in riwayat_terakhir:
            data_terakhir.append([
                item[0].strftime('%Y-%m-%d'),
                item[1],
                db.format_mata_uang(item[2])
            ])
        print(tabulate(data_terakhir, headers=["Tanggal", "Kode", "Total"], tablefmt="fancy_grid"))
    else:
        print("Belum ada transaksi selesai.")
    
    input("\nTekan ENTER untuk kembali...")

# === GRUP 5: FITUR ULASAN & ADUAN ===

def menu_ulasan(toko_id):
    while True:
        db.bersihkan_layar()
        print("--- ULASAN PELANGGAN ---")
        ulasan = db.ambil_ulasan_toko(toko_id)
        
        if not ulasan:
            print("Belum ada ulasan dari pelanggan.")
        else:
            for item in ulasan:
                print(f"\nProduk: {item[1]}")
                print(f"Pelanggan: {item[2]}")
                print(f"Rating: {item[3]}/5")
                print(f"Komentar: {item[4]}")
                print(f"Balasan: {item[5] or 'Belum dibalas'}")
                print(f"ID Ulasan: {item[0]}")
                print("-" * 50)
        
        if ulasan:
            print("\n1. Balas Ulasan")
            print("2. Kembali")
            
            pilihan = input("Pilih aksi: ").strip()
            
            if pilihan == '2': 
                return
            elif pilihan == '1':
                balas_ulasan(toko_id)
        else:
            input("\nTekan ENTER untuk kembali...")
            return


def balas_ulasan(toko_id):
    id_ulasan = input("\nMasukkan ID ulasan: ").strip()
    
    if not id_ulasan:
        return
    
    if not db.cek_kepemilikan_ulasan(id_ulasan, toko_id):
        print("ID ulasan tidak valid atau bukan untuk produk toko Anda.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    isi_balasan = input("Tulis balasan untuk pelanggan: ").strip()
    
    if isi_balasan:
        db.kirim_balasan_ulasan(isi_balasan, id_ulasan)
        print("Balasan berhasil dikirim!")
    else:
        print("Balasan tidak boleh kosong.")
    
    input("Tekan ENTER untuk melanjutkan...")


def menu_aduan(user_id):
    db.bersihkan_layar()
    print("--- KIRIM ADUAN KE ADMIN ---")
    
    subjek = db.input_varchar("Subjek aduan: ", 100)
    if not subjek:
        print("Subjek wajib diisi.")
        input("Tekan ENTER untuk melanjutkan...")
        return
        
    deskripsi = input("Deskripsi aduan: ").strip()
    if not deskripsi:
        print("Deskripsi wajib diisi.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    db.kirim_aduan(subjek, deskripsi, user_id)
    print("Aduan berhasil dikirim ke Admin!")
    input("Tekan ENTER untuk melanjutkan...")
