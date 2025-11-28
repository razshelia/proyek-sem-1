# === GRUP 1: IMPORTS & DASHBOARD ===
import os
from tabulate import tabulate
import query as db


def dashboard_pembeli(sesi):
    while True:
        db.bersihkan_layar()
        
        print(f"Halo, {sesi['nama']}!")
        print("=" * 50)
        print(f"[ KERANJANG: {sum(x['qty'] for x in sesi['keranjang'])} Item ]")
        print("-" * 50)
        
        print('''
1. Cari Produk (Filter/Promo)
2. Keranjang & Checkout
3. Riwayat Pesanan
4. Aduan
5. Logout''')
        
        pilihan = input("Silakan pilih aksi yang menarik: ").strip()
        
        if pilihan == '1': 
            menu_cari_produk(sesi)
        elif pilihan == '2': 
            menu_keranjang(sesi)
        elif pilihan == '3': 
            menu_riwayat_pesanan(sesi)
        elif pilihan == '4': 
            menu_aduan(sesi['id'])
        elif pilihan == '5': 
            return
        else:
            print("Pilihan tidak valid.")
            input("Tekan ENTER untuk melanjutkan...")

# === GRUP 2: FITUR CARI PRODUK ===

def menu_cari_produk(sesi):
    while True:
        db.bersihkan_layar()
        print('''
--- CARI PRODUK ---
1. Produk Promo (<7 Hari)
2. Cari Berdasarkan Nama
3. Filter Lokasi/Kategori
4. Kembali''')
        
        pilihan = input("Silakan pilih aksi yang menarik: ").strip()
        if pilihan == '4': 
            return
        
        sql, params = "", []
        if pilihan == '1': 
            sql = "p.tanggal_kadaluarsa BETWEEN CURRENT_DATE AND CURRENT_DATE + 7"
        elif pilihan == '2': 
            kata_kunci = db.input_varchar("Masukkan nama produk: ", 100)
            if kata_kunci:
                sql = "p.nama_produk ILIKE %s"
                params = [f"%{kata_kunci}%"]
        elif pilihan == '3':
            lokasi = db.input_varchar("Masukkan nama kecamatan: ", 100)
            kategori = db.ambil_semua_kategori()
            print(tabulate(kategori, headers=["ID", "Nama"], tablefmt="fancy_grid"))
            id_kategori = input("Pilih ID kategori (Enter untuk skip): ").strip()
            
            filter_list = []
            if lokasi: 
                filter_list.append("kec.nama_kecamatan ILIKE %s")
                params.append(f"%{lokasi}%")
            if id_kategori and id_kategori.isdigit(): 
                filter_list.append("k.id_kategori=%s")
                params.append(id_kategori)
            if filter_list: 
                sql = " AND ".join(filter_list)
        else:
            print("Pilihan tidak valid.")
            continue
        
        produk = db.cari_produk_pembeli(sql, params)
        if not produk: 
            print("Produk tidak ditemukan.")
            input("Tekan ENTER untuk melanjutkan...")
            continue

        data_produk = []
        for item in produk:
            harga_akhir = int(item[4] * (1 - (item[5] or 0)))
            data_produk.append([
                item[0], 
                item[1], 
                item[2], 
                item[3], 
                db.format_mata_uang(item[4]), 
                f"{int((item[5] or 0)*100)}%", 
                db.format_mata_uang(harga_akhir), 
                item[7]
            ])
            
        print(tabulate(data_produk, headers=["ID", "Produk", "Toko", "Lokasi", "Asli", "Diskon", "Hemat", "Exp"], tablefmt="fancy_grid"))
        
        beli = input("\nBeli produk? (y/n): ").strip().lower()
        if beli == 'y':
            id_produk = input("Masukkan ID produk: ").strip()
            if not id_produk:
                continue
                
            produk_terpilih = next((p for p in produk if str(p[0]) == id_produk), None)
            
            if produk_terpilih:
                db.bersihkan_layar()
                print(f"--- {produk_terpilih[1]} ---")
                print(f"Deskripsi : {produk_terpilih[9]}")
                print(f"Toko      : {produk_terpilih[2]} ({produk_terpilih[10]}, {produk_terpilih[3]})")
                print(f"Ambil Sblm: {produk_terpilih[11]}")
                harga_akhir = int(produk_terpilih[4] * (1 - (produk_terpilih[5] or 0)))
                print(f"Harga     : {db.format_mata_uang(produk_terpilih[4])} -> {db.format_mata_uang(harga_akhir)}")
                
                input_qty = input(f"Jumlah beli (Stok {produk_terpilih[6]}): ").strip()
                if input_qty and input_qty.isdigit():
                    qty = int(input_qty)
                    if 0 < qty <= produk_terpilih[6]:
                        sesi['keranjang'].append({
                            'id': produk_terpilih[0],
                            'nm': produk_terpilih[1],
                            'hrg': harga_akhir,
                            'qty': qty,
                            'pid': produk_terpilih[8]
                        })
                        print("Produk ditambahkan ke keranjang.")
                    else:
                        print("Stok tidak cukup.")
                else:
                    print("Jumlah tidak valid.")
            else:
                print("ID produk salah.")
            
            input("Tekan ENTER untuk melanjutkan...")

# === GRUP 3: FITUR KERANJANG & CHECKOUT ===

