# === GRUP 1: IMPORTS & DASHBOARD ===
from tabulate import tabulate
import query as db

def dashboard_admin(sesi):
    # Menampilkan menu admin dan mengarahkan ke fitur yang dipilih sampai logout
    while True:  # Loop menu utama admin; terus berjalan hingga pengguna memilih Logout (opsi 6)
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        print(f'''
--- ADMIN PANEL | {sesi['nama']} ---
1. Verifikasi Mitra
2. Laporan Penjualan 
3. Daftar Transaksi
4. Kelola Kategori
5. Lihat Aduan
6. Logout''')
        
        try:
            pilihan = input("Silakan pilih aksi yang menarik: ").strip()  # Ambil pilihan menu
        except Exception as e:
            print(f"Error input: {e}")
            continue

        if not pilihan:  # Jika kosong, ulangi
            continue

        if pilihan == '1':  # Masuk ke fitur verifikasi penjual (mitra)
            verifikasi_penjual()
        elif pilihan == '2':  # Masuk ke fitur laporan penjualan per toko
            laporan_penjualan()
        elif pilihan == '3':  # Masuk ke daftar transaksi dan ubah status
            daftar_transaksi()
        elif pilihan == '4':  # Masuk ke fitur kelola kategori (tambah/edit/hapus)
            kelola_kategori()
        elif pilihan == '5':  # Melihat daftar aduan dan detailnya
            lihat_aduan()
        elif pilihan == '6':  # Logout dari menu admin
            return
        else:  # Input tidak termasuk 1-6
            print("Pilihan tidak valid.")  # Beri informasi kesalahan input
            try:
                input("Tekan ENTER untuk melanjutkan...")  # Jeda agar pesan terbaca
            except Exception as e:
                print(f"Error input: {e}")
                continue

# === GRUP 2: FITUR VERIFIKASI ===

def verifikasi_penjual():
    # Menampilkan daftar toko yang belum diverifikasi dan melakukan verifikasi berdasarkan ID
    toko = db.ambil_toko_belum_verifikasi()  # db.ambil_toko_belum_verifikasi: ambil daftar toko yang belum diverifikasi
    if not toko:  # Jika tidak ada toko yang menunggu verifikasi
        print("Tidak ada toko yang perlu diverifikasi.")  # Beri informasi kosong
        try:
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
        except Exception as e:
            print(f"Error input: {e}")
            return
        return  # Kembali ke menu admin
    
    print("\n--- VERIFIKASI MITRA ---")
    
    headers = ["ID", "Toko", "Pemilik", "Username", "NIK", "KK", "Alamat", "KTP", "Usaha"]
    tabel_data = []  # Penampung baris data untuk ditampilkan dalam tabel
    
    for item in toko:  # Loop setiap toko untuk menyusun data baris tabel
        alamat_lengkap = f"{item[10]}, {item[11]}, {item[12]}, {item[13]}"  # Susun alamat lengkap dari beberapa kolom
        
        tabel_data.append([
            item[0],           # ID profil penjual
            item[1],           # Nama toko
            item[2],           # Nama pemilik
            item[3],           # Username pemilik
            item[6],           # NIK
            item[7],           # Nomor KK
            alamat_lengkap,    # Alamat lengkap
            item[9],           # Dokumen KTP
            item[8]            # Bukti usaha
            ])
    
    print(tabulate(tabel_data, headers=headers, tablefmt="fancy_grid"))  # Tampilkan tabel verifikasi

    id_toko = db.input_angka("\nMasukkan ID toko untuk diverifikasi (Enter untuk kembali): ", 10)  # db.input_angka: ambil input angka dengan batas panjang maksimum
    
    if id_toko:  # Jika user memasukkan nilai ID
        id_valid = [str(item[0]) for item in toko]  # Kumpulan ID valid (string) untuk validasi cepat
        if id_toko in id_valid:  # Cek apakah ID yang dimasukkan ada di daftar valid
            konfirmasi = input("Verifikasi toko ini? (y/n): ").strip().lower()  # Konfirmasi sebelum ubah status
            if konfirmasi == 'y':  # Jika setuju verifikasi
                db.verifikasi_toko(id_toko)  # db.verifikasi_toko: set status verifikasi toko menjadi true
                print("Toko berhasil diverifikasi!")  # Beri pesan sukses
        else:  # Jika ID tidak ditemukan
            print("ID toko tidak valid.")  # Beri informasi kesalahan ID
    
    print("Kembali ke menu admin...")  # Informasi navigasi

