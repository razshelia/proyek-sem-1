from tabulate import tabulate  # Mengimpor fungsi tabulate untuk menampilkan data dalam bentuk tabel di terminal
import query as db             # Mengimpor modul query.py sebagai db (berisi fungsi-fungsi untuk interaksi data/"database")
import admin as ad             # Mengimpor modul admin.py sebagai ad (menu dan logika untuk admin)
import penjual as pj           # Mengimpor modul penjual.py sebagai pj (menu dan logika untuk penjual/mitra)
import pembeli as pb           # Mengimpor modul pembeli.py sebagai pb (menu dan logika untuk pembeli/customer)

# Variabel global untuk menyimpan informasi sesi pengguna yang sedang login
# - id: id user yang login (None jika belum login)
# - nama: nama user
# - peran: 1=Admin, 2=Penjual, 3=Pembeli
# - keranjang: list item yang akan dibeli (khusus pembeli)
SESI = {"id": None, "nama": None, "peran": None, "keranjang": []}
2
def input_alamat():
    # Memilih alamat bertingkat (provinsi->kabupaten->kecamatan->detail) lalu simpan, mengembalikan id_alamat atau None
    print("\n--- PILIH LOKASI ---")  # Judul bagian pemilihan alamat

    # === TAHAP 1: PROVINSI ===
    provinsi = db.ambil_semua_provinsi()  # db.ambil_semua_provinsi: mengambil daftar semua provinsi dari database
    if not provinsi:  # Jika daftar provinsi kosong
        print("Tidak ada data provinsi.")
        return None  # Proses input alamat dibatalkan

    # Membuat daftar ID valid (ubah ke string agar bisa dibandingkan dengan input)
    valid_ids_prov = [str(p[0]) for p in provinsi]

    while True:  # Loop validasi input agar program tidak berhenti jika salah input
        # Menampilkan daftar provinsi dalam bentuk tabel dengan header ID dan Provinsi
        print(tabulate(provinsi, headers=["ID","Provinsi"], tablefmt="fancy_grid"))
        id_provinsi = db.input_angka("Pilih ID Provinsi: ", 10)  # db.input_angka: mengambil input angka dengan batas panjang maksimum

        if not id_provinsi:  # Jika input kosong (Enter saja), proses dibatalkan
            return None
        
        if id_provinsi in valid_ids_prov:  # Mengecek apakah ID ada di daftar valid
            break  # ID Valid, lanjut ke tahap berikutnya
        
        print("ID Provinsi tidak valid/tidak ditemukan. Silakan pilih dari tabel.")
        # Loop akan mengulang meminta input jika ID tidak ditemukan

    # === TAHAP 2: KABUPATEN ===
    kabupaten = db.ambil_kabupaten(id_provinsi)  # db.ambil_kabupaten: mengambil daftar kabupaten berdasarkan id provinsi
    if not kabupaten:  # Jika daftar kabupaten kosong
        print("Data Kabupaten kosong untuk provinsi ini.")
        return None  # Proses input alamat dibatalkan

    # Membuat daftar ID valid untuk kabupaten
    valid_ids_kab = [str(k[0]) for k in kabupaten]

    while True:  # Loop validasi input kabupaten
        # Menampilkan daftar kabupaten
        print(tabulate(kabupaten, headers=["ID","Kabupaten"], tablefmt="fancy_grid"))
        id_kabupaten = db.input_angka("Pilih ID Kabupaten: ", 10)  # db.input_angka: mengambil input angka

        if not id_kabupaten:  # Jika input kosong, proses dibatalkan
            return None
        
        if id_kabupaten in valid_ids_kab:  # Mengecek apakah ID kabupaten valid
            break
        
        print("ID Kabupaten tidak valid. Silakan coba lagi.")

    # === TAHAP 3: KECAMATAN ===
    kecamatan = db.ambil_kecamatan(id_kabupaten)  # db.ambil_kecamatan: mengambil daftar kecamatan berdasarkan id kabupaten
    if not kecamatan:  # Jika daftar kecamatan kosong
        print("Data Kecamatan kosong untuk kabupaten ini.")
        return None  # Proses input alamat dibatalkan

    # Membuat daftar ID valid untuk kecamatan
    valid_ids_kec = [str(k[0]) for k in kecamatan]

    while True:  # Loop validasi input kecamatan
        # Menampilkan daftar kecamatan
        print(tabulate(kecamatan, headers=["ID","Kecamatan"], tablefmt="fancy_grid"))
        id_kecamatan = db.input_angka("Pilih ID Kecamatan: ", 10)  # db.input_angka: mengambil input angka

        if not id_kecamatan:  # Jika input kosong, proses dibatalkan
            return None
        
        if id_kecamatan in valid_ids_kec:  # Mengecek apakah ID kecamatan valid
            break
        
        print("ID Kecamatan tidak valid. Silakan coba lagi.")

    # === TAHAP 4: DETAIL JALAN ===
    while True:  # Loop untuk memastikan detail alamat terisi (Mandatory)
        detail_alamat = db.input_varchar("Detail Jalan (RT/RW): ", 100)  # db.input_varchar: mengambil input teks dengan batas panjang maksimum
        if detail_alamat: # Pastikan tidak kosong
            break  # Jika terisi, keluar dari loop
        print("Detail alamat wajib diisi.")  # Pesan peringatan jika kosong

    # Menyimpan alamat lengkap ke database dan mengembalikan id_alamat hasil simpan
    return db.tambah_alamat(detail_alamat, id_kecamatan)  # db.tambah_alamat: simpan alamat baru

