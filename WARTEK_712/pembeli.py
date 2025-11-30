# === GRUP 1: IMPORTS & DASHBOARD ===
from tabulate import tabulate
import query as db

def dashboard_pembeli(sesi):
    # Menampilkan menu utama pembeli dan mengarahkan ke fitur hingga logout
    while True:  # Loop menu utama; terus berulang sampai pengguna memilih Logout (opsi 5)
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        
        print(f"Halo, {sesi['nama']}!")
        print("=" * 50)
        # Menampilkan ringkasan jumlah item di keranjang dengan menjumlahkan banyaknya jumlah setiap item
        print(f"[ KERANJANG: {sum(x['jumlah'] for x in sesi['keranjang'])} Item ]")
        print("-" * 50)
        
        print('''
1. Cari Produk (Filter/Promo)
2. Keranjang & Checkout
3. Riwayat Pesanan
4. Aduan
5. Logout''')
        
        pilihan = input("Silakan pilih aksi yang menarik: ").strip()  # Ambil input pilihan menu

        if not pilihan:  # Jika kosong, ulangi
            continue

        if pilihan == '1':  # Jika pilih 1, masuk ke fitur pencarian dan filter produk
            menu_cari_produk(sesi)
        elif pilihan == '2':  # Jika pilih 2, masuk ke tampilan keranjang dan proses checkout
            menu_keranjang(sesi)
        elif pilihan == '3':  # Jika pilih 3, lihat riwayat pesanan dan aksi terkait
            menu_riwayat_pesanan(sesi)
        elif pilihan == '4':  # Jika pilih 4, kirim aduan ke admin
            menu_aduan(sesi['id'])
        elif pilihan == '5':  # Jika pilih 5, keluar dari dashboard pembeli
            return
        else:  # Jika input di luar 1-5
            print("Pilihan tidak valid.")  # Beri info kesalahan input
            input("Tekan ENTER untuk melanjutkan...")  # Jeda agar pesan terbaca

# === GRUP 2: FITUR CARI PRODUK ===

def menu_cari_produk(sesi):  # Fungsi utama menu pencarian produk
    db.bersihkan_layar()   # db.bersihkan_layar: membersihkan tampilan terminal
    while True:  # Loop agar menu terus tampil sampai user memilih keluar
        print('''
--- CARI PRODUK ---
1. Produk Promo (<7 Hari)
2. Cari Berdasarkan Nama
3. Filter Lokasi/Kategori
4. Kembali''')

        pilihan = input("Pilih menu (1-4): ").strip()  # Ambil input pilihan user

        # Arahkan ke fungsi sesuai pilihan
        if pilihan == "1":    # Jika pilih 1, masuk ke fitur pencarian produk promo (<7 hari)
                cari_produk_promo(sesi)
        elif pilihan == "2":  # Jika pilih 2, masuk ke fitur pencarian produk berdasar nama produk
                cari_berdasarkan_nama(sesi)
        elif pilihan == "3":  # Jika pilih 3, masuk ke fitur pencarian produk berdasarkan lokasi dan kategori
                filter_lokasi_dan_kategori(sesi)
        elif pilihan == "4":  # Jika pilih 4, keluar dari menu cari produk
            print("Kembali ke menu utama...")
            break  # Keluar dari loop menu
        else:  # Jika input di luar 1-5
            print("Pilihan tidak valid.")  # Beri info kesalahan input
            input("Tekan ENTER untuk melanjutkan...")  # Jeda agar pesan terbaca

def tampilkan_tabel(produk):  # Fungsi untuk menampilkan tabel produk
    data_produk = []  # List untuk menampung baris tabel
    for item in produk:  # Loop setiap produk
        harga_diskon = int(item[4] * (1 - (item[5] or 0)))  # Mengitung harga setelah diskon
        data_produk.append([
            item[0],  # ID Produk
            item[1],  # Nama Produk
            item[2],  # Nama Toko
            item[3],  # Lokasi
            db.format_mata_uang(item[4]),  # Harga Asli (format Rupiah)
            f"{int((item[5] or 0) * 100)}%",  # Diskon dalam persen
            db.format_mata_uang(harga_diskon),  # Harga Setelah Diskon
            str(item[7])   # Tanggal Kadaluarsa
        ])

    # Cetak tabel dengan tabulate
    print(tabulate(data_produk, headers=["ID", "Produk", "Toko", "Lokasi", "Asli", "Diskon", "Hemat", "Exp"], tablefmt="fancy_grid")) 

