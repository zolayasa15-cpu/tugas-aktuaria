# formulas/premi.py
# Modul perhitungan premi asuransi jiwa - Standar Aktuaria

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.helper import (
    validate_age,
    validate_non_negative,
    validate_period,
    validate_age_plus_term,
    validate_and_display,
    get_qx,
    get_px,
    probability_live_t_years,
    v_factor,
    format_rupiah,
    format_decimal,
    format_percent
)

def format_rupiah_axis(x, p):
    """Format untuk sumbu Y grafik dalam Rupiah"""
    if x >= 1e9:
        return f'Rp {x/1e9:.1f}M'
    elif x >= 1e6:
        return f'Rp {x/1e6:.0f}Jt'
    elif x >= 1e3:
        return f'Rp {x/1e3:.0f}Rb'
    else:
        return f'Rp {x:.0f}'

def hitung_premi_berjangka(df, usia, n, i, up):
    """
    Menghitung premi bersih asuransi jiwa berjangka n tahun
    Rumus: A_x:n|^1 = sum_{k=0}^{n-1} v^(k+1) * _k p_x * q_{x+k} * UP
    """
    v = v_factor(i)
    total = 0
    detail = []
    
    for k in range(n):
        # Hitung _k p_x (probabilitas hidup sampai usia x+k)
        if k == 0:
            p_k = 1.0
        else:
            p_k = probability_live_t_years(df, usia, k)
            if p_k is None:
                return None, None
        
        # Hitung q_{x+k}
        q = get_qx(df, usia + k)
        if q is None:
            return None, None
        
        # Hitung kontribusi
        faktor_diskon = v ** (k + 1)
        kontribusi = faktor_diskon * p_k * q * up
        
        detail.append({
            "Tahun ke-": k + 1,
            "Usia": usia + k,
            "ₖpₓ": p_k,
            "qₓ₊ₖ": q,
            "v^(k+1)": faktor_diskon,
            "Kontribusi": kontribusi
        })
        
        total += kontribusi
    
    return total, detail

def hitung_premi_endowment(df, usia, n, i, up):
    """
    Menghitung premi bersih asuransi endowment n tahun
    Rumus: A_x:n| = A_x:n|^1 + A_x:n|^1 (endowment)
    """
    # Bagian berjangka
    premi_berjangka, detail_berjangka = hitung_premi_berjangka(df, usia, n, i, up)
    if premi_berjangka is None:
        return None, None, None
    
    # Bagian endowment (uang pertanggungan dibayar jika hidup sampai n tahun)
    v = v_factor(i)
    p_n = probability_live_t_years(df, usia, n)
    if p_n is None:
        return None, None, None
    
    premi_endowment = up * (v ** n) * p_n
    
    detail_endowment = {
        "Tahun ke-": n,
        "Usia": usia + n,
        "ₙpₓ": p_n,
        "v^n": v ** n,
        "Kontribusi Endowment": premi_endowment
    }
    
    return premi_berjangka + premi_endowment, detail_berjangka, detail_endowment

def hitung_premi_tahunan(premi_sekali, n, i, jenis="berjangka"):
    """
    Menghitung premi tahunan dari premi sekali bayar
    Menggunakan rumus anuitas: P = A / ä_x:n|
    """
    if i == 0:
        anuitas = n
    else:
        v = v_factor(i)
        anuitas = (1 - v**n) / i  # a_n (anuitas immediate)
    
    premi_tahunan = premi_sekali / anuitas if anuitas > 0 else premi_sekali / n
    
    return premi_tahunan, anuitas

