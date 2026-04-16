import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import plots
from about_project import render_about_project

# Eigene Module importieren
from data_provider import fetch_lasair_data
import calculations as calc

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="The Age of the Universe",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DATEN LADEN ---
@st.cache_data(ttl=3600)
def load_data():
    return fetch_lasair_data()

def draw_sidebar(df_raw):
    with st.sidebar:
        st.header("📡 Status & Filters")
        
        # 1. DATEN-VORBEREITUNG
        df_valid = df_raw.dropna(subset=['z', 'h0_estimate']).copy()
        df_valid = df_valid[(df_valid['z'] > 0) & (df_valid['h0_estimate'] > 0)]
        
        # METRICS
        st.markdown("**Total SN Type 1a** (confirmed by Rubin/Lasair)")
        st.metric("", len(df_raw))
        
        # NEU: Kleine Grafik in der Sidebar zur Entdeckungshistorie
        with st.expander("Show Discovery Timeline", expanded=False):
            fig_side = plots.plot_discovery_stats(df_raw)
            st.pyplot(fig_side)
        
        st.divider()

        # 2. DYNAMISCHE SLIDER
        z_max_data = float(df_valid['z'].max()) if not df_valid.empty else 0.1
        
        z_min = st.slider(
            "Min. Redshift (z)", 
            min_value=0.0, 
            max_value=z_max_data, 
            value=0.015, 
            step=0.001, 
            format="%.3f"
        )
        
        h0_range = st.slider(
            "H₀ Filter Range", 
            min_value=20.0, 
            max_value=200.0, 
            value=(50.0, 150.0),
            step=1.0
        )
        
        # Tippfehler korrigiert: Quality Threshold
        qual_p = st.slider("Quality Threshold (Top %)", 0, 100, 50)
        
        # 3. FILTERUNG ANWENDEN
        df_f = df_valid[
            (df_valid['z'] >= z_min) & 
            (df_valid['h0_estimate'].between(h0_range[0], h0_range[1]))
        ].copy()

        # Elite-Berechnung
        col_n = next((c for c in df_raw.columns if c.lower() == 'ndiasources'), df_raw.columns[0])
        anzahl_elite = 0
        if not df_f.empty:
            schwelle = np.percentile(df_f[col_n].fillna(0), qual_p)
            anzahl_elite = len(df_f[df_f[col_n] >= schwelle])

        # Status Metrics
        st.metric("Used after filtering", len(df_f), delta=len(df_f) - len(df_raw))
        st.metric("Elite Selection", anzahl_elite)

        return z_min, h0_range, qual_p, df_f, anzahl_elite
    
def render_about_me():
    st.title("About Me")
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### Contact Details")
        st.info("**Rolf Bense** 📍 Jork, Germany\n\n📧 [rolf.bense@web.de](mailto:rolf.bense@web.de)")
        st.markdown("### Interests")
        st.write("🔭 Observational Cosmology\n💻 Data Science & Python\n🌌 Open Science Communication")
    with col2:
        st.markdown("### The Person Behind the Project")
        st.write("Hi, I'm Rolf. I am a passionate astronomy enthusiast based in Northern Germany. My fascination with the stars led me to the question that has occupied the greatest minds in physics for decades: **How fast is our universe really expanding?**")
        st.write("With the advent of next-generation observatories like the **Vera C. Rubin Observatory**, we are entering a new era of 'Big Data' in astronomy. I built this platform to bridge the gap between raw scientific data streams and interactive visualization.")
        st.success("✨ *\"Equipped with his five senses, man explores the universe around him and calls the adventure Science.\"* – Edwin Hubble")

def main():
    # --- NAVIGATION ---
    with st.sidebar:
        st.title("🌌 Navigation")
        page = st.selectbox("Menu", ["Analysis", "About the Project", "About Me"], label_visibility="collapsed")
        st.divider()

    df_raw = load_data()


    if page == "Analysis":
        st.title("🔭 age-of-the-universe.com")
        st.markdown("### Real-time Analysis of Cosmic Expansion")
        
        z_min, h0_range, qual_p, df_f, anzahl_elite = draw_sidebar(df_raw)

        if df_f.empty:
            st.error("No data found for the selected filters. Please adjust the sliders.")
            return

        # Calculations
        col_n = next((c for c in df_f.columns if c.lower() == 'ndiasources'), df_f.columns[0])
        schwelle = np.percentile(df_f[col_n], qual_p)
        df_elite = df_f[df_f[col_n] >= schwelle].copy()
        h0_elite = df_elite['h0_estimate'].median()
        h0_alle = df_f['h0_estimate'].median()

        # --- TABLE ---
        st.subheader("Model Comparison")
        vergleich_df = pd.DataFrame({
            "Planck (CMB)": ["67.4", f"{calc.calculate_universe_age(67.4, 0.95):.2f}"],
            "SH0ES (SN Ia)": ["73.0", f"{calc.calculate_universe_age(73.0, 0.96):.2f}"],
            "Rubin (All)": [f"{h0_alle:.1f}", f"{calc.calculate_universe_age(h0_alle, 0.96):.2f}"],
            "Elite (Your Choice)": [f"{h0_elite:.1f}", f"{calc.calculate_universe_age(h0_elite):.2f}"]
        }, index=["H₀ (km/s/Mpc)", "Age of the Universe (Gyr)"])
        st.table(vergleich_df)

        # --- GRAFIKEN ---
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.pyplot(plots.plot_h0_distribution(df_elite, h0_elite))
        with col_g2:
            st.pyplot(plots.plot_h0_redshift(df_f, col_n, h0_elite))

        # --- STABILISIERUNG ---
        df_k = calc.get_rolling_stats(df_f)
        if 'running_median' in df_k.columns:
            st.write("### Chronological Convergence")
            time_x = next((c for c in df_k.columns if c.lower() == 'lastdiasourcemjdtai'), df_k.index)
            st.pyplot(plots.plot_convergence(df_k, time_x))

    elif page == "About the Project":
        render_about_project()

    elif page == "About Me":
        render_about_me()

    st.divider()
    st.caption("© 2026 age-of-the-universe.com | Jork, Germany")

if __name__ == "__main__":
    main()