def proses_pembelian(sesi, produk):  # Proses pembelian produk dari hasil pencarian
    beli = input("\nApakah Anda ingin membeli produk? (y/n): ").strip().lower() #Inputkan y apabila ingin memesan produk, tidak memedulikan bentuk huruf (besar/kecil)

    if beli != 'y':  # Jika inputan tidak y atau tidak ingin beli
        input("Tekan ENTER untuk kembali ke menu...")
        return # Kembali ke menu pencarian produk

    id_produk = db.input_angka("Masukkan ID produk: ", 10)  # db.input_angka: ambil input angka dengan batas panjang maksimum
    if not id_produk:  # Jika bukan id produk yang di inputkan
        input("ID Produk salah, tekan ENTER untuk kembali...")
        return # Kembali ke menu pencarian produk

    produk_terpilih = None  # Siapkan wadah kosong (Default None)
    for p in produk:
        if str(p[0]) == id_produk:
            produk_terpilih = p
            break
      # Cari produk sesuai ID yang diinputkan oleh pembeli
    if not produk_terpilih:  # Jika tidak ditemukan
        print("ID produk tidak ditemukan.")
        return  # Kembali ke menu pencarian produk

    # Menampilkan detail produk (deskripsi produk, Nama toko, alamat, kecamatan, dan batas waktu pengambilan produk)
    print(f'''
\n--- Detail Produk {produk_terpilih[1]} ---   
Deskripsi : {produk_terpilih[9]}               
Toko      : {produk_terpilih[2]} ({produk_terpilih[10]}, {produk_terpilih[3]})  
Ambil Sebelum: {produk_terpilih[11]}''')       

    harga_diskon = int(produk_terpilih[4] * (1 - (produk_terpilih[5] or 0)))  # Hitung harga setelah diskon (harga asli * (1 - diskon))
    print(f"Harga     : {db.format_mata_uang(produk_terpilih[4])} -> {db.format_mata_uang(harga_diskon)}")  
    # Cetak harga asli (format Rupiah) dan harga setelah diskon

    jumlah = db.input_angka(f"Jumlah beli (Stok {produk_terpilih[6]}): ", 10)  # db.input_angka: ambil input angka dengan batas panjang maksimum
    if not jumlah:  # Validasi: input jumlah harus berupa angka
        print("Jumlah tidak valid.")  # Jika bukan angka, beri infomrasi
        return  # Keluar dari fungsi
    if jumlah <= 0 or jumlah > produk_terpilih[6]:  # Validasi: jumlah harus >0 dan tidak melebihi stok
        print("Stok tidak cukup.")  # Jika stok tidak mencukupi, beri informasi stok tidak cukup
        return  # Keluar dari fungsi

    # Tambahkan produk ke keranjang (dictionary berisi detail produk)
    sesi['keranjang'].append({
'id': produk_terpilih[0],       # ID produk
'nama': produk_terpilih[1],     # Nama produk
'harga': harga_diskon,          # Harga setelah diskon
'jumlah': jumlah,               # Jumlah yang dibeli
'id_penjual': produk_terpilih[8]  # ID penjual
    })
    print("Produk berhasil ditambahkan ke keranjang.")  # Konfirmasi bahwa produk masuk ke keranjang
    input("Tekan ENTER untuk melanjutkan...")  # Jeda agar user bisa membaca pesan sebelum lanjut

def cari_produk_promo(sesi):  # Pencarian produk promo (<7 hari)
    db.bersihkan_layar()    # db.bersihkan_layar: membersihkan tampilan terminal
    sql = "p.tanggal_kadaluarsa BETWEEN CURRENT_DATE AND CURRENT_DATE + 7"  # Sintaks database 
    produk = db.cari_produk_pembeli(sql, [])  
    if not produk:  # Jika tidak ada hasil
        print("Tidak ada produk promo.")
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
        return
    tampilkan_tabel(produk)  # Tampilkan hasil
    proses_pembelian(sesi, produk)  # Proses pembelian