def tampilkan_premi(df):
    """Menampilkan halaman perhitungan premi asuransi jiwa"""
    st.header("🛡️ Premi Asuransi Jiwa (Standar Aktuaria)")
    
    # Informasi awal
    st.markdown("""
    <div style='background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
    <b>📖 Tentang Premi Asuransi Jiwa:</b><br>
    Premi asuransi jiwa adalah jumlah uang yang dibayarkan tertanggung kepada perusahaan asuransi 
    sebagai imbalan atas perlindungan yang diberikan. Perhitungan menggunakan prinsip aktuaria 
    dengan mempertimbangkan mortalitas, suku bunga, dan uang pertanggungan.
    </div>
    """, unsafe_allow_html=True)
    
    if df is None:
        st.error("❌ Tabel mortalitas tidak tersedia. Periksa file data/tabel_mortalitas.csv")
        return
    
    # Form input parameter - semua dalam satu area
    with st.form(key="form_premi"):
        st.subheader("📝 Parameter Asuransi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            usia = st.number_input(
                "**Usia Tertanggung (x)**",
                min_value=0,
                max_value=90,
                value=30,
                step=1,
                help="Usia saat mulai perlindungan"
            )
            
            masa_pertanggungan = st.number_input(
                "**Masa Pertanggungan (n)**",
                min_value=1,
                max_value=50,
                value=20,
                step=1,
                help="Lama masa perlindungan asuransi (tahun)"
            )
        
        with col2:
            suku_bunga = st.number_input(
                "**Suku Bunga Teknis**",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                format="%.2f",
                help="Tingkat bunga yang diasumsikan dalam perhitungan (% per tahun)"
            )
            
            uang_pertanggungan = st.number_input(
                "**Uang Pertanggungan (UP)**",
                min_value=1_000_000,
                value=100_000_000,
                step=10_000_000,
                format="%.0f",
                help="Jumlah yang dibayarkan jika terjadi klaim (Rp)"
            )
        
        with col3:
            jenis_asuransi = st.selectbox(
                "**Jenis Asuransi**",
                ["Berjangka (Term Life)", "Endowment (Dwiguna)"],
                help="""
                - Berjangka: Perlindungan selama n tahun, UP dibayar jika meninggal dalam periode tersebut
                - Endowment: UP dibayar jika meninggal dalam n tahun ATAU hidup sampai akhir periode
                """
            )
            
            metode_pembayaran = st.selectbox(
                "**Metode Pembayaran Premi**",
                ["Sekali Bayar (Single Premium)", "Tahunan (Annual Premium)"],
                help="Pilih metode pembayaran premi"
            )
        
        submit = st.form_submit_button("🔢 HITUNG PREMI", type="primary", use_container_width=True)
    
    # HASIL PERHITUNGAN - DITAMPILKAN DI BAWAH TOMBOL
    if submit:
        errors = []
        i = suku_bunga / 100
        
        valid1, msg1 = validate_age(usia)
        if not valid1:
            errors.append(msg1)
        
        valid2, msg2 = validate_period(masa_pertanggungan, 1)
        if not valid2:
            errors.append(msg2)
        
        valid3, msg3 = validate_non_negative(i, "Suku bunga")
        if not valid3:
            errors.append(msg3)
        
        valid4, msg4 = validate_age_plus_term(usia, masa_pertanggungan)
        if not valid4:
            errors.append(msg4)
        
        if uang_pertanggungan <= 0:
            errors.append("Uang pertanggungan harus lebih besar dari 0")
        
        if not validate_and_display(errors):
            return
        
        st.divider()
        st.subheader("📊 HASIL PERHITUNGAN PREMI")
        
        # Hitung premi berdasarkan jenis asuransi
        if jenis_asuransi == "Berjangka (Term Life)":
            premi_sekali, detail_tabel = hitung_premi_berjangka(df, usia, masa_pertanggungan, i, uang_pertanggungan)
            
            if premi_sekali is None:
                st.error("❌ Gagal menghitung premi. Data mortalitas tidak mencukupi.")
                return
            
            # Ringkasan parameter
            col_param1, col_param2, col_param3, col_param4 = st.columns(4)
            with col_param1:
                st.metric("📊 Usia Tertanggung", f"{usia} tahun")
            with col_param2:
                st.metric("⏱️ Masa Pertanggungan", f"{masa_pertanggungan} tahun")
            with col_param3:
                st.metric("💰 Uang Pertanggungan", format_rupiah(uang_pertanggungan))
            with col_param4:
                st.metric("📈 Suku Bunga", f"{suku_bunga}%")
            
            # Hasil premi
            if metode_pembayaran == "Sekali Bayar (Single Premium)":
                st.success(f"### 🎯 Premi Bersih Sekali Bayar")
                st.markdown(f"""
                <div style='background-color: #d4edda; padding: 25px; border-radius: 10px; text-align: center; margin: 10px 0;'>
                <h1 style='color: #155724; margin: 0;'>{format_rupiah(premi_sekali)}</h1>
                <p style='margin: 10px 0 0 0; color: #155724; font-size: 16px;'>Premium Single (Pembayaran 1 kali)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                premi_tahunan, anuitas = hitung_premi_tahunan(premi_sekali, masa_pertanggungan, i, "berjangka")
                st.info(f"### 📅 Premi Bersih Tahunan")
                st.markdown(f"""
                <div style='background-color: #fff3cd; padding: 25px; border-radius: 10px; text-align: center; margin: 10px 0;'>
                <h1 style='color: #856404; margin: 0;'>{format_rupiah(premi_tahunan)}</h1>
                <p style='margin: 10px 0 0 0; color: #856404; font-size: 16px;'>per tahun selama {masa_pertanggungan} tahun</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"Berdasarkan anuitas faktor ä = {anuitas:.4f}")
            
            # Tabel detail perhitungan
            with st.expander("📋 Tabel Detail Perhitungan Premi (per tahun)", expanded=False):
                df_detail = pd.DataFrame(detail_tabel)
                df_detail["ₖpₓ"] = df_detail["ₖpₓ"].apply(lambda x: format_decimal(x, 6))
                df_detail["qₓ₊ₖ"] = df_detail["qₓ₊ₖ"].apply(lambda x: format_decimal(x, 6))
                df_detail["v^(k+1)"] = df_detail["v^(k+1)"].apply(lambda x: format_decimal(x, 6))
                df_detail["Kontribusi"] = df_detail["Kontribusi"].apply(format_rupiah)
                
                st.dataframe(df_detail, use_container_width=True, hide_index=True)
                
                st.info(f"""
                **Ringkasan Perhitungan:**
                - Total Premi Sekali Bayar: {format_rupiah(premi_sekali)}
                - Uang Pertanggungan: {format_rupiah(uang_pertanggungan)}
                - Rasio Premi/UP: {format_percent(premi_sekali / uang_pertanggungan)}
                """)
            
            # Grafik kontribusi risiko per tahun
            st.subheader("📊 Visualisasi Distribusi Risiko")
            fig, ax = plt.subplots(figsize=(12, 5))
            tahun = [d["Tahun ke-"] for d in detail_tabel]
            kontribusi = [d["Kontribusi"] for d in detail_tabel]
            
            bars = ax.bar(tahun, kontribusi, width=0.8, color='steelblue', alpha=0.7)
            ax.set_xlabel('Tahun', fontsize=11)
            ax.set_ylabel('Kontribusi Premi (Rp)', fontsize=11)
            ax.set_title('Distribusi Risiko Premi per Tahun - Asuransi Berjangka', fontsize=12, fontweight='bold')
            
            # Perbaikan format sumbu Y
            ax.yaxis.set_major_formatter(plt.FuncFormatter(format_rupiah_axis))
            
            # Tambahkan nilai di atas bar
            for bar, kontrib in zip(bars, kontribusi):
                if kontrib > 0:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                           f'{format_rupiah(kontrib)}', ha='center', va='bottom', fontsize=8, rotation=45)
            
            ax.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            st.pyplot(fig)
            
        else:  # Endowment
            premi_sekali, detail_berjangka, detail_endowment = hitung_premi_endowment(
                df, usia, masa_pertanggungan, i, uang_pertanggungan
            )
            
            if premi_sekali is None:
                st.error("❌ Gagal menghitung premi. Data mortalitas tidak mencukupi.")
                return
            
            # Ringkasan parameter
            col_param1, col_param2, col_param3, col_param4 = st.columns(4)
            with col_param1:
                st.metric("📊 Usia Tertanggung", f"{usia} tahun")
            with col_param2:
                st.metric("⏱️ Masa Pertanggungan", f"{masa_pertanggungan} tahun")
            with col_param3:
                st.metric("💰 Uang Pertanggungan", format_rupiah(uang_pertanggungan))
            with col_param4:
                st.metric("📈 Suku Bunga", f"{suku_bunga}%")
            
            # Hasil premi
            if metode_pembayaran == "Sekali Bayar (Single Premium)":
                st.success(f"### 🎯 Premi Bersih Sekali Bayar (Endowment)")
                st.markdown(f"""
                <div style='background-color: #d4edda; padding: 25px; border-radius: 10px; text-align: center; margin: 10px 0;'>
                <h1 style='color: #155724; margin: 0;'>{format_rupiah(premi_sekali)}</h1>
                <p style='margin: 10px 0 0 0; color: #155724; font-size: 16px;'>Premium Single (Pembayaran 1 kali)</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Breakdown premi
                premi_berjangka = sum(d["Kontribusi"] for d in detail_berjangka)
                premi_endowment_val = detail_endowment["Kontribusi Endowment"]
                
                col_break1, col_break2 = st.columns(2)
                with col_break1:
                    st.metric("Komponen Berjangka (Risiko Kematian)", format_rupiah(premi_berjangka))
                with col_break2:
                    st.metric("Komponen Endowment (Tabungan)", format_rupiah(premi_endowment_val))
            else:
                premi_tahunan, anuitas = hitung_premi_tahunan(premi_sekali, masa_pertanggungan, i, "endowment")
                st.info(f"### 📅 Premi Bersih Tahunan (Endowment)")
                st.markdown(f"""
                <div style='background-color: #fff3cd; padding: 25px; border-radius: 10px; text-align: center; margin: 10px 0;'>
                <h1 style='color: #856404; margin: 0;'>{format_rupiah(premi_tahunan)}</h1>
                <p style='margin: 10px 0 0 0; color: #856404; font-size: 16px;'>per tahun selama {masa_pertanggungan} tahun</p>
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"Berdasarkan anuitas faktor ä = {anuitas:.4f}")
            
            # Tabel detail perhitungan berjangka
            with st.expander("📋 Tabel Detail Perhitungan Premi Berjangka", expanded=False):
                df_detail = pd.DataFrame(detail_berjangka)
                df_detail["ₖpₓ"] = df_detail["ₖpₓ"].apply(lambda x: format_decimal(x, 6))
                df_detail["qₓ₊ₖ"] = df_detail["qₓ₊ₖ"].apply(lambda x: format_decimal(x, 6))
                df_detail["v^(k+1)"] = df_detail["v^(k+1)"].apply(lambda x: format_decimal(x, 6))
                df_detail["Kontribusi"] = df_detail["Kontribusi"].apply(format_rupiah)
                
                st.dataframe(df_detail, use_container_width=True, hide_index=True)
            
            # Detail komponen endowment
            with st.expander("📋 Detail Komponen Endowment", expanded=False):
                st.markdown(f"""
                - **Probabilitas hidup {masa_pertanggungan} tahun (ₙpₓ):** {format_decimal(detail_endowment['ₙpₓ'], 6)} ({format_percent(detail_endowment['ₙpₓ'])})
                - **Faktor diskon (v^n):** {format_decimal(detail_endowment['v^n'], 6)}
                - **Kontribusi Endowment:** {format_rupiah(detail_endowment['Kontribusi Endowment'])}
                """)
            
            # Ringkasan
            premi_berjangka = sum(d["Kontribusi"] for d in detail_berjangka)
            premi_endowment_val = detail_endowment["Kontribusi Endowment"]
            
            st.info(f"""
            **Ringkasan Perhitungan Endowment:**
            - Total Premi Sekali Bayar: {format_rupiah(premi_sekali)}
            - Komponen Risiko Kematian: {format_rupiah(premi_berjangka)} ({format_percent(premi_berjangka/premi_sekali)})
            - Komponen Tabungan (Endowment): {format_rupiah(premi_endowment_val)} ({format_percent(premi_endowment_val/premi_sekali)})
            - Uang Pertanggungan: {format_rupiah(uang_pertanggungan)}
            """)
            
            # Grafik
            st.subheader("📊 Visualisasi Komponen Premi")
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # Pie chart komponen premi
            labels = ['Risiko Kematian', 'Komponen Tabungan']
            sizes = [premi_berjangka, premi_endowment_val]
            colors = ['#ff9999', '#66b3ff']
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Komposisi Premi Endowment', fontsize=12, fontweight='bold')
            
            # Bar chart kontribusi risiko per tahun
            tahun = [d["Tahun ke-"] for d in detail_berjangka]
            kontribusi = [d["Kontribusi"] for d in detail_berjangka]
            bars = ax2.bar(tahun, kontribusi, width=0.8, color='steelblue', alpha=0.7)
            ax2.set_xlabel('Tahun', fontsize=11)
            ax2.set_ylabel('Kontribusi Premi (Rp)', fontsize=11)
            ax2.set_title('Distribusi Risiko Premi per Tahun', fontsize=12, fontweight='bold')
            
            # Perbaikan format sumbu Y
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_rupiah_axis))
            
            # Tambahkan nilai di atas bar
            for bar, kontrib in zip(bars, kontribusi):
                if kontrib > 0:
                    height = bar.get_height()
                    ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                            f'{format_rupiah(kontrib)}', ha='center', va='bottom', fontsize=8, rotation=45)
            
            ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # Catatan kaki
        st.divider()
        st.caption("📌 **Catatan:** Perhitungan menggunakan premi bersih (net premium) tanpa loading biaya akuisisi, administrasi, dan cadangan. Untuk premi kotor (gross premium), tambahkan loading factor sesuai kebijakan perusahaan.")