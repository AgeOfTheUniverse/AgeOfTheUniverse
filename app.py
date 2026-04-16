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
def load_data():
    return fetch_lasair_data()

def draw_sidebar(df_raw):
    st.sidebar.header("📡 Status & Filters")
    
    available_cols = df_raw.columns.tolist()
    
    # Prüfen, ob wissenschaftliche Daten für SN Ia vorhanden sind
    has_science_data = all(c in available_cols for c in ['z', 'h0_estimate'])
    
    if has_science_data:
        # Nur Zeilen behalten, die wirklich z und h0 haben
        df_valid = df_raw.dropna(subset=['z', 'h0_estimate']).copy()
        df_valid = df_valid[(df_valid['z'] > 0) & (df_valid['h0_estimate'] > 0)]
    else:
        df_valid = pd.DataFrame(columns=available_cols)

    # METRICS in der Sidebar
    st.sidebar.markdown("**Confirmed SN Type 1a**")
    st.sidebar.metric("", len(df_valid))
    
    # Die Entdeckungs-Grafik (Graue vs. Blaue Linie)
    with st.sidebar.expander("Show Discovery Timeline", expanded=False):
        fig_side = plots.plot_discovery_stats(df_raw)
        st.pyplot(fig_side)
    
    st.sidebar.divider()

    # SLIDER (Sicherheitscheck für leere Daten)
    z_max_val = float(df_valid['z'].max()) if not df_valid.empty else 0.5
    
    z_min = st.sidebar.slider("Min. Redshift (z)", 0.0, z_max_val, 0.015, 0.001, format="%.3f")
    h0_range = st.sidebar.slider("H₀ Filter Range", 20.0, 200.0, (50.0, 150.0), 1.0)
    qual_p = st.sidebar.slider("Quality Threshold (Top %)", 0, 100, 50)
    
    # FILTERUNG
    df_f = df_valid[
        (df_valid['z'] >= z_min) & 
        (df_valid['h0_estimate'].between(h0_range[0], h0_range[1]))
    ].copy()

    # Elite-Selektion
    col_n = next((c for c in df_raw.columns if c.lower() == 'ndiasources'), None)
    anzahl_elite = 0
    if not df_f.empty and col_n:
        df_f[col_n] = df_f[col_n].fillna(0)
        schwelle = np.percentile(df_f[col_n], qual_p)
        anzahl_elite = len(df_f[df_f[col_n] >= schwelle])

    st.sidebar.metric("Used in Analysis", len(df_f))
    st.sidebar.metric("Elite Selection", anzahl_elite)

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
        st.write("Hi, I'm Rolf. I built this platform to bridge the gap between raw scientific data streams and interactive visualization.")
        st.success("✨ *\"Equipped with his five senses, man explores the universe around him and calls the adventure Science.\"* – Edwin Hubble")

def main():
    # NAVIGATION
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
            st.warning("No validated Supernovae found for current filter settings. Try lowering the 'Min. Redshift'.")
            return

        # BERECHNUNGEN
        col_n = next((c for c in df_f.columns if c.lower() == 'ndiasources'), df_f.columns[0])
        schwelle = np.percentile(df_f[col_n], qual_p)
        df_elite = df_f[df_f[col_n] >= schwelle].copy()
        
        h0_elite = df_elite['h0_estimate'].median()
        h0_alle = df_f['h0_estimate'].median()

        # TABELLE
        st.subheader("Model Comparison")
        vergleich_df = pd.DataFrame({
            "Planck (CMB)": ["67.4", f"{calc.calculate_universe_age(67.4, 0.95):.2f}"],
            "SH0ES (SN Ia)": ["73.0", f"{calc.calculate_universe_age(73.0, 0.96):.2f}"],
            "Rubin (All)": [f"{h0_alle:.1f}", f"{calc.calculate_universe_age(h0_alle, 0.96):.2f}"],
            "Elite (Your Choice)": [f"{h0_elite:.1f}", f"{calc.calculate_universe_age(h0_elite):.2f}"]
        }, index=["H₀ (km/s/Mpc)", "Age of the Universe (Gyr)"])
        st.table(vergleich_df)

        # PLOTS
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.pyplot(plots.plot_h0_distribution(df_elite, h0_elite))
        with col_g2:
            st.pyplot(plots.plot_h0_redshift(df_f, col_n, h0_elite))

        # CONVERGENCE
        df_k = calc.get_rolling_stats(df_f)
        if not df_k.empty and 'running_median' in df_k.columns:
            st.write("### Chronological Convergence")
            time_x = next((c for c in df_k.columns if c.lower() == 'lastdiasourcemjdtai'), None)
            if time_x:
                st.pyplot(plots.plot_convergence(df_k, time_x))

    elif page == "About the Project":
        render_about_project()
    elif page == "About Me":
        render_about_me()

    st.divider()
    st.caption("© 2026 age-of-the-universe.com | Jork, Germany")

if __name__ == "__main__":
    main()