# === GRUP 3: FITUR LAPORAN & TRANSAKSI ===

def laporan_penjualan():
    # Menampilkan laporan penjualan per toko (jumlah transaksi dan pendapatan)
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
    
    print('''
====================================================
                  LAPORAN PENJUALAN               
====================================================''')
    
    data_toko = db.laporan_penjualan_per_toko()  # db.laporan_penjualan_per_toko: ambil ringkasan penjualan per toko
    if not data_toko:  # Jika belum ada transaksi selesai
        print("Belum ada data penjualan.")  # Informasikan kosong
    else:  # Jika ada data
        tabel = []  # Penampung baris untuk tabel
        for row in data_toko:  # Loop tiap toko untuk membentuk baris tabel
            tabel.append([
                row[0], # Nama Toko
                row[1], # Jumlah Transaksi
                db.format_mata_uang(row[2])  # db.format_mata_uang: format angka ke Rupiah
            ])
            
        print(tabulate(tabel, headers=["Toko", "Transaksi", "Pendapatan"], tablefmt="fancy_grid"))  # Tampilkan tabel
    try:
        input("Tekan ENTER untuk melanjutkan...")  # Jeda sebelum kembali
    except Exception as e:
        print(f"Error input: {e}")
        return


def daftar_transaksi():
    # Menampilkan daftar transaksi, memungkinkan filter berdasarkan kode, dan ubah status pesanan
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
    print('''
====================================================
                  DAFTAR TRANSAKSI                               
====================================================''')

    try:
        kode_pesanan = input("Masukkan kode pemesanan (Enter untuk semua): ").strip()  # Ambil filter opsional kode pesanan
    except Exception as e:
        print(f"Error input: {e}")
        return
    transaksi = db.ambil_semua_transaksi(kode_pesanan if kode_pesanan else None)  # db.ambil_semua_transaksi: ambil transaksi (opsional filter kode)
    
    if not transaksi:  # Jika tidak ada transaksi sesuai filter
        print("Tidak ada transaksi.")
        try:
            input("Tekan ENTER untuk melanjutkan...")
        except Exception as e:
            print(f"Error input: {e}")
            return
        return  # Kembali ke menu admin
    
    data = []  # Siapkan data untuk tabel transaksi
    for item in transaksi:  # Loop setiap transaksi untuk membentuk baris tabel
        data.append([
            item[1],  # Kode Pemesanan
            item[2],  # Nama Toko
            db.format_mata_uang(item[3]),  # db.format_mata_uang: format jumlah ke Rupiah
            item[4],  # Nama Pembeli
            item[5],  # Tanggal Pemesanan
            item[6]   # Status Pesanan (teks)
        ])
    
    print(tabulate(data, headers=["Kode", "Toko", "Jumlah", "Pembeli", "Tanggal", "Status"], tablefmt="fancy_grid"))

    # 1. Buat daftar Kode Transaksi yang valid dari data yang ada
    #    (Agar sistem tahu kode mana saja yang tersedia)
    list_kode_valid = [item[1] for item in transaksi]

    while True:
        # Minta input kode transaksi
        ubah_kode = input("\nMasukkan kode untuk ubah status (Enter untuk batal): ").strip()
        # Skenario Batal
        if not ubah_kode:
            return  # Langsung kembali ke menu admin jika di-Enter kosong
        # Validasi: Cek apakah kode ada di daftar valid?
        if ubah_kode in list_kode_valid:
            break  # Kode valid! Lanjut ke tahap berikutnya
        print("Kode transaksi tidak ditemukan. Silakan cek tabel dan coba lagi.")
    # Jika kode valid, lanjut pilih status
    status_opsi = [(1, "Menunggu Diambil"), (2, "Selesai"), (3, "Dibatalkan")]
    print(tabulate(status_opsi, headers=["ID", "Status"], tablefmt="fancy_grid"))

    while True:
        # Minta input ID status baru
        status_baru = db.input_angka("Masukkan ID status baru (1-3): ", 1)
        # Validasi input kosong (Wajib isi jika sudah pilih kode)
        if not status_baru:
            print("Status wajib dipilih.")
            continue
        # Validasi apakah input adalah "1", "2", atau "3"
        if status_baru in ['1', '2', '3']:
            # Cari ID transaksi (Primary Key) berdasarkan Kode yang dipilih tadi
            id_transaksi_target = None
            for item in transaksi:
                if item[1] == ubah_kode:
                    id_transaksi_target = item[0]
                    break
            # Lakukan Update ke Database
            if id_transaksi_target:
                # Konversi status_baru ke integer untuk database
                db.update_status_pesanan(id_transaksi_target, int(status_baru))
                print("Status berhasil diubah!")
            break # Selesai, keluar dari loop
        else:
            print("Pilihan status tidak valid. Hanya masukkan 1, 2, atau 3.")
    try:
        input("Tekan ENTER untuk melanjutkan...")
    except Exception as e:
        print(f"Error input: {e}")
        return

