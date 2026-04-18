# 📊 SE2026 Ujicoba CAPI - Automated Monitoring System

Sistem monitoring otomatis untuk memantau progres upload file laporan di Google Drive secara real-time. Sistem ini mengintegrasikan Google Drive API, Google Sheets API, dan Streamlit Dashboard dengan otomasi penuh berbasis Cloud.

## 🚀 Fitur Utama
- **Monitoring Kumulatif Harian:** Melakukan snapshot otomatis setiap jam untuk melihat seluruh isi folder.
- **Data Cleaning Otomatis:** Membersihkan nama file (menghapus ekstensi, nomor kode, dan merapikan format teks).
- **Dashboard Interaktif (Streamlit):** Visualisasi progres, metrik harian, dan tabel pencarian uploader yang user-friendly.
- **Otomasi GitHub Actions:** Script berjalan otomatis setiap 1 jam di Cloud tanpa perlu menyalakan komputer lokal.
- **Sinkronisasi Multi-Platform:** Laporan diupdate sekaligus ke Excel Lokal dan Google Sheets.

## 🛠️ Stack Teknologi
- **Bahasa:** Python 3.10+
- **API:** Google Drive API v3 & Google Sheets API v4
- **Dashboard:** Streamlit & Plotly
- **Automation:** GitHub Actions (Cron Job)
- **Data Processing:** Pandas & Openpyxl

## 📂 Struktur Project
- `monitor_drive.py`: Core logic untuk mengambil data dari Drive dan update Sheets/Excel.
- `app.py`: Source code untuk Dashboard Streamlit.
- `.github/workflows/auto_monitor.yml`: Konfigurasi otomasi tiap 1 jam di GitHub.
- `requirements.txt`: Daftar library yang dibutuhkan.

## ⚙️ Cara Setup (Otomasi Cloud)
Sistem ini dirancang untuk berjalan otomatis di GitHub Actions. Berikut langkah konfigurasinya:
1.  **GitHub Secrets:** Masukkan isi file `credentials.json` dan `token.json` Anda ke menu **Settings > Secrets and variables > Actions** di repository ini dengan nama:
    - `CREDENTIALS_JSON`
    - `TOKEN_JSON`
2.  **Streamlit Cloud:** Hubungkan repository ini ke [Streamlit Cloud](https://share.streamlit.io/) dan masukkan isi `token.json` ke bagian **Secrets** aplikasi dengan format TOML:
    ```toml
    [google]
    token = '''{ ... isi token.json ... }'''
    ```

## 💻 Penggunaan Lokal
Jika ingin menjalankan secara manual di komputer Anda:
```bash
# Install Library
pip install -r requirements.txt

# Jalankan Monitoring
python monitor_drive.py

# Jalankan Dashboard
python -m streamlit run app.py
```

## 🛑 Cara Menghentikan Otomasi
Jika proyek `SE2026` sudah selesai, Anda bisa menghentikan otomasi dengan cara:
1. Buka tab **Actions** di GitHub.
2. Pilih **Hourly Drive Monitor**.
3. Klik tombol **"..."** dan pilih **Disable Workflow**.

---
Developed by **nazara13**.
