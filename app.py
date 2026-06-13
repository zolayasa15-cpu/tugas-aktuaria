# app.py
# Aplikasi Kalkulator Aktuaria Sederhana
# Entry point utama Streamlit

import streamlit as st
from utils.helper import load_mortality_table

# Custom CSS untuk tampilan lebih menarik
st.markdown("""
<style>
    /* Ganti background utama */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8edf2 100%);
    }
    
    /* Header utama */
    h1, h2, h3 {
        color: #1E3A5F !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A5F 0%, #0F2A4A 100%);
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.1rem;
        font-weight: 500;
        padding: 8px 12px;
        border-radius: 10px;
        transition: 0.3s;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: rgba(255,255,255,0.1);
    }
    
    /* Tombol utama */
    .stButton > button {
        background: linear-gradient(90deg, #1E3A5F, #2E5A8F);
        color: white;
        font-weight: bold;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 30px;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #2E5A8F, #3E7AAF);
        transform: scale(1.02);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Metric card */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #1E3A5F !important;
        background: linear-gradient(135deg, #ffffff, #f0f2f6);
        padding: 10px 15px;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        color: #4A5568 !important;
        font-weight: 600;
    }
    
    /* Info box */
    .stAlert {
        border-radius: 15px;
        border-left: 5px solid #1E3A5F;
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .dataframe th {
        background-color: #1E3A5F !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 10px;
        font-weight: bold;
        color: #1E3A5F;
    }
    
    /* Number input */
    .stNumberInput input {
        border-radius: 10px;
        border: 1px solid #cbd5e0;
        padding: 8px 12px;
    }
    
    /* Selectbox */
    .stSelectbox div[data-baseweb="select"] {
        border-radius: 10px;
    }
    
    /* Radio button */
    .stRadio > div {
        gap: 1rem;
    }
    
    /* Tab menu */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #f0f2f6;
        border-radius: 30px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 30px;
        padding: 8px 20px;
        font-weight: bold;
    }
    
    /* Footer */
    footer {
        visibility: hidden;
    }
    
    /* Title utama */
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #1E3A5F, #3E7AAF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Tampilkan judul dengan styling
st.markdown('<div class="main-title">📐 Aplikasi Kalkulator Aktuaria</div>', unsafe_allow_html=True)
# Load tabel mortalitas (dengan cache agar tidak reload terus)
MORTALITY_DF = load_mortality_table("data/tabel_mortalitas.csv")

# ============================================
# SIDEBAR NAVIGASI
# ============================================

with st.sidebar:
    st.markdown("# 📐 Kalkulator Aktuaria")
    st.markdown("---")
    
    menu = st.radio(
        "Pilih Modul:",
        [
            "🏠 Beranda",
            "💰 Bunga",
            "📅 Anuitas",
            "📊 Tabel Mortalitas",
            "🛡️ Premi Asuransi Jiwa",
            "📈 Cadangan Premi",
            "ℹ️ Tentang"
        ],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"Versi 1.0 | Python + Streamlit")

# ============================================
# KONTEN UTAMA (BERDASARKAN MENU)
# ============================================

if menu == "🏠 Beranda":
    # Custom CSS untuk tampilan yang elegan dan profesional
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem 2rem 1.8rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color:#e0e7ff;
        margin: 0 0 0.5rem 0;
        font-size: 1.8rem;
        font-weight: 500;
    }
    .main-header p {
        color: #e0e7ff;
        margin: 0;
        font-size: 1rem;
    }
    .section-card {
        background: white;
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3c72;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #eef2f6;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.75rem 1.5rem;
        margin: 0;
    }
    .feature-item {
        color: #2d3748;
        font-size: 0.95rem;
        padding: 0.25rem 0;
    }
    .step-list {
        margin: 0;
        padding-left: 1.2rem;
    }
    .step-list li {
        margin: 0.5rem 0;
        color: #2d3748;
    }
    hr {
        margin: 1rem 0;
        border-color: #eef2f6;
    }
    .footer-ref {
        font-size: 0.8rem;
        color: #718096;
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eef2f6;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header utama
    st.markdown("""
    <div class="main-header">
        <p>Platform perhitungan aktuaria dasar untuk keperluan analisis dan pembelajaran</p>
    </div>
    """, unsafe_allow_html=True)

    # Dua kolom utama
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">📋 Ruang Lingkup Perhitungan</div>
            <div class="feature-grid">
                <div class="feature-item">• Bunga (Future Value & Present Value)</div>
                <div class="feature-item">• Anuitas (Immediate, Due, Deferred)</div>
                <div class="feature-item">• Tabel Mortalitas</div>
                <div class="feature-item">• Premi Asuransi Jiwa</div>
                <div class="feature-item">• Cadangan Premi (Prospektif & Retrospektif)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="section-card">
            <div class="section-title">📌 Prosedur Penggunaan</div>
            <ol class="step-list">
                <li>Pilih modul perhitungan pada menu di sidebar kiri</li>
                <li>Masukkan parameter sesuai dengan ketentuan yang ditampilkan</li>
                <li>Klik tombol <strong>HITUNG</strong></li>
                <li>Hasil perhitungan akan ditampilkan pada panel hasil</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    # Informasi tambahan yang ringkas
    st.markdown("""
    <div class="section-card">
        <div class="section-title">ℹ️ Keterangan Umum</div>
        <p style="margin: 0; color: #2d3748;">
            Seluruh perhitungan dalam aplikasi ini mengacu pada prinsip-prinsip aktuaria standar. 
            Pengguna diharapkan untuk memverifikasi parameter yang dimasukkan sebelum melakukan 
            perhitungan guna memastikan akurasi hasil.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Footer referensi
    st.markdown("""
    <div class="footer-ref">
        Referensi: Rumus aktuaria standar
    </div>
    """, unsafe_allow_html=True)
    # Tampilkan status tabel mortalitas
    if MORTALITY_DF is not None:
        st.success(f"✅ Tabel mortalitas loaded: {len(MORTALITY_DF)} baris data")
    else:
        st.warning("⚠️ Tabel mortalitas tidak ditemukan. Fitur mortalitas, premi, dan cadangan tidak dapat digunakan.")

elif menu == "💰 Bunga":
    from formulas.bunga import tampilkan_bunga
    tampilkan_bunga()

elif menu == "📅 Anuitas":
    from formulas.anuitas import tampilkan_anuitas
    tampilkan_anuitas()
    
    # Nanti setelah modul anuitas.py selesai:
    # from formulas.anuitas import tampilkan_anuitas
    # tampilkan_anuitas()

elif menu == "📊 Tabel Mortalitas":
    from formulas.mortalitas import tampilkan_mortalitas
    tampilkan_mortalitas(MORTALITY_DF)
    
    # Nanti setelah modul mortalitas.py selesai:
    # from formulas.mortalitas import tampilkan_mortalitas
    # tampilkan_mortalitas(MORTALITY_DF)

elif menu == "🛡️ Premi Asuransi Jiwa":
    from formulas.premi import tampilkan_premi
    tampilkan_premi(MORTALITY_DF)
    # Nanti setelah modul premi.py selesai:
    # from formulas.premi import tampilkan_premi
    # tampilkan_premi(MORTALITY_DF)

elif menu == "📈 Cadangan Premi":
    from formulas.cadangan import tampilkan_cadangan
    tampilkan_cadangan(MORTALITY_DF)

elif menu == "ℹ️ Tentang":
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 30px;'>
        <h1 style='color: white; margin: 0; text-align: center;'>Kalkulator Aktuaria Sederhana</h1>
        <p style='color: #e0e0e0; text-align: center; margin: 10px 0 0 0;'>Tools Perhitungan Dasar Matematika Aktuaria</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 100%;'>
            <h3 style='margin-top: 0;'>Developer</h3>
            <hr style='margin: 10px 0;'>
            <p><strong>Nama:</strong> EMI LAZOLA</p>
            <p><strong>NIM:</strong> 2210432010</p>
            <p><strong>Program Studi:</strong> S1 Matematika</p>
            <p><strong>Universitas:</strong> UNIVERSITAS ANDALAS</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; height: 100%;'>
            <h3 style='margin-top: 0;'>Informasi Aplikasi</h3>
            <hr style='margin: 10px 0;'>
            <p><strong>Versi:</strong> 1.0</p>
            <p><strong>Status:</strong> Work In Progress</p>
            <p><strong>Update Terakhir:</strong> 21 Mei 2026</p>
            <p><strong>Framework:</strong> Streamlit, Python 3.10+</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;'>
        <strong>Tujuan Pembuatan</strong><br>
        Aplikasi ini dikembangkan sebagai pemenuhan tugas mata kuliah Matematika Aktuaria.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #e8f4f8; padding: 20px; border-radius: 10px;'>
        <strong>Fitur yang Tersedia</strong>
        <table style='width: 100%; margin-top: 10px; border-collapse: collapse;'>
            <tr style='border-bottom: 1px solid #ddd;'>
                <td style='padding: 8px;'>Perhitungan Bunga (FV/PV)</td>
                <td style='padding: 8px; color: green;'>Tersedia</td>
            </tr>
            <tr style='border-bottom: 1px solid #ddd;'>
                <td style='padding: 8px;'>Perhitungan Anuitas</td>
                <td style='padding: 8px; color: green;'>Tersedia</td>
            </tr>
            <tr style='border-bottom: 1px solid #ddd;'>
                <td style='padding: 8px;'>Tabel Mortalitas</td>
                <td style='padding: 8px; color: green;'>Tersedia</td>
            </tr>
            <tr style='border-bottom: 1px solid #ddd;'>
                <td style='padding: 8px;'>Perhitungan Premi</td>
                <td style='padding: 8px; color: green;'>Tersedia</td>
            </tr>
            <tr>
                <td style='padding: 8px;'>Perhitungan Cadangan Premi</td>
                <td style='padding: 8px; color: green;'>Tersedia</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("""
    **Catatan Penting**
    
        Data Mortalitas masih contoh (fiktif), bukan standar TMI/CSO
    Seluruh perhitungan dalam aplikasi ini menggunakan data contoh dan rumus dasar.
    Belum dilakukan verifikasi kesesuaian dengan standar aktuaria yang berlaku.
    Hasil perhitungan belum dapat digunakan untuk keperluan resmi.
    """)