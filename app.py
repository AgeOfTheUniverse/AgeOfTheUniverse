import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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

# --- 2. DATEN LADEN (GECACHED) ---
@st.cache_data(ttl=3600)
def load_data():
    return fetch_lasair_data()

df_raw = load_data()

# --- 3. SIDEBAR FUNKTION (JETZT MIT ZAHLEN) ---
def draw_sidebar(df_raw):
    with st.sidebar:
        st.header("📡 Status & Daten")
        
        # Verbindungstatus
        is_api = "lastdiasourcemjdtai" in df_raw.columns
        if is_api:
            st.success("Verbindung: Lasair Live")
            st.caption(f"Letzter Abgleich: {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.warning("Quelle: Backup-Daten (CSV)")

        st.divider()

        # --- NEU: Kennzahlen in der Sidebar ---
        st.subheader("Daten-Statistik")
        
        # Wir definieren hier schon mal die Filterwerte, um die Vorschau-Zahlen zu berechnen
        z_min = st.slider("Min. Rotverschiebung (z)", 0.0, 0.1, 0.02, 0.01)
        h0_range = st.slider("H₀ Bereich", 20, 150, (40, 120))
        qual_p = st.slider("Elite-Schwelle (Top %)", 0, 100, 50)
        
        st.divider()
        
        # Berechnung der Mengen für die Anzeige
        df_f = df_raw[(df_raw['z'] > z_min) & (df_raw['h0_estimate'].between(h0_range[0], h0_range[1]))].copy()
        
        col_n = next((c for c in df_f.columns if c.lower() == 'ndiasources'), df_f.columns[0])
        anzahl_elite = 0
        if not df_f.empty:
            schwelle = np.percentile(df_f[col_n], qual_p)
            anzahl_elite = len(df_f[df_f[col_n] >= schwelle])

        # Anzeige der Metrics untereinander in der Sidebar
        st.metric("Supernovae (Basis)", len(df_raw))
        st.metric("Nach Filter", len(df_f), delta=len(df_f) - len(df_raw))
        st.metric("Elite-Auswahl", anzahl_elite)
        
        return z_min, h0_range, qual_p

# --- 4. HAUPTSEITE LAYOUT ---
def main():
    st.title("🔭 age-of-the-universe.com")
    st.markdown("### Echtzeit-Kosmologie Monitor")
    
    # Sidebar aufrufen und Filterwerte erhalten
    z_min, h0_range, qual_p = draw_sidebar(df_raw)
    
    # Filterung für die Hauptseite anwenden
    df_f = df_raw[(df_raw['z'] > z_min) & (df_raw['h0_estimate'].between(h0_range[0], h0_range[1]))].copy()

    if df_f.empty:
        st.error("Keine Daten im gewählten Filterbereich gefunden. Bitte die Slider anpassen.")
        return

    # Elite-Berechnung für Tabellen und Plots
    col_n = next((c for c in df_f.columns if c.lower() == 'ndiasources'), df_f.columns[0])
    schwelle = np.percentile(df_f[col_n], qual_p)
    df_elite = df_f[df_f[col_n] >= schwelle].copy()
    
    h0_elite = df_elite['h0_estimate'].median()
    h0_alle = df_f['h0_estimate'].median()

    # --- TABELLE ---
    st.subheader("Vergleich der kosmologischen Modelle")
    vergleich_df = pd.DataFrame({
        "Planck (CMB)": ["67.4", f"{calc.calculate_universe_age(67.4, 0.95):.2f}"],
        "SH0ES (SN Ia)": ["73.0", f"{calc.calculate_universe_age(73.0, 0.96):.2f}"],
        "Rubin (Alle)": [f"{h0_alle:.1f}", f"{calc.calculate_universe_age(h0_alle, 0.96):.2f}"],
        "Elite (Deine Wahl)": [f"{h0_elite:.1f}", f"{calc.calculate_universe_age(h0_elite):.2f}"]
    }, index=["H₀ (km/s/Mpc)", "Weltalter (Mrd. J.)"])
    st.table(vergleich_df)

    # --- GRAFIKEN ---
    c1, c2 = st.columns(2)
    with c1:
        st.write("### H₀ Verteilung (Elite)")
        fig1, ax1 = plt.subplots()
        sns.histplot(df_elite['h0_estimate'], kde=True, ax=ax1, color="skyblue")
        ax1.axvline(h0_elite, color="orange", linewidth=2, label=f"Median: {h0_elite:.1f}")
        ax1.legend()
        st.pyplot(fig1)
    with c2:
        st.write("### H₀ vs. Rotverschiebung")
        fig2, ax2 = plt.subplots()
        scatter = ax2.scatter(df_f['z'], df_f['h0_estimate'], alpha=0.4, c=df_f[col_n], cmap='viridis')
        ax2.set_xlabel("Rotverschiebung (z)")
        ax2.set_ylabel("H₀")
        plt.colorbar(scatter, label="Datenqualität (nDiaSources)")
        st.pyplot(fig2)

    # --- STABILISIERUNG ---
    st.write("### Chronologische Konvergenz")
    df_k = calc.get_rolling_stats(df_f)
    if 'running_median' in df_k.columns:
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        time_x = next((c for c in df_k.columns if c.lower() == 'lastdiasourcemjdtai'), df_k.index)
        ax3.plot(df_k[time_x], df_k['running_median'], color='purple', linewidth=2, label="Laufender Median")
        ax3.fill_between(df_k[time_x], 
                         df_k['running_median'] - df_k['stderr'], 
                         df_k['running_median'] + df_k['stderr'], 
                         alpha=0.2, color='purple')
        ax3.axhline(67.4, color='red', linestyle='--', alpha=0.5, label="Planck")
        ax3.axhline(73.0, color='green', linestyle='--', alpha=0.5, label="SH0ES")
        ax3.set_xlabel("Zeit (MJD)")
        ax3.set_ylabel("Hubble-Konstante H₀")
        ax3.legend()
        st.pyplot(fig3)

    # --- FOOTER ---
    st.divider()
    st.markdown(f"**Impressum:** Rolf Bense, Jork | Kontakt: rolf.bense@web.de")
    st.caption("© 2026 age-of-the-universe.com | Wissenschaftliche Live-Analyse")

if __name__ == "__main__":
    main()