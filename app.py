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
def get_cached_data():
    return fetch_lasair_data()

df_raw = get_cached_data()

# --- 3. SIDEBAR FUNKTION ---
def draw_sidebar(df):
    with st.sidebar:
        st.header("Status & Filter")
        # Check ob Daten von API kommen (Spalte ist dann kleingeschrieben)
        is_api = "lastdiasourcemjdtai" in df.columns
        
        if is_api:
            st.success("✅ VERBUNDEN: Lasair-API")
            st.caption(f"Letzter Abgleich: {datetime.now().strftime('%H:%M:%S')}")
        else:
            st.warning("⚠️ QUELLE: Lokale Backup-CSV")
            
        st.info(f"Objekte im Speicher: {len(df)}")
        st.divider()
        
        st.subheader("Filter-Einstellungen")
        z = st.slider("Minimale Rotverschiebung (z)", 0.0, 0.1, 0.02, 0.01)
        h0_range = st.slider("H₀ Bereich", 20, 150, (40, 120))
        qual = st.slider("Elite-Schwelle (Top % Qualität)", 0, 100, 50)
        
        return z, h0_range, qual

# --- 4. HAUPTSEITE LAYOUT ---
def draw_main_content(df_raw):
    st.title("🔭 age-of-the-universe.com")
    st.markdown("### Live-Analyse der Hubble-Konstante & des Weltalters")
    
    # Sidebar zeichnen und Werte abholen
    z_min, h0_range, qual_p = draw_sidebar(df_raw)
    
    # Filterung via calculations.py
    df_filtered = df_raw[(df_raw['z'] > z_min) & (df_raw['h0_estimate'].between(h0_range[0], h0_range[1]))].copy()

    if df_filtered.empty:
        st.error("Keine Daten im gewählten Filterbereich verfügbar!")
        return

    # Elite-Daten berechnen via calculations.py Logik
    # (Wir nutzen hier die kleingeschriebene Spalte 'ndiasources' vom Provider)
    col_n = 'ndiasources' if 'ndiasources' in df_filtered.columns else 'nDiaSources'
    schwelle = np.percentile(df_filtered[col_n], qual_p)
    df_elite = df_filtered[df_filtered[col_n] >= schwelle].copy()
    
    h0_elite = df_elite['h0_estimate'].median()
    h0_alle = df_filtered['h0_estimate'].median()

    # --- VERGLEICHS-TABELLE ---
    st.subheader("Vergleich der kosmologischen Modelle")
    
    # Weltalter-Berechnungen (Faktoren laut deinem Modell)
    alter_planck = calc.calculate_universe_age(67.4, 0.95)
    alter_shoes = calc.calculate_universe_age(73.0, 0.96)
    alter_alle = calc.calculate_universe_age(h0_alle, 0.96)
    alter_elite = calc.calculate_universe_age(h0_elite) # Lineare Hypothese (Faktor 1.0)

    vergleich_data = {
        "Planck (CMB)": ["67.4", f"{alter_planck:.2f}"],
        "SH0ES (SN Ia)": ["73.0", f"{alter_shoes:.2f}"],
        "Alle Rubin-Daten": [f"{h0_alle:.1f}", f"{alter_alle:.2f}"],
        "Elite-Daten (Deine Wahl)": [f"{h0_elite:.1f}", f"{alter_elite:.2f}"]
    }
    st.table(pd.DataFrame(vergleich_data, index=["Hubble-Konstante (H₀)", "Weltalter (Mrd. Jahre)"]))

    # --- GRAFIKEN ---
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.write("### Elite-Verteilung")
        fig1, ax1 = plt.subplots()
        sns.histplot(df_elite['h0_estimate'], bins=10, kde=True, ax=ax1, color='skyblue')
        ax1.axvline(h0_elite, color='gold', linewidth=3, label=f"Median: {h0_elite:.1f}")
        ax1.legend()
        st.pyplot(fig1)

    with col_g2:
        st.write("### H₀ vs. Rotverschiebung (Elite-Trend)")
        fig2, ax2 = plt.subplots()
        ax2.scatter(df_filtered['z'], df_filtered['h0_estimate'], c=df_filtered[col_n], alpha=0.5)
        if len(df_elite) > 1:
            m, b = np.polyfit(df_elite['z'], df_elite['h0_estimate'], 1)
            ax2.plot(df_filtered['z'], m*df_filtered['z'] + b, color='orange', label="Elite-Trend")
        ax2.legend()
        st.pyplot(fig2)

    # --- STABILISIERUNGS-PLOT ---
    def get_rolling_stats(df):
    """Berechnet den laufenden Median und den statistischen Fehler."""
    # WICHTIG: Die Spalte muss hier kleingeschrieben sein
    col_time = 'lastdiasourcemjdtai' 
    
    if col_time not in df.columns:
        # Falls die Spalte doch großgeschrieben ist, hier abfangen
        available = [c for c in df.columns if c.lower() == col_time]
        if available:
            col_time = available[0]
        else:
            return df # Sicherheits-Fallback, falls Spalte fehlt

    df_sorted = df.sort_values(col_time).copy()
    df_sorted['running_median'] = df_sorted['h0_estimate'].expanding().median()
    df_sorted['running_std'] = df_sorted['h0_estimate'].expanding().std()
    df_sorted['running_n'] = np.arange(1, len(df_sorted) + 1)
    df_sorted['stderr'] = df_sorted['running_std'] / np.sqrt(df_sorted['running_n'])
    return df_sorted

# --- 5. FOOTER & INFOS ---
def draw_footer():
    st.divider()
    st.markdown("""
    ### Über dieses Projekt
    Dieses Dashboard analysiert die Expansion des Universums in Echtzeit. 
    Während das Standardmodell der Kosmologie einen Korrekturfaktor für die Dunkle Energie nutzt, 
    basiert die Spalte **'Elite-Daten'** auf einer rein linearen Expansionshypothese ($t = 1/H_0$).
    """)
    st.divider()
    m_col1, m_col2 = st.columns([2, 1])
    with m_col1:
        st.markdown("#### Impressum & Kontakt\n**Herausgeber:** Rolf Bense | Achtern Wehrt Hoff 1 | 21635 Jork\n\n**Kontakt:** 📧 rolf.bense@web.de")
    with m_col2:
        st.markdown("#### Über die Daten\nDie Analysen basieren auf SN Ia Daten des **Vera C. Rubin Observatory**, bereitgestellt durch den **Lasair Broker**.")
    st.caption("© 2026 age-of-the-universe.com | Wissenschaftliche Analyse")

# --- APP STARTEN ---
if __name__ == "__main__":
    draw_main_content(df_raw)
    draw_footer()