def menu_keranjang(sesi):
    while True:
        db.bersihkan_layar()
        keranjang = sesi['keranjang']
        if not keranjang: 
            print("Keranjang kosong.")
            input("Tekan ENTER untuk melanjutkan...")
            return
        
        data_keranjang = []
        for i, item in enumerate(keranjang):
            data_keranjang.append([
                i+1, 
                item['nm'], 
                item['qty'], 
                db.format_mata_uang(item['hrg']), 
                db.format_mata_uang(item['hrg'] * item['qty'])
            ])
        
        print(tabulate(data_keranjang, headers=["#", "Produk", "Qty", "Harga", "Subtotal"], tablefmt="fancy_grid"))
        print(f"Total Estimasi: {db.format_mata_uang(sum(item['hrg'] * item['qty'] for item in keranjang))}")
        
        print('''
\n1. Checkout
2. Hapus Item
3. Kembali''')
        
        pilihan = input("Pilih aksi: ").strip()
        
        if pilihan == '3': 
            return
        elif pilihan == '1':
            dikelompokkan = {}
            for item in keranjang:
                dikelompokkan.setdefault(item['pid'], []).append(item)
            
            hitung_sukses = 0
            for toko_id, items in dikelompokkan.items():
                nama_toko = db.proses_checkout_transaksi(items, sesi['id'])
                if nama_toko:
                    print(f"Berhasil order ke {nama_toko}")
                    hitung_sukses += 1
                else:
                    print(f"Gagal order ke toko {toko_id}")
            
            if hitung_sukses > 0:
                sesi['keranjang'] = []
            input("Tekan ENTER untuk melanjutkan...")
        elif pilihan == '2':
            input_nomor = input("Masukkan nomor item: ").strip()
            if input_nomor and input_nomor.isdigit():
                try:
                    nomor_item = int(input_nomor) - 1
                    if 0 <= nomor_item < len(keranjang):
                        item_dihapus = keranjang[nomor_item]
                        del keranjang[nomor_item]
                        print(f"{item_dihapus['nm']} dihapus dari keranjang.")
                    else:
                        print("Nomor item tidak valid.")
                except:
                    print("Nomor item tidak valid.")
            input("Tekan ENTER untuk melanjutkan...")

# === GRUP 4: FITUR RIWAYAT & ULASAN ===

def menu_riwayat_pesanan(sesi):
    while True:
        db.bersihkan_layar()
        pesanan = db.ambil_riwayat_pesanan_pembeli(sesi['id'])
        if not pesanan: 
            print("Belum ada riwayat pesanan.")
            input("Tekan ENTER untuk melanjutkan...")
            return
        
        data_pesanan = []
        for item in pesanan:
            data_pesanan.append([
                item[0], 
                item[1], 
                item[2], 
                item[3], 
                db.format_mata_uang(item[4])
            ])
            
        print(tabulate(data_pesanan, headers=["ID", "Kode", "Toko", "Status", "Total"], tablefmt="fancy_grid"))
        
        print('''
\n1. Detail Lengkap
2. Batalkan Pesanan (Menunggu)
3. Beri Ulasan (Selesai)
4. Kembali''')
        
        pilihan = input("Pilih aksi: ").strip()
        if pilihan == '4': 
            return
        
        id_pesanan = input("Masukkan ID pesanan: ").strip()
        if not id_pesanan:
            continue
        
        if pilihan == '1':
            header, items = db.ambil_detail_pesanan(id_pesanan)
            if header:
                db.bersihkan_layar()
                print(f"--- DETAIL PESANAN {id_pesanan} ---")
                print(f"Toko: {header[0]}")
                print(f"Alamat: {header[1]}, {header[2]}")
                print(f"Batas Ambil: {header[3]}")
                print("-" * 40)
                
                total_asli = 0
                total_bayar = 0
                for item in items:
                    print(f"- {item[0]} (x{item[1]})")
                    print(f"  Normal: {db.format_mata_uang(item[3])} | Bayar: {db.format_mata_uang(item[2])}")
                    total_asli += (item[1] * item[3])
                    total_bayar += (item[1] * item[2])
                
                print("-" * 40)
                print(f"Total Bayar : {db.format_mata_uang(total_bayar)}")
                if total_asli > total_bayar:
                    print(f"ANDA HEMAT  : {db.format_mata_uang(total_asli - total_bayar)}!")
            else:
                print("Pesanan tidak ditemukan.")
            input("Tekan ENTER untuk melanjutkan...")
            
        elif pilihan == '2':
            status = db.ambil_status_pesanan(id_pesanan)
            if status and status[0] == 1:
                konfirmasi = input("Yakin ingin membatalkan pesanan? (y/n): ").strip().lower()
                if konfirmasi == 'y':
                    if db.batalkan_pesanan_pembeli(id_pesanan):
                        print("Pesanan berhasil dibatalkan.")
                    else:
                        print("Gagal membatalkan pesanan.")
                else:
                    print("Pembatalan dibatalkan.")
            else:
                print("Hanya bisa membatalkan pesanan yang berstatus 'Menunggu'.")
            input("Tekan ENTER untuk melanjutkan...")
            
        elif pilihan == '3':
            status = db.ambil_status_pesanan(id_pesanan)
            if status and status[0] == 2:
                rating = input("Rating (1-5): ").strip()
                komentar = input("Komentar: ").strip()
                id_produk = input("ID Produk: ").strip()
                
                if rating and rating in ['1','2','3','4','5'] and komentar and id_produk:
                    if db.kirim_ulasan_pembeli(rating, komentar, id_produk, sesi['id']):
                        print("Ulasan terkirim.")
                    else:
                        print("Gagal mengirim ulasan.")
                else:
                    print("Data ulasan tidak lengkap.")
            else:
                print("Hanya bisa memberi ulasan untuk pesanan yang selesai.")
            input("Tekan ENTER untuk melanjutkan...")

# === GRUP 5: FITUR ADUAN ===

def menu_aduan(user_id):
    db.bersihkan_layar()
    print("--- KIRIM ADUAN ---")
    
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
    print("Aduan terkirim ke Admin!")
    input("Tekan ENTER untuk melanjutkan...")