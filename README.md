# Tubes3_10123004
Tugas Besar 3 IF2211 Strategi Algoritma 2025

# Deskripsi
Repositori ini berisi implementasi dari Tugas Besar 3 IF2211 Strategi Algoritma 2025, yakni "Pemanfaatan Pattern Matching untuk Membangun Sistem ATS (Applicant Tracking System) Berbasis CV Digital" berupa aplikasi GUI. Aplikasi ini dibuat dengan bahasa Python dan kakas GUI PyQT dengan *source code* yang terdokumentasi dengan format Doxygen. 
Aplikasi ini mengimplementasikan dua algoritma *string matching*, yaitu Knuth-Morris-Pratt (KMP) dan Boyer-Moore (BM). Algoritma KMP melakukan pencocokan dari kiri ke kanan dan memanfaatkan *preprocessing* pada pola untuk membangun tabel LPS (Longest Prefix Suffix). Tabel ini digunakan untuk menghindari perbandingan karakter yang tidak perlu saat terjadi ketidakcocokan, sehingga pergeseran bisa lebih efisien. Sementara itu, algoritma BM mencocokkan pola dari kanan ke kiri. BM menggunakan dua heuristik yaitu Bad Character dan Good Suffix untuk menentukan jumlah pergeseran. Pendekatan ini sering kali menghasilkan lompatan yang sangat besar sehingga bisa cepat kalau menghandle pola yang panjang dan teks yang banyak.

# Prasyarat
1. Python 3 (cara ngecek `python --version`; sudah diuji ke v3.13.3).
2. `uv` untuk manajemen dependensi (cara ngecek `uv --version`).
3. **MySQL Server** (cara ngecek `mysql --version`) yang sedang berjalan di `localhost` (cek pake `sudo systemctl status mysql`).

# Cara Menjalankan
1. Clone repository ini lalu masuk ke direktori `Tubes3_10123004`
```bash
git clone https://github.com/nayakazna/Tubes3_10123004.git
cd Tubes3_10123004
```
2. Buat virtual environment dengan `uv`:
```bash
uv venv
```
3. Instal dependensi dengan `uv`:
```bash
uv pip install -r requirements.txt
```

4. Unduh file CV yang diperlukan:
```bash
mkdir data
cd data
curl -L -o data.zip "https://drive.google.com/uc?export=download&id=181GUZWLDVKUJRv8Jv5UOkM18cw5Ewg2P"
unzip data.zip
rm data.zip
```

5. Setup databasenya (masukkan password dari root MySQL Server):
```bash
cd ../
sudo python setup_db.py
```

6. Jalankan program:
```bash
uv run src/main.py
```
7. Enjoy 

# Pembuat
- Farrel Athalla Putra (13523118)
- Zulfaqqar Nayaka Athadiansyah (13523094)
- Adiel Rum (10123004)