def cari_berdasarkan_nama(sesi):  # Pencarian produk berdasarkan nama produk
    db.bersihkan_layar()    # db.bersihkan_layar: membersihkan tampilan terminal
    kata_kunci = db.input_varchar("Masukkan nama produk: ", 100)  # Input kata kunci
    if not kata_kunci:  # Jika kata kunci kosong, maka akan mengeluarkan informasi produk tidak ditemukan
        print("Produk tidak ditemukan")
        input("Tekan ENTER untuk kembali...") # Jeda
        return
    sql = "p.nama_produk ILIKE %s" # Mencari nama produk dgn ILIKE, (ILIKE digunakan agar tidak case sensitive)
    produk = db.cari_produk_pembeli(sql, [f"%{kata_kunci}%"])
    if not produk:  # Jika produk tidak ada, maka akan mengeluarkan informasi produk tidak ditemukan
        print("Produk tidak ditemukan.")
        input("Tekan ENTER untuk kembali...") # Jeda
        return  
    tampilkan_tabel(produk)  # Tampilkan hasil (memanggil fungsi)
    proses_pembelian(sesi, produk)  # Proses pembelian (memanggil fungsi)

def filter_lokasi_dan_kategori(sesi):  # Pencarian produk berdasarkan lokasi/kategori
    db.bersihkan_layar()    # db.bersihkan_layar: membersihkan tampilan terminal

    lokasi = db.input_varchar("Masukkan nama kecamatan: ", 100)  # Input lokasi toko berdasarkan kecamatan
    kategori = db.ambil_semua_kategori()  # Mengambil daftar kategori dari database dengan memanggil fungsi ambil_semua_kategori()

    print(tabulate(kategori, headers=["ID", "Nama"], tablefmt="fancy_grid"))  # Menampilkan kategori produk dalam bentuk tabel
    id_kategori = input("Pilih ID kategori (Enter untuk skip): ")  # Meminta input id kategori atau tekan enter

    filter_list, params = [], []   # Inisialisasi list filter SQL dan parameter query
    if lokasi:  
        filter_list.append("kec.nama_kecamatan ILIKE %s")  # Tambahkan filter lokasi (case-insensitive)
        params.append(f"%{lokasi}%")  # Simpan parameter lokasi dengan wildcard untuk pencarian LIKE

    if id_kategori.isdigit():  # Jika kategori valid berupa angka
        filter_list.append("k.id_kategori=%s")  # Tambahkan filter kategori berdasarkan ID Kategori
        params.append(id_kategori)   # Simpan parameter kategori

    if not filter_list:  # Jika tidak ada filter yang dipilih, kembali
        return

    sql = " AND ".join(filter_list)   # Gabungkan semua filter dengan operator AND untuk query SQL
    produk = db.cari_produk_pembeli(sql, params)   # Jalankan query pencarian produk dengan filter dan parameter yang sudah dibuat
    if not produk:  # Jika hasil pencarian kosong, maka akan terdapat informasi 
        print("Produk tidak ditemukan.")
        input("Tekan ENTER untuk kembali...") # Jeda
        return
    tampilkan_tabel(produk)  # Tampilkan hasil
    proses_pembelian(sesi, produk)  # Proses pembelian

# === GRUP 3: FITUR KERANJANG & CHECKOUT ===

