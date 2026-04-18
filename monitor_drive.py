import os
import re
import datetime
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ==========================================
# KONFIGURASI MONITORING
# ==========================================
FOLDER_ID = '1yuTQ1kj0vAW4A0QENXKjy6C8gY3a5kTt'
EXCEL_FILE = 'Monitoring_Laporan_Ujicoba_CAPI.xlsx'
GSHEET_NAME = 'Monitoring_Laporan_Ujicoba_CAPI'
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

def get_services():
    """Mengelola autentikasi Google Drive & Sheets API (Mendukung Local, Streamlit Cloud, & GitHub Actions)."""
    creds = None
    
    # 1. Coba baca dari GitHub Actions (Environment Variables)
    env_token = os.environ.get('TOKEN_JSON')
    if env_token:
        try:
            from google.oauth2.credentials import Credentials as GCoords
            import json
            creds_info = json.loads(env_token)
            creds = GCoords.from_authorized_user_info(creds_info, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
        except Exception as e:
            print(f"[DEBUG] Gagal baca token dari env: {e}")

    # 2. Coba baca dari Streamlit Secrets (Jika di Hosting Streamlit)
    if not creds:
        try:
            import streamlit as st
            if "google" in st.secrets:
                from google.oauth2.credentials import Credentials as GCoords
                import json
                creds_info = json.loads(st.secrets["google"]["token"])
                creds = GCoords.from_authorized_user_info(creds_info, SCOPES)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
        except:
            pass

    # 3. Jika bukan di cloud, cek file lokal
    if not creds:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("\n[ERROR] File 'credentials.json' tidak ditemukan!")
                    return None, None
                
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

def clean_name(name):
    """Membersihkan nama file (Hapus extension & kode wilayah)."""
    name = re.sub(r'\.[^/.]+$', "", name)
    name = re.sub(r'^[0-9_\-\s]+', '', name)
    name = re.sub(r'[_-]', ' ', name)
    name = re.sub(r'\s+', ' ', name)
    return name.strip().title()

def sync_to_google_sheets(sheets_service, drive_service, today_str, today_files):
    """Sinkronisasi data ke Google Sheets."""
    # 1. Cari atau buat Spreadsheet
    query = f"name = '{GSHEET_NAME}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, webViewLink)").execute()
    files = results.get('files', [])
    
    if not files:
        print("[*] Membuat Google Sheet baru di Cloud...")
        spreadsheet = {'properties': {'title': GSHEET_NAME}}
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
    else:
        spreadsheet_id = files[0]['id']

    # Ambil info spreadsheet (nama-nama sheet & ID-nya)
    sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets_info = {s.get('properties', {}).get('title'): s.get('properties', {}).get('sheetId') for s in sheet_metadata.get('sheets', [])}

    # 2. Update/Buat Sheet Harian
    header = ['Waktu Upload', 'Nama (Clean)', 'Nama Asli File', 'Uploader', 'Link File']
    values = [header] + [[f['Waktu Upload'], f['Nama (Clean)'], f['Nama Asli File'], f['Uploader'], f['Link File']] for f in today_files]

    # Tambah tab baru jika belum ada
    if today_str not in sheets_info:
        body = {'requests': [{'addSheet': {'properties': {'title': today_str}}}]}
        res = sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        new_sheet_id = res['replies'][0]['addSheet']['properties']['sheetId']
        sheets_info[today_str] = new_sheet_id

    # Tulis data ke sheet harian
    range_name = f"'{today_str}'!A1"
    body = {'values': values}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()

    # 3. Update Rekap Total
    update_gsheet_rekap(sheets_service, spreadsheet_id, sheets_info, today_str, len(today_files))
    
    # Dapatkan link untuk ditampilkan ke user
    res = drive_service.files().get(fileId=spreadsheet_id, fields='webViewLink').execute()
    return res.get('webViewLink')

def update_gsheet_rekap(sheets_service, spreadsheet_id, sheets_info, today_str, count):
    rekap_name = 'REKAP TOTAL'
    if rekap_name not in sheets_info:
        body = {'requests': [{'addSheet': {'properties': {'title': rekap_name, 'index': 0}}}]}
        sheets_service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=f"'{rekap_name}'!A1",
            valueInputOption='RAW', body={'values': [['Tanggal', 'Laporan', 'Link ke Detail']]}).execute()

    # Link formula (internal hyperlink) - Menggunakan ';' karena GSheets Anda berbahasa Indonesia
    sheet_id = sheets_info.get(today_str)
    link_formula = f'=HYPERLINK("#gid={sheet_id}"; "Buka Detail {today_str}")'

    # Baca data rekap untuk cek apakah tanggal sudah ada
    res = sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f"'{rekap_name}'!A:C").execute()
    rows = res.get('values', [])
    
    found_idx = -1
    for i, row in enumerate(rows):
        if row and row[0] == today_str:
            found_idx = i + 1
            break
    
    if found_idx != -1:
        sheets_service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=f"'{rekap_name}'!B{found_idx}:C{found_idx}",
            valueInputOption='USER_ENTERED', body={'values': [[count, link_formula]]}).execute()
    else:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=f"'{rekap_name}'!A1",
            valueInputOption='USER_ENTERED', body={'values': [[today_str, count, link_formula]]}).execute()