# === GRUP 4: FITUR KELOLA KATEGORI ===

def kelola_kategori():
    # Menampilkan menu kelola kategori (tambah, edit/pulihkan, hapus) berulang sampai kembali
    while True:  # Loop menu kelola kategori hingga pengguna pilih kembali (opsi 4)
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        print('''
====================================================
                    KELOLA KATEGORI
====================================================''')
        
        kategori = db.ambil_semua_kategori_admin()  # db.ambil_semua_kategori_admin: ambil seluruh kategori beserta status dihapus
        print(tabulate(kategori, headers=["ID", "Nama Kategori", "Dihapus"], tablefmt="fancy_grid"))
        
        print('''
Pilihan Aksi:
1. Tambah Kategori
2. Edit Kategori  
3. Hapus Kategori
4. Kembali''')

        try:
            pilihan = input("Masukkan pilihan: ").strip()  # Ambil pilihan menu kelola kategori
        except Exception as e:
            print(f"Error input: {e}")
            return

        if pilihan not in ['1', '2', '3', '4']:
            print("Pilihan tidak valid.")
            try:
                input("Tekan ENTER untuk melanjutkan...")
            except Exception as e:
                print(f"Error input: {e}")
            continue

        if pilihan == '4':  # Kembali ke menu admin
            return
        elif pilihan == '1':  # Tambah kategori baru
            nama = db.input_varchar("Nama kategori: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
            if nama:  # Validasi nama tidak kosong
                db.tambah_kategori(nama)  # db.tambah_kategori: tambah kategori baru
                print(f"Kategori '{nama}' berhasil ditambahkan.")
        elif pilihan == '2':  # Edit/pulihkan kategori
            id_kategori = input("ID kategori yang ingin diedit: ").strip()
            # 1. Membuat daftar ID valid dari variabel 'kategori' yang sudah diambil sebelumnya
            # (variabel 'kategori' berisi list tuple [(id, nama, status), ...])
            id_valid = [str(item[0]) for item in kategori]
            # 2. Cek apakah ID input ada di daftar valid
            if id_kategori not in id_valid:
                print("ID kategori tidak ditemukan.") # Tampilkan pesan error
                try:
                    input("Tekan ENTER untuk melanjutkan...")
                except:
                    pass
                continue # Kembali ke awal loop, batalkan proses edit
            if id_kategori:  
                nama_baru = db.input_varchar("Nama baru kategori: ", 100)
                if nama_baru:
                    pulihkan = input("Pulihkan kategori? (y/n): ").strip().lower() == "y"
                    db.update_kategori(id_kategori, nama_baru, pulihkan)
                    print("Kategori berhasil diubah.")
        elif pilihan == '3':  # Hapus Kategori (Soft Delete)
            id_kategori = input("ID kategori yang ingin dihapus: ").strip()
            # 1. Membuat daftar ID valid dari variabel 'kategori'
            id_valid = [str(item[0]) for item in kategori]
            # 2. Cek apakah ID input ada di daftar valid
            if id_kategori not in id_valid:
                print("ID kategori tidak ditemukan.") # Tampilkan pesan error
                try:
                    input("Tekan ENTER untuk melanjutkan...")
                except:
                    pass
                continue # Kembali ke awal loop, batalkan proses hapus
            if id_kategori:  
                db.hapus_kategori(id_kategori)
                print("Kategori berhasil disembunyikan.")

        try:
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
        except Exception as e:
            print(f"Error input: {e}")
            continue

# === GRUP 5: FITUR ADUAN ===

def lihat_aduan():
    # Menampilkan daftar aduan, dan bisa melihat detail aduan berdasarkan ID
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
    aduan = db.ambil_semua_aduan()  # db.ambil_semua_aduan: ambil daftar aduan terbaru
    
    print('''
====================================================
                    LIHAT ADUAN                    
====================================================''')
    
    if not aduan:  # Jika tidak ada aduan
        print("Belum ada aduan masuk.")
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
        return  # Kembali ke menu admin
    
    headers = ["ID", "Tanggal", "Peran", "Pengirim", "Subjek"]
    tabel_data = []  # Penampung baris tabel aduan
    
    for item in aduan:  # Loop setiap aduan untuk menyusun baris tabel
        tabel_data.append([
            item[0],  # ID aduan
            item[1].strftime('%Y-%m-%d'),  # Tanggal aduan (format YYYY-MM-DD)
            item[2],  # Peran pengirim
            item[3],  # Nama pengirim
            item[4][:50] + "..." if len(item[4]) > 50 else item[4]  # Potong subjek agar rapi
            ])
    
    print(tabulate(tabel_data, headers=headers, tablefmt="fancy_grid"))  # Tampilkan tabel aduan
    
    print("\n" + "="*60)
    print("Tips: Masukkan ID aduan untuk melihat detail lengkap")
    print("         Tekan ENTER saja untuk kembali ke menu admin")
    print("="*60)
    
    id_aduan = input("\nMasukkan ID aduan untuk melihat detail: ").strip()  # Ambil ID aduan target
    
    if id_aduan:  # Jika diisi, cari aduan yang cocok
        aduan_terpilih = None  # Variabel untuk menyimpan aduan yang terpilih
        for item in aduan:  # Loop daftar aduan untuk mencari berdasarkan ID
            if str(item[0]) == id_aduan:  # Bandingkan ID (string) untuk kecocokan
                aduan_terpilih = item  # Simpan aduan yang cocok
                break  # Hentikan pencarian saat sudah ketemu
        
        if aduan_terpilih:  # Jika ditemukan
            tampilkan_detail_aduan(aduan_terpilih)  # Tampilkan detail aduan
        else:  # Jika tidak ditemukan
            print("ID aduan tidak ditemukan.")  # Beri informasi kesalahan
            try:
                input("Tekan ENTER untuk melanjutkan...")  # Jeda
            except Exception as e:
                print(f"Error input: {e}")
                return


def tampilkan_detail_aduan(aduan):
    # Menampilkan detail lengkap dari satu aduan (format paragraf terbungkus lebar)
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
    
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
    
    deskripsi = aduan[5]  # Ambil teks deskripsi aduan
    kata = deskripsi.split()  # Pecah deskripsi berdasarkan spasi menjadi list kata
    baris = []  # Penampung tiap baris hasil pembungkusan
    baris_saat_ini = ""  # Buffer untuk baris yang sedang dibangun
    
    for kata_item in kata:  # Loop setiap kata untuk membentuk baris terbatasi lebar
        if len(baris_saat_ini + " " + kata_item) <= 68:  # Jika penambahan kata masih muat dalam lebar 68 karakter
            if baris_saat_ini:  # Jika baris saat ini tidak kosong
                baris_saat_ini += " " + kata_item  # Tambahkan kata dengan spasi
            else:  # Jika baris saat ini kosong
                baris_saat_ini = kata_item  # Mulai baris dengan kata pertama
        else:  # Jika tidak muat (melewati batas lebar)
            baris.append(baris_saat_ini)  # Simpan baris saat ini ke list
            baris_saat_ini = kata_item  # Mulai baris baru dengan kata yang tidak muat tadi
    
    if baris_saat_ini:  # Setelah loop, jika masih ada sisa baris yang belum ditambahkan
        baris.append(baris_saat_ini)  # Tambahkan sisa baris ke list
    
    for baris_item in baris:  # Loop untuk menampilkan setiap baris deskripsi yang telah dibungkus
        print(f"  {baris_item}")
    
    print("-" * 70)

    try:
        input("\nTekan ENTER untuk kembali ke daftar aduan...")  # Jeda sebelum kembali
    except Exception as e:
        print(f"Error input: {e}")
        return