def menu_keranjang(sesi):
    # Menampilkan isi keranjang, melakukan checkout per toko, dan hapus item
    while True:  # Loop tampilan keranjang sampai pengguna kembali
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        keranjang = sesi['keranjang']  # Ambil referensi list keranjang
        if not keranjang:  # Jika keranjang kosong
            print("Keranjang kosong.")
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
            return
      
        data_keranjang = []  # List kosong untuk data keranjang
        nomor = 1            # Variabel penghitung mulai dari 1

        for item in keranjang:  # Loop item tanpa indeks
            data_keranjang.append([
                nomor,                                               # Nomor urut manual
                item['nama'],                                        # Nama produk
                item['jumlah'],                                      # Jumlah
                db.format_mata_uang(item['harga']),                  # Harga satuan
                db.format_mata_uang(item['harga'] * item['jumlah'])  # Subtotal
            ])
            nomor += 1  # Nomor bertambah 1 setiap putaran
        
        print(tabulate(data_keranjang, headers=["No", "Produk", "Jumlah", "Harga", "Subtotal"], tablefmt="fancy_grid"))
        # Total estimasi seluruh item dihitung dengan penjumlahan subtotal
        print(f"Total Estimasi: {db.format_mata_uang(sum(item['harga'] * item['jumlah'] for item in keranjang))}")
        
        print('''
\n1. Checkout
2. Hapus Item
3. Kembali''')

        pilihan = input("Pilih aksi: ").strip()  # Ambil pilihan aksi keranjang
        
        if pilihan == '3':  # Jika kembali
            return  # Keluar ke dashboard pembeli
        elif pilihan == '1':  # Proses checkout
            # Kelompokkan item keranjang berdasarkan id_penjual agar setiap toko menjadi pesanan terpisah
            dikelompokkan = {}
            for item in keranjang:  # Loop setiap item untuk memasukkan ke grup per toko
                toko_id = item['id_penjual']
                if toko_id not in dikelompokkan:  # Jika toko belum ada di dict, inisialisasi dengan list kosong
                    dikelompokkan[toko_id] = []
                dikelompokkan[toko_id].append(item)  # Tambahkan item ke list toko terkait

            hitung_sukses = 0  # Counter jumlah pesanan yang berhasil dibuat
            for toko_id, items in dikelompokkan.items():  # Loop setiap grup toko untuk membuat pesanan masing-masing
                nama_toko = db.proses_checkout_transaksi(items, sesi['id'])  # db.proses_checkout_transaksi: buat pesanan, detail, transaksi
                if nama_toko:  # Jika proses checkout berhasil
                    print(f"Berhasil order ke {nama_toko}")
                    hitung_sukses += 1
                else:  # Jika proses checkout gagal
                    print(f"Gagal order ke toko {toko_id}")

            if hitung_sukses > 0:  # Jika ada minimal satu pesanan berhasil
                sesi['keranjang'] = []  # Kosongkan keranjang setelah checkout
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
        elif pilihan == '2':  # Hapus satu item dari keranjang
            input_nomor = input("Masukkan nomor item: ").strip()  # Ambil nomor urut item yang ingin dihapus
            if input_nomor and input_nomor.isdigit():  # Validasi input nomor adalah angka
                        
                nomor_item = int(input_nomor) - 1  # Ubah ke indeks list (mulai 0)
                if 0 <= nomor_item < len(keranjang):  # Cek batas indeks agar tidak error
                    item_dihapus = keranjang[nomor_item]  # Simpan item yang akan dihapus (untuk pesan)
                    del keranjang[nomor_item]  # Hapus item dari list
                    print(f"{item_dihapus['nama']} dihapus dari keranjang.")
                else:  # Jika nomor di luar jangkauan
                    print("Nomor item tidak valid.")
                
            input("Tekan ENTER untuk melanjutkan...")  # Jeda

# === GRUP 4: FITUR RIWAYAT & ULASAN ===

