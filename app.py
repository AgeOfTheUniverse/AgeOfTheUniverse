import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plots 

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
        st.markdown("Total Amount of Supernovae Type 1a found by<br>Vera C. Rubin Observatory", unsafe_allow_html=True)
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
            "Min. Rotverschiebung (z)", 
            min_value=0.0, 
            max_value=z_max_data, 
            value=0.015, 
            step=0.001, 
            format="%.3f"
        )
        
        # Slider für H0 Bereich
        h0_range = st.slider(
            "H₀ Filterbereich", 
            min_value=20.0, 
            max_value=200.0, 
            value=(50.0, 150.0), # <-- Sinnvoller Default
            step=1.0
        )
        
        # Slider für Qualität (Elite)
        qual_p = st.slider("Qualitäts-Schwelle (Top %)", 0, 100, 50)
        
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
        count_placeholder.metric("Analysierbar", len(df_f), delta=len(df_f) - len(df_raw))
        st.metric("Davon Elite", anzahl_elite)

        return z_min, h0_range, qual_p, df_f, anzahl_elite
    
# --- 4. HAUPTSEITE LOGIK ---
def main():
    st.title("🔭 age-of-the-universe.com")
    st.markdown("### Echtzeit-Analyse der kosmischen Expansion")
    
    df_raw = load_data()

    # Sidebar aufrufen und alle berechneten Werte abholen
    z_min, h0_range, qual_p, df_f, anzahl_elite = draw_sidebar(df_raw)

    if df_f.empty:
        st.error("Keine Daten im gewählten Filterbereich gefunden. Bitte Slider anpassen.")
        return

    # Elite-Berechnung für Plots
    col_n = next((c for c in df_f.columns if c.lower() == 'ndiasources'), df_f.columns[0])
    schwelle = np.percentile(df_f[col_n], qual_p)
    df_elite = df_f[df_f[col_n] >= schwelle].copy()
    h0_elite = df_elite['h0_estimate'].median()
    h0_alle = df_f['h0_estimate'].median()

    # --- TABELLE ---
    st.subheader("Modellvergleich")
    vergleich_df = pd.DataFrame({
        "Planck (CMB)": ["67.4", f"{calc.calculate_universe_age(67.4, 0.95):.2f}"],
        "SH0ES (SN Ia)": ["73.0", f"{calc.calculate_universe_age(73.0, 0.96):.2f}"],
        "Rubin (Alle)": [f"{h0_alle:.1f}", f"{calc.calculate_universe_age(h0_alle, 0.96):.2f}"],
        "Elite (Deine Wahl)": [f"{h0_elite:.1f}", f"{calc.calculate_universe_age(h0_elite):.2f}"]
    }, index=["H₀ (km/s/Mpc)", "Weltalter (Mrd. J.)"])
    st.table(vergleich_df)

    # --- GRAFIKEN ---
    # --- GRAFIKEN ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Hier nutzen wir das neue Histogramm mit den 3 Linien
        fig1 = plots.plot_h0_distribution(df_elite, h0_elite)
        st.pyplot(fig1)

    with col_g2:
        # Hier nutzen wir den Scatterplot mit der Median-Linie
        # col_n wurde vorher in deiner main bereits definiert
        fig2 = plots.plot_h0_redshift(df_f, col_n, h0_elite)
        st.pyplot(fig2)

    # --- STABILISIERUNG ---
    df_k = calc.get_rolling_stats(df_f)
    if 'running_median' in df_k.columns:
        st.write("### Chronologische Konvergenz")
        # Zeit-Achse finden
        time_x = next((c for c in df_k.columns if c.lower() == 'lastdiasourcemjdtai'), df_k.index)
        
        # Hier nutzen wir den Konvergenz-Plot mit Planck & SH0ES Linien
        fig3 = plots.plot_convergence(df_k, time_x)
        st.pyplot(fig3)

    # --- FOOTER ---
    st.divider()
    st.markdown("**Impressum:** Rolf Bense, Jork | Kontakt: rolf.bense@web.de")
    st.caption("© 2026 age-of-the-universe.com")

if __name__ == "__main__":
    main()