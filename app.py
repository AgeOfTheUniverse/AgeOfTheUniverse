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

# --- 2. DATEN LADEN ---
@st.cache_data(ttl=3600)
def load_data():
    return fetch_lasair_data()

df_raw = load_data()

# --- 3. SIDEBAR FUNKTION ---
def draw_sidebar(df_raw):
    with st.sidebar:
        st.header("📡 Status & Daten")
        
        # Verbindungstatus prüfen
        is_api = "lastdiasourcemjdtai" in df_raw.columns
        if is_api:
            st.success("Verbindung: Lasair Live")
        else:
            st.warning("Quelle: Backup-Daten")

        st.divider()

        # --- 1. METRICS BEREICH (OBEN) ---
        st.subheader("Aktuelle Auswahl")
        metric_container = st.container()
        
        st.divider()

        # --- 2. FILTER EINSTELLUNGEN ---
        st.subheader("Filter-Einstellungen")
        
        # Der Master-Schalter für deine Logik (Standard: AN)
        clean_default = st.checkbox("Nur valide Daten (H₀ & z vorhanden)", value=True)
        
        # Datenbasis für die Histogramme (alle 65 oder nur die 16 validen)
        df_hist_base = df_raw.dropna(subset=['h0_estimate', 'z']) if clean_default else df_raw

        # --- A. ROTVERSCHIEBUNG (z) ---
        # Slider zuerst für die Logik
        z_min = st.slider("Min. Rotverschiebung (z)", 0.0, 0.1, 0.0, 0.001, format="%.3f")
        
        # Histogramm exakt bündig zum Slider
        fig_z, ax_z = plt.subplots(figsize=(4, 0.8))
        z_data = df_hist_base['z'].dropna()
        if not z_data.empty:
            counts, bins, patches = ax_z.hist(z_data, bins=50, range=(0.0, 0.1), color="lightgray", alpha=0.3)
            # Dynamische Einfärbung: Blau wenn >= Slider, sonst Rot
            for count, bin_edge, patch in zip(counts, bins, patches):
                if bin_edge >= z_min:
                    patch.set_facecolor('#4682B4')
                    patch.set_alpha(0.8)
                else:
                    patch.set_facecolor('#FF4B4B') # Streamlit-Rot
                    patch.set_alpha(0.2)
        
        ax_z.set_xlim(0.0, 0.1)
        ax_z.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        st.pyplot(fig_z)

        # --- B. HUBBLE-KONSTANTE (H₀) ---
        h0_range = st.slider("H₀ Bereich", 20, 150, (20, 150))
        
        fig_h, ax_h = plt.subplots(figsize=(4, 0.8))
        h_data = df_hist_base['h0_estimate'].dropna()
        if not h_data.empty:
            counts, bins, patches = ax_h.hist(h_data, bins=50, range=(20, 150), color="lightgray", alpha=0.3)
            for count, bin_edge, patch in zip(counts, bins, patches):
                if h0_range[0] <= bin_edge <= h0_range[1]:
                    patch.set_facecolor('#4682B4')
                    patch.set_alpha(0.8)
                else:
                    patch.set_facecolor('#FF4B4B')
                    patch.set_alpha(0.2)
                    
        ax_h.set_xlim(20, 150)
        ax_h.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        st.pyplot(fig_h)

        # --- C. DATENQUALITÄT (ELITE) ---
        col_n = next((c for c in df_raw.columns if c.lower() == 'ndiasources'), df_raw.columns[0])
        qual_p = st.slider("Elite-Schwelle (Top %)", 0, 100, 50)
        
        fig_q, ax_q = plt.subplots(figsize=(4, 0.8))
        q_data = df_hist_base[col_n].dropna()
        q_max = float(df_raw[col_n].max()) if not df_raw[col_n].empty else 100
        if not q_data.empty:
            ax_q.hist(q_data, bins=50, range=(0, q_max), color="#4682B4", alpha=0.6)
            
        ax_q.set_xlim(0, q_max)
        ax_q.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        st.pyplot(fig_q)

        # --- 3. FINALE FILTER-LOGIK (KEINE VERSTECKTEN FILTER!) ---
        df_f = df_raw.copy()
        
        if clean_default:
            df_f = df_f.dropna(subset=['h0_estimate', 'z'])
            
        df_f = df_f[
            (df_f['z'] >= z_min) & 
            (df_f['h0_estimate'] >= h0_range[0]) & 
            (df_f['h0_estimate'] <= h0_range[1])
        ]
        
        # Elite-Anzahl berechnen
        anzahl_elite = 0
        if not df_f.empty:
            schwelle = np.percentile(df_f[col_n].dropna(), qual_p)
            anzahl_elite = len(df_f[df_f[col_n] >= schwelle])

        # Metrics in den oberen Container schreiben
        with metric_container:
            c1, c2 = st.columns(2)
            c1.metric("Basis (Gesamt)", len(df_raw))
            # Delta zeigt jetzt genau an, wie viele durch Slider + Checkbox verloren gehen
            c2.metric("Aktiv", len(df_f), delta=len(df_f) - len(df_raw))
            st.metric("Elite-Auswahl", anzahl_elite)
            
        return z_min, h0_range, qual_p, df_f, anzahl_elite
    
# --- 4. HAUPTSEITE LOGIK ---
def main():
    st.title("🔭 age-of-the-universe.com")
    st.markdown("### Echtzeit-Analyse der kosmischen Expansion")
    
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
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.write("### H₀ Verteilung (Elite)")
        fig1, ax1 = plt.subplots()
        sns.histplot(df_elite['h0_estimate'], kde=True, ax=ax1, color="skyblue")
        ax1.axvline(h0_elite, color="orange", linewidth=2, label=f"Median: {h0_elite:.1f}")
        ax1.legend()
        st.pyplot(fig1)

    with col_g2:
        st.write("### H₀ vs. Rotverschiebung")
        fig2, ax2 = plt.subplots()
        scatter = ax2.scatter(df_f['z'], df_f['h0_estimate'], alpha=0.4, c=df_f[col_n], cmap='viridis')
        ax2.set_xlabel("Rotverschiebung (z)")
        ax2.set_ylabel("H₀")
        plt.colorbar(scatter, label="Datenqualität")
        st.pyplot(fig2)

    # --- STABILISIERUNG ---
    st.write("### Chronologische Konvergenz")
    df_k = calc.get_rolling_stats(df_f)
    if 'running_median' in df_k.columns:
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        time_x = next((c for c in df_k.columns if c.lower() == 'lastdiasourcemjdtai'), df_k.index)
        ax3.plot(df_k[time_x], df_k['running_median'], color='purple', linewidth=2)
        ax3.fill_between(df_k[time_x], df_k['running_median'] - df_k['stderr'], 
                         df_k['running_median'] + df_k['stderr'], alpha=0.2, color='purple')
        st.pyplot(fig3)

    # --- FOOTER ---
    st.divider()
    st.markdown("**Impressum:** Rolf Bense, Jork | Kontakt: rolf.bense@web.de")
    st.caption("© 2026 age-of-the-universe.com")

if __name__ == "__main__":
    main()