def menu_riwayat_pesanan(sesi):
    # Menampilkan riwayat pesanan dan menyediakan aksi detail, batalkan, atau beri ulasan
    while True:  # Loop menu riwayat sampai pengguna kembali
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        pesanan = db.ambil_riwayat_pesanan_pembeli(sesi['id'])  # db.ambil_riwayat_pesanan_pembeli: ambil riwayat pesanan pembeli
        if not pesanan:  # Jika belum ada transaksi sebelumnya
            print("Belum ada riwayat pesanan.")
            input("Tekan ENTER untuk melanjutkan...")
            return  # Keluar dari menu riwayat jika kosong
        
        data_pesanan = []  # Siapkan data untuk tabel riwayat
        for item in pesanan:  # Loop setiap pesanan untuk membentuk baris tabel
            data_pesanan.append([
                item[0],  # ID Pesanan
                item[1],  # Kode Pemesanan
                item[2],  # Nama Toko
                item[3],  # Status Pesanan (teks)
                db.format_mata_uang(item[4])  # Total Pembayaran (format Rupiah)
            ])
            
        print(tabulate(data_pesanan, headers=["ID", "Kode", "Toko", "Status", "Total"], tablefmt="fancy_grid"))
        
        print('''
\n1. Detail Lengkap
2. Batalkan Pesanan (Menunggu)
3. Beri Ulasan (Selesai)
4. Kembali''')
        
        pilihan = input("Pilih aksi: ").strip()  # Ambil pilihan aksi
        if pilihan == '4':  # Kembali ke dashboard pembeli
            return

        id_pesanan = db.input_angka("Masukkan ID pesanan: ", 10)  # db.input_angka: ambil input angka dengan batas panjang maksimum
        if not id_pesanan:  # Jika kosong, ulangi menu
            continue
        
        if pilihan == '1':  # Menampilkan detail lengkap satu pesanan
            header, items = db.ambil_detail_pesanan(id_pesanan)  # db.ambil_detail_pesanan: ambil header dan item dari satu pesanan
            if header:  # Jika pesanan ditemukan
                db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
                print(f'''
--- DETAIL PESANAN {id_pesanan} ---
Toko: {header[0]}
Alamat: {header[1]}, {header[2]}
Batas Ambil: {header[3]}''')
                print("-" * 40)
                
                total_asli = 0  # Akumulator total harga normal
                total_bayar = 0  # Akumulator total harga saat beli (setelah diskon)
                for item in items:  # Loop semua item pada pesanan
                    print(f"- {item[0]} (x{item[1]})")  # Tampilkan nama dan jumlah
                    print(f"  Normal: {db.format_mata_uang(item[3])} | Bayar: {db.format_mata_uang(item[2])}")  # Bandingkan normal vs bayar
                    total_asli += (item[1] * item[3])  # Tambah ke total normal
                    total_bayar += (item[1] * item[2])  # Tambah ke total bayar
                
                print("-" * 40)
                print(f"Total Bayar : {db.format_mata_uang(total_bayar)}")  # Tampilkan total bayar
                if total_asli > total_bayar:  # Jika ada penghematan
                    print(f"ANDA HEMAT  : {db.format_mata_uang(total_asli - total_bayar)}!")  # Tampilkan jumlah penghematan
            else:  # Jika ID pesanan tidak ditemukan di database
                print("Pesanan tidak ditemukan.")
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
            
        elif pilihan == '2':  # Membatalkan pesanan jika status masih menunggu
            status = db.ambil_status_pesanan(id_pesanan)  # db.ambil_status_pesanan: ambil status pesanan (id_status)
            if status and status[0] == 1:  # Hanya boleh batalkan jika status 1 (Menunggu)
                konfirmasi = input("Yakin ingin membatalkan pesanan? (y/n): ").strip().lower()  # Minta konfirmasi
                if konfirmasi == 'y':  # Jika setuju
                    if db.batalkan_pesanan_pembeli(id_pesanan):  # db.batalkan_pesanan_pembeli: ubah status pesanan ke batal dan restore stok
                        print("Pesanan berhasil dibatalkan.")
                    else:  # Jika terjadi kegagalan saat update
                        print("Gagal membatalkan pesanan.")
                else:  # Jika batal konfirmasi
                    print("Pembatalan dibatalkan.")
            else:  # Jika status bukan menunggu
                print("Hanya bisa membatalkan pesanan yang berstatus 'Menunggu'.")
            input("Tekan ENTER untuk melanjutkan...")  # Jeda
            
        elif pilihan == '3':  # Memberi ulasan untuk pesanan yang selesai
            status = db.ambil_status_pesanan(id_pesanan)  # db.ambil_status_pesanan: ambil status pesanan (id_status)
            if status and status[0] == 2:  # Hanya bisa ulasan jika status 2 (Selesai)
                rating = input("Rating (1-5): ").strip()  # Ambil rating
                komentar = input("Komentar: ").strip()  # Ambil komentar
                id_produk = input("ID Produk: ").strip()  # Ambil id produk untuk ulasan
                
                if rating and rating in ['1','2','3','4','5'] and komentar and id_produk:  # Validasi input ulasan lengkap
                    if db.kirim_ulasan_pembeli(rating, komentar, id_produk, sesi['id']):  # db.kirim_ulasan_pembeli: simpan ulasan baru
                        print("Ulasan terkirim.")
                    else:  # Jika simpan ulasan gagal
                        print("Gagal mengirim ulasan.")
                else:  # Jika input tidak lengkap/valid
                    print("Data ulasan tidak lengkap.")
            else:  # Jika status bukan selesai
                print("Hanya bisa memberi ulasan untuk pesanan yang selesai.")
            input("Tekan ENTER untuk melanjutkan...")  # Jeda

# === GRUP 5: FITUR ADUAN ===

def menu_aduan(user_id):
    # Mengirim aduan dari pembeli ke admin
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
    print("--- KIRIM ADUAN ---")
    
    subjek = db.input_varchar("Subjek aduan: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not subjek:  # Validasi: subjek wajib diisi
        print("Subjek wajib diisi.")
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
        return  # Kembali jika tidak diisi
        
    deskripsi = input("Deskripsi aduan: ").strip()  # Ambil deskripsi aduan
    if not deskripsi:  # Validasi: deskripsi wajib diisi
        print("Deskripsi wajib diisi.")
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
        return
    
    db.kirim_aduan(subjek, deskripsi, user_id)  # db.kirim_aduan: simpan aduan baru ke database
    print("Aduan terkirim ke Admin!")
    input("Tekan ENTER untuk melanjutkan...")  # Jeda