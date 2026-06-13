# formulas/bunga.py
# Modul perhitungan bunga (FV, PV, sederhana, majemuk dengan frekuensi)

import streamlit as st
import pandas as pd
from utils.helper import (
    validate_positive_number,
    validate_non_negative,
    validate_period,
    validate_and_display,
    format_rupiah
)

def future_value(pv, rate, period, compound=True, m=1):
    """Menghitung future value"""
    if compound:
        # Bunga majemuk dengan frekuensi m kali per tahun
        return pv * (1 + rate/m) ** (period * m)
    else:
        # Bunga sederhana
        return pv * (1 + rate * period)

def present_value(fv, rate, period, compound=True, m=1):
    """Menghitung present value"""
    if compound:
        # Bunga majemuk dengan frekuensi m kali per tahun
        return fv / ((1 + rate/m) ** (period * m))
    else:
        # Bunga sederhana
        return fv / (1 + rate * period)

def hitung_tabel_tabungan_majemuk(pv, rate, period, m):
    """Menghitung tabel pertumbuhan tabungan dengan bunga majemuk per sub-periode"""
    tabel = []
    saldo = pv
    rate_per_periode = rate / m
    total_sub_periode = int(period * m)  # Konversi ke integer
    
    for t in range(1, total_sub_periode + 1):
        bunga = saldo * rate_per_periode
        saldo += bunga
        
        periode_ke = (t - 1) // m + 1
        sub_ke = (t - 1) % m + 1
        
        tabel.append({
            "Periode ke-": periode_ke,
            "Sub-periode ke-": sub_ke,
            "Bunga": bunga,
            "Saldo Akhir": saldo
        })
    
    return tabel

def hitung_tabel_tabungan_sederhana(pv, rate, period):
    """Menghitung tabel pertumbuhan tabungan dengan bunga sederhana"""
    tabel = []
    bunga_per_periode = pv * rate
    
    for t in range(1, period + 1):
        saldo = pv + (bunga_per_periode * t)
        
        tabel.append({
            "Periode ke-": t,
            "Bunga Periode Ini": bunga_per_periode,
            "Total Bunga Sampai Periode Ini": bunga_per_periode * t,
            "Saldo Akhir": saldo
        })
    
    return tabel

def hitung_tabel_angsuran_majemuk(pv, rate, period, m):
    """Menghitung tabel angsuran untuk pinjaman dengan bunga majemuk"""
    rate_per_periode = rate / m
    total_sub_periode = int(period * m)  # Konversi ke integer
    
    if rate_per_periode > 0:
        cicilan = pv * (rate_per_periode * (1 + rate_per_periode) ** total_sub_periode) / ((1 + rate_per_periode) ** total_sub_periode - 1)
    else:
        cicilan = pv / total_sub_periode
    
    tabel = []
    sisa_pokok = pv
    
    for t in range(1, total_sub_periode + 1):
        bunga = sisa_pokok * rate_per_periode
        angsuran_pokok = cicilan - bunga
        sisa_pokok -= angsuran_pokok
        
        periode_ke = (t - 1) // m + 1
        sub_ke = (t - 1) % m + 1
        
        tabel.append({
            "Periode ke-": periode_ke,
            "Sub-periode ke-": sub_ke,
            "Angsuran Pokok": angsuran_pokok,
            "Bunga": bunga,
            "Total Cicilan": cicilan,
            "Sisa Pokok": max(0, sisa_pokok)
        })
    
    return tabel, cicilan

def hitung_tabel_angsuran_sederhana(pv, rate, period):
    """Menghitung tabel angsuran untuk pinjaman dengan bunga sederhana"""
    angsuran_pokok = pv / period
    tabel = []
    sisa_pokok = pv
    
    for t in range(1, period + 1):
        bunga = sisa_pokok * rate
        total_cicilan = angsuran_pokok + bunga
        sisa_pokok -= angsuran_pokok
        
        tabel.append({
            "Periode ke-": t,
            "Angsuran Pokok": angsuran_pokok,
            "Bunga": bunga,
            "Total Cicilan": total_cicilan,
            "Sisa Pokok": max(0, sisa_pokok)
        })
    
    return tabel

