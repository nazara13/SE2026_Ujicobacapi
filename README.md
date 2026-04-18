# 🚀 Google Drive Automated Monitoring Tool (SE2026 Ujicoba CAPI)

Alat monitoring otomatis berbasis Python untuk melacak aktivitas upload pada folder Google Drive tertentu. Tools ini dirancang untuk melakukan snapshot kumulatif setiap hari dan menyimpannya dalam format **Excel Lokal** serta **Google Sheets (Cloud)**.

## ✨ Fitur Utama
- **Daily Snapshot Logic**: Setiap kali dijalankan, script akan membuat tab baru berdasarkan tanggal hari ini (WIB) berisi seluruh daftar file yang ada di folder (Snapshot Kumulatif).
- **Auto Name Cleaning**: 
  - Menghapus kode awal (seperti `1200_`, `1200-`).
  - Menghapus ekstensi file.
  - Mengubah format nama menjadi *Title Case* (Contoh: `laporan_bandi_ucok` -> `Laporan Bandi Ucok`).
- **Internal Hyperlinking**: Tab **REKAP TOTAL** memiliki link otomatis yang bisa diklik untuk langsung pindah ke rincian tanggal tertentu (Berlaku di Excel & Google Sheets).
- **Dual Output**: Sinkronisasi otomatis ke file `.xlsx` lokal dan Google Spreadsheet di cloud.
- **Support Locale Indonesia**: Rumus menggunakan pemisah titik koma (`;`) sesuai standar regional Indonesia.

## 🛠️ Prasyarat
- Python 3.8 atau lebih baru.
- Akun Google Cloud dengan Google Drive API & Google Sheets API aktif.

## 📦 Instalasi

1. **Clone Repository**
   ```bash
   git clone https://github.com/nazara13/SE2026_Ujicobacapi.git
   cd SE2026_Ujicobacapi
   ```

2. **Buat Virtual Environment (Opsional tapi Disarankan)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Untuk Linux/Mac
   .venv\Scripts\activate     # Untuk Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 Konfigurasi Google API

Aplikasi ini membutuhkan file `credentials.json` untuk berfungsi:
1. Buka [Google Cloud Console](https://console.cloud.google.com/).
2. Buat Project baru dan aktifkan **Google Drive API** & **Google Sheets API**.
3. Di bagian **OAuth Consent Screen**, pilih *External* dan tambahkan email Anda di **Test Users**.
4. Di bagian **Credentials**, buat *OAuth Client ID* (Desktop App).
5. Download filenya, ganti namanya menjadi `credentials.json`, dan letakkan di folder utama project ini.

## 🚀 Cara Menjalankan
Cukup jalankan perintah berikut di terminal:
```bash
python monitor_drive.py
```
*Catatan: Pada login pertama, jendela browser akan terbuka untuk meminta izin akses Google.*

## 🔒 Keamanan
File rahasia berikut sudah terdaftar di `.gitignore` dan **TIDAK AKAN** terupload ke GitHub:
- `credentials.json`
- `token.json`
- `*.xlsx` (Hasil laporan)

---
Developed by **nazara13** using Antigravity AI.
