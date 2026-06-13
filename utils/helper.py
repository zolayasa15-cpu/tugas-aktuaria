# utils/helper.py
# Fungsi utilitas untuk aplikasi kalkulator aktuaria

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# 1. FUNGSI VALIDASI INPUT
# ============================================

def validate_positive_number(value, field_name):
    """Validasi angka > 0"""
    if value <= 0:
        return False, f"{field_name} harus lebih besar dari 0"
    return True, ""

def validate_non_negative(value, field_name):
    """Validasi angka >= 0"""
    if value < 0:
        return False, f"{field_name} tidak boleh negatif"
    return True, ""

def validate_age(age):
    """Validasi usia 0-120"""
    if age < 0 or age > 120:
        return False, "Usia harus antara 0 dan 120 tahun"
    return True, ""

def validate_period(period, min_period=1):
    """Validasi periode minimal tertentu"""
    if period < min_period:
        return False, f"Periode harus minimal {min_period}"
    return True, ""

def validate_age_plus_term(age, term):
    """Validasi usia + periode tidak melebihi 120"""
    if age + term > 120:
        return False, f"Usia + periode tidak boleh melebihi 120 tahun (saat ini {age + term})"
    return True, ""

# ============================================
# 2. FUNGSI LOAD DATA TABEL MORTALITAS
# ============================================

@st.cache_data
def load_mortality_table(file_path="data/tabel_mortalitas.csv"):
    """Membaca file CSV tabel mortalitas"""
    path = Path(file_path)
    
    if not path.exists():
        st.error(f"File tidak ditemukan: {file_path}")
        return None
    
    try:
        df = pd.read_csv(file_path)
        
        required_cols = ["x", "lx", "qx"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Kolom tidak ditemukan: {missing_cols}")
            return None
        
        df = df.dropna(subset=["x", "lx"])
        df = df[df["x"] >= 0]
        
        if "px" not in df.columns:
            df["px"] = 1 - df["qx"]
        
        return df
        
    except Exception as e:
        st.error(f"Gagal membaca file: {str(e)}")
        return None

# ============================================
# 3. FUNGSI MORTALITAS DASAR
# ============================================

def get_lx(df, age):
    """Mendapatkan l_x untuk usia tertentu"""
    row = df[df["x"] == age]
    if row.empty:
        return None
    return row.iloc[0]["lx"]

def get_qx(df, age):
    """Mendapatkan q_x untuk usia tertentu"""
    row = df[df["x"] == age]
    if row.empty:
        return None
    return row.iloc[0]["qx"]

def get_px(df, age):
    """Mendapatkan p_x untuk usia tertentu"""
    row = df[df["x"] == age]
    if row.empty:
        return None
    return row.iloc[0].get("px", 1 - row.iloc[0]["qx"])

def probability_live_t_years(df, age, t):
    """Menghitung probabilitas hidup dari usia x selama t tahun (tpx)"""
    lx = get_lx(df, age)
    lx_plus_t = get_lx(df, age + t)
    
    if lx is None or lx_plus_t is None:
        return None
    
    if lx == 0:
        return 0
    
    return lx_plus_t / lx

# ============================================
# 4. FUNGSI BUNGA DAN DISKONTO
# ============================================

def v_factor(interest_rate):
    """Faktor diskonto v = 1 / (1 + i)"""
    return 1 / (1 + interest_rate)

def future_value(pv, i, n, compound=True):
    """Menghitung Future Value"""
    if compound:
        return pv * (1 + i) ** n
    else:
        return pv * (1 + i * n)

def present_value(fv, i, n, compound=True):
    """Menghitung Present Value"""
    if compound:
        return fv / (1 + i) ** n
    else:
        return fv / (1 + i * n)

# ============================================
# 5. FUNGSI ANUITAS
# ============================================

def annuity_immediate_pv(i, n):
    """Nilai sekarang anuitas immediate: a_n|i"""
    if i == 0:
        return n
    v = v_factor(i)
    return (1 - v ** n) / i

def annuity_due_pv(i, n):
    """Nilai sekarang anuitas due: a_n|i (dengan asumsi due)"""
    return annuity_immediate_pv(i, n) * (1 + i)

def deferred_annuity_pv(i, n, m):
    """Nilai sekarang anuitas ditunda m periode: m|a_n|i"""
    v = v_factor(i)
    return (v ** m) * annuity_immediate_pv(i, n)

# ============================================
# 6. FUNGSI FORMAT ANGKA
# ============================================

def format_rupiah(amount):
    """Format angka ke Rupiah"""
    return f"Rp {amount:,.0f}".replace(",", ".")

def format_percent(value, decimals=2):
    """Format ke persen"""
    return f"{value * 100:.{decimals}f}%"

def format_decimal(value, decimals=4):
    """Format desimal umum"""
    return f"{value:.{decimals}f}"

# ============================================
# 7. FUNGSI MENAMPILKAN HASIL DAN ERROR
# ============================================

def display_result_metric(label, value, format_func=format_rupiah):
    """Menampilkan hasil dalam bentuk metric Streamlit"""
    st.metric(label, format_func(value))

def display_error_messages(errors):
    """Menampilkan daftar error"""
    for err in errors:
        st.error(f"{err}")

def validate_and_display(errors):
    """Jika ada error, tampilkan dan return False"""
    if errors:
        display_error_messages(errors)
        return False
    return True