from tabulate import tabulate  # Mengimpor fungsi tabulate untuk menampilkan data dalam bentuk tabel di terminal
import query as db            # Mengimpor modul query.py sebagai db (berisi fungsi-fungsi untuk interaksi data/"database")
import admin as ad            # Mengimpor modul admin.py sebagai ad (menu dan logika untuk admin)
import penjual as pj          # Mengimpor modul penjual.py sebagai pj (menu dan logika untuk penjual/mitra)
import pembeli as pb          # Mengimpor modul pembeli.py sebagai pb (menu dan logika untuk pembeli/customer)

# Variabel global untuk menyimpan informasi sesi pengguna yang sedang login
# - id: id user yang login (None jika belum login)
# - nama: nama user
# - peran: 1=Admin, 2=Penjual, 3=Pembeli
# - keranjang: list item yang akan dibeli (khusus pembeli)
SESI = {"id": None, "nama": None, "peran": None, "keranjang": []}

def input_alamat():
    # Memilih alamat bertingkat (provinsi->kabupaten->kecamatan->detail) lalu simpan, mengembalikan id_alamat atau None
    print("\n--- PILIH LOKASI ---")  # Judul bagian pemilihan alamat

    provinsi = db.ambil_semua_provinsi()  # db.ambil_semua_provinsi: ambil daftar semua provinsi dari database
    if not provinsi:  # Jika daftar provinsi kosong
        print("Tidak ada data provinsi.")
        return None  # Batalkan proses input alamat

    # Tampilkan daftar provinsi dalam bentuk tabel dengan header ID dan Provinsi
    print(tabulate(provinsi, headers=["ID","Provinsi"], tablefmt="fancy_grid"))
    try:
        id_provinsi = input("Pilih ID Provinsi: ").strip()  # Input pilihan provinsi
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return None
    except Exception as e:
        print(f"Error input: {e}")
        return None

    if not id_provinsi:  # Jika input kosong, batalkan
        return None

    kabupaten = db.ambil_kabupaten(id_provinsi)  # db.ambil_kabupaten: ambil daftar kabupaten berdasarkan id provinsi
    if not kabupaten:  # Jika daftar kabupaten kosong
        print("Kabupaten kosong.")
        return None  # Batalkan proses input alamat

    # Tampilkan daftar kabupaten
    print(tabulate(kabupaten, headers=["ID","Kabupaten"], tablefmt="fancy_grid"))
    try:
        id_kabupaten = input("Pilih ID Kabupaten: ").strip()  # Input pilihan kabupaten
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return None
    except Exception as e:
        print(f"Error input: {e}")
        return None

    if not id_kabupaten:  # Jika input kosong, batalkan
        return None

    kecamatan = db.ambil_kecamatan(id_kabupaten)  # db.ambil_kecamatan: ambil daftar kecamatan berdasarkan id kabupaten
    if not kecamatan:  # Jika daftar kecamatan kosong
        print("Kecamatan kosong.")
        return None  # Batalkan proses input alamat

    # Tampilkan daftar kecamatan
    print(tabulate(kecamatan, headers=["ID","Kecamatan"], tablefmt="fancy_grid"))
    try:
        id_kecamatan = input("Pilih ID Kecamatan: ").strip()  # Input pilihan kecamatan
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return None
    except Exception as e:
        print(f"Error input: {e}")
        return None

    if not id_kecamatan:  # Jika input kosong, batalkan
        return None

    try:
        detail_alamat = input("Detail Jalan (RT/RW): ").strip()  # Input detail jalan (alamat lengkap)
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return None
    except Exception as e:
        print(f"Error input: {e}")
        return None
    if not detail_alamat:  # Validasi wajib isi
        print("Detail alamat wajib diisi.")
        return None

    # Simpan alamat ke database dan kembalikan id_alamat hasil simpan
    return db.tambah_alamat(detail_alamat, id_kecamatan)  # db.tambah_alamat: simpan alamat baru dan kembalikan id_alamat


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
        
    telepon = db.input_varchar("No HP: ", 20)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not telepon:  # Validasi wajib isi
        print("No HP wajib diisi.")
        return
        
    email = db.input_varchar("Email: ", 100)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
    if not email:  # Validasi wajib isi
        print("Email wajib diisi.")
        return
    
    # Validasi password: harus diisi dan lolos aturan dari db.cek_password
    while True:  # Loop untuk memastikan password valid; berhenti ketika password lolos validasi
        try:
            password = input("Password (minimal 8 karakter): ").strip()  # Ambil password
        except KeyboardInterrupt:
            print("\nInput dibatalkan.")
            return
        except Exception as e:
            print(f"Error input: {e}")
            return
        if not password:  # Jika kosong -> batalkan pendaftaran
            print("Password wajib diisi.")
            return
        if not db.cek_password(password):  # db.cek_password: validasi aturan password
            continue  # Jika gagal validasi, minta ulang password (kembali ke atas loop)
        break  # Jika lolos -> keluar loop

    # Konfirmasi password harus sama
    try:
        konfirmasi_password = input("Konfirmasi Password: ").strip()
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return
    except Exception as e:
        print(f"Error input: {e}")
        return
    if password != konfirmasi_password:  # Jika password dan konfirmasi tidak sama
        print("Password tidak sama.")
        try:
            input("Tekan ENTER untuk melanjutkan...")
        except KeyboardInterrupt:
            print("\nInput dibatalkan.")
            return
        except Exception as e:
            print(f"Error input: {e}")
            return
        return

    # Pilih peran
    print("\n[ PILIH PERAN ]")
    print("2. Penjual (Mitra)\n3. Pembeli (Customer)")
    try:
        input_peran = input("Pilih peran (2/3): ").strip()
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return
    except Exception as e:
        print(f"Error input: {e}")
        return
    
    if input_peran not in ["2", "3"]:  # Validasi hanya menerima 2 atau 3
        print("Peran tidak valid.")
        return
        
    peran = int(input_peran)  # Ubah string menjadi integer

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
            
        nik = db.input_varchar("NIK Pemilik: ", 16)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
        if not nik:  # Validasi wajib isi
            print("NIK wajib diisi.")
            return
            
        kartu_keluarga = db.input_varchar("Nomor KK: ", 16)  # db.input_varchar: ambil input teks dengan batas panjang maksimum
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
    try:
        username = input("Username: ").strip()
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return
    except Exception as e:
        print(f"Error input: {e}")
        return
    try:
        password = input("Password: ").strip()
    except KeyboardInterrupt:
        print("\nInput dibatalkan.")
        return
    except Exception as e:
        print(f"Error input: {e}")
        return

    if not username or not password:  # Validasi sederhana agar tidak kosong
        print("Username dan password wajib diisi.")
        try:
            input("Tekan ENTER untuk melanjutkan...")
        except KeyboardInterrupt:
            print("\nInput dibatalkan.")
            return
        except Exception as e:
            print(f"Error input: {e}")
            return
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
                except KeyboardInterrupt:
                    print("\nInput dibatalkan.")
                    return
                except Exception as e:
                    print(f"Error input: {e}")
                    return
                return
            if not profil[0]:  # profil[0] adalah status verifikasi (False jika belum)
                print(f"\nToko '{profil[1]}' belum diverifikasi Admin.")
                try:
                    input("Tekan ENTER untuk melanjutkan...")
                except KeyboardInterrupt:
                    print("\nInput dibatalkan.")
                    return
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
            except KeyboardInterrupt:
                print("\n\nProgram dihentikan paksa (Ctrl+C).")
                print("Kembali ke menu utama...")
                input("Tekan ENTER untuk restart...")
                continue
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