def update_local_excel(today_str, today_files):
    """Tetap simpan backup di Excel Local dengan rumus Link (menggunakan ';' untuk locale Indonesia)."""
    try:
        link_formula = f'=HYPERLINK("#\'{today_str}\'!A1"; "Lihat Detail")'
        
        if not os.path.exists(EXCEL_FILE):
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                df_rekap = pd.DataFrame([{'Tanggal': today_str, 'Laporan': len(today_files), 'Detail': link_formula}])
                df_rekap.to_excel(writer, sheet_name='REKAP TOTAL', index=False)
                if today_files: pd.DataFrame(today_files).to_excel(writer, sheet_name=today_str, index=False)
        else:
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                if today_files: pd.DataFrame(today_files).to_excel(writer, sheet_name=today_str, index=False)
                
                try:
                    df_rekap = pd.read_excel(EXCEL_FILE, sheet_name='REKAP TOTAL')
                    # Pastikan kolom Detail bisa menerima string/objek (menghindari warning pandas)
                    df_rekap['Detail'] = df_rekap['Detail'].astype(object)
                except:
                    df_rekap = pd.DataFrame(columns=['Tanggal', 'Laporan', 'Detail'])
                
                if today_str in df_rekap['Tanggal'].astype(str).values:
                    df_rekap.loc[df_rekap['Tanggal'].astype(str) == today_str, 'Laporan'] = len(today_files)
                    df_rekap.loc[df_rekap['Tanggal'].astype(str) == today_str, 'Detail'] = link_formula
                else:
                    new_row = pd.DataFrame([{'Tanggal': today_str, 'Laporan': len(today_files), 'Detail': link_formula}])
                    df_rekap = pd.concat([df_rekap, new_row], ignore_index=True)
                
                df_rekap.to_excel(writer, sheet_name='REKAP TOTAL', index=False)
    except Exception as e:
        print(f"[!] Gagal update Excel Lokal (Mungkin sedang dibuka atau di Cloud): {e}")

def main():
    print("="*50); print("🚀 DRIVE + SHEETS DAILY SNAPSHOT STARTING..."); print("="*50)
    drive_service, sheets_service = get_services()
    if not drive_service: return

    # Paksa gunakan waktu WIB (UTC+7)
    now_wib = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
    today_str = now_wib.strftime('%Y-%m-%d')
    print(f"[*] Menarik SELURUH isi folder untuk Snapshot {today_str}...")
    
    query = f"'{FOLDER_ID}' in parents and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name, createdTime, webViewLink, owners)", orderBy="createdTime desc").execute()
    
    items = results.get('files', [])
    all_files_snapshot = []
    
    for item in items:
        created_time = datetime.datetime.fromisoformat(item['createdTime'].replace('Z', '+00:00')).astimezone()
        all_files_snapshot.append({
            'Waktu Upload': created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'Nama (Clean)': clean_name(item['name']),
            'Nama Asli File': item['name'],
            'Uploader': item.get('owners', [{}])[0].get('displayName', 'Unknown'),
            'Link File': item['webViewLink']
        })

    print(f"[*] Snapshot Selesai: Ditemukan total {len(all_files_snapshot)} file di dalam folder.")

    # 1. Update Local Excel (Snapshot Hari Ini)
    print(f"[*] Mengupdate Excel Local (Tab: {today_str})...")
    update_local_excel(today_str, all_files_snapshot)
    
    # 2. Update Google Sheets (Snapshot Hari Ini)
    try:
        print(f"[*] Sinkronisasi ke Google Sheets (Tab: {today_str})...")
        gsheet_url = sync_to_google_sheets(sheets_service, drive_service, today_str, all_files_snapshot)
        print(f"✅ GOOGLE SHEETS UPDATED: {gsheet_url}")
    except Exception as e:
        print(f"❌ Gagal update Google Sheets: {e}")

    print("="*50); print(f"✅ SELESAI! Snapshot {today_str} Berhasil."); print("="*50)

if __name__ == '__main__':
    main()
