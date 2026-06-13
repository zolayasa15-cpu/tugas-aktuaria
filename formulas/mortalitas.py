# formulas/mortalitas.py
# Modul tabel mortalitas dan probabilitas hidup/mati - Standar Aktuaria

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from utils.helper import (
    validate_age,
    validate_period,
    validate_age_plus_term,
    validate_and_display,
    get_lx,
    get_qx,
    get_px,
    probability_live_t_years,
    format_decimal,
    format_percent
)

def tampilkan_mortalitas(df):
    """Menampilkan halaman tabel mortalitas"""
    st.header("📊 Tabel Mortalitas & Probabilitas Hidup/Mati")
    
    # Informasi awal
    st.markdown("""
    <div style='background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
    <b>📖 Tentang Tabel Mortalitas:</b><br>
    Tabel mortalitas adalah tabel aktuaria yang menunjukkan tingkat kematian pada setiap usia. 
    Digunakan dalam perhitungan asuransi jiwa, dana pensiun, dan anuitas.
    <br><br>
    <b>Notasi yang digunakan:</b><br>
    • lₓ = Jumlah orang yang hidup pada usia x<br>
    • dₓ = Jumlah kematian antara usia x dan x+1<br>
    • qₓ = Probabilitas kematian pada usia x (dₓ/lₓ)<br>
    • pₓ = Probabilitas hidup dari usia x ke x+1 (1 - qₓ)<br>
    • ₜpₓ = Probabilitas hidup dari usia x ke x+t<br>
    • ₜqₓ = Probabilitas mati dalam t tahun<br>
    • ₜ|ₖqₓ = Probabilitas hidup t tahun, kemudian mati dalam k tahun berikutnya
    </div>
    """, unsafe_allow_html=True)
    
    # Cek apakah data tersedia
    if df is None:
        st.error("❌ Tabel mortalitas tidak tersedia. Periksa file data/tabel_mortalitas.csv")
        return
    
    # Layout utama
    tab1, tab2, tab3 = st.tabs(["🎯 Kalkulator Probabilitas", "📈 Visualisasi Grafik", "📄 Tabel Mortalitas"])
    
    with tab1:
        st.subheader("🔍 Kalkulator Probabilitas Hidup & Mati")
        
        col1, col2 = st.columns(2)
        
        with col1:
            usia = st.number_input(
                "**Usia Saat Ini (x) - tahun**",
                min_value=0,
                max_value=100,
                value=30,
                step=1,
                help="Usia tertanggung dalam tahun"
            )
            
            periode = st.number_input(
                "**Periode (t) - tahun**",
                min_value=0,
                max_value=70,
                value=5,
                step=1,
                help="Jangka waktu dalam tahun"
            )
            
            periode_2 = st.number_input(
                "**Periode Kedua (k) - tahun**",
                min_value=0,
                max_value=70,
                value=5,
                step=1,
                help="Untuk perhitungan deferred mortality"
            )
        
        with col2:
            st.info("📌 **Pilih jenis probabilitas yang ingin dihitung:**")
            jenis_prob = st.radio(
                "Jenis Perhitungan:",
                ["ₜpₓ (Hidup t tahun)", 
                 "ₜqₓ (Mati dalam t tahun)",
                 "qₓ (Mati 1 tahun)",
                 "ₜ|ₖqₓ (Hidup t tahun, mati dalam k tahun berikutnya)"],
                help="""
                - ₜpₓ: Probabilitas bertahan hidup hingga usia x+t
                - ₜqₓ: Probabilitas meninggal dalam t tahun ke depan
                - qₓ: Probabilitas meninggal dalam 1 tahun
                - ₜ|ₖqₓ: Probabilitas hidup t tahun, kemudian meninggal dalam k tahun
                """
            )
            
            hitung = st.button("🔢 HITUNG PROBABILITAS", type="primary", use_container_width=True)
        
        if hitung:
            errors = []
            
            valid1, msg1 = validate_age(usia)
            if not valid1:
                errors.append(msg1)
            
            valid2, msg2 = validate_period(periode, 0)
            if not valid2:
                errors.append(msg2)
            
            valid3, msg3 = validate_age_plus_term(usia, periode)
            if not valid3:
                errors.append(msg3)
            
            if not validate_and_display(errors):
                return
            
            # Ambil data dasar
            qx = get_qx(df, usia)
            px = get_px(df, usia)
            tpx = probability_live_t_years(df, usia, periode)
            
            if qx is None:
                st.error(f"❌ Data untuk usia {usia} tidak ditemukan dalam tabel")
                return
            
            # Tampilkan hasil
            st.divider()
            st.subheader("📊 Hasil Perhitungan Probabilitas")
            
            # Card hasil utama
            col_result1, col_result2, col_result3 = st.columns(3)
            
            with col_result1:
                st.metric(
                    "📌 pₓ", 
                    format_decimal(px, 6),
                    help=f"Probabilitas hidup dari usia {usia} ke {usia+1}"
                )
                st.caption(f"Hidup 1 tahun: {format_percent(px)}")
            
            with col_result2:
                st.metric(
                    "⚠️ qₓ", 
                    format_decimal(qx, 6),
                    help=f"Probabilitas meninggal pada usia {usia}"
                )
                st.caption(f"Mati 1 tahun: {format_percent(qx)}")
            
            with col_result3:
                if tpx is not None:
                    st.metric(
                        f"ₜpₓ (t={periode})", 
                        format_decimal(tpx, 6),
                        help=f"Probabilitas hidup dari usia {usia} ke {usia+periode}"
                    )
                    st.caption(f"Hidup {periode} tahun: {format_percent(tpx)}")
                else:
                    st.warning("Data tidak tersedia untuk periode ini")
            
            # Perhitungan spesifik berdasarkan pilihan
            st.divider()
            
            if jenis_prob == "ₜpₓ (Hidup t tahun)":
                if tpx is not None:
                    st.success(f"### ✅ Probabilitas hidup {periode} tahun ke depan")
                    st.markdown(f"""
                    <div style='background-color: #d4edda; padding: 20px; border-radius: 10px;'>
                    <h3 style='text-align: center; color: #155724;'>{format_percent(tpx)}</h3>
                    <p style='text-align: center; margin: 0;'>atau 1 : {1/tpx:.2f} orang</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Interpretasi
                    st.info(f"""
                    📖 **Interpretasi:**  
                    Dari 1.000 orang yang berusia {usia} tahun, diperkirakan sekitar **{int(tpx * 1000):,} orang** (atau {format_percent(tpx)}) 
                    akan masih hidup pada usia {usia + periode} tahun.
                    """)
                else:
                    st.error(f"Data tidak tersedia untuk usia {usia} + {periode} = {usia + periode}")
            
            elif jenis_prob == "ₜqₓ (Mati dalam t tahun)":
                if tpx is not None:
                    tqx = 1 - tpx
                    st.warning(f"### ⚠️ Probabilitas mati dalam {periode} tahun ke depan")
                    st.markdown(f"""
                    <div style='background-color: #f8d7da; padding: 20px; border-radius: 10px;'>
                    <h3 style='text-align: center; color: #721c24;'>{format_percent(tqx)}</h3>
                    <p style='text-align: center; margin: 0;'>atau 1 : {1/tqx:.2f} orang</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.info(f"""
                    📖 **Interpretasi:**  
                    Dari 1.000 orang yang berusia {usia} tahun, diperkirakan sekitar **{int(tqx * 1000):,} orang** (atau {format_percent(tqx)}) 
                    akan meninggal dalam {periode} tahun ke depan.
                    """)
                else:
                    st.error(f"Data tidak tersedia untuk usia {usia} + {periode} = {usia + periode}")
            
            elif jenis_prob == "qₓ (Mati 1 tahun)":
                st.warning(f"### ⚠️ Probabilitas mati dalam 1 tahun")
                st.markdown(f"""
                <div style='background-color: #f8d7da; padding: 20px; border-radius: 10px;'>
                <h3 style='text-align: center; color: #721c24;'>{format_percent(qx)}</h3>
                <p style='text-align: center; margin: 0;'>atau 1 : {1/qx:.2f} orang</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.info(f"""
                📖 **Interpretasi:**  
                Dari 1.000 orang yang berusia {usia} tahun, diperkirakan sekitar **{int(qx * 1000):,} orang** akan meninggal 
                sebelum mencapai usia {usia + 1} tahun.
                """)
            
            else:  # ₜ|ₖqₓ
                if tpx is not None:
                    # Hitung probabilitas hidup t tahun kemudian mati dalam k tahun
                    age_t = usia + periode
                    qx_t = get_qx(df, age_t)
                    
                    if qx_t is not None and periode_2 > 0:
                        # Sederhanakan: ₜ|ₖqₓ = ₜpₓ × ₖq_{x+t}
                        # Untuk k tahun, perlu dihitung probabilitas mati dalam k tahun
                        prob_death_k_years = 1 - probability_live_t_years(df, age_t, periode_2)
                        deferred_prob = tpx * prob_death_k_years if prob_death_k_years is not None else None
                        
                        if deferred_prob is not None:
                            st.info(f"### 📊 Probabilitas: Hidup {periode} tahun, kemudian mati dalam {periode_2} tahun berikutnya")
                            st.markdown(f"""
                            <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px;'>
                            <h3 style='text-align: center; color: #856404;'>{format_percent(deferred_prob)}</h3>
                            <p style='text-align: center; margin: 0;'>ₜ|ₖqₓ = {format_percent(tpx)} × {format_percent(prob_death_k_years)}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.info(f"""
                            📖 **Interpretasi:**  
                            Probabilitas seseorang berusia {usia} tahun akan hidup selama {periode} tahun 
                            (mencapai usia {age_t} tahun) dan kemudian meninggal dalam {periode_2} tahun berikutnya 
                            (antara usia {age_t} dan {age_t + periode_2}) adalah **{format_percent(deferred_prob)}**.
                            """)
                        else:
                            st.error("Data tidak tersedia untuk perhitungan deferred mortality")
                    else:
                        st.error("Periode k harus > 0 dan data tersedia")
                else:
                    st.error("Data tidak tersedia untuk periode pertama")
        
        # Tabel ringkasan untuk berbagai usia
        with st.expander("📊 Tabel Ringkasan Probabilitas untuk Berbagai Usia"):
            usia_range = list(range(0, 91, 10))
            data_ringkasan = []
            
            for u in usia_range:
                qx_val = get_qx(df, u)
                px_val = get_px(df, u)
                tpx_10 = probability_live_t_years(df, u, 10)
                tpx_20 = probability_live_t_years(df, u, 20)
                
                if qx_val is not None:
                    data_ringkasan.append({
                        "Usia": u,
                        "qₓ (mati 1 tahun)": f"{format_percent(qx_val)}",
                        "pₓ (hidup 1 tahun)": f"{format_percent(px_val)}",
                        "₁₀pₓ (hidup 10 tahun)": f"{format_percent(tpx_10) if tpx_10 else 'N/A'}",
                        "₂₀pₓ (hidup 20 tahun)": f"{format_percent(tpx_20) if tpx_20 else 'N/A'}"
                    })
            
            df_ringkasan = pd.DataFrame(data_ringkasan)
            st.dataframe(df_ringkasan, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("📈 Visualisasi Grafik Mortalitas")
        
        # Filter usia untuk grafik
        usia_min_grafik = st.slider(
            "Rentang Usia Minimal (tahun):",
            min_value=0,
            max_value=90,
            value=0,
            step=5
        )
        
        usia_max_grafik = st.slider(
            "Rentang Usia Maksimal (tahun):",
            min_value=usia_min_grafik + 1,
            max_value=100,
            value=min(80, 100),
            step=5
        )
        
        # Siapkan data untuk grafik
        df_filtered = df[(df["x"] >= usia_min_grafik) & (df["x"] <= usia_max_grafik)].copy()
        
        if not df_filtered.empty:
            # Grafik 1: Kurva Kehidupan (lx)
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # Plot lx
            axes[0, 0].plot(df_filtered["x"], df_filtered["lx"], 'b-', linewidth=2, marker='o', markersize=4)
            axes[0, 0].set_xlabel('Usia (tahun)', fontsize=10)
            axes[0, 0].set_ylabel('Jumlah yang Hidup (lₓ)', fontsize=10)
            axes[0, 0].set_title('Kurva Kehidupan (lₓ)', fontsize=12, fontweight='bold')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].fill_between(df_filtered["x"], df_filtered["lx"], alpha=0.3)
            
            # Plot qx
            axes[0, 1].plot(df_filtered["x"], df_filtered["qx"], 'r-', linewidth=2, marker='s', markersize=4)
            axes[0, 1].set_xlabel('Usia (tahun)', fontsize=10)
            axes[0, 1].set_ylabel('Probabilitas Kematian (qₓ)', fontsize=10)
            axes[0, 1].set_title('Tingkat Kematian per Usia (qₓ)', fontsize=12, fontweight='bold')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].set_ylim([0, max(df_filtered["qx"]) * 1.1])
            
            # Plot dx
            axes[1, 0].bar(df_filtered["x"], df_filtered["dx"], width=0.8, color='orange', alpha=0.7)
            axes[1, 0].set_xlabel('Usia (tahun)', fontsize=10)
            axes[1, 0].set_ylabel('Jumlah Kematian (dₓ)', fontsize=10)
            axes[1, 0].set_title('Jumlah Kematian per Usia (dₓ)', fontsize=12, fontweight='bold')
            axes[1, 0].grid(True, alpha=0.3, axis='y')
            
            # Plot perbandingan px dan qx
            axes[1, 1].plot(df_filtered["x"], df_filtered["px"], 'g-', linewidth=2, marker='^', markersize=4, label='pₓ (Prob. Hidup)')
            axes[1, 1].plot(df_filtered["x"], df_filtered["qx"], 'r-', linewidth=2, marker='v', markersize=4, label='qₓ (Prob. Mati)')
            axes[1, 1].set_xlabel('Usia (tahun)', fontsize=10)
            axes[1, 1].set_ylabel('Probabilitas', fontsize=10)
            axes[1, 1].set_title('Perbandingan pₓ dan qₓ', fontsize=12, fontweight='bold')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].set_ylim([0, 1])
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Grafik Harapan Hidup
            st.subheader("📊 Harapan Hidup (Life Expectancy)")
            
            # Hitung harapan hidup sederhana (eₓ)
            df_life_exp = df.copy()
            lx_reversed = df_life_exp["lx"].values[::-1]
            cumsum_lx = np.cumsum(lx_reversed)[::-1]
            df_life_exp["eₓ"] = cumsum_lx / df_life_exp["lx"]
            df_life_exp_filtered = df_life_exp[(df_life_exp["x"] >= usia_min_grafik) & (df_life_exp["x"] <= usia_max_grafik)]
            
            fig2, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df_life_exp_filtered["x"], df_life_exp_filtered["eₓ"], 'purple', linewidth=2, marker='o', markersize=4)
            ax.set_xlabel('Usia (tahun)', fontsize=11)
            ax.set_ylabel('Harapan Hidup (tahun)', fontsize=11)
            ax.set_title('Harapan Hidup (Life Expectancy) per Usia', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.fill_between(df_life_exp_filtered["x"], df_life_exp_filtered["eₓ"], alpha=0.3)
            st.pyplot(fig2)
            
        else:
            st.warning("Tidak ada data dalam rentang usia yang dipilih")
    
    with tab3:
        st.subheader("📄 Tabel Mortalitas Lengkap")
        
        # Filter untuk tabel
        col_filter1, col_filter2 = st.columns(2)
        
        with col_filter1:
            usia_min = st.number_input(
                "Tampilkan dari usia:", 
                min_value=0, 
                max_value=100, 
                value=0,
                key="min_age"
            )
        
        with col_filter2:
            usia_max = st.number_input(
                "Sampai usia:", 
                min_value=0, 
                max_value=100, 
                value=30,
                key="max_age"
            )
        
        if usia_min <= usia_max:
            df_filtered = df[(df["x"] >= usia_min) & (df["x"] <= usia_max)].copy()
            
            # Format kolom persentase
            df_display = df_filtered.copy()
            df_display["qx"] = df_display["qx"].apply(lambda x: f"{x:.6f} ({x*100:.4f}%)")
            df_display["px"] = df_display["px"].apply(lambda x: f"{x:.6f} ({x*100:.4f}%)")
            df_display["lx"] = df_display["lx"].apply(lambda x: f"{int(x):,}")
            df_display["dx"] = df_display["dx"].apply(lambda x: f"{int(x):,}")
            
            st.dataframe(
                df_display[["x", "lx", "dx", "qx", "px"]],
                use_container_width=True,
                height=500,
                column_config={
                    "x": "Usia (x)",
                    "lx": "Jumlah Hidup (lₓ)",
                    "dx": "Jumlah Kematian (dₓ)",
                    "qx": "Prob. Kematian (qₓ)",
                    "px": "Prob. Hidup (pₓ)"
                }
            )
            
            # Statistik ringkasan
            st.divider()
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.metric("📊 Total Usia", f"{len(df)} tahun")
            with col_stat2:
                st.metric("👥 Populasi Awal", f"{int(df['lx'].iloc[0]):,}")
            with col_stat3:
                max_age = df[df['lx'] > 0]['x'].max()
                st.metric("🎯 Usia Maksimal", f"{max_age} tahun")
            with col_stat4:
                avg_qx = df['qx'].mean()
                st.metric("📈 Rata-rata qₓ", f"{avg_qx:.4f}")
        else:
            st.warning("Usia minimal harus lebih kecil dari usia maksimal")
        
        with st.expander("ℹ️ Keterangan Kolom & Notasi"):
            st.markdown("""
            ### Kolom dalam Tabel Mortalitas:
            
            | Kolom | Notasi | Keterangan |
            |-------|--------|-------------|
            | **x** | x | Usia dalam tahun |
            | **lx** | lₓ | Jumlah orang yang hidup pada usia x (dari total populasi awal) |
            | **dx** | dₓ | Jumlah kematian antara usia x dan x+1 (dₓ = lₓ - lₓ₊₁) |
            | **qx** | qₓ | Probabilitas kematian pada usia x (qₓ = dₓ / lₓ) |
            | **px** | pₓ | Probabilitas hidup dari usia x ke x+1 (pₓ = 1 - qₓ) |
            
            ### Notasi Probabilitas Lainnya:
            
            - **ₜpₓ** = Probabilitas seseorang berusia x akan hidup t tahun (mencapai usia x+t)
            - **ₜqₓ** = Probabilitas seseorang berusia x akan meninggal dalam t tahun
            - **ₜ|ₖqₓ** = Probabilitas seseorang berusia x akan hidup t tahun, kemudian meninggal dalam k tahun berikutnya
            - **eₓ** = Harapan hidup (rata-rata tahun yang akan dijalani) seseorang berusia x
            
            ### Rumus Dasar:
            pₓ = 1 - qₓ
ₜpₓ = pₓ × pₓ₊₁ × pₓ₊₂ × ... × pₓ₊ₜ₋₁
ₜqₓ = 1 - ₜpₓ
ₜ|ₖqₓ = ₜpₓ × ₖqₓ₊ₜ
""")