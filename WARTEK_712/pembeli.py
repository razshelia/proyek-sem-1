# === GRUP 1: IMPORTS & DASHBOARD ===
from tabulate import tabulate
import query as db


def dashboard_pembeli(sesi):
    # Menampilkan menu utama pembeli dan mengarahkan ke fitur hingga logout
    while True:  # Loop menu utama; terus berulang sampai pengguna memilih Logout (opsi 5)
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        
        print(f"Halo, {sesi['nama']}!")
        print("=" * 50)
        # Menampilkan ringkasan jumlah item di keranjang dengan menjumlahkan qty setiap item
        print(f"[ KERANJANG: {sum(x['qty'] for x in sesi['keranjang'])} Item ]")
        print("-" * 50)
        
        print('''
1. Cari Produk (Filter/Promo)
2. Keranjang & Checkout
3. Riwayat Pesanan
4. Aduan
5. Logout''')
        
        pilihan = input("Silakan pilih aksi yang menarik: ").strip()  # Ambil input pilihan menu
        
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

def menu_cari_produk(sesi):
    # Mencari produk berdasarkan promo, nama, atau filter lokasi/kategori; dapat menambah ke keranjang
    while True:  # Loop menu pencarian; selesai jika pilih kembali (opsi 4)
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        print('''
--- CARI PRODUK ---
1. Produk Promo (<7 Hari)
2. Cari Berdasarkan Nama
3. Filter Lokasi/Kategori
4. Kembali''')
        
        try:
            pilihan = input("Silakan pilih aksi yang menarik: ").strip()  # Ambil pilihan fitur pencarian
        except KeyboardInterrupt:
            print("\nInput dibatalkan.")
            continue
        except Exception as e:
            print(f"Error input: {e}")
            continue
        if pilihan == '4':  # Jika pilih kembali
            return  # Keluar ke dashboard pembeli
        
        sql, params = "", []  # Inisialisasi filter dinamis untuk query pencarian
        if pilihan == '1':  # Filter produk promo: kadaluarsa dalam 7 hari ke depan
            sql = "p.tanggal_kadaluarsa BETWEEN CURRENT_DATE AND CURRENT_DATE + 7"
        elif pilihan == '2':  # Pencarian produk berdasarkan nama (LIKE)
            kata_kunci = db.input_varchar("Masukkan nama produk: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
            if kata_kunci:
                sql = "p.nama_produk ILIKE %s"  # Gunakan ILIKE agar tidak case-sensitive
                params = [f"%{kata_kunci}%"]
        elif pilihan == '3':  # Filter gabungan lokasi dan/atau kategori
            lokasi = db.input_varchar("Masukkan nama kecamatan: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
            kategori = db.ambil_semua_kategori()  # db.ambil_semua_kategori: ambil daftar kategori aktif
            print(tabulate(kategori, headers=["ID", "Nama"], tablefmt="fancy_grid"))
            try:
                id_kategori = input("Pilih ID kategori (Enter untuk skip): ").strip()
            except KeyboardInterrupt:
                print("\nInput dibatalkan.")
                continue
            except Exception as e:
                print(f"Error input: {e}")
                continue
            
            filter_list = []  # List penampung klausa filter
            if lokasi:  # Jika user mengisi lokasi, tambahkan filter nama kecamatan
                filter_list.append("kec.nama_kecamatan ILIKE %s")
                params.append(f"%{lokasi}%")
            if id_kategori and id_kategori.isdigit():  # Jika user memilih kategori valid, tambahkan filter id_kategori
                filter_list.append("k.id_kategori=%s")
                params.append(id_kategori)
            if filter_list:  # Jika ada setidaknya satu filter, gabungkan dengan AND
                sql = " AND ".join(filter_list)
        else:  # Jika input pilihan tidak valid
            print("Pilihan tidak valid.")  # Beri tahu kesalahan input
            continue  # Kembali ke awal loop pencarian
        
        produk = db.cari_produk_pembeli(sql, params)  # db.cari_produk_pembeli: ambil produk dengan filter dinamis
        if not produk:  # Jika tidak ada hasil sesuai filter
            print("Produk tidak ditemukan.")
            try:
                input("Tekan ENTER untuk melanjutkan...")  # Jeda
            except KeyboardInterrupt:
                print("\nInput dibatalkan.")
                continue
            except Exception as e:
                print(f"Error input: {e}")
                continue
            continue  # Kembali ke awal loop pencarian

        data_produk = []  # Persiapkan tabel untuk tampilan hasil
        for item in produk:  # Loop setiap produk untuk hitung harga akhir dan bentuk baris tabel
            harga_akhir = int(item[4] * (1 - (item[5] or 0)))  # Harga setelah diskon (diskon disimpan 0..1)
            data_produk.append([
                item[0],  # ID Produk
                item[1],  # Nama Produk
                item[2],  # Nama Toko
                item[3],  # Lokasi (kecamatan)
                db.format_mata_uang(item[4]),  # Harga asli (format Rupiah)
                f"{int((item[5] or 0)*100)}%",  # Diskon dalam persen
                db.format_mata_uang(harga_akhir),  # Harga setelah diskon (format Rupiah)
                item[7]  # Tanggal kadaluarsa
            ])
            
        print(tabulate(data_produk, headers=["ID", "Produk", "Toko", "Lokasi", "Asli", "Diskon", "Hemat", "Exp"], tablefmt="fancy_grid"))

        try:
            beli = input("\nBeli produk? (y/n): ").strip().lower()  # Tanyakan apakah ingin menambahkan ke keranjang
        except KeyboardInterrupt:
            print("\nInput dibatalkan.")
            continue
        except Exception as e:
            print(f"Error input: {e}")
            continue
        if beli == 'y':  # Jika ya, proses pemilihan produk dan jumlah
            id_produk = input("Masukkan ID produk: ").strip()  # Ambil ID produk yang ingin dibeli
            if not id_produk:  # Jika tidak diisi, kembali ke loop
                continue
                
            # Cari produk yang ID-nya sesuai input
            produk_terpilih = next((p for p in produk if str(p[0]) == id_produk), None)
            
            if produk_terpilih:  # Jika produk ditemukan
                db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
                print(f"--- {produk_terpilih[1]} ---")
                print(f"Deskripsi : {produk_terpilih[9]}")
                print(f"Toko      : {produk_terpilih[2]} ({produk_terpilih[10]}, {produk_terpilih[3]})")
                print(f"Ambil Sblm: {produk_terpilih[11]}")
                harga_akhir = int(produk_terpilih[4] * (1 - (produk_terpilih[5] or 0)))  # Harga setelah diskon
                print(f"Harga     : {db.format_mata_uang(produk_terpilih[4])} -> {db.format_mata_uang(harga_akhir)}")

                try:
                    input_qty = input(f"Jumlah beli (Stok {produk_terpilih[6]}): ").strip()  # Ambil jumlah yang ingin dibeli
                except KeyboardInterrupt:
                    print("\nInput dibatalkan.")
                    continue
                except Exception as e:
                    print(f"Error input: {e}")
                    continue
                if input_qty and input_qty.isdigit():  # Validasi jumlah harus diisi dan berupa angka
                    qty = int(input_qty)
                    if 0 < qty <= produk_terpilih[6]:  # Validasi jumlah tidak boleh melebihi stok
                        # Simpan item ke keranjang sebagai dict yang berisi informasi penting
                        sesi['keranjang'].append({
                            'id': produk_terpilih[0],
                            'nm': produk_terpilih[1],
                            'hrg': harga_akhir,
                            'qty': qty,
                            'id_penjual': produk_terpilih[8]
                        })
                        print("Produk ditambahkan ke keranjang.")
                    else:  # Jika jumlah melebihi stok atau nol
                        print("Stok tidak cukup.")
                else:  # Jika format jumlah tidak valid
                    print("Jumlah tidak valid.")
            else:  # Jika tidak ditemukan produk dengan ID tersebut
                print("ID produk salah.")
            
            input("Tekan ENTER untuk melanjutkan...")  # Jeda agar pesan terbaca

# === GRUP 3: FITUR KERANJANG & CHECKOUT ===

def menu_keranjang(sesi):
    # Menampilkan isi keranjang, melakukan checkout per toko, dan hapus item
    while True:  # Loop tampilan keranjang sampai pengguna kembali
        db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
        keranjang = sesi['keranjang']  # Ambil referensi list keranjang
        if not keranjang:  # Jika keranjang kosong
            print("Keranjang kosong.")
            try:
                input("Tekan ENTER untuk melanjutkan...")  # Jeda
            except KeyboardInterrupt:
                print("\nInput dibatalkan.")
                return
            except Exception as e:
                print(f"Error input: {e}")
                return
            return  # Kembali ke dashboard
        
        data_keranjang = []  # Siapkan data untuk tabel keranjang
        for i, item in enumerate(keranjang):  # Loop setiap item keranjang sambil memberi nomor urut
            data_keranjang.append([
                i+1,  # Nomor urut (mulai dari 1)
                item['nm'],  # Nama produk
                item['qty'],  # Jumlah dibeli
                db.format_mata_uang(item['hrg']),  # Harga per item (format Rupiah)
                db.format_mata_uang(item['hrg'] * item['qty'])  # Subtotal (harga*qty) format Rupiah
            ])
        
        print(tabulate(data_keranjang, headers=["#", "Produk", "Qty", "Harga", "Subtotal"], tablefmt="fancy_grid"))
        # Total estimasi seluruh item dihitung dengan penjumlahan subtotal
        print(f"Total Estimasi: {db.format_mata_uang(sum(item['hrg'] * item['qty'] for item in keranjang))}")
        
        print('''
\n1. Checkout
2. Hapus Item
3. Kembali''')

        try:
            pilihan = input("Pilih aksi: ").strip()  # Ambil pilihan aksi keranjang
        except KeyboardInterrupt:
            print("\nInput dibatalkan.")
            continue
        except Exception as e:
            print(f"Error input: {e}")
            continue
        
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
            try:
                input_nomor = input("Masukkan nomor item: ").strip()  # Ambil nomor urut item yang ingin dihapus
            except KeyboardInterrupt:
                print("\nInput dibatalkan.")
                continue
            except Exception as e:
                print(f"Error input: {e}")
                continue
            if input_nomor and input_nomor.isdigit():  # Validasi input nomor adalah angka
                        
                nomor_item = int(input_nomor) - 1  # Ubah ke indeks list (mulai 0)
                if 0 <= nomor_item < len(keranjang):  # Cek batas indeks agar tidak error
                    item_dihapus = keranjang[nomor_item]  # Simpan item yang akan dihapus (untuk pesan)
                    del keranjang[nomor_item]  # Hapus item dari list
                    print(f"{item_dihapus['nm']} dihapus dari keranjang.")
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
            try:
                input("Tekan ENTER untuk melanjutkan...")
            except KeyboardInterrupt:
                print("\nInput dibatalkan.")
                return
            except Exception as e:
                print(f"Error input: {e}")
                return
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

        try:
            id_pesanan = input("Masukkan ID pesanan: ").strip()  # Ambil ID pesanan target
        except KeyboardInterrupt:
            print("\nInput dibatalkan.")
            continue
        except Exception as e:
            print(f"Error input: {e}")
            continue
        if not id_pesanan:  # Jika kosong, ulangi menu
            continue
        
        if pilihan == '1':  # Menampilkan detail lengkap satu pesanan
            header, items = db.ambil_detail_pesanan(id_pesanan)  # db.ambil_detail_pesanan: ambil header dan item dari satu pesanan
            if header:  # Jika pesanan ditemukan
                db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal
                print(f"--- DETAIL PESANAN {id_pesanan} ---")
                print(f"Toko: {header[0]}")
                print(f"Alamat: {header[1]}, {header[2]}")
                print(f"Batas Ambil: {header[3]}")
                print("-" * 40)
                
                total_asli = 0  # Akumulator total harga normal
                total_bayar = 0  # Akumulator total harga saat beli (setelah diskon)
                for item in items:  # Loop semua item pada pesanan
                    print(f"- {item[0]} (x{item[1]})")  # Tampilkan nama dan qty
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
                try:
                    konfirmasi = input("Yakin ingin membatalkan pesanan? (y/n): ").strip().lower()  # Minta konfirmasi
                except KeyboardInterrupt:
                    print("\nInput dibatalkan.")
                    continue
                except Exception as e:
                    print(f"Error input: {e}")
                    continue
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
                try:
                    rating = input("Rating (1-5): ").strip()  # Ambil rating
                except KeyboardInterrupt:
                    print("\nInput dibatalkan.")
                    continue
                except Exception as e:
                    print(f"Error input: {e}")
                    continue
                try:
                    komentar = input("Komentar: ").strip()  # Ambil komentar
                except KeyboardInterrupt:
                    print("\nInput dibatalkan.")
                    continue
                except Exception as e:
                    print(f"Error input: {e}")
                    continue
                try:
                    id_produk = input("ID Produk: ").strip()  # Ambil id produk untuk ulasan
                except KeyboardInterrupt:
                    print("\nInput dibatalkan.")
                    continue
                except Exception as e:
                    print(f"Error input: {e}")
                    continue
                
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
    try:
        input("Tekan ENTER untuk melanjutkan...")  # Jeda
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return
    except Exception as e:
        print(f"Error input: {e}")
        return
