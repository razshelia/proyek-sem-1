# === GRUP 1: IMPORTS & DASHBOARD ===
from tabulate import tabulate
import query as db


def dashboard_admin(sesi):
    while True:
        db.bersihkan_layar()
        print(f'''
--- ADMIN PANEL | {sesi['nama']} ---
1. Verifikasi Mitra
2. Laporan Penjualan 
3. Daftar Transaksi
4. Kelola Kategori
5. Lihat Aduan
6. Logout''')
        
        pilihan = input("Silakan pilih aksi yang menarik: ").strip()
        
        if pilihan == '1': verifikasi_penjual()
        elif pilihan == '2': laporan_penjualan()
        elif pilihan == '3': daftar_transaksi()
        elif pilihan == '4': kelola_kategori()
        elif pilihan == '5': lihat_aduan()
        elif pilihan == '6': return
        else:
            print("Pilihan tidak valid.")
            input("Tekan ENTER untuk melanjutkan...")

# === GRUP 2: FITUR VERIFIKASI ===

def verifikasi_penjual():
    toko = db.ambil_toko_belum_verifikasi()
    if not toko: 
        print("Tidak ada toko yang perlu diverifikasi.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    print("\n--- VERIFIKASI MITRA ---")
    
    headers = ["ID", "Toko", "Pemilik", "Username", "NIK", "KK", "Alamat", "KTP", "Usaha"]
    tabel_data = []
    
    for item in toko:
        alamat_lengkap = f"{item[10]}, {item[11]}, {item[12]}, {item[13]}"
        
        tabel_data.append([
            item[0],           
            item[1],           
            item[2],           
            item[3],           
            item[6],           
            item[7],           
            alamat_lengkap,    
            item[9],           
            item[8] 
            ])
    
    print(tabulate(tabel_data, headers=headers, tablefmt="fancy_grid"))
    
    id_toko = input("\nMasukkan ID toko untuk diverifikasi (Enter untuk kembali): ").strip()
    
    if id_toko:
        id_valid = [str(item[0]) for item in toko]
        if id_toko in id_valid:
            konfirmasi = input("Verifikasi toko ini? (y/n): ").strip().lower()
            if konfirmasi == 'y':
                db.verifikasi_toko(id_toko)
                print("Toko berhasil diverifikasi!")
        else:
            print("ID toko tidak valid.")
    
    print("Kembali ke menu admin...")

# === GRUP 3: FITUR LAPORAN & TRANSAKSI ===

def laporan_penjualan():
    db.bersihkan_layar()
    
    print('''
====================================================
                  LAPORAN PENJUALAN               
====================================================''')
    
    data_toko = db.laporan_penjualan_per_toko() 
    if not data_toko:
        print("Belum ada data penjualan.")
    else:
        tabel = []
        for row in data_toko:
            tabel.append([
                row[0], # Nama Toko
                row[1], # Jumlah Transaksi
                db.format_mata_uang(row[2])]) # Total Pendapatan
            
        print(tabulate(tabel, headers=["Toko", "Transaksi", "Pendapatan"], tablefmt="fancy_grid"))
    input("Tekan ENTER untuk melanjutkan...")


def daftar_transaksi():
    db.bersihkan_layar()
    print('''
====================================================
                  DAFTAR TRANSAKSI                               
====================================================''')
    
    kode_pesanan = input("Masukkan kode pemesanan (Enter untuk semua): ").strip()
    transaksi = db.ambil_semua_transaksi(kode_pesanan if kode_pesanan else None)
    
    if not transaksi:
        print("Tidak ada transaksi.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    data = []
    for item in transaksi:
        data.append([item[1], item[2], db.format_mata_uang(item[3]), 
                    item[4], item[5], item[6]])
    
    print(tabulate(data, headers=["Kode", "Toko", "Jumlah", "Pembeli", "Tanggal", "Status"], tablefmt="fancy_grid"))
    
    ubah_kode = input("\nMasukkan kode untuk ubah status (Enter untuk batal): ").strip()
    if ubah_kode:
        status = [(1, "Menunggu Diambil"), (2, "Selesai"), (3, "Dibatalkan")]
        print(tabulate(status, headers=["ID", "Status"], tablefmt="fancy_grid"))
        
        status_baru = input("Masukkan ID status baru: ").strip()
        if status_baru:
            for item in transaksi:
                if item[1] == ubah_kode:
                    db.update_status_pesanan(item[0], status_baru)
                    print("Status berhasil diubah!")
                    break
    
    input("Tekan ENTER untuk melanjutkan...")

# === GRUP 4: FITUR KELOLA KATEGORI ===

def kelola_kategori():
    while True:
        db.bersihkan_layar()
        print('''
====================================================
                    KELOLA KATEGORI
====================================================''')
        
        kategori = db.ambil_semua_kategori_admin()
        print(tabulate(kategori, headers=["ID", "Nama Kategori", "Dihapus"], tablefmt="fancy_grid"))
        
        print('''
Pilihan Aksi:
1. Tambah Kategori
2. Edit Kategori  
3. Hapus Kategori
4. Kembali''')
        
        pilihan = input("Masukkan pilihan: ").strip()
        
        if pilihan == '4': return
        elif pilihan == '1':
            nama = db.input_varchar("Nama kategori: ", 100)
            if nama:
                db.tambah_kategori(nama)
                print(f"Kategori '{nama}' berhasil ditambahkan.")
        elif pilihan == '2':
            id_kategori = input("ID kategori yang ingin diedit: ").strip()
            if id_kategori:
                nama_baru = db.input_varchar("Nama baru kategori: ", 100)
                if nama_baru:
                    pulihkan = input("Pulihkan kategori? (y/n): ").strip().lower() == "y"
                    db.update_kategori(id_kategori, nama_baru, pulihkan)
                    print("Kategori berhasil diubah.")
        elif pilihan == '3':
            id_kategori = input("ID kategori yang ingin dihapus: ").strip()
            if id_kategori:
                db.hapus_kategori(id_kategori)
                print("Kategori berhasil disembunyikan.")
        
        input("Tekan ENTER untuk melanjutkan...")

# === GRUP 5: FITUR ADUAN ===

def lihat_aduan():
    db.bersihkan_layar()
    aduan = db.ambil_semua_aduan()
    
    print('''
====================================================
                    LIHAT ADUAN                    
====================================================''')
    
    if not aduan:
        print("Belum ada aduan masuk.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    headers = ["ID", "Tanggal", "Peran", "Pengirim", "Subjek"]
    tabel_data = []
    
    for item in aduan:
        tabel_data.append([
            item[0],
            item[1].strftime('%Y-%m-%d'),
            item[2],
            item[3],
            item[4][:50] + "..." if len(item[4]) > 50 else item[4]
            ])
    
    print(tabulate(tabel_data, headers=headers, tablefmt="fancy_grid"))
    
    print("\n" + "="*60)
    print("Tips: Masukkan ID aduan untuk melihat detail lengkap")
    print("         Tekan ENTER saja untuk kembali ke menu admin")
    print("="*60)
    
    id_aduan = input("\nMasukkan ID aduan untuk melihat detail: ").strip()
    
    if id_aduan:
        aduan_terpilih = None
        for item in aduan:
            if str(item[0]) == id_aduan:
                aduan_terpilih = item
                break
        
        if aduan_terpilih:
            tampilkan_detail_aduan(aduan_terpilih)
        else:
            print("ID aduan tidak ditemukan.")
            input("Tekan ENTER untuk melanjutkan...")

def tampilkan_detail_aduan(aduan):
    db.bersihkan_layar()
    
    print("="*70)
    print("               DETAIL ADUAN LENGKAP")
    print("="*70)
    
    print(f"\nID ADUAN    : {aduan[0]}")
    print(f"TANGGAL    : {aduan[1].strftime('%Y-%m-%d %H:%M')}")
    print(f"PERAN      : {aduan[2]}")
    print(f"PENGGIRIM  : {aduan[3]}")
    print(f"SUBJEK     : {aduan[4]}")
    
    print(f"\nDESKRIPSI ADUAN:")
    print("-" * 70)
    
    deskripsi = aduan[5]
    kata = deskripsi.split()
    baris = []
    baris_saat_ini = ""
    
    for kata_item in kata:
        if len(baris_saat_ini + " " + kata_item) <= 68: 
            if baris_saat_ini:
                baris_saat_ini += " " + kata_item
            else:
                baris_saat_ini = kata_item
        else:
            baris.append(baris_saat_ini)
            baris_saat_ini = kata_item
    
    if baris_saat_ini:
        baris.append(baris_saat_ini)
    
    for baris_item in baris:
        print(f"  {baris_item}")
    
    print("-" * 70)
    
    input("\nTekan ENTER untuk kembali ke daftar aduan...")
