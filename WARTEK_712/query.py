# === GRUP 1: IMPORTS & KONEKSI & UTILITIES ===
import psycopg2
from datetime import date
import os

DB_CONFIG = {
    'host': 'localhost',
    'port': '7721',              
    'user': 'postgres',          
    'password': 'OLAA12', 
    'database': 'wartek_ddl'   
}

def buat_koneksi():
    try: 
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        return conn
    except Exception as e: 
        print(f"Koneksi Error: {e}")
        return None

def bersihkan_layar():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_mata_uang(jumlah):
    return f"Rp {int(jumlah):,.0f}".replace(',', '.')

def format_desimal(nilai):
    try:
        return float("{:.2f}".format(float(nilai)))
    except:
        return nilai

def cek_panjang_teks(teks, max_panjang):
    if teks and len(teks) > max_panjang:
        print(f"Input terlalu panjang. Maksimal {max_panjang} karakter.")
        return False
    return True

def pilihan_input(prompt, pilihan_valid):
    while True:
        input_user = input(prompt).strip()
        if input_user in pilihan_valid:
            return input_user
        if not input_user:  
            return ""
        print(f"Pilihan tidak valid. Silakan pilih dari: {', '.join(pilihan_valid)}")

def input_varchar(prompt, max_panjang):
    while True:
        input_user = input(prompt).strip()
        if not input_user: 
            return input_user
        if cek_panjang_teks(input_user, max_panjang):
            return input_user

def cek_password(password):
    if len(password) < 8:
        print("Password minimal 8 karakter.")
        return False
    return True

# === GRUP 2: AUTH, REGISTRASI & WILAYAH ===
# Login & Akun

