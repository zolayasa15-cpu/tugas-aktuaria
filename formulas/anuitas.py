# formulas/anuitas.py
# Modul perhitungan anuitas (Immediate, Due, Deferred) - Standar Aktuaria

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils.helper import (
    validate_positive_number,
    validate_non_negative,
    validate_period,
    validate_and_display,
    format_rupiah,
    format_decimal
)

def annuity_immediate_pv(i, n):
    """PV anuitas immediate: a_n = (1 - v^n) / i"""
    if i == 0:
        return n
    v = 1 / (1 + i)
    return (1 - v**n) / i

def annuity_immediate_fv(i, n):
    """FV anuitas immediate: s_n = ((1+i)^n - 1) / i"""
    if i == 0:
        return n
    return ((1 + i)**n - 1) / i

def annuity_due_pv(i, n):
    """PV anuitas due: ä_n = (1 - v^n) / d, dimana d = i/(1+i)"""
    if i == 0:
        return n
    d = i / (1 + i)
    v = 1 / (1 + i)
    return (1 - v**n) / d

def annuity_due_fv(i, n):
    """FV anuitas due: s̈_n = ((1+i)^n - 1) / d"""
    if i == 0:
        return n
    d = i / (1 + i)
    return ((1 + i)**n - 1) / d

def deferred_annuity_pv(i, n, k):
    """PV anuitas deferred: k|a_n = v^k * a_n"""
    if i == 0:
        return n
    v = 1 / (1 + i)
    return v**k * annuity_immediate_pv(i, n)

def perpetual_annuity_pv(pmt, i):
    """PV anuitas perpetual: a_infinity = 1/i"""
    if i == 0:
        return float('inf')
    return pmt / i

def buat_tabel_amortisasi(pmt, i, n, jenis="Immediate"):
    """Membuat tabel amortisasi anuitas"""
    tabel = []
    saldo = 0
    
    # Hitung PV untuk menentukan nilai pinjaman awal
    if jenis == "Immediate":
        pv_total = pmt * annuity_immediate_pv(i, n)
    else:  # Due
        pv_total = pmt * annuity_due_pv(i, n)
    
    saldo_pinjaman = pv_total
    
    for t in range(1, n + 1):
        if jenis == "Immediate":
            bunga = saldo_pinjaman * i
            angsuran_pokok = pmt - bunga
            saldo_pinjaman -= angsuran_pokok
        else:  # Due: pembayaran di awal periode
            if t == 1:
                angsuran_pokok = pmt
                bunga = 0
                saldo_pinjaman -= angsuran_pokok
            else:
                bunga = saldo_pinjaman * i
                angsuran_pokok = pmt - bunga
                saldo_pinjaman -= angsuran_pokok
        
        tabel.append({
            "Periode": t,
            "Pembayaran": pmt,
            "Bunga": max(0, bunga),
            "Angsuran Pokok": max(0, angsuran_pokok),
            "Sisa Pinjaman": max(0, saldo_pinjaman)
        })
    
    return tabel, pv_total