def daftar():
    # Proses pendaftaran akun baru (data user, pilih peran, jika penjual isi data toko dan alamat)
    db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal agar rapi
    print("--- DAFTAR AKUN BARU ---")

    # Input data dasar. Fungsi db.input_varchar membatasi panjang input.
    nama = db.input_varchar("Nama lengkap: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not nama:  # Validasi wajib isi
        print("Nama wajib diisi.")
        return
        
    username = db.input_varchar("Username: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not username:  # Validasi wajib isi
        print("Username wajib diisi.")
        return
        
    telepon = db.input_angka("No HP: ", 20)  # db.input_angka: ambil input angka dengan batas panjang maksimum
    if not telepon:  # Validasi wajib isi
        print("No HP wajib diisi.")
        return
        
    email = db.input_varchar("Email: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not email:  # Validasi wajib isi
        print("Email wajib diisi.")
        return
    
    # Validasi password: harus diisi dan lolos aturan dari db.cek_password
    while True:  # Loop untuk memastikan password valid; berhenti ketika password lolos validasi
        password = db.input_varchar("Password (minimal 8 karakter): ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
        if not password:  # Jika kosong -> batalkan pendaftaran
            print("Password wajib diisi.")
            return
        if not db.cek_password(password):  # db.cek_password: validasi aturan password
            continue  # Jika gagal validasi, minta ulang password (kembali ke atas loop)
        break  # Jika lolos -> keluar loop

    # Konfirmasi password harus sama
    konfirmasi_password = db.input_varchar("Konfirmasi Password: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if password != konfirmasi_password:  # Jika password dan konfirmasi tidak sama
        print("Password tidak sama.")
        try:
            input("Tekan ENTER untuk melanjutkan...")
        except Exception as e:
            print(f"Error input: {e}")
            return
        return

    # Pilih peran
    print("\n[ PILIH PERAN ]")
    print("2. Penjual (Mitra)\n3. Pembeli (Customer)")
    
    while True:
        # 1. Minta input (sebagai String agar tidak crash jika diisi huruf)
        input_peran = input("Pilih peran (2/3): ").strip()
        
        # 2. Validasi: Cek apakah input ada di daftar pilihan yang valid (String)
        if input_peran in ["2", "3"]:
            peran = int(input_peran) # Konversi ke integer agar siap masuk database
            break # Input benar -> Hentikan loop dan lanjut ke bawah
        else:
            # 3. Jika input salah (huruf, kosong, atau angka lain)
            print("Pilihan tidak valid. Harap masukkan angka 2 atau 3.")
            # Loop akan mengulang otomatis dari atas (meminta input lagi)

    # Simpan user baru ke database
    id_user = db.daftar_user_baru(nama, username, password, telepon, email, peran)  # db.daftar_user_baru: simpan akun baru dan kembalikan id_user
    if not id_user:  # Jika gagal simpan (username/email sudah dipakai)
        print("Gagal Daftar (Username/Email sudah terdaftar).")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    # Jika peran sebagai penjual, minta data toko
    if peran == 2:  # Percabangan khusus peran penjual
        print("\n--- DATA TOKO ---")
        nama_toko = db.input_varchar("Nama Toko: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
        if not nama_toko:  # Validasi wajib isi
            print("Nama toko wajib diisi.")
            return
            
        nik = db.input_angka("NIK Pemilik: ", 16)  # db.input_angka: ambil input angka dengan batas panjang maksimum
        if not nik:  # Validasi wajib isi
            print("NIK wajib diisi.")
            return

        kartu_keluarga = db.input_angka("Nomor KK: ", 16)  # db.input_angka: ambil input angka dengan batas panjang maksimum
        if not kartu_keluarga:  # Validasi wajib isi
            print("Nomor KK wajib diisi.")
            return
            
        bukti_usaha = db.input_varchar("Link Bukti Usaha: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
        ktp = db.input_varchar("Link KTP: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
        id_alamat = input_alamat()  # Memilih dan menyimpan alamat toko
        
        if not id_alamat:  # Validasi wajib isi alamat
            print("Alamat wajib diisi.")
            return
            
        # Simpan data toko ke database; jika sukses, beri pesan menunggu verifikasi admin
        if db.daftar_toko_baru(nama_toko, nik, kartu_keluarga, bukti_usaha, ktp, id_user, id_alamat):  # db.daftar_toko_baru: simpan data toko baru
            print("Toko berhasil didaftarkan! Menunggu verifikasi Admin.")
        else:
            print("Gagal mendaftarkan toko.")
    
    print("\nRegistrasi Selesai. Silakan Login.")
    input("Tekan ENTER untuk melanjutkan...")


def login():
    # Proses login user, validasi kredensial, cek status penjual, lalu arahkan ke dashboard sesuai peran
    print("\n--- LOGIN WARTEK ---")
    username = db.input_varchar("Username: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not username:
        return
    password = db.input_varchar("Password: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not password:
        return
    
    data_user = db.cek_login(username, password)  # db.cek_login: verifikasi kredensial user, kembalikan tuple (id, nama, peran) jika benar
    
    if data_user:  # Jika kredensial benar
        id_user, nama_user, peran_user = data_user  # Unpack hasil (id, nama, peran)

        # Jika penjual, cek status verifikasi toko
        if peran_user == 2:  # Percabangan khusus untuk penjual
            profil = db.cek_verifikasi_toko(id_user)  # db.cek_verifikasi_toko: cek status verifikasi toko penjual
            if not profil:  # Jika profil toko tidak ditemukan atau akses ke DB gagal
                print("Akun Penjual bermasalah.")
                try:
                    input("Tekan ENTER untuk melanjutkan...")
                except Exception as e:
                    print(f"Error input: {e}")
                    return
                return
            if not profil[0]:  # profil[0] adalah status verifikasi (False jika belum)
                print(f"\nToko '{profil[1]}' belum diverifikasi Admin.")
                try:
                    input("Tekan ENTER untuk melanjutkan...")
                except Exception as e:
                    print(f"Error input: {e}")
                    return
                return
        
        # Simpan info user ke variabel sesi global
        SESI.update({"id": id_user, "nama": nama_user, "peran": peran_user})
        
        # Arahkan ke dashboard sesuai peran
        if peran_user == 1:  # Admin
            ad.dashboard_admin(SESI)
        elif peran_user == 2:  # Penjual
            pj.dashboard_penjual(SESI)
        elif peran_user == 3:  # Pembeli
            pb.dashboard_pembeli(SESI)
            
        # Setelah keluar dari dashboard, reset sesi
        SESI.update({"id": None, "nama": None, "peran": None, "keranjang": []})
    else:  # Jika kredensial salah
        print("Gagal Login.")
        input("Tekan ENTER untuk melanjutkan...")


def main():
    # Menampilkan menu utama aplikasi dan menangani navigasi hingga pengguna memilih keluar
    while True:  # Loop tak hingga sampai user memilih keluar
        try:  # Pembungkus utama untuk menangkap KeyboardInterrupt global
            db.bersihkan_layar()  # db.bersihkan_layar: membersihkan tampilan terminal agar rapi setiap iterasi
            print('''
==============================================
          SELAMAT DATANG DI WARTEK!
   Yuk bantu kurangi limbah pangan sambil
               hemat belanja.
==============================================
1. Daftar
2. Masuk
3. Keluar''')  # Teks menu utama

            try:
                pilihan = input("Pilih menu: ").strip()  # Ambil pilihan menu dari user
            except Exception as e:
                print(f"Error input: {e}")
                continue

            if not pilihan:  # Jika kosong, ulangi
                continue

            if pilihan == '1':  # Jika pilih 1 -> daftar akun baru
                daftar()  # Panggil proses pendaftaran
            elif pilihan == '2':  # Jika pilih 2 -> login
                login()  # Panggil proses login
            elif pilihan == '3':  # Jika pilih 3 -> keluar aplikasi
                print("\nTerima kasih telah menggunakan WARTEK!")
                break  # Keluar dari loop -> program selesai
            else:  # Jika input bukan 1-3
                print("Pilihan tidak valid.")
                input("Tekan ENTER untuk melanjutkan...")
        except KeyboardInterrupt:  # Penangkap global
            print("\n\nProgram dihentikan paksa (Ctrl+C).")
            print("Kembali ke menu utama...")
            input("Tekan ENTER untuk restart...")

# Memanggil fungsi main() agar program langsung berjalan saat file ini dieksekusi
main()