def tampilkan_bunga():
    """Menampilkan halaman perhitungan bunga"""
    st.header("💰 Perhitungan Bunga")
    
    # Step 1: Pilih jenis bunga (default bunga majemuk)
    jenis_bunga = st.radio(
        "**Pilih Jenis Bunga:**",
        ["Bunga Majemuk", "Bunga Sederhana"],
        horizontal=True
    )
    
    st.divider()
    
    # Step 2: Pilih tipe perhitungan (muncul setelah pilih jenis bunga)
    tipe_hitung = st.radio(
        "**Pilih Tipe Perhitungan:**",
        ["Future Value (FV)", "Present Value (PV)"],
        horizontal=True
    )
    
    st.divider()
    
    # Step 3: Input parameter (muncul bertahap)
    with st.form(key="form_perhitungan"):
        col1, col2 = st.columns(2)
        
        with col1:
            if tipe_hitung == "Future Value (FV)":
                pv = st.number_input(
                    "**Nilai Sekarang (PV)**",
                    min_value=0.0,
                    value=10_000_000.0,
                    step=1_000_000.0,
                    format="%.0f",
                    help="Jumlah uang yang Anda miliki saat ini"
                )
                nilai_input = pv
            else:  # Present Value
                fv = st.number_input(
                    "**Nilai Masa Depan (FV)**",
                    min_value=0.0,
                    value=10_000_000.0,
                    step=1_000_000.0,
                    format="%.0f",
                    help="Jumlah uang yang diinginkan di masa depan"
                )
                nilai_input = fv
            
            suku_bunga = st.number_input(
                "**Suku Bunga (% per tahun)**",
                min_value=0.0,
                value=5.0,
                step=0.5,
                format="%.2f",
                help="Suku bunga dalam persen per tahun"
            )
            
            # Parameter frekuensi hanya untuk bunga majemuk
            if jenis_bunga == "Bunga Majemuk":
                opsi_frekuensi = {
                    "Bulanan (12x/tahun)": 12,
                    "Triwulan (4x/tahun)": 4,
                    "Caturwulan (3x/tahun)": 3,
                    "Semesteran (2x/tahun)": 2,
                    "Tahunan (1x/tahun)": 1
                }
                
                frekuensi_label = st.selectbox(
                    "**Frekuensi Perhitungan Bunga**",
                    options=list(opsi_frekuensi.keys()),
                    help="Seberapa sering bunga dihitung dalam setahun"
                )
                m = opsi_frekuensi[frekuensi_label]
                
                periode = st.number_input(
                    "**Jangka Waktu (dalam tahun)**",
                    min_value=0.25,
                    value=5.0,
                    step=0.5,
                    format="%.2f",
                    help="Lamanya investasi/pinjaman dalam tahun"
                )
            else:
                m = 1
                periode = st.number_input(
                    "**Jumlah Periode (dalam tahun)**",
                    min_value=1,
                    value=5,
                    step=1,
                    help="Jumlah periode (dalam tahun)"
                )
        
        with col2:
            # Informasi tambahan
            st.info("ℹ️ **Informasi:**")
            if jenis_bunga == "Bunga Majemuk":
                st.markdown("""
                - Bunga dihitung secara **berbunga** (bunga menghasilkan bunga)
                - Setiap periode bunga dihitung dari saldo terakhir
                - Semakin sering frekuensi, semakin besar hasil akhir
                """)
            else:
                st.markdown("""
                - Bunga dihitung hanya dari **pokok awal**
                - Besar bunga tetap setiap periode
                - Cocok untuk pinjaman jangka pendek
                """)
        
        submit = st.form_submit_button("🔢 HITUNG", type="primary", use_container_width=True)
    
    # Step 4: Hasil perhitungan (ditampilkan di bawah, proporsional)
    if submit:
        errors = []
        rate = suku_bunga / 100
        
        # Validasi
        valid1, msg1 = validate_positive_number(nilai_input, "Nilai")
        if not valid1:
            errors.append(msg1)
        
        valid2, msg2 = validate_non_negative(rate, "Suku bunga")
        if not valid2:
            errors.append(msg2)
        
        if jenis_bunga == "Bunga Majemuk":
            if periode <= 0:
                errors.append("Jangka waktu harus lebih besar dari 0")
        else:
            if periode < 1:
                errors.append("Jumlah periode minimal 1 tahun")
        
        if not validate_and_display(errors):
            return
        
        # Container untuk hasil
        st.divider()
        st.subheader("📊 HASIL PERHITUNGAN")
        
        # Perhitungan utama
        if tipe_hitung == "Future Value (FV)":
            hasil = future_value(nilai_input, rate, periode, compound=(jenis_bunga=="Bunga Majemuk"), m=m)
            
            col_result1, col_result2, col_result3 = st.columns(3)
            with col_result1:
                st.metric("💵 Nilai Sekarang (PV)", format_rupiah(nilai_input))
            with col_result2:
                if jenis_bunga == "Bunga Majemuk":
                    st.metric("📈 Frekuensi", frekuensi_label)
                else:
                    st.metric("📋 Jenis Bunga", "Sederhana")
            with col_result3:
                st.metric("🎯 Nilai Masa Depan (FV)", format_rupiah(hasil), delta=f"+{format_rupiah(hasil - nilai_input)}")
            
            # Tampilkan rumus
            with st.expander("📐 Lihat Rumus Perhitungan"):
                if jenis_bunga == "Bunga Majemuk":
                    st.markdown("**Rumus Bunga Majemuk dengan Frekuensi m kali per tahun:**")
                    st.latex(r"FV = PV \times \left(1 + \frac{i}{m}\right)^{n \times m}")
                    st.markdown(f"""
                    - PV = {format_rupiah(nilai_input)}
                    - i = {rate:.4f} ({suku_bunga}%)
                    - m = {m} kali per tahun
                    - n = {periode} tahun
                    - n×m = {int(periode * m)} periode
                    
                    **FV =** {format_rupiah(nilai_input)} × (1 + {rate:.4f}/{m})^{periode}×{m}
                    """)
                else:
                    st.markdown("**Rumus Bunga Sederhana:**")
                    st.latex(r"FV = PV \times (1 + i \times n)")
                    st.markdown(f"""
                    - PV = {format_rupiah(nilai_input)}
                    - i = {rate:.4f} ({suku_bunga}%)
                    - n = {periode} tahun
                    
                    **FV =** {format_rupiah(nilai_input)} × (1 + {rate:.4f} × {periode})
                    """)
            
            # Tabel detail tabungan
            st.subheader("📋 Tabel Detail Pertumbuhan Tabungan")
            
            if jenis_bunga == "Bunga Majemuk":
                tabel = hitung_tabel_tabungan_majemuk(nilai_input, rate, periode, m)
                df = pd.DataFrame(tabel)
                df["Bunga"] = df["Bunga"].apply(format_rupiah)
                df["Saldo Akhir"] = df["Saldo Akhir"].apply(format_rupiah)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.caption(f"📌 Total {len(tabel)} sub-periode (setiap {frekuensi_label.lower()})")
            else:
                periode_int = int(periode)
                tabel = hitung_tabel_tabungan_sederhana(nilai_input, rate, periode_int)
                df = pd.DataFrame(tabel)
                df["Bunga Periode Ini"] = df["Bunga Periode Ini"].apply(format_rupiah)
                df["Total Bunga Sampai Periode Ini"] = df["Total Bunga Sampai Periode Ini"].apply(format_rupiah)
                df["Saldo Akhir"] = df["Saldo Akhir"].apply(format_rupiah)
                st.dataframe(df, use_container_width=True, hide_index=True)
        
        else:  # Present Value
            hasil = present_value(nilai_input, rate, periode, compound=(jenis_bunga=="Bunga Majemuk"), m=m)
            
            col_result1, col_result2, col_result3 = st.columns(3)
            with col_result1:
                st.metric("🎯 Nilai Masa Depan (FV)", format_rupiah(nilai_input))
            with col_result2:
                if jenis_bunga == "Bunga Majemuk":
                    st.metric("📈 Frekuensi", frekuensi_label)
                else:
                    st.metric("📋 Jenis Bunga", "Sederhana")
            with col_result3:
                st.metric("💵 Nilai Sekarang (PV)", format_rupiah(hasil), delta=f"-{format_rupiah(nilai_input - hasil)}")
            
            # Tampilkan rumus
            with st.expander("📐 Lihat Rumus Perhitungan"):
                if jenis_bunga == "Bunga Majemuk":
                    st.markdown("**Rumus Bunga Majemuk dengan Frekuensi m kali per tahun:**")
                    st.latex(r"PV = \frac{FV}{\left(1 + \frac{i}{m}\right)^{n \times m}}")
                    st.markdown(f"""
                    - FV = {format_rupiah(nilai_input)}
                    - i = {rate:.4f} ({suku_bunga}%)
                    - m = {m} kali per tahun
                    - n = {periode} tahun
                    - n×m = {int(periode * m)} periode
                    
                    **PV =** {format_rupiah(nilai_input)} / (1 + {rate:.4f}/{m})^{periode}×{m}
                    """)
                else:
                    st.markdown("**Rumus Bunga Sederhana:**")
                    st.latex(r"PV = \frac{FV}{1 + i \times n}")
                    st.markdown(f"""
                    - FV = {format_rupiah(nilai_input)}
                    - i = {rate:.4f} ({suku_bunga}%)
                    - n = {periode} tahun
                    
                    **PV =** {format_rupiah(nilai_input)} / (1 + {rate:.4f} × {periode})
                    """)
            
            # Tabel detail angsuran (skenario pinjaman)
            st.subheader("📋 Tabel Detail Angsuran (Skenario Pinjaman)")
            st.info("💡 Tabel berikut menunjukkan skenario jika nilai sekarang dianggap sebagai **pinjaman** yang harus dilunasi.")
            
            if jenis_bunga == "Bunga Majemuk":
                tabel_angsuran, cicilan_tetap = hitung_tabel_angsuran_majemuk(hasil, rate, periode, m)
                df_angsuran = pd.DataFrame(tabel_angsuran)
                
                st.metric("💳 **Cicilan Tetap per Sub-periode**", format_rupiah(cicilan_tetap))
                
                df_angsuran["Angsuran Pokok"] = df_angsuran["Angsuran Pokok"].apply(format_rupiah)
                df_angsuran["Bunga"] = df_angsuran["Bunga"].apply(format_rupiah)
                df_angsuran["Total Cicilan"] = df_angsuran["Total Cicilan"].apply(format_rupiah)
                df_angsuran["Sisa Pokok"] = df_angsuran["Sisa Pokok"].apply(format_rupiah)
                
                st.dataframe(df_angsuran, use_container_width=True, hide_index=True)
                
                total_bayar = cicilan_tetap * len(tabel_angsuran)
                st.info(f"💰 **Total pembayaran:** {format_rupiah(total_bayar)}")
                st.info(f"📈 **Total bunga yang dibayar:** {format_rupiah(total_bayar - hasil)}")
            else:
                periode_int = int(periode)
                tabel_angsuran = hitung_tabel_angsuran_sederhana(hasil, rate, periode_int)
                df_angsuran = pd.DataFrame(tabel_angsuran)
                
                df_angsuran["Angsuran Pokok"] = df_angsuran["Angsuran Pokok"].apply(format_rupiah)
                df_angsuran["Bunga"] = df_angsuran["Bunga"].apply(format_rupiah)
                df_angsuran["Total Cicilan"] = df_angsuran["Total Cicilan"].apply(format_rupiah)
                df_angsuran["Sisa Pokok"] = df_angsuran["Sisa Pokok"].apply(format_rupiah)
                
                st.dataframe(df_angsuran, use_container_width=True, hide_index=True)
                
                total_bayar = sum(row["Total Cicilan"] for row in tabel_angsuran)
                st.info(f"💰 **Total pembayaran:** {format_rupiah(total_bayar)}")
                st.info(f"📈 **Total bunga yang dibayar:** {format_rupiah(total_bayar - hasil)}")
