# formulas/cadangan.py
# Modul perhitungan cadangan premi (prospektif & retrospektif) - Standar Aktuaria

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from utils.helper import (
    validate_age,
    validate_non_negative,
    validate_period,
    validate_age_plus_term,
    validate_and_display,
    get_qx,
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

def hitung_manfaat_berjangka(df, usia, n, i, up):
    """Menghitung nilai sekarang manfaat asuransi berjangka A_x:n|^1"""
    v = v_factor(i)
    total = 0
    detail = []
    
    for k in range(n):
        if k == 0:
            p_k = 1.0
        else:
            p_k = probability_live_t_years(df, usia, k)
            if p_k is None:
                return None, None
        
        q = get_qx(df, usia + k)
        if q is None:
            return None, None
        
        kontribusi = (v ** (k + 1)) * p_k * q * up
        
        detail.append({
            "Tahun ke-": k + 1,
            "Usia": usia + k,
            "ₖpₓ": p_k,
            "qₓ₊ₖ": q,
            "v^(k+1)": v ** (k + 1),
            "Kontribusi Manfaat": kontribusi
        })
        
        total += kontribusi
    
    return total, detail

def hitung_anuitas_due(df, usia, n, i):
    """Menghitung nilai sekarang anuitas due ä_x:n|"""
    v = v_factor(i)
    total = 0
    detail = []
    
    for k in range(n):
        if k == 0:
            p_k = 1.0
        else:
            p_k = probability_live_t_years(df, usia, k)
            if p_k is None:
                return None, None
        
        kontribusi = (v ** k) * p_k
        
        detail.append({
            "Tahun ke-": k + 1,
            "Usia": usia + k,
            "ₖpₓ": p_k,
            "v^k": v ** k,
            "Kontribusi Anuitas": kontribusi
        })
        
        total += kontribusi
    
    return total, detail

def hitung_cadangan_prospektif(df, usia, n, t, i, up, premi_tahunan):
    """
    Menghitung cadangan prospektif pada tahun ke-t
    Rumus: tV = A_{x+t:n-t|}^1 - P * ä_{x+t:n-t|}
    """
    if t >= n:
        return 0, None, None
    
    # Hitung nilai sekarang manfaat sisa (A_{x+t:n-t|}^1)
    nilai_manfaat, detail_manfaat = hitung_manfaat_berjangka(df, usia + t, n - t, i, up)
    if nilai_manfaat is None:
        return None, None, None
    
    # Hitung nilai sekarang anuitas due sisa (ä_{x+t:n-t|})
    nilai_anuitas, detail_anuitas = hitung_anuitas_due(df, usia + t, n - t, i)
    if nilai_anuitas is None:
        return None, None, None
    
    nilai_premi = premi_tahunan * nilai_anuitas
    
    # Cadangan prospektif = manfaat sisa - premi sisa
    cadangan = nilai_manfaat - nilai_premi
    
    return cadangan, detail_manfaat, detail_anuitas

def hitung_cadangan_retrospektif(df, usia, n, t, i, up, premi_tahunan):
    """
    Menghitung cadangan retrospektif pada tahun ke-t
    Rumus: tV = (P * ä_{x:t|}) / _t p_x - (A_{x:t|}^1) / _t p_x
    """
    if t == 0:
        return 0
    
    # Hitung probabilitas hidup sampai tahun ke-t (tpx)
    tpx = probability_live_t_years(df, usia, t)
    if tpx is None or tpx == 0:
        return None
    
    # Hitung nilai sekarang akumulasi premi (ä_{x:t|})
    nilai_anuitas, _ = hitung_anuitas_due(df, usia, t, i)
    if nilai_anuitas is None:
        return None
    
    akumulasi_premi = premi_tahunan * nilai_anuitas
    
    # Hitung nilai sekarang akumulasi biaya (A_{x:t|}^1)
    nilai_manfaat, _ = hitung_manfaat_berjangka(df, usia, t, i, up)
    if nilai_manfaat is None:
        return None
    
    # Cadangan retrospektif = (akumulasi premi - akumulasi biaya) / tpx
    cadangan = (akumulasi_premi - nilai_manfaat) / tpx
    
    return cadangan

def tampilkan_cadangan(df):
    """Menampilkan halaman perhitungan cadangan premi"""
    st.header("📈 Cadangan Premi Asuransi Jiwa (Standar Aktuaria)")
    
    # Informasi awal
    st.markdown("""
    <div style='background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
    <b>📖 Tentang Cadangan Premi:</b><br>
    Cadangan premi adalah dana yang harus disisihkan oleh perusahaan asuransi untuk memastikan 
    kewajiban pembayaran klaim di masa depan. Perhitungan menggunakan dua metode:
    <br><br>
    <b>• Prospektif:</b> Nilai sekarang manfaat sisa dikurangi nilai sekarang premi sisa<br>
    <b>• Retrospektif:</b> Akumulasi premi yang sudah dibayar dikurangi akumulasi biaya, 
    disesuaikan dengan probabilitas hidup
    </div>
    """, unsafe_allow_html=True)
    
    if df is None:
        st.error("❌ Tabel mortalitas tidak tersedia. Periksa file data/tabel_mortalitas.csv")
        return
    
    # Form input parameter
    with st.form(key="form_cadangan"):
        st.subheader("📝 Parameter Asuransi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            usia = st.number_input(
                "**Usia Saat Polis Mulai (x)**",
                min_value=0,
                max_value=90,
                value=30,
                step=1,
                help="Usia tertanggung saat asuransi dimulai"
            )
            
            masa_pertanggungan = st.number_input(
                "**Masa Pertanggungan (n tahun)**",
                min_value=1,
                max_value=50,
                value=20,
                step=1,
                help="Lama masa perlindungan asuransi"
            )
        
        with col2:
            tahun_ke = st.number_input(
                "**Tahun ke-t (Evaluasi Cadangan)**",
                min_value=0,
                max_value=masa_pertanggungan,
                value=5,
                step=1,
                help="Tahun saat cadangan dihitung (0 = awal polis)"
            )
            
            suku_bunga = st.number_input(
                "**Suku Bunga Teknis (% per tahun)**",
                min_value=0.0,
                max_value=20.0,
                value=5.0,
                step=0.5,
                format="%.2f",
                help="Tingkat bunga yang diasumsikan dalam perhitungan"
            )
        
        with col3:
            uang_pertanggungan = st.number_input(
                "**Uang Pertanggungan (UP)**",
                min_value=10_000_000,
                value=100_000_000,
                step=10_000_000,
                format="%.0f",
                help="Jumlah yang dibayarkan jika terjadi klaim"
            )
            
            premi_tahunan = st.number_input(
                "**Premi Tahunan (P)**",
                min_value=100_000,
                value=5_000_000,
                step=500_000,
                format="%.0f",
                help="Premi yang dibayarkan setiap tahun"
            )
        
        submit = st.form_submit_button("🔢 HITUNG CADANGAN", type="primary", use_container_width=True)
    
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
        
        valid3, msg3 = validate_period(tahun_ke, 0)
        if not valid3:
            errors.append(msg3)
        
        if tahun_ke > masa_pertanggungan:
            errors.append(f"Tahun ke-t ({tahun_ke}) tidak boleh melebihi masa pertanggungan ({masa_pertanggungan})")
        
        valid4, msg4 = validate_non_negative(i, "Suku bunga")
        if not valid4:
            errors.append(msg4)
        
        valid5, msg5 = validate_age_plus_term(usia, masa_pertanggungan)
        if not valid5:
            errors.append(msg5)
        
        if uang_pertanggungan <= 0:
            errors.append("Uang pertanggungan harus lebih besar dari 0")
        
        if premi_tahunan <= 0:
            errors.append("Premi tahunan harus lebih besar dari 0")
        
        if not validate_and_display(errors):
            return
        
        st.divider()
        st.subheader("📊 HASIL PERHITUNGAN CADANGAN")
        
        # Ringkasan parameter
        col_param1, col_param2, col_param3, col_param4 = st.columns(4)
        with col_param1:
            st.metric("📊 Usia Tertanggung", f"{usia} tahun")
        with col_param2:
            st.metric("⏱️ Masa Pertanggungan", f"{masa_pertanggungan} tahun")
        with col_param3:
            st.metric("🔢 Tahun Evaluasi", f"t = {tahun_ke}")
        with col_param4:
            st.metric("📈 Suku Bunga", f"{suku_bunga}%")
        
        # Hitung cadangan
        cadangan_prospektif, detail_manfaat_sisa, detail_anuitas_sisa = hitung_cadangan_prospektif(
            df, usia, masa_pertanggungan, tahun_ke, i, uang_pertanggungan, premi_tahunan
        )
        
        cadangan_retrospektif = hitung_cadangan_retrospektif(
            df, usia, masa_pertanggungan, tahun_ke, i, uang_pertanggungan, premi_tahunan
        )
        
        if cadangan_prospektif is None or cadangan_retrospektif is None:
            st.error("❌ Gagal menghitung cadangan. Data mortalitas tidak mencukupi.")
            st.info("💡 Tip: Pastikan usia + masa pertanggungan tidak melebihi batas data mortalitas (maksimal 100 tahun).")
            return
        
        # Hasil utama dalam card
        col_res1, col_res2 = st.columns(2)
        
        with col_res1:
            st.markdown(f"""
            <div style='background-color: #d4edda; padding: 20px; border-radius: 10px; text-align: center;'>
            <p style='margin: 0; color: #155724; font-size: 14px;'>Cadangan Prospektif</p>
            <h2 style='margin: 10px 0; color: #155724;'>{format_rupiah(cadangan_prospektif)}</h2>
            <p style='margin: 0; color: #155724; font-size: 12px;'>Nilai sekarang manfaat sisa - premi sisa</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_res2:
            st.markdown(f"""
            <div style='background-color: #d4edda; padding: 20px; border-radius: 10px; text-align: center;'>
            <p style='margin: 0; color: #155724; font-size: 14px;'>Cadangan Retrospektif</p>
            <h2 style='margin: 10px 0; color: #155724;'>{format_rupiah(cadangan_retrospektif)}</h2>
            <p style='margin: 0; color: #155724; font-size: 12px;'>(Akumulasi premi - akumulasi biaya) / ₜpₓ</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Selisih
        selisih = abs(cadangan_prospektif - cadangan_retrospektif)
        if selisih < 1000:
            st.success(f"✅ **Kedua metode konsisten** (selisih: {format_rupiah(selisih)})")
        else:
            st.warning(f"⚠️ **Kedua metode memiliki selisih** {format_rupiah(selisih)}. Periksa kembali parameter.")
        
        # Tabel detail perhitungan prospektif
        if tahun_ke < masa_pertanggungan and detail_manfaat_sisa is not None and detail_anuitas_sisa is not None:
            with st.expander("📋 Tabel Detail Perhitungan Cadangan Prospektif", expanded=False):
                st.markdown(f"**Nilai Sekarang Manfaat Sisa (A_{usia + tahun_ke}:{masa_pertanggungan - tahun_ke}|):**")
                
                df_manfaat = pd.DataFrame(detail_manfaat_sisa)
                df_manfaat["ₖpₓ"] = df_manfaat["ₖpₓ"].apply(lambda x: format_decimal(x, 6))
                df_manfaat["qₓ₊ₖ"] = df_manfaat["qₓ₊ₖ"].apply(lambda x: format_decimal(x, 6))
                df_manfaat["v^(k+1)"] = df_manfaat["v^(k+1)"].apply(lambda x: format_decimal(x, 6))
                df_manfaat["Kontribusi Manfaat"] = df_manfaat["Kontribusi Manfaat"].apply(format_rupiah)
                
                st.dataframe(df_manfaat, use_container_width=True, hide_index=True)
                
                st.markdown(f"**Nilai Sekarang Anuitas Due Sisa (ä_{usia + tahun_ke}:{masa_pertanggungan - tahun_ke}|):**")
                
                df_anuitas = pd.DataFrame(detail_anuitas_sisa)
                df_anuitas["ₖpₓ"] = df_anuitas["ₖpₓ"].apply(lambda x: format_decimal(x, 6))
                df_anuitas["v^k"] = df_anuitas["v^k"].apply(lambda x: format_decimal(x, 6))
                df_anuitas["Kontribusi Anuitas"] = df_anuitas["Kontribusi Anuitas"].apply(lambda x: format_decimal(x, 6))
                
                st.dataframe(df_anuitas, use_container_width=True, hide_index=True)
        
        # Detail rumus
        with st.expander("📐 Detail Rumus Perhitungan"):
            # Hitung nilai untuk ditampilkan
            nilai_manfaat_sisa = sum(d["Kontribusi Manfaat"] for d in detail_manfaat_sisa) if detail_manfaat_sisa else 0
            nilai_anuitas_sisa = sum(d["Kontribusi Anuitas"] for d in detail_anuitas_sisa) if detail_anuitas_sisa else 0
            
            st.markdown(f"""
            ### Parameter:
            | Parameter | Nilai |
            |-----------|-------|
            | Usia tertanggung (x) | {usia} tahun |
            | Masa pertanggungan (n) | {masa_pertanggungan} tahun |
            | Tahun evaluasi (t) | {tahun_ke} tahun |
            | Sisa masa pertanggungan (n-t) | {masa_pertanggungan - tahun_ke} tahun |
            | Suku bunga (i) | {suku_bunga}% ({i:.4f}) |
            | Uang pertanggungan (UP) | {format_rupiah(uang_pertanggungan)} |
            | Premi tahunan (P) | {format_rupiah(premi_tahunan)} |
            """)
            
            st.markdown("### Rumus Cadangan Prospektif:")
            st.latex(r"{}_t V = A_{x+t:\overline{n-t}|}^1 - P \cdot \ddot{a}_{x+t:\overline{n-t}|}")
            
            st.markdown(f"""
            Dimana:
            - A_{usia + tahun_ke}:{masa_pertanggungan - tahun_ke}|^1 = {format_rupiah(nilai_manfaat_sisa)}
            - ä_{usia + tahun_ke}:{masa_pertanggungan - tahun_ke}| = {nilai_anuitas_sisa:.6f} (nilai anuitas)
            - P = {format_rupiah(premi_tahunan)}
            """)
            
            st.markdown("### Rumus Cadangan Retrospektif:")
            st.latex(r"{}_t V = \frac{P \cdot \ddot{a}_{x:\overline{t}|} - A_{x:\overline{t}|}^1}{{}_t p_x}")
            
            # Hitung tpx
            tpx = probability_live_t_years(df, usia, tahun_ke)
            if tpx is not None:
                st.markdown(f"""
                Dimana:
                - ä_{usia}:{tahun_ke}| = Nilai sekarang anuitas due {tahun_ke} tahun
                - A_{usia}:{tahun_ke}|^1 = Nilai sekarang manfaat berjangka {tahun_ke} tahun
                - {tahun_ke}p_{usia} = {format_decimal(tpx, 6)} ({format_percent(tpx)})
                """)
        
        # Grafik perkembangan cadangan
        st.subheader("📊 Visualisasi Perkembangan Cadangan")
        
        # Hitung cadangan untuk setiap tahun
        tahun_list = list(range(0, masa_pertanggungan + 1))
        prospektif_list = []
        retrospektif_list = []
        
        for t in tahun_list:
            pros, _, _ = hitung_cadangan_prospektif(df, usia, masa_pertanggungan, t, i, uang_pertanggungan, premi_tahunan)
            ret = hitung_cadangan_retrospektif(df, usia, masa_pertanggungan, t, i, uang_pertanggungan, premi_tahunan)
            prospektif_list.append(pros if pros is not None else 0)
            retrospektif_list.append(ret if ret is not None else 0)
        
        fig, ax = plt.subplots(figsize=(12, 5))
        
        ax.plot(tahun_list, prospektif_list, 'b-o', label='Cadangan Prospektif', linewidth=2, markersize=6, markerfacecolor='blue')
        ax.plot(tahun_list, retrospektif_list, 'r--s', label='Cadangan Retrospektif', linewidth=2, markersize=6, markerfacecolor='red')
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        # Tandai tahun evaluasi
        ax.axvline(x=tahun_ke, color='green', linestyle=':', alpha=0.7, linewidth=2, label=f'Tahun Evaluasi (t={tahun_ke})')
        
        ax.set_xlabel('Tahun ke-', fontsize=12)
        ax.set_ylabel('Cadangan (Rp)', fontsize=12)
        ax.set_title(f'Perkembangan Cadangan Premi (Usia {usia}, {masa_pertanggungan} tahun)', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Format sumbu Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_rupiah_axis))
        
        # Tambahkan nilai pada titik tahun evaluasi
        ax.plot(tahun_ke, cadangan_prospektif, 'go', markersize=10, label='Nilai Cadangan')
        ax.annotate(f'{format_rupiah(cadangan_prospektif)}', 
                   xy=(tahun_ke, cadangan_prospektif),
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # Tabel ringkasan cadangan per tahun
        with st.expander("📊 Tabel Ringkasan Cadangan per Tahun", expanded=False):
            df_cadangan = pd.DataFrame({
                "Tahun ke-": tahun_list,
                "Cadangan Prospektif": [format_rupiah(x) for x in prospektif_list],
                "Cadangan Retrospektif": [format_rupiah(x) for x in retrospektif_list],
                "Selisih": [format_rupiah(abs(p - r)) for p, r in zip(prospektif_list, retrospektif_list)]
            })
            st.dataframe(df_cadangan, use_container_width=True, hide_index=True)
        
        # Interpretasi hasil
        st.divider()
        st.subheader("📖 Interpretasi Hasil")
        
        if cadangan_prospektif > 0:
            st.info(f"""
            💡 **Interpretasi Cadangan Positif (Rp {format_rupiah(cadangan_prospektif)}):**
            
            Pada tahun ke-{tahun_ke}, perusahaan asuransi harus menyisihkan dana sebesar 
            **{format_rupiah(cadangan_prospektif)}** untuk memastikan kewajiban pembayaran klaim di masa depan.
            
            Cadangan positif menunjukkan bahwa nilai sekarang manfaat sisa **LEBIH BESAR** dari nilai sekarang premi sisa,
            sehingga perusahaan perlu menyediakan dana tambahan.
            """)
        elif cadangan_prospektif < 0:
            st.warning(f"""
            ⚠️ **Interpretasi Cadangan Negatif (Rp {format_rupiah(cadangan_prospektif)}):**
            
            Cadangan negatif menunjukkan bahwa premi yang dibayarkan **LEBIH BESAR** dari nilai manfaat saat ini.
            Ini bisa terjadi jika:
            - Premi yang dibayarkan terlalu tinggi
            - Tingkat bunga teknis yang digunakan rendah
            - Probabilitas kematian lebih rendah dari yang diasumsikan
            """)
        else:
            st.info("""
            ℹ️ **Interpretasi Cadangan Nol:**
            
            Cadangan nol menunjukkan bahwa nilai sekarang manfaat sisa **SAMA** dengan nilai sekarang premi sisa,
            atau berada di awal masa pertanggungan (t=0).
            """)
        
        # Catatan
        st.caption("📌 **Catatan:** Perhitungan menggunakan premi bersih (net premium) dan mengasumsikan pembayaran premi dilakukan di awal tahun (annuity due).")