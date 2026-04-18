CARA PERSIAPAN MONITORING GOOGLE DRIVE
=====================================

1. INSTALL LIBRARY
   Buka terminal di folder ini dan jalankan:
   pip install -r requirements.txt

2. DAPATKAN AKSES API (credentials.json)
   Karena ini dijalankan di komputer Anda (Local), Anda butuh kunci dari Google:
   
   a. Buka: https://console.cloud.google.com/
   b. Buat Project Baru (misal: "Drive Monitoring").
   c. Di Search Bar, cari "Google Drive API" lalu klik ENABLE.
   d. Pergi ke tab "OAuth consent screen":
      - Pilih "External", klik Create.
      - Isi App Name (bebas), User Support Email, dan Developer Contact Info. 
      - Klik Save and Continue sampai selesai.
      - PENTING: Tambahkan email Anda sendiri di bagian "Test Users".
   e. Pergi ke tab "Credentials":
      - Klik "+ Create Credentials" > "OAuth client ID".
      - Application Type: "Desktop App".
      - Nama: "Monitoring Local".
      - Klik Create.
   f. Download file JSON yang muncul.
   g. GANTI NAMA file tersebut menjadi "credentials.json" dan masukkan ke folder ini.

3. JALANKAN SCRIPT
   python monitor_drive.py

4. AUTENTIKASI PERTAMA KALI
   Saat pertama kali dijalankan, browser akan terbuka untuk minta izin Google. 
   Klik login, dan jika ada peringatan "Google hasn't verified this app", klik Advanced > Go to (unsafe).

Setelah itu, file "Monitoring_Laporan_Drive.xlsx" akan muncul dan terupdate setiap kali Anda menjalankan script ini!
