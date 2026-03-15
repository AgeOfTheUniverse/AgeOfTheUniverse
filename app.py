import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Eigene Module
from data_provider import fetch_lasair_data
import calculations as calc

# 1. Config (Muss als allererstes stehen)
st.set_page_config(page_title="The Age of the Universe", page_icon="🌌", layout="wide")

# 2. Daten laden
@st.cache_data(ttl=3600)
def load_data():
    return fetch_lasair_data()

df_raw = load_data()

# 3. Sidebar & Filter Logik
def draw_sidebar(df):
    with st.sidebar:
        st.header("📡 Status & Filter")
        is_api = "lastdiasourcemjdtai" in df.columns
        if is_api:
            st.success("Verbindung: Lasair Live")
        else:
            st.warning("Quelle: Backup-Daten")
        
        st.divider()
        z_min = st.slider("Min. Rotverschiebung (z)", 0.0, 0.1, 0.02, 0.01)
        h0_range = st.slider("H₀ Bereich", 20, 150, (40, 120))
        qual_p = st.slider("Elite-Schwelle (Top %)", 0, 100, 50)
        return z_min, h0_range, qual_p

# 4. Haupt-Layout
# 4. Haupt-Layout
def main():
    st.title("🔭 age-of-the-universe.com")
    st.markdown("### Echtzeit-Kosmologie Monitor")
    
    z_min, h0_range, qual_p = draw_sidebar(df_raw)
    
    # --- NEU: DATEN-METRIKEN ANZEIGEN ---
    # Filterung vorbereiten
    df_f = df_raw[(df_raw['z'] > z_min) & (df_raw['h0_estimate'].between(h0_range[0], h0_range[1]))].copy()
    
    # Drei Spalten für die Kennzahlen
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Supernovae (Gesamt)", len(df_raw))
    with m2:
        st.metric("Nach Filtern", len(df_f), delta=f"{len(df_f) - len(df_raw)}", delta_color="normal")
    with m3:
        # Wir berechnen kurz die Elite-Menge für die Anzeige
        col_n = next((c for c in df_f.columns if c.lower() == 'ndiasources'), df_f.columns[0])
        if not df_f.empty:
            schwelle = np.percentile(df_f[col_n], qual_p)
            anzahl_elite = len(df_f[df_f[col_n] >= schwelle])
            st.metric("Elite-Daten", anzahl_elite)
        else:
            st.metric("Elite-Daten", 0)

    st.divider()

    if df_f.empty:
        st.error("Keine Daten im Filterbereich gefunden.")
        return
    
    # ... hier geht es weiter mit der Elite-Berechnung (h0_elite etc.) und der Tabelle ...

    # Elite-Berechnung (Nutzt nDiaSources Spalte)
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
    c1, c2 = st.columns(2)
    with c1:
        st.write("### H₀ Verteilung (Elite)")
        fig, ax = plt.subplots()
        sns.histplot(df_elite['h0_estimate'], kde=True, ax=ax, color="skyblue")
        ax.axvline(h0_elite, color="orange", label="Median")
        st.pyplot(fig)
    with c2:
        st.write("### H₀ vs. Rotverschiebung")
        fig, ax = plt.subplots()
        ax.scatter(df_f['z'], df_f['h0_estimate'], alpha=0.4, c=df_f[col_n])
        st.pyplot(fig)

    # --- STABILISIERUNG ---
    st.write("### Chronologische Konvergenz")
    df_k = calc.get_rolling_stats(df_f)
    if 'running_median' in df_k.columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        time_x = next((c for c in df_k.columns if c.lower() == 'lastdiasourcemjdtai'), df_k.index)
        ax.plot(df_k[time_x], df_k['running_median'], color='purple', label="Trend")
        ax.fill_between(df_k[time_x], df_k['running_median'] - df_k['stderr'], df_k['running_median'] + df_k['stderr'], alpha=0.2, color='purple')
        ax.set_xlabel("Zeit (MJD)")
        ax.set_ylabel("H₀")
        st.pyplot(fig)

    # FOOTER
    st.divider()
    st.markdown(f"**Impressum:** Rolf Bense, Jork | Kontakt: rolf.bense@web.de")
    st.caption("© 2026 age-of-the-universe.com")

if __name__ == "__main__":
    main()