def tampilkan_anuitas():
    """Menampilkan halaman perhitungan anuitas"""
    st.header("📅 Perhitungan Anuitas (Standar Aktuaria)")
    
    st.markdown("""
    <div style='background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
    <b>📖 Tentang Anuitas:</b><br>
    Anuitas adalah rangkaian pembayaran periodik dalam jumlah yang sama. 
    Digunakan dalam perhitungan pinjaman KPR, dana pensiun, asuransi jiwa, dan investasi jangka panjang.
    </div>
    """, unsafe_allow_html=True)
    
    # Form input parameter
    with st.form(key="form_anuitas"):
        col1, col2 = st.columns(2)
        
        with col1:
            jenis_anuitas = st.selectbox(
                "**Jenis Anuitas**",
                ["Annuity Immediate", "Annuity Due", "Deferred Annuity", "Perpetual Annuity"],
                help="""
                - Annuity Immediate: Pembayaran di AKHIR periode
                - Annuity Due: Pembayaran di AWAL periode  
                - Deferred Annuity: Pembayaran ditunda beberapa periode
                - Perpetual Annuity: Anuitas abadi (tanpa batas waktu)
                """
            )
            
            pmt = st.number_input(
                "**Pembayaran Periodik (PMT)**",
                min_value=0.0,
                value=1_000_000.0,
                step=500_000.0,
                format="%.0f",
                help="Jumlah pembayaran setiap periode"
            )
            
            suku_bunga = st.number_input(
                "**Suku Bunga (% per periode)**",
                min_value=0.0,
                value=5.0,
                step=0.5,
                format="%.2f",
                help="Suku bunga per periode (misal: 5% per bulan)"
            )
            
            if jenis_anuitas != "Perpetual Annuity":
                periode = st.number_input(
                    "**Jumlah Periode (n)**",
                    min_value=1,
                    max_value=100,
                    value=10,
                    step=1,
                    help="Lama pembayaran anuitas"
                )
            else:
                periode = 0
                st.info("ℹ️ Anuitas perpetual berlangsung selamanya (n → ∞)")
        
        with col2:
            masa_tunda = 0
            if jenis_anuitas == "Deferred Annuity":
                masa_tunda = st.number_input(
                    "**Masa Tunda (k periode)**",
                    min_value=0,
                    max_value=50,
                    value=3,
                    step=1,
                    help="Jumlah periode penundaan sebelum pembayaran dimulai"
                )
            
            # Pilihan output
            st.markdown("**📊 Pilihan Output:**")
            tampilkan_tabel = st.checkbox("Tampilkan Tabel Amortisasi", value=True)
            tampilkan_grafik = st.checkbox("Tampilkan Grafik", value=True)
        
        submit = st.form_submit_button("🔢 HITUNG ANUITAS", type="primary", use_container_width=True)
    
    if submit:
        # Validasi input
        errors = []
        i = suku_bunga / 100
        
        valid1, msg1 = validate_positive_number(pmt, "Pembayaran periodik")
        if not valid1:
            errors.append(msg1)
        
        valid2, msg2 = validate_non_negative(i, "Suku bunga")
        if not valid2:
            errors.append(msg2)
        
        if jenis_anuitas != "Perpetual Annuity":
            valid3, msg3 = validate_period(periode, 1)
            if not valid3:
                errors.append(msg3)
        
        if not validate_and_display(errors):
            return
        
        # Container hasil
        st.divider()
        st.subheader("📊 HASIL PERHITUNGAN ANUITAS")
        
        # Hitung berdasarkan jenis anuitas
        if jenis_anuitas == "Annuity Immediate":
            if i == 0:
                pv_factor = periode
                fv_factor = periode
                rumus_pv = "n"
                rumus_fv = "n"
            else:
                pv_factor = annuity_immediate_pv(i, periode)
                fv_factor = annuity_immediate_fv(i, periode)
                rumus_pv = f"(1 - v^{periode}) / i"
                rumus_fv = f"((1+i)^{periode} - 1) / i"
            
            pv = pmt * pv_factor
            fv = pmt * fv_factor
            
            # Tampilkan hasil utama
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💵 Nilai Sekarang (PV)", format_rupiah(pv), 
                         help=f"PV = PMT × a_n = {format_rupiah(pmt)} × {pv_factor:.6f}")
            with col2:
                st.metric("📈 Nilai Akhir (FV)", format_rupiah(fv),
                         help=f"FV = PMT × s_n = {format_rupiah(pmt)} × {fv_factor:.6f}")
            with col3:
                st.metric("💰 Total Pembayaran", format_rupiah(pmt * periode),
                         help=f"PMT × n = {format_rupiah(pmt)} × {periode}")
            
            # Tabel amortisasi
            if tampilkan_tabel:
                st.subheader("📋 Tabel Amortisasi Pinjaman")
                tabel, pv_total = buat_tabel_amortisasi(pmt, i, periode, "Immediate")
                df = pd.DataFrame(tabel)
                
                # Format dataframe
                df["Pembayaran"] = df["Pembayaran"].apply(format_rupiah)
                df["Bunga"] = df["Bunga"].apply(format_rupiah)
                df["Angsuran Pokok"] = df["Angsuran Pokok"].apply(format_rupiah)
                df["Sisa Pinjaman"] = df["Sisa Pinjaman"].apply(format_rupiah)
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Ringkasan tambahan
                total_bunga = sum(row["Bunga"] for row in tabel if not isinstance(row["Bunga"], str))
                st.info(f"📊 **Total bunga yang dibayar:** {format_rupiah(total_bunga)}")
                st.info(f"🏦 **Total pembayaran keseluruhan:** {format_rupiah(pmt * periode)}")
        
        elif jenis_anuitas == "Annuity Due":
            if i == 0:
                pv_factor = periode
                fv_factor = periode
                rumus_pv = "n"
                rumus_fv = "n"
            else:
                pv_factor = annuity_due_pv(i, periode)
                fv_factor = annuity_due_fv(i, periode)
                rumus_pv = f"(1 - v^{periode}) / d, d = i/(1+i)"
                rumus_fv = f"((1+i)^{periode} - 1) / d"
            
            pv = pmt * pv_factor
            fv = pmt * fv_factor
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💵 Nilai Sekarang (PV)", format_rupiah(pv),
                         help=f"PV = PMT × ä_n = {format_rupiah(pmt)} × {pv_factor:.6f}")
            with col2:
                st.metric("📈 Nilai Akhir (FV)", format_rupiah(fv),
                         help=f"FV = PMT × s̈_n = {format_rupiah(pmt)} × {fv_factor:.6f}")
            with col3:
                st.metric("💰 Total Pembayaran", format_rupiah(pmt * periode))
            
            if tampilkan_tabel:
                st.subheader("📋 Tabel Amortisasi Pinjaman")
                tabel, pv_total = buat_tabel_amortisasi(pmt, i, periode, "Due")
                df = pd.DataFrame(tabel)
                
                df["Pembayaran"] = df["Pembayaran"].apply(format_rupiah)
                df["Bunga"] = df["Bunga"].apply(format_rupiah)
                df["Angsuran Pokok"] = df["Angsuran Pokok"].apply(format_rupiah)
                df["Sisa Pinjaman"] = df["Sisa Pinjaman"].apply(format_rupiah)
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                total_bunga = sum(row["Bunga"] for row in tabel if not isinstance(row["Bunga"], str))
                st.info(f"📊 **Total bunga yang dibayar:** {format_rupiah(total_bunga)}")
        
        elif jenis_anuitas == "Deferred Annuity":
            if i == 0:
                pv_factor = periode
            else:
                pv_factor = deferred_annuity_pv(i, periode, masa_tunda)
            
            pv = pmt * pv_factor
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("💵 Nilai Sekarang (PV)", format_rupiah(pv),
                         help=f"PV = PMT × {masa_tunda}|a_{periode} = {format_rupiah(pmt)} × {pv_factor:.6f}")
            with col2:
                st.metric("⏰ Masa Tunda", f"{masa_tunda} periode",
                         help="Pembayaran dimulai setelah masa tunda")
            
            st.info(f"📌 **Pembayaran pertama** akan dilakukan pada **periode ke-{masa_tunda + 1}**")
            
        else:  # Perpetual Annuity
            if i == 0:
                pv = float('inf')
                st.warning("⚠️ Dengan suku bunga 0%, anuitas perpetual memiliki nilai tak terhingga")
            else:
                pv = perpetual_annuity_pv(pmt, i)
                
                st.metric("💵 Nilai Sekarang (PV) - Anuitas Abadi", format_rupiah(pv),
                         help=f"PV = PMT / i = {format_rupiah(pmt)} / {i:.4f}")
                
                st.info("🏛️ **Anuitas Perpetual** berlangsung selamanya (n → ∞)")
                st.markdown(f"""
                **Rumus:** PV = PMT / i
                - PMT = {format_rupiah(pmt)}
                - i = {i:.4f} ({suku_bunga}%)
                - PV = {format_rupiah(pv)}
                """)
        
        # Tampilkan detail rumus
        with st.expander("📐 Detail Rumus dan Perhitungan"):
            st.markdown(f"### Rumus {jenis_anuitas}")
            
            if jenis_anuitas == "Annuity Immediate":
                st.latex(r"a_{\overline{n}|} = \frac{1 - v^n}{i}, \quad v = \frac{1}{1+i}")
                st.latex(r"PV = PMT \times a_{\overline{n}|}")
                st.latex(r"FV = PMT \times s_{\overline{n}|}, \quad s_{\overline{n}|} = \frac{(1+i)^n - 1}{i}")
                
            elif jenis_anuitas == "Annuity Due":
                st.latex(r"\ddot{a}_{\overline{n}|} = \frac{1 - v^n}{d}, \quad d = \frac{i}{1+i}")
                st.latex(r"PV = PMT \times \ddot{a}_{\overline{n}|}")
                st.latex(r"FV = PMT \times \ddot{s}_{\overline{n}|}, \quad \ddot{s}_{\overline{n}|} = \frac{(1+i)^n - 1}{d}")
                
            elif jenis_anuitas == "Deferred Annuity":
                st.latex(r"_{k|}a_{\overline{n}|} = v^k \times a_{\overline{n}|}")
                st.latex(r"PV = PMT \times v^k \times a_{\overline{n}|}")
                
            else:  # Perpetual
                st.latex(r"a_{\overline{\infty}|} = \frac{1}{i}")
                st.latex(r"PV = \frac{PMT}{i}")
            
            st.markdown("### Parameter yang digunakan:")
            st.markdown(f"""
            - PMT (Pembayaran periodik) = {format_rupiah(pmt)}
            - i (Suku bunga) = {i:.6f} ({suku_bunga}%)
            - n (Jumlah periode) = {periode if periode > 0 else '∞'}
            """)
            
            if jenis_anuitas == "Deferred Annuity":
                st.markdown(f"- k (Masa tunda) = {masa_tunda} periode")
        
        # Grafik
        if tampilkan_grafik and jenis_anuitas != "Perpetual Annuity":
            st.subheader("📊 Visualisasi Pembayaran Anuitas")
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            
            # Grafik 1: Timeline pembayaran
            if jenis_anuitas == "Deferred Annuity":
                # Timeline dengan masa tunda
                timeline = list(range(1, periode + masa_tunda + 1))
                payments = [0] * masa_tunda + [pmt] * periode
                
                axes[0].bar(timeline, payments, width=0.6, color='steelblue', alpha=0.7)
                axes[0].axvline(x=masa_tunda + 0.5, color='red', linestyle='--', label=f'Masa tunda {masa_tunda} periode')
                axes[0].set_xlabel('Periode', fontsize=11)
                axes[0].set_ylabel('Pembayaran (Rp)', fontsize=11)
                axes[0].set_title(f'Timeline Pembayaran - {jenis_anuitas}', fontsize=12)
                axes[0].legend()
            else:
                timeline = list(range(1, periode + 1))
                axes[0].bar(timeline, [pmt] * periode, width=0.6, color='steelblue', alpha=0.7)
                axes[0].set_xlabel('Periode', fontsize=11)
                axes[0].set_ylabel('Pembayaran (Rp)', fontsize=11)
                axes[0].set_title(f'Timeline Pembayaran - {jenis_anuitas}', fontsize=12)
            
            axes[0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x/1e6:.0f}Jt'))
            axes[0].grid(True, alpha=0.3, axis='y')
            
            # Grafik 2: Pertumbuhan nilai
            if jenis_anuitas in ["Annuity Immediate", "Annuity Due"] and i > 0:
                periods = np.arange(0, periode + 1)
                fv_growth = pmt * annuity_immediate_fv(i, periods) if jenis_anuitas == "Annuity Immediate" else pmt * annuity_due_fv(i, periods)
                
                axes[1].plot(periods, fv_growth, 'b-', linewidth=2, marker='o', markersize=4)
                axes[1].set_xlabel('Periode', fontsize=11)
                axes[1].set_ylabel('Akumulasi Nilai (Rp)', fontsize=11)
                axes[1].set_title('Pertumbuhan Nilai Anuitas', fontsize=12)
                axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Rp {x/1e6:.0f}Jt'))
                axes[1].grid(True, alpha=0.3)
                axes[1].fill_between(periods, fv_growth, alpha=0.3)
            else:
                axes[1].text(0.5, 0.5, 'Grafik pertumbuhan\ntidak tersedia', 
                           ha='center', va='center', transform=axes[1].transAxes, fontsize=12)
                axes[1].set_title('Pertumbuhan Nilai Anuitas', fontsize=12)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # Catatan kaki
        st.caption("📌 **Catatan:** Perhitungan menggunakan standar aktuaria dengan faktor diskon v = 1/(1+i)")