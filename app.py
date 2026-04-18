import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
from monitor_drive import get_services, clean_name, FOLDER_ID, GSHEET_NAME

# Konfigurasi Halaman
st.set_page_config(
    page_title="Dashboard Monitoring SE2026",
    page_icon="📊",
    layout="wide"
)

# Kustomisasi CSS untuk tampilan premium
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def load_data_from_gsheets():
    """Mengambil data rekap dan harian dari Google Sheets."""
    try:
        drive_service, sheets_service = get_services()
        
        # Cari ID Spreadsheet
        query = f"name = '{GSHEET_NAME}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
        results = drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        
        if not files:
            st.error("Google Sheets tidak ditemukan. Pastikan Anda sudah menjalankan monitor_drive.py minimal satu kali.")
            return None, None
        
        spreadsheet_id = files[0]['id']
        
        # 1. Baca Rekap Total
        rekap_res = sheets_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range="'REKAP TOTAL'!A:B").execute()
        rekap_rows = rekap_res.get('values', [])
        df_rekap = pd.DataFrame(rekap_rows[1:], columns=rekap_rows[0]) if rekap_rows else pd.DataFrame()
        
        # 2. Baca Master Data / Semua File (Sebagai sample, kita ambil seluruh isi folder)
        results_files = drive_service.files().list(
            q=f"'{FOLDER_ID}' in parents and trashed = false", 
            fields="files(id, name, createdTime, webViewLink, owners)", 
            orderBy="createdTime desc"
        ).execute()
        
        raw_items = results_files.get('files', [])
        all_files = []
        now_wib = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        for item in raw_items:
            # Parse createdTime as UTC, then convert to WIB
            created_time_utc = datetime.datetime.fromisoformat(item['createdTime'].replace('Z', '+00:00'))
            created_time_wib = created_time_utc + datetime.timedelta(hours=7)
            
            all_files.append({
                'Tanggal': created_time_wib.strftime('%Y-%m-%d'),
                'Waktu': created_time_wib.strftime('%H:%M:%S'),
                'Nama (Clean)': clean_name(item['name']),
                'Uploader': item.get('owners', [{}])[0].get('displayName', 'Unknown'),
                'Link': item['webViewLink']
            })
        
        df_all = pd.DataFrame(all_files)
        return df_rekap, df_all
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return None, None

def main():
    st.title("📊 SE2026 Ujicoba CAPI - Monitoring Portal")
    st.markdown("Dashboard interaktif untuk memantau progres upload laporan secara real-time.")
    st.divider()

    # Sidebar
    st.sidebar.header("Kontrol Dashboard")
    if st.sidebar.button("🔄 Jalankan Sinkronisasi & Refresh"):
        with st.spinner("Sedang menyinkronkan Drive ke Spreadsheet..."):
            try:
                from monitor_drive import main as run_sync
                run_sync() # Menjalankan fungsi utama monitor_drive
                st.cache_data.clear()
                st.sidebar.success("Sinkronisasi Berhasil!")
                st.toast("Spreadsheet telah diperbarui!", icon="✅")
            except Exception as e:
                st.sidebar.error(f"Gagal Sinkronisasi: {e}")
        
    st.sidebar.info("Tombol di atas akan memperbarui Google Sheets & Dashboard sekaligus.")

    # Load Data
    with st.spinner("Mengambil data dari Cloud..."):
        df_rekap, df_all = load_data_from_gsheets()

    if df_all is not None and not df_all.empty:
        # Metrik Utama
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total File Terkumpul", len(df_all))
        with col2:
            now_wib = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
            today_str = now_wib.strftime('%Y-%m-%d')
            today_count = len(df_all[df_all['Tanggal'] == today_str])
            st.metric("Upload Hari Ini", today_count)
        with col3:
            total_uploader = df_all['Uploader'].nunique()
            st.metric("Jumlah Uploader Unik", total_uploader)

        st.divider()

        # Grafik Progres
        st.subheader("📈 Tren Progres Upload (Kumulatif)")
        if df_rekap is not None and not df_rekap.empty:
            # Mengambil nama kolom uploader (kolom kedua) secara otomatis
            uploader_col = df_rekap.columns[1]
            df_rekap[uploader_col] = pd.to_numeric(df_rekap[uploader_col], errors='coerce')
            
            fig = px.line(df_rekap, x='Tanggal', y=uploader_col, markers=True, 
                          title=f'Jumlah File per Sesi Cek', template="plotly_white")
            fig.update_traces(line_color='#1f77b4', line_width=3)
            st.plotly_chart(fig, use_container_width=True)

        # Tabel Interaktif
        st.subheader("📄 Rincian Data Uploader")
        
        # Filter Nama
        search_query = st.text_input("Cari Nama atau Uploader:", placeholder="Ketik nama di sini...")
        if search_query:
            filtered_df = df_all[
                (df_all['Nama (Clean)'].str.contains(search_query, case=False)) | 
                (df_all['Uploader'].str.contains(search_query, case=False))
            ]
        else:
            filtered_df = df_all

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        now_wib = datetime.datetime.utcnow() + datetime.timedelta(hours=7)
        csv = df_all.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data CSV",
            data=csv,
            file_name=f'Monitoring_CAPI_{now_wib.strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
    else:
        st.warning("Belum ada data untuk ditampilkan. Jalankan monitor_drive.py terlebih dahulu.")

if __name__ == "__main__":
    main()
