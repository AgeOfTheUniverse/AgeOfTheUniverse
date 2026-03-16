import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
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
        st.header("📡 Status & Filter")
        
        # 1. DATEN-VORBEREITUNG
        # Wir filtern nur die Zeilen, die für eine Berechnung überhaupt nutzbar sind
        df_valid = df_raw.dropna(subset=['z', 'h0_estimate']).copy()
        df_valid = df_valid[(df_valid['z'] > 0) & (df_valid['h0_estimate'] > 0)]
        
        # METRICS
        st.markdown("Total Amount of Supernovae Type 1a found by Vera C. Rubin Observatory", unsafe_allow_html=True)
        st.metric("",len(df_raw))
        count_placeholder = st.empty()
        
        st.divider()

        # 2. DYNAMISCHE SLIDER
        # Wir holen uns Min/Max direkt aus den Daten, damit die Slider immer passen
        z_min_data = float(df_valid['z'].min()) if not df_valid.empty else 0.0
        z_max_data = float(df_valid['z'].max()) if not df_valid.empty else 0.1
        
        h0_min_data = float(df_valid['h0_estimate'].min()) if not df_valid.empty else 20.0
        h0_max_data = float(df_valid['h0_estimate'].max()) if not df_valid.empty else 150.0

        # Slider für Rotverschiebung
        # Voreingestellt auf 0.0, damit erst mal alles Sichtbare drin bleibt
        z_min = st.slider(
            "Min. Redshift (z)", 
            min_value=0.0, 
            max_value=z_max_data, 
            value=0.015, 
            step=0.001, 
            format="%.3f"
        )
        
        # Slider für H0 Bereich
        h0_range = st.slider(
            "H₀ Filter Range", 
            min_value=20.0, 
            max_value=200.0, 
            value=(50.0, 150.0), # <-- Sinnvoller Default
            step=1.0
        )
        
        # Slider für Qualität (Elite)
        qual_p = st.slider("Qualiity Threshhold (Top %)", 0, 100, 50)
        
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

        # Zahl aktualisieren
        count_placeholder.metric("Used after Filter application", len(df_f), delta=len(df_f) - len(df_raw))
        st.metric("Elite Selection", anzahl_elite)

        return z_min, h0_range, qual_p, df_f, anzahl_elite
    
# --- 4. HAUPTSEITE LOGIK ---
def render_about_me():
    st.title("About Me")
    
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        # Placeholder for a profile picture
        # If you have a photo, uncomment the line below:
        # st.image("your_photo.jpg", caption="Rolf Bense", use_column_width=True)
        
        st.markdown("### Contact Details")
        st.info("""
        **Rolf Bense** 📍 Jork, Germany  
        📧 [rolf.bense@web.de](mailto:rolf.bense@web.de)
        """)
        
        st.markdown("### Interests")
        st.write("🔭 Observational Cosmology")
        st.write("💻 Data Science & Python")
        st.write("🌌 Open Science Communication")

    with col2:
        st.markdown("### The Person Behind the Project")
        st.write("""
        Hi, I'm Rolf. I am a passionate astronomy enthusiast based in Northern Germany. 
        My fascination with the stars led me to the question that has occupied the greatest 
        minds in physics for decades: **How fast is our universe really expanding?**
        
        With the advent of next-generation observatories like the **Vera C. Rubin Observatory**, 
        we are entering a new era of "Big Data" in astronomy. I built this platform to bridge 
        the gap between raw scientific data streams and interactive visualization.
        """)
        
        st.markdown("### Why I Built This")
        st.write("""
        The "Hubble Tension"—the discrepancy between measurements from the early and late 
        universe—is one of the most exciting mysteries in modern science. I wanted to create 
        a tool that allows anyone to:
        * Explore real-time supernova data.
        * Understand the impact of data quality on cosmological constants.
        * Calculate the age of the universe with just a few clicks.
        """)
        
        st.success("✨ *\"Equipped with his five senses, man explores the universe around him and calls the adventure Science.\"* – Edwin Hubble")

def main():
    # --- NAVIGATION IN DER SIDEBAR ---
    with st.sidebar:
        # Ein kleines Logo oder Icon oben in der Sidebar macht sich gut
        st.title("🌌 Navigation")
        page = st.selectbox("Wähle eine Seite:", ["Analysis", "About the Project", "About Me"],
                            label_visibility="collapsed"
                            )
        st.divider()

    # --- DATEN LADEN (Immer notwendig für die Sidebar-Werte) ---
    df_raw = load_data()

    if page == "Analysis":
        # --- DEIN BISHERIGER ANALYSE-CODE ---
        st.title("🔭 age-of-the-universe.com")
        st.markdown("### ### Real-time Analysis of Cosmic Expansion")
        
        # Sidebar aufrufen (Filter erscheinen nur bei Analyse)
        z_min, h0_range, qual_p, df_f, anzahl_elite = draw_sidebar(df_raw)

        if df_f.empty:
            st.error("No data found for the selected filters. Please adjust the sliders.")
            return

        # Elite-Berechnung
        col_n = next((c for c in df_f.columns if c.lower() == 'ndiasources'), df_f.columns[0])
        schwelle = np.percentile(df_f[col_n], qual_p)
        df_elite = df_f[df_f[col_n] >= schwelle].copy()
        h0_elite = df_elite['h0_estimate'].median()
        h0_alle = df_f['h0_estimate'].median()

        # --- TABELLE ---
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
            fig1 = plots.plot_h0_distribution(df_elite, h0_elite)
            st.pyplot(fig1)
        with col_g2:
            fig2 = plots.plot_h0_redshift(df_f, col_n, h0_elite)
            st.pyplot(fig2)

        # --- STABILISIERUNG ---
        df_k = calc.get_rolling_stats(df_f)
        if 'running_median' in df_k.columns:
            st.write("### Chronological Convergence")
            time_x = next((c for c in df_k.columns if c.lower() == 'lastdiasourcemjdtai'), df_k.index)
            fig3 = plots.plot_convergence(df_k, time_x)
            st.pyplot(fig3)

    elif page == "About the Project":
        # Aufruf der neuen englischen Seite aus der separaten Datei
        render_about_project()

    elif page == "About Me":
        render_about_me()


    # --- EINHEITLICHER FOOTER ---
    st.divider()
    st.caption("© 2026 age-of-the-universe.com | Jork, Deutschland")

if __name__ == "__main__":
    main()