# TODO: Deteksi dan Perbaikan Kode Anomalous

## Langkah 1: Hapus fungsi yang jarang digunakan di query.py
- [x] Hapus fungsi format_desimal
- [x] Hapus fungsi pilihan_input
- [x] Hapus fungsi ambil_semua_status_pesanan
- [x] Hapus fungsi ambil_semua_metode_pembayaran

## Langkah 2: Ganti variabel 'pid' dengan 'id_penjual' di pembeli.py
- [x] Ganti 'pid' menjadi 'id_penjual' dalam keranjang

## Langkah 3: Ganti variabel 'pid' dengan 'id_penjual' di query.py
- [x] Ganti 'pid' menjadi 'id_penjual' dalam proses_checkout_transaksi

## Langkah 4: Sederhanakan logika pengelompokan di pembeli.py
- [x] Ganti setdefault dengan loop for untuk pengelompokan item berdasarkan toko