def cek_login(username, password):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("SELECT id_akun, nama, id_peran FROM akun WHERE username=%s AND password=%s", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result

def cek_verifikasi_toko(user_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("SELECT verifikasi_status, nama_toko FROM profil_penjual WHERE id_akun=%s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def daftar_user_baru(nama, username, password, telepon, email, peran_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO akun (nama, username, password, nomor_telepon, email, id_peran) 
                       VALUES (%s,%s,%s,%s,%s,%s) RETURNING id_akun""", 
                       (nama, username, password, telepon, email, peran_id))
        id_user_baru = cursor.fetchone()[0]
        return id_user_baru
    except:
        return None
    finally:
        conn.close()

def daftar_toko_baru(nama_toko, nik, kartu_keluarga, bukti_usaha, ktp, user_id, alamat_id):
    conn = buat_koneksi()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO profil_penjual (nama_toko, nik, nomor_kk, bukti_usaha, 
                       dokumen_kelengkapan, verifikasi_status, id_akun, id_alamat) 
                          VALUES (%s, %s, %s, %s, %s, false, %s, %s)""", 
                       (nama_toko, nik, kartu_keluarga, bukti_usaha, ktp, user_id, alamat_id))
        return True
    except:
        return False
    finally:
        conn.close()

# Alamat/Wilayah

def ambil_semua_provinsi():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_provinsi, nama_provinsi FROM provinsi ORDER BY nama_provinsi")
    result = cursor.fetchall()
    conn.close()
    return result

def ambil_kabupaten(provinsi_id):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_kabupaten, nama_kabupaten FROM kabupaten WHERE id_provinsi=%s ORDER BY nama_kabupaten", (provinsi_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def ambil_kecamatan(kabupaten_id):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_kecamatan, nama_kecamatan FROM kecamatan WHERE id_kabupaten=%s ORDER BY nama_kecamatan", (kabupaten_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def tambah_alamat(detail_alamat, kecamatan_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO alamat (deskripsi_alamat, id_kecamatan) 
                   VALUES (%s, %s) RETURNING id_alamat""", (detail_alamat, kecamatan_id))
    id_alamat_baru = cursor.fetchone()[0]
    conn.close()
    return id_alamat_baru

# === GRUP 3: FITUR ADMIN (BACKOFFICE) ===
# Verifikasi

def ambil_toko_belum_verifikasi():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            pp.id_profil_penjual, 
            pp.nama_toko, 
            a.nama AS nama_pemilik,
            a.username,
            a.email,
            a.nomor_telepon,
            pp.nik,
            pp.nomor_kk, 
            pp.bukti_usaha,
            pp.dokumen_kelengkapan,
            al.deskripsi_alamat,
            kc.nama_kecamatan,
            kb.nama_kabupaten,
            pv.nama_provinsi
        FROM profil_penjual pp 
        JOIN akun a ON pp.id_akun = a.id_akun 
        JOIN alamat al ON pp.id_alamat = al.id_alamat
        JOIN kecamatan kc ON al.id_kecamatan = kc.id_kecamatan
        JOIN kabupaten kb ON kc.id_kabupaten = kb.id_kabupaten
        JOIN provinsi pv ON kb.id_provinsi = pv.id_provinsi
        WHERE pp.verifikasi_status = false
        ORDER BY pp.id_profil_penjual
    """)
    result = cursor.fetchall()
    conn.close()
    return result

def verifikasi_toko(toko_id):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("UPDATE profil_penjual SET verifikasi_status = true WHERE id_profil_penjual = %s", (toko_id,))
    conn.close()

# Laporan & Transaksi Global

def laporan_penjualan_per_toko():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            pp.nama_toko, 
            COUNT(p.id_pesanan) as total_transaksi, 
            COALESCE(SUM(tr.jumlah), 0) as total_pendapatan
        FROM profil_penjual pp
        JOIN pesanan p ON pp.id_profil_penjual = p.id_profil_penjual
        JOIN transaksi tr ON p.id_pesanan = tr.id_pesanan
        WHERE p.id_status_pesanan = 2 
        GROUP BY pp.nama_toko
        ORDER BY total_pendapatan DESC
    """)
    
    result = cursor.fetchall()
    conn.close()
    return result

def ambil_semua_transaksi(kode_pesanan=None):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    
    query = """
        SELECT p.id_pesanan, p.kode_pemesanan, pp.nama_toko, tr.jumlah, a.nama, 
               p.tanggal_pemesanan, sp.pilihan_status
        FROM transaksi tr
        JOIN pesanan p ON tr.id_pesanan = p.id_pesanan
        JOIN akun a ON p.id_akun = a.id_akun
        JOIN profil_penjual pp ON p.id_profil_penjual = pp.id_profil_penjual
        JOIN status_pesanan sp ON p.id_status_pesanan = sp.id_status_pesanan
    """
    
    if kode_pesanan:
        query += " WHERE p.kode_pemesanan = %s"
        cursor.execute(query, (kode_pesanan,))
    else:
        query += " ORDER BY p.tanggal_pemesanan ASC"
        cursor.execute(query)
    
    result = cursor.fetchall()
    conn.close()
    return result

def update_status_pesanan(pesanan_id, status_id_baru):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("UPDATE pesanan SET id_status_pesanan = %s WHERE id_pesanan = %s", (status_id_baru, pesanan_id))
    conn.close()

def ambil_semua_status_pesanan():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_status_pesanan, pilihan_status FROM status_pesanan ORDER BY id_status_pesanan")
    result = cursor.fetchall()
    conn.close()
    return result

def ambil_semua_metode_pembayaran():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_metode_pembayaran, nama_metode FROM metode_pembayaran ORDER BY id_metode_pembayaran")
    result = cursor.fetchall()
    conn.close()
    return result

# Kategori

def ambil_semua_kategori():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_kategori, nama_kategori FROM kategori WHERE is_deleted=false")
    result = cursor.fetchall()
    conn.close()
    return result

def ambil_semua_kategori_admin():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("SELECT id_kategori, nama_kategori, is_deleted FROM kategori ORDER BY id_kategori")
    result = cursor.fetchall()
    conn.close()
    return result

def tambah_kategori(nama):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kategori (nama_kategori) VALUES (%s)", (nama,))
    conn.close()

def update_kategori(kategori_id, nama_baru, pulihkan=False):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    if pulihkan:
        cursor.execute("UPDATE kategori SET nama_kategori = %s, is_deleted = False WHERE id_kategori = %s", (nama_baru, kategori_id))
    else:
        cursor.execute("UPDATE kategori SET nama_kategori = %s WHERE id_kategori = %s", (nama_baru, kategori_id))
    conn.close()

def hapus_kategori(kategori_id):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("UPDATE kategori SET is_deleted = True WHERE id_kategori = %s", (kategori_id,))
    conn.close()

# Aduan

def ambil_semua_aduan():
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ad.id_aduan, ad.tanggal_aduan, p.nama_peran, a.nama AS nama_pengguna, ad.subjek, ad.deskripsi
        FROM aduan ad
        JOIN akun a ON ad.id_akun = a.id_akun
        JOIN peran p ON a.id_peran = p.id_peran
        ORDER BY ad.tanggal_aduan DESC
    """)
    result = cursor.fetchall()
    conn.close()
    return result

# === GRUP 4: FITUR PENJUAL (MITRA) ===
# Profil Toko

def ambil_toko_by_user(user_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("SELECT id_profil_penjual, nama_toko FROM profil_penjual WHERE id_akun=%s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# Produk (Inventaris)

def ambil_produk_toko(toko_id):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""SELECT id_produk, nama_produk, stok_produk, harga_per_produk, diskon FROM produk 
                   WHERE id_profil_penjual=%s AND is_deleted=false ORDER BY id_produk""", (toko_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def tambah_produk_baru(nama, harga, stok, diskon, deskripsi, tanggal_kadaluarsa, batas_ambil, kategori_id, toko_id):
    conn = buat_koneksi()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO produk (nama_produk, harga_per_produk, stok_produk, diskon, deskripsi, tanggal_kadaluarsa, 
                       batas_waktu_pengambilan, id_kategori, id_profil_penjual, is_deleted) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, false)""", 
                       (nama, harga, stok, diskon, deskripsi, tanggal_kadaluarsa, batas_ambil, kategori_id, toko_id))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def update_data_produk(produk_id, nama_kolom, nilai_baru,toko_id):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    query = f"UPDATE produk SET {nama_kolom}=%s WHERE id_produk=%s AND id_profil_penjual=%s"
    cursor.execute(query, (nilai_baru, produk_id, toko_id))
    conn.close()

def hapus_produk(produk_id, toko_id):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("UPDATE produk SET is_deleted=true WHERE id_produk=%s AND id_profil_penjual=%s", (produk_id, toko_id))
    conn.close()

# Pesanan Masuk

def ambil_pesanan_masuk(toko_id):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ps.id_pesanan, ak.nama, st.pilihan_status, tr.jumlah 
        FROM pesanan ps 
        JOIN akun ak ON ps.id_akun=ak.id_akun 
        JOIN status_pesanan st ON ps.id_status_pesanan=st.id_status_pesanan
        JOIN transaksi tr ON ps.id_pesanan=tr.id_pesanan 
        WHERE ps.id_profil_penjual=%s AND ps.id_status_pesanan = 1
    """, (toko_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def update_status_pesanan_penjual(pesanan_id, status_id_baru, toko_id):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("""UPDATE pesanan SET id_status_pesanan=%s 
                   WHERE id_pesanan=%s AND id_profil_penjual=%s""", (status_id_baru, pesanan_id, toko_id))
    conn.close()

# Laporan Toko

def ambil_statistik_toko(toko_id):
    conn = buat_koneksi()
    if not conn: return (0, 0, 0, [])
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM produk WHERE id_profil_penjual=%s AND is_deleted=false", (toko_id,))
    total_produk = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM pesanan WHERE id_profil_penjual=%s AND id_status_pesanan=2", (toko_id,))
    total_transaksi = cursor.fetchone()[0]
    
    cursor.execute("""SELECT COALESCE(SUM(tr.jumlah),0) FROM pesanan ps JOIN transaksi tr ON ps.id_pesanan=tr.id_pesanan 
                   WHERE ps.id_profil_penjual=%s AND ps.id_status_pesanan=2""", (toko_id,))
    total_pendapatan = cursor.fetchone()[0]
    
    cursor.execute("""SELECT ps.tanggal_pemesanan, ps.kode_pemesanan, tr.jumlah FROM pesanan ps 
                   JOIN transaksi tr ON ps.id_pesanan=tr.id_pesanan 
                   WHERE ps.id_profil_penjual=%s AND ps.id_status_pesanan=2 
                   ORDER BY ps.tanggal_pemesanan DESC LIMIT 5""", (toko_id,))
    riwayat_terakhir = cursor.fetchall()
    
    conn.close()
    return total_produk, total_transaksi, total_pendapatan, riwayat_terakhir

# Ulasan Toko

def ambil_ulasan_toko(toko_id):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id_ulasan, p.nama_produk, ak.nama, u.rating, u.komentar, u.balasan
        FROM ulasan u JOIN produk p ON u.id_produk=p.id_produk 
        JOIN akun ak ON u.id_akun=ak.id_akun 
        WHERE p.id_profil_penjual=%s ORDER BY u.id_ulasan DESC
    """, (toko_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def kirim_balasan_ulasan(isi_balasan, ulasan_id):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("UPDATE ulasan SET balasan=%s WHERE id_ulasan=%s", (isi_balasan, ulasan_id))
    conn.close()

def cek_kepemilikan_ulasan(ulasan_id, toko_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("""SELECT id_ulasan FROM ulasan u JOIN produk p ON u.id_produk=p.id_produk 
                   WHERE u.id_ulasan=%s AND p.id_profil_penjual=%s""", (ulasan_id, toko_id))
    result = cursor.fetchone()
    conn.close()
    return result

# === GRUP 5: FITUR PEMBELI (CUSTOMER) ===
# Produk & Cari

def cari_produk_pembeli(sql_tambahan="", parameter=()):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    query = """
        SELECT p.id_produk, p.nama_produk, pp.nama_toko, kec.nama_kecamatan, p.harga_per_produk, 
               p.diskon, p.stok_produk, p.tanggal_kadaluarsa, p.id_profil_penjual, p.deskripsi, a.deskripsi_alamat, p.batas_waktu_pengambilan
        FROM produk p JOIN profil_penjual pp ON p.id_profil_penjual=pp.id_profil_penjual
        JOIN alamat a ON pp.id_alamat=a.id_alamat JOIN kecamatan kec ON a.id_kecamatan=kec.id_kecamatan
        LEFT JOIN kategori k ON p.id_kategori=k.id_kategori WHERE p.stok_produk>0 AND p.is_deleted=false
    """
    
    if sql_tambahan: 
        query += f" AND {sql_tambahan}"
    
    query += " ORDER BY p.tanggal_kadaluarsa ASC"
    
    cursor.execute(query, tuple(parameter))
    result = cursor.fetchall()
    conn.close()
    return result

def ambil_detail_produk(produk_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id_produk, p.nama_produk, p.harga_per_produk, p.stok_produk, p.diskon, 
               p.deskripsi, p.tanggal_kadaluarsa, p.batas_waktu_pengambilan,
               pp.nama_toko, k.nama_kategori
        FROM produk p 
        JOIN profil_penjual pp ON p.id_profil_penjual = pp.id_profil_penjual
        JOIN kategori k ON p.id_kategori = k.id_kategori
        WHERE p.id_produk = %s AND p.is_deleted = false
    """, (produk_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# Transaksi

def proses_checkout_transaksi(daftar_item, user_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    try:
        list_id_produk = tuple(item['id'] for item in daftar_item)
        cursor.execute("""SELECT MIN(p.batas_waktu_pengambilan), MAX(pp.nama_toko) 
            FROM produk p JOIN profil_penjual pp ON p.id_profil_penjual = pp.id_profil_penjual 
            WHERE p.id_produk IN %s""", (list_id_produk,))
        info_toko = cursor.fetchone()
       
        cursor.execute("""INSERT INTO pesanan (kode_pemesanan, tanggal_pemesanan, batas_pengambilan, id_profil_penjual, id_akun, id_status_pesanan) 
                       VALUES ('TMP', CURRENT_DATE, %s, %s, %s, 1) RETURNING id_pesanan""", 
                       (info_toko[0], daftar_item[0]['pid'], user_id))
        id_pesanan_baru = cursor.fetchone()[0]
        
        cursor.execute("UPDATE pesanan SET kode_pemesanan=%s WHERE id_pesanan=%s", (f"WTK-{id_pesanan_baru}", id_pesanan_baru))
        
        total_harga = 0
        for item in daftar_item:
            subtotal = item['qty'] * item['hrg']
            total_harga += subtotal
            cursor.execute("INSERT INTO detail_pesanan (jumlah, harga_saat_beli, diskon, id_pesanan, id_produk) VALUES (%s,%s,0,%s,%s)", 
                           (item['qty'], item['hrg'], id_pesanan_baru, item['id']))
            cursor.execute("UPDATE produk SET stok_produk=stok_produk-%s WHERE id_produk=%s", (item['qty'], item['id']))
        
        cursor.execute("""INSERT INTO transaksi (tanggal_pembayaran, jumlah, id_pesanan, id_metode_pembayaran) 
                       VALUES (CURRENT_DATE, %s, %s, 1)""", (total_harga, id_pesanan_baru))
        return info_toko[1]
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        conn.close()

def ambil_riwayat_pesanan_pembeli(user_id):
    conn = buat_koneksi()
    if not conn: return []
    cursor = conn.cursor()
    cursor.execute("""SELECT ps.id_pesanan, ps.kode_pemesanan, pp.nama_toko, st.pilihan_status, tr.jumlah FROM pesanan ps 
                   JOIN profil_penjual pp ON ps.id_profil_penjual=pp.id_profil_penjual 
                   JOIN status_pesanan st ON ps.id_status_pesanan=st.id_status_pesanan 
                   JOIN transaksi tr ON ps.id_pesanan=tr.id_pesanan WHERE ps.id_akun=%s ORDER BY ps.id_pesanan DESC""", (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def ambil_detail_pesanan(pesanan_id):
    conn = buat_koneksi()
    if not conn: return (None, [])
    cursor = conn.cursor()
    cursor.execute("""SELECT pp.nama_toko, a.deskripsi_alamat, kec.nama_kecamatan, ps.batas_pengambilan FROM pesanan ps 
                   JOIN profil_penjual pp ON ps.id_profil_penjual=pp.id_profil_penjual JOIN alamat a ON pp.id_alamat=a.id_alamat 
                   JOIN kecamatan kec ON a.id_kecamatan=kec.id_kecamatan WHERE ps.id_pesanan=%s""", (pesanan_id,))
    header = cursor.fetchone()
    cursor.execute("""SELECT p.nama_produk, dp.jumlah, dp.harga_saat_beli, p.harga_per_produk FROM detail_pesanan dp 
                   JOIN produk p ON dp.id_produk=p.id_produk WHERE dp.id_pesanan=%s""", (pesanan_id,))
    items = cursor.fetchall()
    conn.close()
    return header, items

def ambil_status_pesanan(pesanan_id):
    conn = buat_koneksi()
    if not conn: return None
    cursor = conn.cursor()
    cursor.execute("SELECT id_status_pesanan FROM pesanan WHERE id_pesanan=%s", (pesanan_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def batalkan_pesanan_pembeli(pesanan_id):
    conn = buat_koneksi()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE pesanan SET id_status_pesanan=3 WHERE id_pesanan=%s", (pesanan_id,))
        cursor.execute("SELECT id_produk, jumlah FROM detail_pesanan WHERE id_pesanan=%s", (pesanan_id,))
        items = cursor.fetchall()
        for item in items:
            cursor.execute("UPDATE produk SET stok_produk=stok_produk+%s WHERE id_produk=%s", (item[1], item[0]))
        return True
    except:
        return False
    finally:
        conn.close()


# Interaksi

def kirim_ulasan_pembeli(rating, komentar, produk_id, user_id):
    conn = buat_koneksi()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ulasan (rating, komentar, id_produk, id_akun) VALUES (%s,%s,%s,%s)", (rating, komentar, produk_id, user_id))
        return True
    except:
        return False
    finally:
        conn.close()

def kirim_aduan(subjek, deskripsi, user_id):
    conn = buat_koneksi()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute("INSERT INTO aduan (subjek,deskripsi,tanggal_aduan,id_akun) VALUES (%s,%s,CURRENT_DATE,%s)", (subjek, deskripsi, user_id))
    conn.close()
