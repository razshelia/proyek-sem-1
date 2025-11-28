from tabulate import tabulate
import query as db
import admin as ad
import penjual as pj
import pembeli as pb

SESI = {"id": None, "nama": None, "peran": None, "keranjang": []}

def input_alamat():
    print("\n--- PILIH LOKASI ---")
    provinsi = db.ambil_semua_provinsi()
    if not provinsi:
        print("Tidak ada data provinsi.")
        return None
        
    print(tabulate(provinsi, headers=["ID","Provinsi"], tablefmt="fancy_grid"))
    id_provinsi = input("Pilih ID Provinsi: ").strip()
    
    if not id_provinsi:
        return None
        
    kabupaten = db.ambil_kabupaten(id_provinsi)
    if not kabupaten: 
        print("Kabupaten kosong.")
        return None
        
    print(tabulate(kabupaten, headers=["ID","Kabupaten"], tablefmt="fancy_grid"))
    id_kabupaten = input("Pilih ID Kabupaten: ").strip()
    
    if not id_kabupaten:
        return None
        
    kecamatan = db.ambil_kecamatan(id_kabupaten)
    if not kecamatan: 
        print("Kecamatan kosong.")
        return None
        
    print(tabulate(kecamatan, headers=["ID","Kecamatan"], tablefmt="fancy_grid"))
    id_kecamatan = input("Pilih ID Kecamatan: ").strip()
    
    if not id_kecamatan:
        return None
        
    detail_alamat = input("Detail Jalan (RT/RW): ").strip()
    if not detail_alamat:
        print("Detail alamat wajib diisi.")
        return None
    
    return db.tambah_alamat(detail_alamat, id_kecamatan)

def daftar():
    db.bersihkan_layar()
    print("--- DAFTAR AKUN BARU ---")
    nama = db.input_varchar("Nama lengkap: ", 100)
    if not nama:
        print("Nama wajib diisi.")
        return
        
    username = db.input_varchar("Username: ", 100)
    if not username:
        print("Username wajib diisi.")
        return
        
    telepon = db.input_varchar("No HP: ", 20)
    if not telepon:
        print("No HP wajib diisi.")
        return
        
    email = db.input_varchar("Email: ", 100)
    if not email:
        print("Email wajib diisi.")
        return
    
    while True:
        password = input("Password (minimal 8 karakter): ").strip()
        if not password:
            print("Password wajib diisi.")
            return
        if not db.cek_password(password):
            continue
        break
        
    konfirmasi_password = input("Konfirmasi Password: ").strip()
    if password != konfirmasi_password:
        print("Password tidak sama.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    print("\n[ PILIH PERAN ]")
    print("2. Penjual (Mitra)\n3. Pembeli (Customer)")
    input_peran = input("Pilih peran (2/3): ").strip()
    
    if input_peran not in ["2", "3"]:
        print("Peran tidak valid.")
        return
        
    peran = int(input_peran)

    id_user = db.daftar_user_baru(nama, username, password, telepon, email, peran)
    if not id_user: 
        print("Gagal Daftar (Username/Email mungkin sudah ada).")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    if peran == 2:
        print("\n--- DATA TOKO ---")
        nama_toko = db.input_varchar("Nama Toko: ", 100)
        if not nama_toko:
            print("Nama toko wajib diisi.")
            return
            
        nik = db.input_varchar("NIK Pemilik: ", 16)
        if not nik:
            print("NIK wajib diisi.")
            return
            
        kartu_keluarga = db.input_varchar("Nomor KK: ", 16)
        if not kartu_keluarga:
            print("Nomor KK wajib diisi.")
            return
            
        bukti_usaha = db.input_varchar("Link Bukti Usaha: ", 100)
        ktp = db.input_varchar("Link KTP: ", 100)
        id_alamat = input_alamat()
        
        if not id_alamat:
            print("Alamat wajib diisi.")
            return
            
        if db.daftar_toko_baru(nama_toko, nik, kartu_keluarga, bukti_usaha, ktp, id_user, id_alamat):
            print("Toko berhasil didaftarkan! Menunggu verifikasi Admin.")
        else:
            print("Gagal mendaftarkan toko.")
    
    print("\nRegistrasi Selesai. Silakan Login.")
    input("Tekan ENTER untuk melanjutkan...")

def login():
    print("\n--- LOGIN WARTEK ---")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("Username dan password wajib diisi.")
        input("Tekan ENTER untuk melanjutkan...")
        return
    
    data_user = db.cek_login(username, password)
    
    if data_user:
        id_user, nama_user, peran_user = data_user
        if peran_user == 2: 
            profil = db.cek_verifikasi_toko(id_user)
            if not profil:
                print("Akun Penjual bermasalah.")
                input("Tekan ENTER untuk melanjutkan...")
                return
            if not profil[0]: 
                print(f"\nToko '{profil[1]}' belum diverifikasi Admin.")
                input("Tekan ENTER untuk melanjutkan...")
                return
        
        SESI.update({"id": id_user, "nama": nama_user, "peran": peran_user})
        
        if peran_user == 1:
            ad.dashboard_admin(SESI)
        elif peran_user == 2:
            pj.dashboard_penjual(SESI)
        elif peran_user == 3:
            pb.dashboard_pembeli(SESI)
            
        SESI.update({"id": None, "nama": None, "peran": None, "keranjang": []})
    else: 
        print("Gagal Login.")
        input("Tekan ENTER untuk melanjutkan...")

def main():
    while True:
        db.bersihkan_layar()
        print('''
==============================================
          SELAMAT DATANG DI WARTEK!       
   Yuk bantu kurangi limbah pangan sambil     
               hemat belanja.                 
==============================================
1. Daftar
2. Masuk
3. Keluar''')
        
        pilihan = input("Pilih menu: ").strip()
        
        if pilihan == '1': 
            daftar()
        elif pilihan == '2': 
            login()
        elif pilihan == '3': 
            print("\nTerima kasih telah menggunakan WARTEK!")
            break
        else:
            print("Pilihan tidak valid.")
            input("Tekan ENTER untuk melanjutkan...")

main()
